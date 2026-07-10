import logging
import asyncio
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import ScheduledClosure
from services.close_service import CloseService

logger = logging.getLogger(__name__)

# Global flag to control the background loop
_scheduler_task: Optional[asyncio.Task] = None
_stop_event = asyncio.Event()

def calculate_next_run(
    frequency: str,
    scheduled_time_str: str,
    specific_date: Optional[date] = None,
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None,
    base_dt: Optional[datetime] = None,
    tz: Optional[timezone] = None
) -> datetime:
    """
    Calcula la fecha y hora de la siguiente ejecución.
    
    Args:
        frequency: "once", "daily", "weekly", "monthly"
        scheduled_time_str: Formato "HH:MM", ej: "18:00"
        specific_date: Fecha específica para frecuencia "once"
        day_of_week: 0 (Lunes) a 6 (Domingo) para frecuencia "weekly"
        day_of_month: 1 a 31 para frecuencia "monthly"
        base_dt: Datetime base desde el cual calcular
        tz: Zona horaria para la ejecución (defecto: tz de base_dt o local de sistema)
    """
    if tz is None:
        if base_dt is not None and base_dt.tzinfo is not None:
            tz = base_dt.tzinfo
        else:
            tz = datetime.now().astimezone().tzinfo

    if base_dt is None:
        base_dt = datetime.now(tz)
    else:
        base_dt = base_dt.astimezone(tz)
        
    try:
        hour, minute = map(int, scheduled_time_str.split(":"))
    except ValueError:
        logger.error(f"Formato de hora inválido: {scheduled_time_str}")
        hour, minute = 0, 0
    
    if frequency == "once":
        if not specific_date:
            specific_date = base_dt.date()
        target_dt = datetime.combine(specific_date, time(hour, minute)).replace(tzinfo=tz)
        # Si la fecha/hora programada ya pasó, dejamos que sea en el pasado (se ejecutará inmediato o marcará expirado)
        return target_dt

    elif frequency == "daily":
        target_dt = datetime.combine(base_dt.date(), time(hour, minute)).replace(tzinfo=tz)
        if target_dt <= base_dt:
            target_dt += timedelta(days=1)
        return target_dt

    elif frequency == "weekly":
        if day_of_week is None:
            day_of_week = 0
        days_ahead = day_of_week - base_dt.weekday()
        if days_ahead < 0:
            days_ahead += 7
        target_dt = datetime.combine(base_dt.date() + timedelta(days=days_ahead), time(hour, minute)).replace(tzinfo=tz)
        if target_dt <= base_dt:
            target_dt += timedelta(days=7)
        return target_dt

    elif frequency == "monthly":
        if day_of_month is None:
            day_of_month = 1
            
        current_year = base_dt.year
        current_month = base_dt.month
        
        # Intentar en el mes actual
        try:
            # Si el día del mes excede los días de este mes, cap al último día
            import calendar
            last_day = calendar.monthrange(current_year, current_month)[1]
            target_day = min(day_of_month, last_day)
            target_dt = datetime.combine(date(current_year, current_month, target_day), time(hour, minute)).replace(tzinfo=tz)
        except Exception:
            target_dt = base_dt  # Fallback seguro
            
        if target_dt <= base_dt:
            # Calcular para el próximo mes
            next_month = current_month + 1
            next_year = current_year
            if next_month > 12:
                next_month = 1
                next_year += 1
            import calendar
            last_day = calendar.monthrange(next_year, next_month)[1]
            target_day = min(day_of_month, last_day)
            target_dt = datetime.combine(date(next_year, next_month, target_day), time(hour, minute)).replace(tzinfo=tz)
            
        return target_dt

    # Fallback por si la frecuencia no es conocida
    return base_dt + timedelta(days=1)


async def check_and_run_schedules():
    """
    Busca programaciones pendientes de ejecución, las ejecuta,
    y recalcula su next_run.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        
        # Obtener programaciones activas pendientes
        pending_schedules = db.query(ScheduledClosure).filter(
            ScheduledClosure.is_active == True,
            ScheduledClosure.next_run <= now
        ).all()
        
        if not pending_schedules:
            return
            
        logger.info(f"⏰ Scheduler: Detectadas {len(pending_schedules)} programaciones pendientes...")
        
        for schedule in pending_schedules:
            try:
                logger.info(f"🚀 Ejecutando cierre programado ID={schedule.id} (Frecuencia={schedule.frequency})...")
                
                # Ejecutar cierre masivo llamando a CloseService
                # La fecha_inicio y fecha_fin para cierres programados diarios/semanales suele ser el día actual
                fecha_actual = date.today()
                
                # Ejecutamos el cierre masivo de contadores
                # Para un scheduler automático, indicamos cerrado_por='Sistema (Programado)'
                results = CloseService.create_close_all_printers(
                    db=db,
                    fecha_inicio=fecha_actual,
                    fecha_fin=fecha_actual,
                    cerrado_por="Sistema (Programado)",
                    notas=schedule.notas or "Cierre masivo ejecutado automáticamente por programación horaria.",
                    empresa_id=schedule.empresa_id
                )
                
                logger.info(f"✅ Cierre masivo ID={schedule.id} completado: {results.get('successful', 0)} exitosos, {results.get('failed', 0)} fallidos.")
                
                # Registrar log de auditoría
                try:
                    from db.audit_db import log_security_event
                    log_security_event(
                        action="SCHEDULED_CLOSURE_RUN",
                        executor="system",
                        status="success",
                        ip_address="127.0.0.1",
                        details=f"Programación ID={schedule.id} ({schedule.frequency}) ejecutada. Cierres exitosos: {results.get('successful')}, fallados: {results.get('failed')}"
                    )
                except Exception as ae:
                    logger.error(f"Error registrando auditoria de cierre programado: {ae}")

                # Actualizar campos de control de ejecución
                schedule.last_run = now
                if schedule.frequency == "once":
                    # Las programaciones únicas se desactivan una vez ejecutadas
                    schedule.is_active = False
                    schedule.next_run = None
                else:
                    # Recalcular siguiente ejecución basada en la fecha/hora actual
                    schedule.next_run = calculate_next_run(
                        frequency=schedule.frequency,
                        scheduled_time_str=schedule.scheduled_time,
                        day_of_week=schedule.day_of_week,
                        day_of_month=schedule.day_of_month,
                        base_dt=now,
                        tz=datetime.now().astimezone().tzinfo
                    )
                
                db.commit()
                
            except Exception as job_err:
                db.rollback()
                logger.error(f"❌ Error ejecutando programación ID={schedule.id}: {job_err}")
                
    except Exception as e:
        logger.error(f"Error general en check_and_run_schedules: {e}")
    finally:
        db.close()


async def run_scheduler_periodically():
    """
    Bucle periódico ejecutado por asyncio que corre cada 60 segundos
    para comprobar programaciones.
    """
    logger.info("⏰ Bucle periódico del programador iniciado (intervalo de 60 segundos).")
    _stop_event.clear()
    
    while not _stop_event.is_set():
        try:
            await check_and_run_schedules()
        except asyncio.CancelledError:
            logger.info("⏰ Bucle del programador cancelado.")
            break
        except Exception as e:
            logger.error(f"Excepción en el bucle del programador: {e}")
            
        try:
            # Esperar 60 segundos de forma cancelable
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            break
            
    logger.info("⏰ Bucle periódico del programador finalizado.")

"""
Servicio para sincronizar usuarios detectados en equipos con la tabla users.
Implementa sincronización automática al leer contadores.

IMPORTANTE: Los códigos de usuario en Ricoh son de 4 dígitos con formato fijo.
NO se deben eliminar ceros a la izquierda. Ejemplo: "0547" es el código correcto.
"""

from sqlalchemy.orm import Session
from db.models import User, ContadorUsuario
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


def format_user_code(code: str) -> str:
    """
    Formatea código de usuario a 4 dígitos con ceros a la izquierda.
    
    Los códigos de usuario en Ricoh son de 4 dígitos con formato fijo.
    Esta función asegura que el código tenga el formato correcto.
    
    Args:
        code: Código de usuario (puede venir sin ceros a la izquierda)
    
    Returns:
        Código formateado a 4 dígitos con ceros a la izquierda
    
    Examples:
        >>> format_user_code("547")
        "0547"
        >>> format_user_code("8599")
        "8599"
        >>> format_user_code("37")
        "0037"
        >>> format_user_code("0547")
        "0547"
    """
    if not code or not code.strip():
        return "0000"
    
    # Eliminar espacios
    code_clean = code.strip()
    
    # Si el código tiene más de 4 dígitos, dejarlo como está
    if len(code_clean) > 4:
        return code_clean
    
    # Rellenar con ceros a la izquierda hasta 4 dígitos
    return code_clean.zfill(4)


class UserSyncService:
    """
    Servicio para sincronizar usuarios detectados en equipos
    con la tabla users.
    
    Este servicio implementa la sincronización automática:
    - Primera vez: Crea masivamente usuarios faltantes
    - Lecturas posteriores: Solo crea usuarios nuevos
    """
    
    @staticmethod
    def sync_user_from_counter(
        codigo_usuario: str,
        nombre_usuario: str,
        db: Session,
        printer_id: Optional[int] = None,
        smb_path: Optional[str] = None  # ← NUEVO: ruta SMB desde libreta de direcciones
    ) -> int:
        """
        Sincroniza un usuario detectado en contador.
        Si no existe, lo crea automáticamente con permisos deshabilitados.
        
        IMPORTANTE: Formatea el código de usuario a 4 dígitos con ceros a la izquierda.
        Los códigos en Ricoh son de formato fijo de 4 dígitos (ej: "0547").
        
        Args:
            codigo_usuario: Código único del usuario (puede venir sin ceros)
            nombre_usuario: Nombre completo del usuario
            db: Sesión de base de datos
            printer_id: ID de la impresora donde se detectó (opcional, para logging)
            smb_path: Ruta SMB desde libreta de direcciones (opcional)
        
        Returns:
            user_id del usuario (existente o recién creado)
        """
        # ✓ FORMATEAR código a 4 dígitos con ceros a la izquierda
        codigo_formateado = format_user_code(codigo_usuario)
        
        # Buscar usuario existente por código FORMATEADO
        user = db.query(User).filter(
            User.codigo_de_usuario == codigo_formateado
        ).first()
        
        if user:
            # Usuario ya existe, retornar su ID
            return user.id
        
        # Determinar ruta SMB
        if smb_path and smb_path.strip():
            # Usar ruta desde libreta de direcciones
            final_smb_path = smb_path.strip()
        else:
            # Usar carpeta compartida genérica como fallback
            final_smb_path = "\\\\192.168.91.5\\Escaner"
        
        # Usuario no existe, crear automáticamente con código FORMATEADO
        new_user = User(
            name=nombre_usuario,
            codigo_de_usuario=codigo_formateado,  # ← Código formateado a 4 dígitos (ej: "0547")
            network_username="reliteltda\\scaner",  # Valor por defecto del sistema
            network_password_encrypted="",  # Sin password inicial
            smb_server="192.168.91.5",  # Servidor SMB por defecto
            smb_port=21,
            smb_path=final_smb_path,  # Ruta desde libreta o genérica
            func_copier=False,  # Permisos deshabilitados por defecto
            func_printer=False,  # Se habilitan manualmente según necesidad
            func_scanner=False,
            is_active=True  # Usuario activo (detectado en equipo)
        )
        
        db.add(new_user)
        db.flush()  # Para obtener el ID sin hacer commit
        
        printer_info = f" en impresora {printer_id}" if printer_id else ""
        codigo_info = f" (formateado: '{codigo_usuario}' → '{codigo_formateado}')" if codigo_usuario != codigo_formateado else ""
        logger.info(
            f"✓ Usuario auto-creado{printer_info}: "
            f"{codigo_formateado} - {nombre_usuario}{codigo_info} (ID: {new_user.id}, SMB: {final_smb_path})"
        )
        
        return new_user.id
    
    @staticmethod
    def sync_all_users_from_counters(db: Session, days: int = 30) -> Dict[str, int]:
        """
        Sincronización masiva de todos los usuarios detectados en contadores.
        Útil para la migración inicial.
        
        Args:
            db: Sesión de base de datos
            days: Días hacia atrás para considerar usuarios activos
        
        Returns:
            dict con estadísticas: {created: int, existing: int, total: int}
        """
        logger.info(f"Iniciando sincronización masiva de usuarios (últimos {days} días)...")
        
        # Obtener usuarios únicos de contadores (últimos N días)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Obtener user_ids únicos y luego los datos de users
        usuarios_detectados = db.query(
            User.id,
            User.codigo_de_usuario,
            User.name
        ).join(
            ContadorUsuario, User.id == ContadorUsuario.user_id
        ).filter(
            ContadorUsuario.fecha_lectura >= cutoff_date
        ).distinct().all()
        
        logger.info(f"Encontrados {len(usuarios_detectados)} usuarios únicos en contadores")
        
        created = 0
        existing = len(usuarios_detectados)  # Ya existen todos porque vienen de users
        errors = 0
        
        for codigo, nombre in usuarios_detectados:
            try:
                # Verificar si existe
                user = db.query(User).filter(
                    User.codigo_de_usuario == codigo
                ).first()
                
                if user:
                    existing += 1
                else:
                    # Crear usuario
                    new_user = User(
                        name=nombre,
                        codigo_de_usuario=codigo,
                        network_username="reliteltda\\scaner",
                        network_password_encrypted="",
                        smb_server="192.168.91.5",
                        smb_port=21,
                        smb_path="\\\\PENDIENTE\\Escaner",  # Placeholder - configurar manualmente
                        func_copier=False,
                        func_printer=False,
                        func_scanner=False,
                        is_active=True
                    )
                    db.add(new_user)
                    created += 1
                    
                    # Commit cada 50 usuarios para evitar transacciones muy largas
                    if created % 50 == 0:
                        db.commit()
                        logger.info(f"Progreso: {created} usuarios creados...")
                        
            except Exception as e:
                logger.error(f"Error al sincronizar usuario {codigo} - {nombre}: {e}")
                errors += 1
                db.rollback()
        
        # Commit final
        db.commit()
        
        logger.info(
            f"✓ Sincronización masiva completada: "
            f"{created} usuarios creados, {existing} ya existían, {errors} errores"
        )
        
        return {
            "created": created,
            "existing": existing,
            "total": created + existing,
            "errors": errors
        }
    
    @staticmethod
    def get_sync_stats(db: Session) -> Dict[str, int]:
        """
        Obtiene estadísticas de sincronización.
        
        Returns:
            dict con estadísticas: {
                users_in_db: int,
                users_in_counters: int,
                users_missing: int
            }
        """
        # Usuarios en tabla users
        users_in_db = db.query(User).count()
        
        # Usuarios únicos en contadores (últimos 30 días) - usar user_id
        cutoff_date = datetime.now() - timedelta(days=30)
        users_in_counters = db.query(ContadorUsuario.user_id).filter(
            ContadorUsuario.fecha_lectura >= cutoff_date,
            ContadorUsuario.user_id.isnot(None)
        ).distinct().count()
        
        # Usuarios en contadores que NO están en users (debería ser 0 con normalización)
        usuarios_contadores = db.query(ContadorUsuario.user_id).filter(
            ContadorUsuario.fecha_lectura >= cutoff_date,
            ContadorUsuario.user_id.isnot(None)
        ).distinct().all()
        
        # Verificar cuántos user_ids no existen en users (debería ser 0)
        user_ids_contadores = [uid[0] for uid in usuarios_contadores]
        users_missing = 0
        if user_ids_contadores:
            users_existing = db.query(User.id).filter(User.id.in_(user_ids_contadores)).count()
            users_missing = len(user_ids_contadores) - users_existing
        
        return {
            "users_in_db": users_in_db,
            "users_in_counters": users_in_counters,
            "users_missing": users_missing
        }
    
    @staticmethod
    def sync_users_from_printer_addressbook(
        db: Session,
        printer_id: int,
        admin_user: str = "admin",
        admin_password: str = ""
    ) -> Dict[str, int]:
        """
        Sincroniza usuarios desde la libreta de direcciones de una impresora.
        Obtiene las rutas SMB reales de cada usuario.
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            admin_user: Usuario admin de la impresora
            admin_password: Password admin de la impresora
        
        Returns:
            dict con estadísticas: {created: int, existing: int, updated: int, total: int}
        """
        from db.models import Printer
        from services.ricoh_web_client import RicohWebClient
        
        # Obtener impresora
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            raise ValueError(f"Impresora {printer_id} no encontrada")
        
        logger.info(f"Sincronizando usuarios desde libreta de direcciones de {printer.hostname} ({printer.ip_address})...")
        
        # Leer usuarios desde la impresora
        client = RicohWebClient(admin_user=admin_user, admin_password=admin_password)
        users_from_printer = client.read_users_from_printer(printer.ip_address, fast_list=False)
        
        if not users_from_printer:
            logger.warning(f"No se pudieron leer usuarios de {printer.hostname}")
            return {"created": 0, "existing": 0, "updated": 0, "total": 0, "errors": 1}
        
        logger.info(f"Encontrados {len(users_from_printer)} usuarios en libreta de direcciones")
        
        created = 0
        existing = 0
        updated = 0
        errors = 0
        
        for user_data in users_from_printer:
            try:
                codigo = user_data.get('codigo', '').strip()
                nombre = user_data.get('nombre', '').strip()
                carpeta = user_data.get('carpeta', '').strip()
                
                if not codigo or not nombre:
                    continue
                
                # ✓ FORMATEAR código a 4 dígitos con ceros a la izquierda
                codigo_formateado = format_user_code(codigo)
                
                # Buscar usuario existente por código FORMATEADO
                user = db.query(User).filter(
                    User.codigo_de_usuario == codigo_formateado
                ).first()
                
                if user:
                    # Usuario existe - actualizar ruta SMB si es diferente y no está vacía
                    if carpeta and carpeta != user.smb_path:
                        old_path = user.smb_path
                        user.smb_path = carpeta
                        updated += 1
                        logger.info(f"✓ Actualizado SMB path para {codigo_formateado} - {nombre}: {old_path} → {carpeta}")
                    else:
                        existing += 1
                else:
                    # Usuario no existe - crear con ruta SMB desde libreta y código FORMATEADO
                    new_user = User(
                        name=nombre,
                        codigo_de_usuario=codigo_formateado,  # ← Código formateado a 4 dígitos
                        network_username="reliteltda\\scaner",
                        network_password_encrypted="",
                        smb_server="192.168.91.5",
                        smb_port=21,
                        smb_path=carpeta if carpeta else "\\\\192.168.91.5\\Escaner",
                        func_copier=False,
                        func_printer=False,
                        func_scanner=False,
                        is_active=True
                    )
                    db.add(new_user)
                    created += 1
                    
                    codigo_info = f" (formateado: '{codigo}' → '{codigo_formateado}')" if codigo != codigo_formateado else ""
                    logger.info(f"✓ Usuario creado: {codigo_formateado} - {nombre}{codigo_info} (SMB: {new_user.smb_path})")
                
                # Commit cada 50 usuarios
                if (created + updated) % 50 == 0:
                    db.commit()
                    logger.info(f"Progreso: {created} creados, {updated} actualizados...")
                    
            except Exception as e:
                logger.error(f"Error al sincronizar usuario {codigo} - {nombre}: {e}")
                errors += 1
                db.rollback()
        
        # Commit final
        db.commit()
        
        logger.info(
            f"✓ Sincronización desde libreta completada: "
            f"{created} creados, {updated} actualizados, {existing} sin cambios, {errors} errores"
        )
        
        return {
            "created": created,
            "existing": existing,
            "updated": updated,
            "total": created + existing + updated,
            "errors": errors
        }

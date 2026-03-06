"""
Counter API endpoints
Provides REST API for printer counters
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.database import get_db
from db.models import Printer, ContadorImpresora, ContadorUsuario, CierreMensual
from services.counter_service import CounterService
from . import counter_schemas
from .counter_schemas import (
    ContadorImpresoraResponse,
    ContadorUsuarioResponse,
    CierreMensualResponse,
    CierreMensualRequest,
    CierreRequest,
    ComparacionCierresResponse,
    ReadCounterResponse,
    ReadAllCountersResponse,
)
from services.close_service import CloseService

router = APIRouter(prefix="/api/counters", tags=["counters"])


# ============================================================================
# Printer Counter Endpoints
# ============================================================================

@router.get("/printer/{printer_id}", response_model=ContadorImpresoraResponse)
def get_latest_printer_counter(
    printer_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el último contador total de una impresora
    
    - **printer_id**: ID de la impresora
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    # Obtener último contador
    contador = CounterService.get_latest_counter(db, printer_id)
    
    if not contador:
        raise HTTPException(
            status_code=404, 
            detail=f"No hay contadores registrados para impresora {printer_id}"
        )
    
    return contador


@router.get("/printer/{printer_id}/history", response_model=List[ContadorImpresoraResponse])
def get_printer_counter_history(
    printer_id: int,
    start_date: Optional[datetime] = Query(None, description="Fecha inicial"),
    end_date: Optional[datetime] = Query(None, description="Fecha final"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el histórico de contadores totales de una impresora
    
    - **printer_id**: ID de la impresora
    - **start_date**: Fecha inicial (opcional)
    - **end_date**: Fecha final (opcional)
    - **limit**: Límite de registros (default: 100, max: 1000)
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    # Construir query
    query = db.query(ContadorImpresora).filter(ContadorImpresora.printer_id == printer_id)
    
    if start_date:
        query = query.filter(ContadorImpresora.fecha_lectura >= start_date)
    
    if end_date:
        query = query.filter(ContadorImpresora.fecha_lectura <= end_date)
    
    # Ordenar por fecha descendente y limitar
    contadores = query.order_by(ContadorImpresora.fecha_lectura.desc()).limit(limit).all()
    
    return contadores


# ============================================================================
# User Counter Endpoints
# ============================================================================

@router.get("/users/{printer_id}", response_model=List[ContadorUsuarioResponse])
def get_latest_user_counters(
    printer_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los últimos contadores por usuario de una impresora
    
    - **printer_id**: ID de la impresora
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    # Obtener últimos contadores por usuario
    usuarios = CounterService.get_user_counters_latest(db, printer_id)
    
    return usuarios


@router.get("/users/{printer_id}/history", response_model=List[ContadorUsuarioResponse])
def get_user_counter_history(
    printer_id: int,
    codigo_usuario: Optional[str] = Query(None, max_length=8, description="Código de usuario"),
    start_date: Optional[datetime] = Query(None, description="Fecha inicial"),
    end_date: Optional[datetime] = Query(None, description="Fecha final"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el histórico de contadores por usuario
    
    - **printer_id**: ID de la impresora
    - **codigo_usuario**: Código de usuario (opcional, filtra por usuario específico)
    - **start_date**: Fecha inicial (opcional)
    - **end_date**: Fecha final (opcional)
    - **limit**: Límite de registros (default: 100, max: 1000)
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    # Construir query
    query = db.query(ContadorUsuario).filter(ContadorUsuario.printer_id == printer_id)
    
    if codigo_usuario:
        query = query.filter(ContadorUsuario.codigo_usuario == codigo_usuario)
    
    if start_date:
        query = query.filter(ContadorUsuario.fecha_lectura >= start_date)
    
    if end_date:
        query = query.filter(ContadorUsuario.fecha_lectura <= end_date)
    
    # Ordenar por fecha descendente y limitar
    usuarios = query.order_by(ContadorUsuario.fecha_lectura.desc()).limit(limit).all()
    
    return usuarios


# ============================================================================
# Read Counter Endpoints
# ============================================================================

@router.post("/read/{printer_id}", response_model=ReadCounterResponse)
def read_printer_counters(
    printer_id: int,
    db: Session = Depends(get_db)
):
    """
    Ejecuta lectura de contadores de una impresora (total + usuarios)
    
    - **printer_id**: ID de la impresora
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    result = {
        'success': False,
        'printer_id': printer_id,
        'contador_total': None,
        'usuarios_count': 0,
        'error': None
    }
    
    try:
        # Leer contador total
        contador_total = CounterService.read_printer_counters(db, printer_id)
        result['contador_total'] = contador_total
        result['success'] = True
        
        # Leer contadores por usuario (si está configurado)
        if printer.tiene_contador_usuario or printer.usar_contador_ecologico:
            try:
                usuarios = CounterService.read_user_counters(db, printer_id)
                result['usuarios_count'] = len(usuarios)
            except Exception as e:
                result['error'] = f"Error al leer usuarios: {str(e)}"
        
    except Exception as e:
        result['error'] = str(e)
        raise HTTPException(status_code=500, detail=f"Error al leer contadores: {str(e)}")
    
    return result


@router.post("/read-all", response_model=ReadAllCountersResponse)
def read_all_printer_counters(
    db: Session = Depends(get_db)
):
    """
    Ejecuta lectura de contadores de TODAS las impresoras
    
    Esta operación puede tomar varios minutos dependiendo del número de impresoras.
    """
    try:
        results_dict = CounterService.read_all_printers(db)
        
        # Convertir resultados a formato de respuesta
        results = []
        successful = 0
        failed = 0
        
        for printer_id, result in results_dict.items():
            response = {
                'success': result['success'],
                'printer_id': printer_id,
                'contador_total': result['contador_total'],
                'usuarios_count': len(result['contadores_usuarios']),
                'error': result['error']
            }
            
            results.append(response)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        return {
            'success': True,
            'total_printers': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer contadores: {str(e)}")


# ============================================================================
# Close Endpoints (Sistema Unificado)
# ============================================================================

@router.post("/close", response_model=CierreMensualResponse)
def create_close(
    request: CierreRequest,
    db: Session = Depends(get_db)
):
    """
    Crea un cierre de contadores para cualquier período
    
    - **printer_id**: ID de la impresora
    - **tipo_periodo**: Tipo de período (diario, semanal, mensual, personalizado)
    - **fecha_inicio**: Fecha de inicio del período
    - **fecha_fin**: Fecha de fin del período
    - **cerrado_por**: Usuario que realiza el cierre (opcional)
    - **notas**: Notas adicionales (opcional)
    
    Ejemplos:
    - Cierre diario: tipo_periodo='diario', fecha_inicio=fecha_fin='2026-03-03'
    - Cierre semanal: tipo_periodo='semanal', fecha_inicio='2026-03-01', fecha_fin='2026-03-07'
    - Cierre mensual: tipo_periodo='mensual', fecha_inicio='2026-03-01', fecha_fin='2026-03-31'
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == request.printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {request.printer_id} no encontrada")
    
    try:
        cierre = CloseService.create_close(
            db=db,
            printer_id=request.printer_id,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            tipo_periodo=request.tipo_periodo,
            cerrado_por=request.cerrado_por,
            notas=request.notas
        )
        
        return cierre
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear cierre: {str(e)}")


@router.post("/close-month", response_model=CierreMensualResponse)
def create_monthly_close(
    request: CierreMensualRequest,
    db: Session = Depends(get_db)
):
    """
    Realiza cierre mensual de contadores (mantiene compatibilidad con código existente)
    
    - **printer_id**: ID de la impresora
    - **anio**: Año del cierre
    - **mes**: Mes del cierre (1-12)
    - **cerrado_por**: Usuario que realiza el cierre (opcional)
    - **notas**: Notas adicionales (opcional)
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == request.printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {request.printer_id} no encontrada")
    
    try:
        cierre = CloseService.close_month_helper(
            db,
            request.printer_id,
            request.anio,
            request.mes,
            request.cerrado_por,
            request.notas
        )
        
        return cierre
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear cierre mensual: {str(e)}")


@router.get("/monthly/{printer_id}", response_model=List[CierreMensualResponse])
def get_monthly_closes(
    printer_id: int,
    year: Optional[int] = Query(None, ge=2020, le=2100, description="Año (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los cierres mensuales de una impresora
    
    - **printer_id**: ID de la impresora
    - **year**: Año (opcional, si no se especifica trae todos)
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    cierres = CounterService.get_monthly_closes(db, printer_id, year)
    
    return cierres


@router.get("/closes/{printer_id}", response_model=List[CierreMensualResponse])
def get_closes(
    printer_id: int,
    tipo_periodo: Optional[str] = Query(None, description="Filtrar por tipo: diario, semanal, mensual, personalizado"),
    year: Optional[int] = Query(None, ge=2020, le=2100, description="Año (opcional)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (opcional)"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los cierres de una impresora con filtros opcionales
    
    - **printer_id**: ID de la impresora
    - **tipo_periodo**: Filtrar por tipo (opcional)
    - **year**: Año (opcional)
    - **month**: Mes (opcional)
    - **limit**: Límite de registros (default: 100, max: 1000)
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    # Construir query
    query = db.query(CierreMensual).filter(CierreMensual.printer_id == printer_id)
    
    if tipo_periodo:
        tipos_validos = ['diario', 'semanal', 'mensual', 'personalizado']
        if tipo_periodo not in tipos_validos:
            raise HTTPException(
                status_code=400,
                detail=f"tipo_periodo debe ser uno de: {', '.join(tipos_validos)}"
            )
        query = query.filter(CierreMensual.tipo_periodo == tipo_periodo)
    
    if year:
        query = query.filter(CierreMensual.anio == year)
    
    if month:
        query = query.filter(CierreMensual.mes == month)
    
    # Ordenar por fecha de fin descendente y limitar
    cierres = query.order_by(CierreMensual.fecha_fin.desc()).limit(limit).all()
    
    return cierres


@router.get("/monthly/{printer_id}/{year}/{month}", response_model=CierreMensualResponse)
def get_monthly_close(
    printer_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un cierre mensual específico
    
    - **printer_id**: ID de la impresora
    - **year**: Año
    - **month**: Mes (1-12)
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    # Buscar cierre específico
    cierre = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id,
        CierreMensual.tipo_periodo == 'mensual',
        CierreMensual.anio == year,
        CierreMensual.mes == month
    ).first()
    
    if not cierre:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró cierre mensual para {year}-{month:02d}"
        )
    
    return cierre


@router.get("/closes/{cierre_id}", response_model=CierreMensualResponse)
def get_close_by_id(
    cierre_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un cierre específico por ID
    
    - **cierre_id**: ID del cierre
    """
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    
    if not cierre:
        raise HTTPException(status_code=404, detail=f"Cierre {cierre_id} no encontrado")
    
    return cierre


@router.get("/monthly/{cierre_id}/users", response_model=List[counter_schemas.CierreMensualUsuarioResponse])
def get_monthly_close_users(
    cierre_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el snapshot de usuarios de un cierre mensual específico
    
    - **cierre_id**: ID del cierre mensual
    
    Returns:
        Lista de usuarios con sus contadores y consumos al momento del cierre
    """
    from db.models import CierreMensualUsuario
    
    # Verificar que el cierre existe
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail=f"Cierre {cierre_id} no encontrado")
    
    # Obtener usuarios del cierre
    usuarios = db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre_id
    ).order_by(CierreMensualUsuario.consumo_total.desc()).all()
    
    return usuarios


@router.get("/monthly/{cierre_id}/detail", response_model=counter_schemas.CierreMensualDetalleResponse)
def get_monthly_close_detail(
    cierre_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un cierre mensual con el detalle completo de usuarios
    
    - **cierre_id**: ID del cierre mensual
    
    Returns:
        Cierre mensual con lista de usuarios incluida
    """
    from db.models import CierreMensualUsuario
    
    # Verificar que el cierre existe
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail=f"Cierre {cierre_id} no encontrado")
    
    # Obtener usuarios del cierre
    usuarios = db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre_id
    ).order_by(CierreMensualUsuario.consumo_total.desc()).all()
    
    # Construir respuesta
    response = counter_schemas.CierreMensualDetalleResponse(
        id=cierre.id,
        printer_id=cierre.printer_id,
        anio=cierre.anio,
        mes=cierre.mes,
        total_paginas=cierre.total_paginas,
        total_copiadora=cierre.total_copiadora,
        total_impresora=cierre.total_impresora,
        total_escaner=cierre.total_escaner,
        total_fax=cierre.total_fax,
        diferencia_total=cierre.diferencia_total,
        diferencia_copiadora=cierre.diferencia_copiadora,
        diferencia_impresora=cierre.diferencia_impresora,
        diferencia_escaner=cierre.diferencia_escaner,
        diferencia_fax=cierre.diferencia_fax,
        fecha_cierre=cierre.fecha_cierre,
        cerrado_por=cierre.cerrado_por,
        notas=cierre.notas,
        hash_verificacion=cierre.hash_verificacion,
        created_at=cierre.created_at,
        usuarios=[counter_schemas.CierreMensualUsuarioResponse.model_validate(u) for u in usuarios]
    )
    
    return response


@router.get("/closes/{cierre_id1}/compare/{cierre_id2}", response_model=ComparacionCierresResponse)
def compare_closes(
    cierre_id1: int,
    cierre_id2: int,
    top_usuarios: int = Query(10, ge=1, le=100, description="Cantidad de usuarios en top"),
    db: Session = Depends(get_db)
):
    """
    Compara dos cierres y muestra las diferencias
    
    - **cierre_id1**: ID del primer cierre
    - **cierre_id2**: ID del segundo cierre
    - **top_usuarios**: Cantidad de usuarios a mostrar en tops (default: 10)
    
    Returns:
        Comparación detallada con diferencias de totales y usuarios
    """
    from db.models import CierreMensualUsuario
    from api.counter_schemas import UsuarioComparacion
    
    # Obtener ambos cierres
    cierre1 = db.query(CierreMensual).filter(CierreMensual.id == cierre_id1).first()
    cierre2 = db.query(CierreMensual).filter(CierreMensual.id == cierre_id2).first()
    
    if not cierre1:
        raise HTTPException(status_code=404, detail=f"Cierre {cierre_id1} no encontrado")
    if not cierre2:
        raise HTTPException(status_code=404, detail=f"Cierre {cierre_id2} no encontrado")
    
    # Validar que sean de la misma impresora
    if cierre1.printer_id != cierre2.printer_id:
        raise HTTPException(
            status_code=400,
            detail=f"Los cierres deben ser de la misma impresora (cierre1: {cierre1.printer_id}, cierre2: {cierre2.printer_id})"
        )
    
    # Calcular diferencias de totales
    diferencia_total = cierre2.total_paginas - cierre1.total_paginas
    diferencia_copiadora = cierre2.total_copiadora - cierre1.total_copiadora
    diferencia_impresora = cierre2.total_impresora - cierre1.total_impresora
    diferencia_escaner = cierre2.total_escaner - cierre1.total_escaner
    diferencia_fax = cierre2.total_fax - cierre1.total_fax
    
    # Calcular días entre cierres
    dias_entre_cierres = (cierre2.fecha_fin - cierre1.fecha_fin).days
    
    # Obtener usuarios de ambos cierres
    usuarios1 = {u.codigo_usuario: u for u in db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre_id1
    ).all()}
    
    usuarios2 = {u.codigo_usuario: u for u in db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre_id2
    ).all()}
    
    # Comparar usuarios
    comparaciones = []
    codigos_usuarios = set(usuarios1.keys()) | set(usuarios2.keys())
    
    for codigo in codigos_usuarios:
        u1 = usuarios1.get(codigo)
        u2 = usuarios2.get(codigo)
        
        consumo1 = u1.total_paginas if u1 else 0
        consumo2 = u2.total_paginas if u2 else 0
        diferencia = consumo2 - consumo1
        
        # Calcular porcentaje de cambio
        if consumo1 > 0:
            porcentaje_cambio = (diferencia / consumo1) * 100
        elif diferencia > 0:
            porcentaje_cambio = 100.0
        else:
            porcentaje_cambio = 0.0
        
        nombre = u2.nombre_usuario if u2 else (u1.nombre_usuario if u1 else "Desconocido")
        
        comparaciones.append(UsuarioComparacion(
            codigo_usuario=codigo,
            nombre_usuario=nombre,
            consumo_cierre1=consumo1,
            consumo_cierre2=consumo2,
            diferencia=diferencia,
            porcentaje_cambio=porcentaje_cambio
        ))
    
    # Ordenar por diferencia
    comparaciones_ordenadas = sorted(comparaciones, key=lambda x: x.diferencia, reverse=True)
    
    # Top usuarios con mayor aumento
    top_aumento = [c for c in comparaciones_ordenadas if c.diferencia > 0][:top_usuarios]
    
    # Top usuarios con mayor disminución
    top_disminucion = sorted([c for c in comparaciones_ordenadas if c.diferencia < 0], key=lambda x: x.diferencia)[:top_usuarios]
    
    # Estadísticas
    total_usuarios_activos = len([c for c in comparaciones if c.consumo_cierre2 > 0])
    promedio_consumo = sum(c.consumo_cierre2 for c in comparaciones) / len(comparaciones) if comparaciones else 0
    
    return ComparacionCierresResponse(
        cierre1=cierre1,
        cierre2=cierre2,
        diferencia_total=diferencia_total,
        diferencia_copiadora=diferencia_copiadora,
        diferencia_impresora=diferencia_impresora,
        diferencia_escaner=diferencia_escaner,
        diferencia_fax=diferencia_fax,
        dias_entre_cierres=dias_entre_cierres,
        top_usuarios_aumento=top_aumento,
        top_usuarios_disminucion=top_disminucion,
        total_usuarios_activos=total_usuarios_activos,
        promedio_consumo_por_usuario=promedio_consumo
    )


@router.delete("/closes/{cierre_id}")
def delete_close(
    cierre_id: int,
    force: bool = Query(False, description="Forzar eliminación sin validaciones"),
    db: Session = Depends(get_db)
):
    """
    Elimina un cierre de contadores
    
    - **cierre_id**: ID del cierre a eliminar
    - **force**: Forzar eliminación sin validaciones (default: False)
    
    ADVERTENCIA: Esta operación es irreversible y eliminará el cierre y todos sus usuarios asociados.
    
    Validaciones (si force=False):
    - No se puede eliminar si hay cierres posteriores que dependen de este
    - Solo se puede eliminar el cierre más reciente de cada tipo
    """
    from db.models import CierreMensualUsuario
    
    # Verificar que el cierre existe
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail=f"Cierre {cierre_id} no encontrado")
    
    # Validaciones si no es forzado
    if not force:
        # Verificar que no haya cierres posteriores del mismo tipo
        cierre_posterior = db.query(CierreMensual).filter(
            CierreMensual.printer_id == cierre.printer_id,
            CierreMensual.tipo_periodo == cierre.tipo_periodo,
            CierreMensual.fecha_fin > cierre.fecha_fin
        ).first()
        
        if cierre_posterior:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"No se puede eliminar este cierre porque hay cierres posteriores que dependen de él. "
                    f"Cierre posterior: {cierre_posterior.tipo_periodo} del {cierre_posterior.fecha_inicio} al {cierre_posterior.fecha_fin}. "
                    f"Use force=true para forzar la eliminación."
                )
            )
    
    try:
        # Contar usuarios antes de eliminar
        usuarios_count = db.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre_id
        ).count()
        
        # Eliminar cierre (cascade eliminará usuarios automáticamente)
        db.delete(cierre)
        db.commit()
        
        return {
            "success": True,
            "message": f"Cierre {cierre_id} eliminado exitosamente",
            "cierre": {
                "id": cierre_id,
                "printer_id": cierre.printer_id,
                "tipo_periodo": cierre.tipo_periodo,
                "fecha_inicio": cierre.fecha_inicio.isoformat(),
                "fecha_fin": cierre.fecha_fin.isoformat(),
                "usuarios_eliminados": usuarios_count
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cierre: {str(e)}")

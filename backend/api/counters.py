from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.database import get_db
from db.models import CierreMensual, CierreMensualUsuario, Printer, ContadorImpresora, ContadorUsuario
from .counter_schemas import (
    ContadorImpresoraResponse, ContadorUsuarioResponse, 
    CierreMensualResponse, CierreMensualDetalleResponse,
    CierreMensualUsuarioResponse, CierreRequest, CierreMensualRequest,
    ReadCounterResponse, ComparacionCierresResponse
)
from services.counter_service import CounterService
from services.close_service import CloseService

router = APIRouter(
    prefix="/api/counters",
    tags=["counters"]
)

@router.get("/printer/{printer_id}", response_model=ContadorImpresoraResponse)
def get_latest_counter(printer_id: int, db: Session = Depends(get_db)):
    """Obtener el último contador total de una impresora"""
    contador = CounterService.get_latest_counter(db, printer_id)
    if not contador:
        raise HTTPException(status_code=404, detail=f"No hay contadores para la impresora {printer_id}")
    return contador

@router.get("/users/{printer_id}", response_model=List[ContadorUsuarioResponse])
def get_user_counters_latest(printer_id: int, db: Session = Depends(get_db)):
    """Obtener los últimos contadores por usuario de una impresora"""
    return CounterService.get_user_counters_latest(db, printer_id)


@router.get("/latest/{printer_id}")
def get_latest_counters_with_printer(printer_id: int, db: Session = Depends(get_db)):
    """
    Obtener los últimos contadores por usuario junto con información de la impresora
    
    Incluye las capacidades de la impresora para que el frontend pueda adaptar
    la visualización de columnas.
    """
    from .schemas import PrinterResponse, CapabilitiesResponse
    from models.capabilities import Capabilities
    
    # Get printer
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    # Get latest user counters
    counters = CounterService.get_user_counters_latest(db, printer_id)
    
    # Prepare printer response with capabilities
    printer_dict = {
        "id": printer.id,
        "hostname": printer.hostname,
        "ip_address": printer.ip_address,
        "location": printer.location,
        "empresa": printer.empresa,
        "status": printer.status.value,
        "detected_model": printer.detected_model,
        "serial_number": printer.serial_number,
        "has_color": printer.has_color,
        "has_scanner": printer.has_scanner,
        "has_fax": printer.has_fax,
        "toner_cyan": printer.toner_cyan,
        "toner_magenta": printer.toner_magenta,
        "toner_yellow": printer.toner_yellow,
        "toner_black": printer.toner_black,
        "last_seen": printer.last_seen,
        "notes": printer.notes,
        "created_at": printer.created_at,
        "updated_at": printer.updated_at,
    }
    
    # Add capabilities (or safe defaults)
    if printer.capabilities_json:
        printer_dict["capabilities"] = printer.capabilities_json
    else:
        # Safe defaults for backward compatibility
        default_caps = Capabilities.create_default()
        printer_dict["capabilities"] = default_caps.to_json()
    
    return {
        "printer": printer_dict,
        "counters": counters,
        "total_users": len(counters)
    }


@router.get("/printer/{printer_id}/history", response_model=List[ContadorImpresoraResponse])
def get_history(printer_id: int, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Obtener el histórico de contadores de una impresora"""
    contadores = db.query(ContadorImpresora).filter(
        ContadorImpresora.printer_id == printer_id
    ).order_by(ContadorImpresora.fecha_lectura.desc()).limit(limit).all()
    return contadores

@router.post("/read/{printer_id}", response_model=ReadCounterResponse)
def read_counter(printer_id: int, db: Session = Depends(get_db)):
    """Ejecutar lectura manual de contadores de una impresora (TOTAL + USUARIOS)"""
    try:
        # Leer contador total
        contador_total = CounterService.read_printer_counters(db, printer_id)
        
        # Obtener info de impresora para saber si leer usuarios
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            raise HTTPException(status_code=404, detail="Impresora no encontrada")
            
        contadores_usuarios = []
        if printer.tiene_contador_usuario or printer.usar_contador_ecologico:
            contadores_usuarios = CounterService.read_user_counters(db, printer_id)
            
        return ReadCounterResponse(
            success=True,
            printer_id=printer_id,
            contador_total=contador_total,
            usuarios_count=len(contadores_usuarios),
            error=None
        )
    except Exception as e:
        return ReadCounterResponse(
            success=False,
            printer_id=printer_id,
            contador_total=None,
            usuarios_count=0,
            error=str(e)
        )

# ============================================================================
# ENDPOINTS DE CIERRES MENSUALES
# ============================================================================

@router.post("/monthly", response_model=CierreMensualResponse)
def create_monthly_close(request: CierreMensualRequest, db: Session = Depends(get_db)):
    """
    Crea un cierre mensual (compatibilidad retroactiva)
    """
    try:
        cierre = CloseService.close_month_helper(
            db=db,
            printer_id=request.printer_id,
            year=request.anio,
            month=request.mes,
            cerrado_por=request.cerrado_por,
            notas=request.notas
        )
        return cierre
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/close", response_model=CierreMensualResponse)
def create_close(request: CierreRequest, db: Session = Depends(get_db)):
    """
    Crea un cierre de contadores para cualquier período
    
    IMPORTANTE: Este endpoint lee automáticamente los contadores de la impresora
    antes de crear el cierre, garantizando que el snapshot sea actual.
    
    - **printer_id**: ID de la impresora
    - **tipo_periodo**: Tipo de período (diario, semanal, mensual, personalizado)
    - **fecha_inicio**: Fecha de inicio del período
    - **fecha_fin**: Fecha de fin del período
    - **cerrado_por**: Usuario que realiza el cierre (opcional)
    - **notas**: Notas adicionales (opcional)
    """
    # Verificar que la impresora existe
    printer = db.query(Printer).filter(Printer.id == request.printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {request.printer_id} no encontrada")
    
    try:
        # PASO 1: Leer contadores actuales de la impresora
        # El cierre ES una lectura - guardamos un snapshot del estado actual
        print(f"\n{'='*80}")
        print(f"📖 CREANDO CIERRE PARA IMPRESORA {request.printer_id}")
        print(f"   Tipo: {request.tipo_periodo}")
        print(f"   Período: {request.fecha_inicio} a {request.fecha_fin}")
        print(f"   Configuración impresora:")
        print(f"     - tiene_contador_usuario: {printer.tiene_contador_usuario}")
        print(f"     - usar_contador_ecologico: {printer.usar_contador_ecologico}")
        print(f"{'='*80}\n")
        
        # Leer contador total
        print(f"📊 Leyendo contador total...")
        contador_total = CounterService.read_printer_counters(db, request.printer_id)
        if not contador_total:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al leer contador total de la impresora"
            )
        print(f"✅ Contador total leído: {contador_total.total} páginas")
        
        # Leer contadores por usuario (si está configurado)
        usuarios_count = 0
        if printer.tiene_contador_usuario or printer.usar_contador_ecologico:
            print(f"👥 Leyendo contadores por usuario...")
            usuarios = CounterService.read_user_counters(db, request.printer_id)
            usuarios_count = len(usuarios)
            print(f"✅ Contadores de usuarios leídos: {usuarios_count} usuarios")
            
            # Mostrar primeros 5 usuarios para debugging
            if usuarios_count > 0:
                print(f"   Primeros usuarios:")
                for u in usuarios[:5]:
                    print(f"     - {u.codigo_usuario}: {u.nombre_usuario} ({u.total_paginas} páginas)")
        else:
            print(f"⚠️ Impresora NO tiene contador por usuario configurado")
        
        # IMPORTANTE: Hacer commit de la lectura antes de crear el cierre
        print(f"💾 Guardando lecturas en base de datos...")
        db.commit()
        print(f"✅ Lecturas guardadas")
        
        # PASO 2: Crear el cierre con los datos recién leídos
        print(f"🔒 Creando cierre...")
        cierre = CloseService.create_close(
            db=db,
            printer_id=request.printer_id,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            tipo_periodo=request.tipo_periodo,
            cerrado_por=request.cerrado_por,
            notas=request.notas
        )
        
        print(f"✅ Cierre creado exitosamente:")
        print(f"   ID: {cierre.id}")
        print(f"   Total páginas: {cierre.total_paginas}")
        print(f"   Usuarios en cierre: {len(cierre.usuarios)}")
        print(f"{'='*80}\n")
        
        return cierre
        
    except ValueError as e:
        print(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al crear cierre: {str(e)}")

@router.get("/monthly", response_model=List[CierreMensualResponse])
def list_closes(printer_id: int, db: Session = Depends(get_db)):
    """Obtiene todos los cierres de una impresora"""
    cierres = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id
    ).order_by(CierreMensual.fecha_inicio.desc()).all()
    return cierres

@router.get("/monthly/{printer_id}", response_model=List[CierreMensualResponse])
def get_monthly_closes_by_printer(printer_id: int, db: Session = Depends(get_db)):
    """Obtiene cierres de una impresora (compatibilidad endpoints antiguos)"""
    return list_closes(printer_id, db)

@router.get("/monthly/compare/{cierre1_id}/{cierre2_id}", response_model=ComparacionCierresResponse)
def compare_closes(cierre1_id: int, cierre2_id: int, db: Session = Depends(get_db)):
    """
    Compara dos cierres entre sí.
    El cierre1 debe ser el más antiguo y el cierre2 el más reciente.
    """
    try:
        resultado = CloseService.comparar_cierres(db, cierre1_id, cierre2_id)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly/{printer_id}/{year}/{month}", response_model=CierreMensualResponse)
def get_monthly_close_specific(printer_id: int, year: int, month: int, db: Session = Depends(get_db)):
    """Obtiene un cierre mensual específico"""
    cierre = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id,
        CierreMensual.anio == year,
        CierreMensual.mes == month,
        CierreMensual.tipo_periodo == 'mensual'
    ).first()
    
    if not cierre:
        raise HTTPException(status_code=404, detail=f"No se encontró cierre para {year}-{month:02d}")
        
    return cierre

@router.get("/monthly/close/{cierre_id}", response_model=CierreMensualResponse)
def get_close_by_id(cierre_id: int, db: Session = Depends(get_db)):
    """Obtiene un cierre por su ID"""
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    return cierre

@router.get("/monthly/{cierre_id}/users", response_model=List[CierreMensualUsuarioResponse])
def get_close_users(cierre_id: int, db: Session = Depends(get_db)):
    """Obtiene los usuarios de un cierre"""
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
        
    return cierre.usuarios

@router.get("/monthly/{cierre_id}/detail", response_model=CierreMensualDetalleResponse)
def get_close_detail(
    cierre_id: int, 
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle completo de un cierre con paginación
    
    Args:
        cierre_id: ID del cierre
        page: Número de página (default: 1)
        page_size: Tamaño de página (default: 50, sin límite máximo)
        search: Búsqueda por nombre o código de usuario
    """
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    
    # Get printer with capabilities
    printer = db.query(Printer).filter(Printer.id == cierre.printer_id).first()
    
    # Query usuarios with pagination and search
    usuarios_query = db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre_id
    )
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        usuarios_query = usuarios_query.filter(
            (CierreMensualUsuario.nombre_usuario.ilike(search_term)) |
            (CierreMensualUsuario.codigo_usuario.ilike(search_term))
        )
    
    # Get total count
    total_usuarios = usuarios_query.count()
    
    # Apply pagination (sin límite máximo para permitir cargar todos los usuarios)
    offset = (page - 1) * page_size
    usuarios = usuarios_query.order_by(
        CierreMensualUsuario.total_paginas.desc()
    ).offset(offset).limit(page_size).all()
    
    # Create response dict with all required fields
    response = CierreMensualDetalleResponse(
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
        fecha_inicio=cierre.fecha_inicio,
        fecha_fin=cierre.fecha_fin,
        cerrado_por=cierre.cerrado_por,
        notas=cierre.notas,
        hash_verificacion=cierre.hash_verificacion,
        created_at=cierre.created_at,
        printer=printer,
        usuarios=usuarios,
        total_usuarios=total_usuarios,
        page=page,
        page_size=page_size,
        total_pages=(total_usuarios + page_size - 1) // page_size
    )
    
    return response


@router.get("/monthly/compare/{cierre1_id}/{cierre2_id}/verificar")
def verificar_coherencia_comparativo(cierre1_id: int, cierre2_id: int, db: Session = Depends(get_db)):
    """
    Verifica la coherencia del comparativo entre dos cierres
    Comprueba que la suma de B/N + COLOR de usuarios = diferencia del contador general
    """
    cierre1 = db.query(CierreMensual).filter(CierreMensual.id == cierre1_id).first()
    cierre2 = db.query(CierreMensual).filter(CierreMensual.id == cierre2_id).first()
    
    if not cierre1 or not cierre2:
        raise HTTPException(status_code=404, detail="Uno o ambos cierres no encontrados")
    
    # Diferencia del contador general
    diff_total_contador = cierre2.total_paginas - cierre1.total_paginas
    
    # Calcular suma de usuarios
    usuarios1 = {u.codigo_usuario: u for u in cierre1.usuarios}
    usuarios2 = {u.codigo_usuario: u for u in cierre2.usuarios}
    
    codigos = set(usuarios1.keys()).union(set(usuarios2.keys()))
    
    suma_bn = 0
    suma_color = 0
    suma_total = 0
    usuarios_con_consumo = []
    
    for codigo in codigos:
        u1 = usuarios1.get(codigo)
        u2 = usuarios2.get(codigo)
        
        # Totales acumulados
        total1 = u1.total_paginas if u1 else 0
        total2 = u2.total_paginas if u2 else 0
        
        # B/N y Color acumulados
        bn1 = u1.total_bn if u1 else 0
        bn2 = u2.total_bn if u2 else 0
        color1 = u1.total_color if u1 else 0
        color2 = u2.total_color if u2 else 0
        
        # Diferencias (consumo del período - puede ser negativo si hay correcciones)
        diff_total = total2 - total1
        diff_bn = bn2 - bn1
        diff_color = color2 - color1
        
        if diff_total != 0:  # Incluir usuarios con cambios (positivos o negativos)
            suma_bn += diff_bn
            suma_color += diff_color
            suma_total += diff_total
            
            usuarios_con_consumo.append({
                'codigo': codigo,
                'nombre': u2.nombre_usuario if u2 else u1.nombre_usuario,
                'diff_bn': diff_bn,
                'diff_color': diff_color,
                'diff_total': diff_total
            })
    
    # Verificar coherencia
    coherente_bn_color = (suma_bn + suma_color == suma_total)
    coherente_suma_contador = (suma_total == diff_total_contador)
    
    return {
        "cierre1": {
            "id": cierre1.id,
            "fecha": str(cierre1.fecha_inicio),
            "total_paginas": cierre1.total_paginas
        },
        "cierre2": {
            "id": cierre2.id,
            "fecha": str(cierre2.fecha_inicio),
            "total_paginas": cierre2.total_paginas
        },
        "contador_general": {
            "cierre1": cierre1.total_paginas,
            "cierre2": cierre2.total_paginas,
            "diferencia": diff_total_contador
        },
        "suma_usuarios": {
            "bn": suma_bn,
            "color": suma_color,
            "bn_mas_color": suma_bn + suma_color,
            "total": suma_total,
            "usuarios_con_consumo": len(usuarios_con_consumo)
        },
        "verificacion": {
            "bn_mas_color_igual_total": coherente_bn_color,
            "suma_usuarios_igual_contador": coherente_suma_contador,
            "coherente": coherente_bn_color and coherente_suma_contador,
            "diferencia_usuarios_contador": abs(suma_total - diff_total_contador),
            "porcentaje_diferencia": round(abs(suma_total - diff_total_contador) / diff_total_contador * 100, 2) if diff_total_contador > 0 else 0
        },
        "top_10_usuarios": sorted(usuarios_con_consumo, key=lambda x: x['diff_total'], reverse=True)[:10]
    }


@router.get("/monthly/{cierre_id}/suma-usuarios")
def obtener_suma_usuarios(cierre_id: int, db: Session = Depends(get_db)):
    """
    Obtiene la suma de total_paginas de todos los usuarios de un cierre
    y la compara con el total_paginas del contador general
    """
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    
    suma_usuarios = sum(u.total_paginas for u in cierre.usuarios)
    
    return {
        "cierre_id": cierre.id,
        "fecha": str(cierre.fecha_inicio),
        "contador_general": cierre.total_paginas,
        "suma_usuarios": suma_usuarios,
        "diferencia": abs(cierre.total_paginas - suma_usuarios),
        "porcentaje_diferencia": round(abs(cierre.total_paginas - suma_usuarios) / cierre.total_paginas * 100, 2) if cierre.total_paginas > 0 else 0,
        "total_usuarios": len(cierre.usuarios),
        "coherente": cierre.total_paginas == suma_usuarios
    }

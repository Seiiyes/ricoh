from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from db.database import get_db
from db.models import CierreMensual, CierreMensualUsuario, Printer, ContadorImpresora, ContadorUsuario, ComparacionGuardada
from .counter_schemas import (
    ContadorImpresoraResponse, ContadorUsuarioResponse, 
    CierreMensualResponse, CierreMensualDetalleResponse,
    CierreMensualUsuarioResponse, CierreRequest, CierreMensualRequest,
    CierreMasivoRequest, ReadCounterResponse, ComparacionCierresResponse, 
    CloseAllPrintersResponse,
    CierreUsuarioUpdateRequest, CierreUsuarioGlobalResponse,
    PaginatedCierreUsuarioGlobalResponse,
    ComparacionGuardadaCreate, ComparacionGuardadaResponse
)
from services.counter_service import CounterService
from services.close_service import CloseService
from middleware.auth_middleware import get_current_user
from services.company_filter_service import CompanyFilterService

router = APIRouter(
    prefix="/api/counters",
    tags=["counters"]
)

@router.get("/printer/{printer_id}", response_model=ContadorImpresoraResponse, status_code=status.HTTP_200_OK)
async def get_latest_counter(printer_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtener el último contador total de una impresora"""
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impresora {printer_id} no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    contador = CounterService.get_latest_counter(db, printer_id)
    if not contador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No hay contadores para la impresora {printer_id}")
    return contador

@router.get("/users/{printer_id}", response_model=List[ContadorUsuarioResponse], status_code=status.HTTP_200_OK)
async def get_user_counters_latest(printer_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtener los últimos contadores por usuario de una impresora"""
    from db.models import User
    from sqlalchemy.orm import joinedload
    
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impresora {printer_id} no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    # Obtener contadores con JOIN de users
    contadores = CounterService.get_user_counters_latest(db, printer_id)
    
    # Serializar con datos de usuario
    result = []
    for contador in contadores:
        user = db.query(User).filter(User.id == contador.user_id).first()
        contador_dict = {
            **{k: getattr(contador, k) for k in contador.__dict__ if not k.startswith('_')},
            'codigo_usuario': user.codigo_de_usuario if user else str(contador.user_id),
            'nombre_usuario': user.name if user else f"Usuario {contador.user_id}"
        }
        result.append(ContadorUsuarioResponse(**contador_dict))
    
    return result


@router.get("/latest/{printer_id}", status_code=status.HTTP_200_OK)
async def get_latest_counters_with_printer(printer_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impresora {printer_id} no encontrada")
    
    # Validar acceso a la impresora
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    # Get latest user counters
    from db.models import User
    contadores = CounterService.get_user_counters_latest(db, printer_id)
    
    # Serializar contadores con datos de usuario
    counters_serialized = []
    for contador in contadores:
        user = db.query(User).filter(User.id == contador.user_id).first()
        contador_dict = {
            **{k: getattr(contador, k) for k in contador.__dict__ if not k.startswith('_')},
            'codigo_usuario': user.codigo_de_usuario if user else str(contador.user_id),
            'nombre_usuario': user.name if user else f"Usuario {contador.user_id}"
        }
        counters_serialized.append(contador_dict)
    
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
        "counters": counters_serialized,
        "total_users": len(counters_serialized)
    }


@router.get("/printer/{printer_id}/history", response_model=List[ContadorImpresoraResponse], status_code=status.HTTP_200_OK)
async def get_history(printer_id: int, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtener el histórico de contadores de una impresora"""
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impresora {printer_id} no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    contadores = db.query(ContadorImpresora).filter(
        ContadorImpresora.printer_id == printer_id
    ).order_by(ContadorImpresora.fecha_lectura.desc()).limit(limit).all()
    return contadores

# IMPORTANTE: /read-all debe estar ANTES de /read/{printer_id} para evitar conflictos de rutas
@router.post("/read-all", status_code=status.HTTP_200_OK)
async def read_all_counters(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Ejecutar lectura manual de contadores de TODAS las impresoras activas
    
    Retorna un resumen de lecturas exitosas y fallidas.
    Solo lee impresoras a las que el usuario tiene acceso.
    """
    try:
        print(f"\n{'='*80}")
        print(f"📖 INICIANDO LECTURA DE TODAS LAS IMPRESORAS")
        print(f"{'='*80}\n")
        
        # Obtener todas las impresoras activas con acceso del usuario
        query = db.query(Printer).filter(Printer.status != 'offline')
        
        # Aplicar filtro de empresa
        query = CompanyFilterService.apply_filter(query, current_user)
        
        printers = query.all()
        print(f"📊 Total de impresoras a leer: {len(printers)}")
        
        if not printers:
            return {
                "success": True,
                "message": "No hay impresoras disponibles para leer",
                "successful": 0,
                "failed": 0,
                "total": 0,
                "results": []
            }
        
        results = []
        successful = 0
        failed = 0
        
        for printer in printers:
            try:
                print(f"📖 Leyendo impresora {printer.id}: {printer.hostname}")
                
                # Leer contador total
                contador_total = CounterService.read_printer_counters(db, printer.id)
                print(f"✅ Contador total leído para {printer.hostname}: {contador_total.total if contador_total else 'None'}")
                
                # Leer contadores de usuarios si aplica
                usuarios_count = 0
                if printer.tiene_contador_usuario or printer.usar_contador_ecologico:
                    contadores_usuarios = CounterService.read_user_counters(db, printer.id)
                    usuarios_count = len(contadores_usuarios)
                    print(f"✅ Contadores de usuarios leídos para {printer.hostname}: {usuarios_count}")
                
                results.append({
                    "printer_id": printer.id,
                    "printer_name": printer.hostname,
                    "success": True,
                    "usuarios_count": usuarios_count,
                    "error": None
                })
                successful += 1
                print(f"✅ Lectura exitosa para {printer.hostname}")
                
            except Exception as e:
                print(f"❌ Error leyendo {printer.hostname}: {str(e)}")
                results.append({
                    "printer_id": printer.id,
                    "printer_name": printer.hostname,
                    "success": False,
                    "usuarios_count": 0,
                    "error": str(e)
                })
                failed += 1
        
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN FINAL:")
        print(f"   Total: {len(printers)}")
        print(f"   Exitosas: {successful}")
        print(f"   Fallidas: {failed}")
        print(f"{'='*80}\n")
        
        return {
            "success": True,
            "message": f"Lectura completada: {successful} exitosas, {failed} fallidas",
            "successful": successful,
            "failed": failed,
            "total": len(printers),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer contadores: {str(e)}"
        )

@router.post("/read/{printer_id}", response_model=ReadCounterResponse, status_code=status.HTTP_200_OK)
async def read_counter(printer_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Ejecutar lectura manual de contadores de una impresora (TOTAL + USUARIOS)"""
    try:
        # Obtener info de impresora y validar acceso
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impresora no encontrada")
        
        if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
        
        # Leer contador total
        contador_total = CounterService.read_printer_counters(db, printer_id)
            
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

@router.post("/monthly", response_model=CierreMensualResponse, status_code=status.HTTP_201_CREATED)
async def create_monthly_close(request: CierreMensualRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Crea un cierre mensual (compatibilidad retroactiva)
    """
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == request.printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impresora {request.printer_id} no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/close-all", response_model=CloseAllPrintersResponse, status_code=status.HTTP_200_OK)
async def create_close_all_printers(request: CierreMasivoRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Crea cierres para TODAS las impresoras activas simultáneamente
    
    IMPORTANTE: Este endpoint lee automáticamente los contadores de todas las impresoras
    antes de crear los cierres, garantizando que los snapshots sean actuales.
    
    - **fecha_inicio**: Fecha de inicio del período
    - **fecha_fin**: Fecha de fin del período
    - **cerrado_por**: Usuario que realiza el cierre (para auditoría)
    - **notas**: Notas adicionales (opcional)
    
    Retorna un resumen de cierres exitosos y fallidos.
    Solo crea cierres en impresoras a las que el usuario tiene acceso.
    """
    try:
        print(f"\n{'='*80}")
        print(f"🔒 INICIANDO CIERRE MASIVO EN TODAS LAS IMPRESORAS")
        print(f"{'='*80}\n")
        
        # Obtener todas las impresoras activas con acceso del usuario
        query = db.query(Printer).filter(Printer.status != 'offline')
        
        # Aplicar filtro de empresa
        query = CompanyFilterService.apply_filter(query, current_user)
        
        printers = query.all()
        print(f"📊 Total de impresoras a cerrar: {len(printers)}")
        
        if not printers:
            return {
                "success": True,
                "message": "No hay impresoras disponibles para cerrar",
                "successful": 0,
                "failed": 0,
                "total": 0,
                "results": []
            }
        
        # PASO 1: Leer contadores de todas las impresoras primero
        print(f"\n📖 PASO 1: Leyendo contadores de todas las impresoras...")
        lecturas_exitosas = 0
        lecturas_fallidas = 0
        
        for printer in printers:
            try:
                print(f"📖 Leyendo impresora {printer.id}: {printer.hostname}")
                
                # Leer contador total
                contador_total = CounterService.read_printer_counters(db, printer.id)
                
                # Leer contadores de usuarios si aplica
                if printer.tiene_contador_usuario or printer.usar_contador_ecologico:
                    contadores_usuarios = CounterService.read_user_counters(db, printer.id)
                    print(f"✅ Leídos: total + {len(contadores_usuarios)} usuarios")
                else:
                    print(f"✅ Leído: total (sin usuarios)")
                
                lecturas_exitosas += 1
                
            except Exception as e:
                print(f"❌ Error leyendo {printer.hostname}: {str(e)}")
                lecturas_fallidas += 1
        
        print(f"\n📊 Lecturas completadas: {lecturas_exitosas} exitosas, {lecturas_fallidas} fallidas")
        
        # Hacer commit de todas las lecturas
        print(f"💾 Guardando lecturas en base de datos...")
        db.commit()
        print(f"✅ Lecturas guardadas")
        
        # PASO 2: Crear cierres en todas las impresoras
        print(f"\n🔒 PASO 2: Creando cierres...")
        
        # Obtener empresa_id del usuario si aplica
        empresa_id = None
        if hasattr(current_user, 'empresa_id') and current_user.empresa_id:
            empresa_id = current_user.empresa_id
        
        resultado = CloseService.create_close_all_printers(
            db=db,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            cerrado_por=request.cerrado_por,
            notas=request.notas,
            empresa_id=empresa_id
        )
        
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN FINAL:")
        print(f"   Total: {resultado['total']}")
        print(f"   Exitosos: {resultado['successful']}")
        print(f"   Fallidos: {resultado['failed']}")
        print(f"{'='*80}\n")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear cierres masivos: {str(e)}"
        )

@router.post("/close", response_model=CierreMensualResponse, status_code=status.HTTP_201_CREATED)
async def create_close(request: CierreRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Crea un cierre de contadores para cualquier período
    
    IMPORTANTE: Este endpoint lee automáticamente los contadores de la impresora
    antes de crear el cierre, garantizando que el snapshot sea actual.
    
    Un cierre es simplemente un snapshot de contadores en un momento dado.
    El usuario decide cómo interpretarlo (diario, semanal, mensual, etc.)
    
    - **printer_id**: ID de la impresora
    - **fecha_inicio**: Fecha de inicio del período
    - **fecha_fin**: Fecha de fin del período
    - **cerrado_por**: Usuario que realiza el cierre (opcional)
    - **notas**: Notas adicionales (opcional)
    """
    # Verificar que la impresora existe y validar acceso
    printer = db.query(Printer).filter(Printer.id == request.printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impresora {request.printer_id} no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    try:
        # PASO 1: Leer contadores actuales de la impresora
        # El cierre ES una lectura - guardamos un snapshot del estado actual
        print(f"\n{'='*80}")
        print(f"📖 CREANDO CIERRE PARA IMPRESORA {request.printer_id}")
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
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
                from db.models import User
                for u in usuarios[:5]:
                    user = db.query(User).filter(User.id == u.user_id).first()
                    codigo = user.codigo_de_usuario if user else str(u.user_id)
                    nombre = user.name if user else f"Usuario {u.user_id}"
                    print(f"     - {codigo}: {nombre} ({u.total_paginas} páginas)")
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear cierre: {str(e)}")

@router.get("/monthly", response_model=List[CierreMensualResponse], status_code=status.HTTP_200_OK)
async def list_closes(printer_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtiene todos los cierres de una impresora"""
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impresora {printer_id} no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    cierres = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id
    ).order_by(CierreMensual.fecha_inicio.desc()).all()
    return cierres

@router.get("/monthly/{printer_id}", response_model=List[CierreMensualResponse], status_code=status.HTTP_200_OK)
async def get_monthly_closes_by_printer(printer_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtiene cierres de una impresora (compatibilidad endpoints antiguos)"""
    return await list_closes(printer_id, db, current_user)

@router.get("/monthly/compare/{cierre1_id}/{cierre2_id}", response_model=ComparacionCierresResponse, status_code=status.HTTP_200_OK)
async def compare_closes(cierre1_id: int, cierre2_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Compara dos cierres entre sí.
    El cierre1 debe ser el más antiguo y el cierre2 el más reciente.
    """
    # Validar acceso a ambos cierres
    cierre1 = db.query(CierreMensual).filter(CierreMensual.id == cierre1_id).first()
    cierre2 = db.query(CierreMensual).filter(CierreMensual.id == cierre2_id).first()
    
    if not cierre1 or not cierre2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uno o ambos cierres no encontrados")
    
    # Validar que ambos cierres pertenecen a la misma impresora
    if cierre1.printer_id != cierre2.printer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Los cierres deben ser de la misma impresora")
    
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == cierre1.printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impresora no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    try:
        resultado = CloseService.comparar_cierres(db, cierre1_id, cierre2_id)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/monthly/{printer_id}/{year}/{month}", response_model=CierreMensualResponse)
def get_monthly_close_specific(printer_id: int, year: int, month: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtiene un cierre mensual específico"""
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail=f"Impresora {printer_id} no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta impresora")
    
    cierre = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id,
        CierreMensual.anio == year,
        CierreMensual.mes == month
    ).first()
    
    if not cierre:
        raise HTTPException(status_code=404, detail=f"No se encontró cierre para {year}-{month:02d}")
        
    return cierre

@router.get("/monthly/close/{cierre_id}", response_model=CierreMensualResponse, status_code=status.HTTP_200_OK)
async def get_close_by_id(cierre_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtiene un cierre por su ID"""
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cierre no encontrado")
    
    # Validar acceso a la impresora del cierre
    printer = db.query(Printer).filter(Printer.id == cierre.printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impresora no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a este cierre")
    return cierre

@router.get("/monthly/{cierre_id}/users", response_model=List[CierreMensualUsuarioResponse], status_code=status.HTTP_200_OK)
async def get_close_users(cierre_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Obtiene los usuarios de un cierre"""
    from db.models import User
    
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    if not cierre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cierre no encontrado")
    
    # Validar acceso a la impresora del cierre
    printer = db.query(Printer).filter(Printer.id == cierre.printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impresora no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a este cierre")
    
    # Serializar usuarios con datos de user
    result = []
    for usuario in cierre.usuarios:
        user = db.query(User).filter(User.id == usuario.user_id).first()
        usuario_dict = {
            **{k: getattr(usuario, k) for k in usuario.__dict__ if not k.startswith('_')},
            'codigo_usuario': user.codigo_de_usuario if user else str(usuario.user_id),
            'nombre_usuario': user.name if user else f"Usuario {usuario.user_id}"
        }
        result.append(CierreMensualUsuarioResponse(**usuario_dict))
    
    return result

@router.get("/monthly/{cierre_id}/detail", response_model=CierreMensualDetalleResponse, status_code=status.HTTP_200_OK)
async def get_close_detail(
    cierre_id: int, 
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cierre no encontrado")
    
    # Get printer with capabilities
    printer = db.query(Printer).filter(Printer.id == cierre.printer_id).first()
    
    # Validar acceso a la impresora del cierre
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impresora no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a este cierre")
    
    # Query usuarios with pagination and search
    usuarios_query = db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.cierre_mensual_id == cierre_id
    )
    
    # Apply search filter
    if search:
        from db.models import User
        search_term = f"%{search}%"
        # Buscar por user_id que coincida con usuarios que tengan el código o nombre
        user_ids = db.query(User.id).filter(
            (User.codigo_de_usuario.ilike(search_term)) |
            (User.name.ilike(search_term))
        ).all()
        user_ids_list = [uid[0] for uid in user_ids]
        
        if user_ids_list:
            usuarios_query = usuarios_query.filter(
                CierreMensualUsuario.user_id.in_(user_ids_list)
            )
        else:
            # Si no se encontraron usuarios, retornar query vacío
            usuarios_query = usuarios_query.filter(CierreMensualUsuario.user_id == -1)
    
    # Get total count
    total_usuarios = usuarios_query.count()
    
    # Apply pagination (sin límite máximo para permitir cargar todos los usuarios)
    offset = (page - 1) * page_size
    usuarios = usuarios_query.order_by(
        CierreMensualUsuario.total_paginas.desc()
    ).offset(offset).limit(page_size).all()
    
    # Serializar usuarios con datos de user
    from db.models import User
    usuarios_serialized = []
    for usuario in usuarios:
        user = db.query(User).filter(User.id == usuario.user_id).first()
        usuario_dict = {
            **{k: getattr(usuario, k) for k in usuario.__dict__ if not k.startswith('_')},
            'codigo_usuario': user.codigo_de_usuario if user else str(usuario.user_id),
            'nombre_usuario': user.name if user else f"Usuario {usuario.user_id}"
        }
        usuarios_serialized.append(CierreMensualUsuarioResponse(**usuario_dict))
    
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
        usuarios=usuarios_serialized,
        total_usuarios=total_usuarios,
        page=page,
        page_size=page_size,
        total_pages=(total_usuarios + page_size - 1) // page_size
    )
    
    return response


@router.get("/monthly/compare/{cierre1_id}/{cierre2_id}/verificar", status_code=status.HTTP_200_OK)
async def verificar_coherencia_comparativo(cierre1_id: int, cierre2_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Verifica la coherencia del comparativo entre dos cierres
    Comprueba que la suma de B/N + COLOR de usuarios = diferencia del contador general
    """
    cierre1 = db.query(CierreMensual).filter(CierreMensual.id == cierre1_id).first()
    cierre2 = db.query(CierreMensual).filter(CierreMensual.id == cierre2_id).first()
    
    if not cierre1 or not cierre2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uno o ambos cierres no encontrados")
    
    # Validar acceso a la impresora
    printer = db.query(Printer).filter(Printer.id == cierre1.printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impresora no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta impresora")
    
    # Diferencia del contador general
    diff_total_contador = cierre2.total_paginas - cierre1.total_paginas
    
    # Calcular suma de usuarios usando user_id
    from db.models import User
    usuarios1 = {u.user_id: u for u in cierre1.usuarios}
    usuarios2 = {u.user_id: u for u in cierre2.usuarios}
    
    user_ids = set(usuarios1.keys()).union(set(usuarios2.keys()))
    
    suma_bn = 0
    suma_color = 0
    suma_total = 0
    usuarios_con_consumo = []
    
    for user_id in user_ids:
        u1 = usuarios1.get(user_id)
        u2 = usuarios2.get(user_id)
        
        # Obtener datos del usuario
        user = db.query(User).filter(User.id == user_id).first()
        codigo = user.codigo_de_usuario if user else str(user_id)
        nombre = user.name if user else f"Usuario {user_id}"
        
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
                'nombre': nombre,
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


@router.get("/monthly/{cierre_id}/suma-usuarios", status_code=status.HTTP_200_OK)
async def obtener_suma_usuarios(cierre_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Obtiene la suma de total_paginas de todos los usuarios de un cierre
    y la compara con el total_paginas del contador general
    """
    cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
    
    if not cierre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cierre no encontrado")
    
    # Validar acceso a la impresora del cierre
    printer = db.query(Printer).filter(Printer.id == cierre.printer_id).first()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impresora no encontrada")
    
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a este cierre")
    
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


@router.get("/monthly/users/all", response_model=PaginatedCierreUsuarioGlobalResponse, status_code=status.HTTP_200_OK)
async def get_all_users_closes(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=500, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Búsqueda por usuario o impresora"),
    printer_id: Optional[int] = Query(None, description="Filtrar por impresora"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio de período"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin de período"),
    centro_costos: Optional[str] = Query(None, description="Filtrar por centro de costos"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene un listado paginado y filtrado de consumos de usuario en cierres mensuales.
    Enfuerza multi-tenancy filtrando por la empresa asignada al usuario no-superadmin.
    """
    from db.models import User, Printer, CierreMensual
    from sqlalchemy import or_, date as sql_date
    from datetime import date as dt_date

    # Query base con joins para obtener datos de impresora y del cierre
    query = db.query(CierreMensualUsuario).join(
        CierreMensual, CierreMensual.id == CierreMensualUsuario.cierre_mensual_id
    ).join(
        Printer, Printer.id == CierreMensual.printer_id
    )

    # Filtrar por empresa si no es superadmin
    if not current_user.is_superadmin():
        query = query.filter(Printer.empresa_id == current_user.empresa_id)

    # Filtros adicionales directos
    if printer_id:
        query = query.filter(CierreMensual.printer_id == printer_id)
    if user_id:
        query = query.filter(CierreMensualUsuario.user_id == user_id)
        
    # Filtros por rango de fechas
    if fecha_inicio:
        query = query.filter(CierreMensual.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        query = query.filter(CierreMensual.fecha_fin <= fecha_fin)

    # Filtro por centro de costos
    if centro_costos:
        # Hacemos join explícito con User si no se busca por texto
        query = query.join(User, User.id == CierreMensualUsuario.user_id).filter(
            User.centro_costos.ilike(f"%{centro_costos}%")
        )

    # Búsqueda de texto (nombre de usuario, código, IP, ubicación, hostname)
    if search:
        search_term = f"%{search}%"
        # Obtener IDs de usuarios que coincidan con el nombre/código/centro de costo
        matching_users = db.query(User.id).filter(
            or_(
                User.name.ilike(search_term),
                User.codigo_de_usuario.ilike(search_term),
                User.centro_costos.ilike(search_term)
            )
        ).subquery()
        
        query = query.filter(
            or_(
                CierreMensualUsuario.user_id.in_(matching_users),
                Printer.hostname.ilike(search_term),
                Printer.ip_address.ilike(search_term),
                Printer.location.ilike(search_term)
            )
        )

    # Conteo total
    total = query.count()

    # Ordenar por fecha de cierre desc, luego consumo desc
    query = query.order_by(
        CierreMensual.fecha_fin.desc(),
        CierreMensualUsuario.consumo_total.desc()
    )

    # Paginación
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    # Serializar resultados
    serialized_items = []
    for snapshot in items:
        # Cierre e Impresora asociados
        cierre = snapshot.cierre
        printer = cierre.printer
        # Usuario asociado
        user = db.query(User).filter(User.id == snapshot.user_id).first()
        
        serialized_items.append(
            CierreUsuarioGlobalResponse(
                id=snapshot.id,
                cierre_mensual_id=snapshot.cierre_mensual_id,
                user_id=snapshot.user_id,
                codigo_usuario=user.codigo_de_usuario if user else str(snapshot.user_id),
                nombre_usuario=user.name if user else f"Usuario {snapshot.user_id}",
                
                # Contadores al cierre
                total_paginas=snapshot.total_paginas,
                total_bn=snapshot.total_bn,
                total_color=snapshot.total_color,
                copiadora_bn=snapshot.copiadora_bn,
                copiadora_color=snapshot.copiadora_color,
                impresora_bn=snapshot.impresora_bn,
                impresora_color=snapshot.impresora_color,
                escaner_bn=snapshot.escaner_bn,
                escaner_color=snapshot.escaner_color,
                fax_bn=snapshot.fax_bn,
                
                # Consumo del mes
                consumo_total=snapshot.consumo_total,
                consumo_copiadora=snapshot.consumo_copiadora,
                consumo_impresora=snapshot.consumo_impresora,
                consumo_escaner=snapshot.consumo_escaner,
                consumo_fax=snapshot.consumo_fax,
                
                created_at=snapshot.created_at,
                printer_id=cierre.printer_id,
                printer_hostname=printer.hostname,
                printer_ip=printer.ip_address,
                printer_location=printer.location,
                fecha_inicio=cierre.fecha_inicio,
                fecha_fin=cierre.fecha_fin,
                fecha_cierre=cierre.fecha_cierre,
                cerrado_por=cierre.cerrado_por
            )
        )

    pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "items": serialized_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.put("/monthly/users/{cierre_usuario_id}", response_model=CierreMensualUsuarioResponse, status_code=status.HTTP_200_OK)
async def update_cierre_usuario(
    cierre_usuario_id: int,
    payload: CierreUsuarioUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Modifica un registro de CierreMensualUsuario (el total acumulado y consumo mensual).
    Audita el cambio en auditoria_sistema.
    """
    from db.models import User, Printer, CierreMensual
    from sqlalchemy import text

    # Obtener el registro a actualizar
    snapshot = db.query(CierreMensualUsuario).filter(CierreMensualUsuario.id == cierre_usuario_id).first()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de consumo no encontrado")

    # Validar acceso a la impresora correspondiente
    cierre = snapshot.cierre
    printer = cierre.printer
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso para modificar este registro")

    # Guardar valores antiguos para auditoría
    old_total = snapshot.total_paginas
    old_consumo = snapshot.consumo_total

    # Actualizar valores
    snapshot.total_paginas = payload.total_paginas
    snapshot.consumo_total = payload.consumo_total

    # Obtener datos de usuario para el log
    user = db.query(User).filter(User.id == snapshot.user_id).first()
    user_name = user.name if user else f"Usuario ID {snapshot.user_id}"

    # Guardar en base de datos
    try:
        db.commit()
        db.refresh(snapshot)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar: {e}")

    # Registrar en auditoría de sistema
    descripcion_log = (
        f"Consumo mensual de usuario '{user_name}' en impresora '{printer.hostname}' modificado: "
        f"Consumo ({old_consumo} -> {payload.consumo_total}), "
        f"Total ({old_total} -> {payload.total_paginas})"
    )
    
    db.execute(
        text("""
            INSERT INTO auditoria_sistema (tipo, descripcion, usuario, printer_id, user_id, status)
            VALUES (:tipo, :descripcion, :usuario, :printer_id, :user_id, :status)
        """),
        {
            "tipo": "Modificación Cierre",
            "descripcion": descripcion_log,
            "usuario": current_user.nombre_completo,
            "printer_id": printer.id,
            "user_id": snapshot.user_id,
            "status": "warning"
        }
    )
    db.commit()

    # Formatear respuesta compatible con CierreMensualUsuarioResponse
    usuario_dict = {
        **{k: getattr(snapshot, k) for k in snapshot.__dict__ if not k.startswith('_')},
        'codigo_usuario': user.codigo_de_usuario if user else str(snapshot.user_id),
        'nombre_usuario': user.name if user else f"Usuario {snapshot.user_id}"
    }
    
    return CierreMensualUsuarioResponse(**usuario_dict)


@router.post("/comparaciones", response_model=ComparacionGuardadaResponse, status_code=status.HTTP_201_CREATED)
async def save_comparacion(
    payload: ComparacionGuardadaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Guarda una comparación mensual de cierres.
    Valida que ambos cierres pertenezcan a la misma empresa y que el usuario tenga acceso a ella.
    """
    # 1. Obtener cierres y validar existencia
    cierre1 = db.query(CierreMensual).filter(CierreMensual.id == payload.cierre1_id).first()
    cierre2 = db.query(CierreMensual).filter(CierreMensual.id == payload.cierre2_id).first()
    
    if not cierre1 or not cierre2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uno o ambos cierres mensuales no fueron encontrados"
        )
    
    # 2. Obtener impresoras asociadas para validar empresa
    printer1 = cierre1.printer
    printer2 = cierre2.printer
    
    if not printer1 or not printer2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las impresoras asociadas a los cierres no son válidas"
        )
        
    if printer1.empresa_id != printer2.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los cierres comparados deben pertenecer a la misma empresa"
        )
        
    # 3. Validar permisos de multi-tenancy
    if not CompanyFilterService.validate_company_access(current_user, printer1.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a los cierres de esta empresa"
        )
    
    # 4. Resolver empresa_id: puede ser None si la impresora no tiene empresa asignada
    # En ese caso usamos la empresa del usuario logueado. Si tampoco tiene, error explícito.
    empresa_id_final = printer1.empresa_id or getattr(current_user, 'empresa_id', None)
    if empresa_id_final is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede determinar la empresa: asigne una empresa a la impresora o al usuario antes de guardar comparaciones."
        )
        
    # 5. Crear registro
    nueva_comparacion = ComparacionGuardada(
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        cierre1_id=payload.cierre1_id,
        cierre2_id=payload.cierre2_id,
        snapshot_json=payload.snapshot_json,
        creado_por=current_user.nombre_completo,
        admin_user_id=current_user.id,
        empresa_id=empresa_id_final
    )
    
    db.add(nueva_comparacion)
    db.commit()
    db.refresh(nueva_comparacion)
    
    return nueva_comparacion


@router.get("/comparaciones", response_model=List[ComparacionGuardadaResponse], status_code=status.HTTP_200_OK)
async def list_comparaciones(
    cierre1_id: Optional[int] = Query(None),
    cierre2_id: Optional[int] = Query(None),
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lista las comparaciones guardadas para la empresa asignada del usuario (o todas si es superadmin).
    """
    query = db.query(ComparacionGuardada)
    
    # Enforce multi-tenancy
    if not current_user.is_superadmin():
        query = query.filter(ComparacionGuardada.empresa_id == current_user.empresa_id)
    elif empresa_id is not None:
        query = query.filter(ComparacionGuardada.empresa_id == empresa_id)
        
    # Filtros adicionales
    if cierre1_id is not None:
        query = query.filter(ComparacionGuardada.cierre1_id == cierre1_id)
    if cierre2_id is not None:
        query = query.filter(ComparacionGuardada.cierre2_id == cierre2_id)
        
    # Ordenar por fecha de creación descendente
    query = query.order_by(ComparacionGuardada.created_at.desc())
    
    return query.all()


@router.delete("/comparaciones/{comparacion_id}", status_code=status.HTTP_200_OK)
async def delete_comparacion(
    comparacion_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Elimina una comparación guardada.
    Valida el acceso a la empresa asociada a la comparación.
    """
    comparacion = db.query(ComparacionGuardada).filter(ComparacionGuardada.id == comparacion_id).first()
    if not comparacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La comparación guardada no fue encontrada"
        )
        
    # Validar permisos de multi-tenancy
    if not CompanyFilterService.validate_company_access(current_user, comparacion.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso para eliminar esta comparación"
        )
        
    db.delete(comparacion)
    db.commit()
    
    return {"message": "Comparación eliminada correctamente"}



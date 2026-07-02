"""
Network discovery API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os
import logging
from typing import Optional

from db.database import get_db
from db.repository import PrinterRepository
from db.models import PrinterStatus, User, UserPrinterAssignment
from services.network_scanner import NetworkScanner
from services.snmp_client import get_snmp_client
from middleware.auth_middleware import get_current_user
from .schemas import ScanRequest, ScanResponse, DiscoveredDevice, MessageResponse

router = APIRouter(prefix="/discovery", tags=["discovery"])
logger = logging.getLogger(__name__)


@router.post("/scan", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_network_endpoint(
    scan_request: ScanRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Scan network for Ricoh printers
    
    Performs real network scan - no demo mode
    """
    start_time = datetime.now()
    
    try:
        # Always perform actual network scan
        scanner = NetworkScanner(timeout=1.0)
        devices_data = await scanner.scan_network(scan_request.ip_range)
        
        # Calculate total IPs scanned
        import ipaddress
        network = ipaddress.ip_network(scan_request.ip_range, strict=False)
        total_scanned = network.num_addresses - 2
        
        # Convert to response schema
        devices = [DiscoveredDevice(**device) for device in devices_data]
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return ScanResponse(
            devices=devices,
            total_scanned=total_scanned,
            total_found=len(devices),
            scan_duration_seconds=round(duration, 2),
            timestamp=datetime.now()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scan failed: {str(e)}"
        )


@router.post("/register-discovered", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register_discovered_printers(
    devices: list[DiscoveredDevice],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Register discovered printers to database
    Skips printers that already exist (by IP)
    """
    registered_count = 0
    skipped_count = 0
    errors = []
    
    for device in devices:
        try:
            # Check if printer already exists
            existing = PrinterRepository.get_by_ip(db, device.ip_address)
            if existing:
                skipped_count += 1
                continue
            
            # Create new printer
            PrinterRepository.create(
                db,
                hostname=device.hostname,
                ip_address=device.ip_address,
                location=device.location,
                detected_model=device.detected_model,
                has_color=device.has_color,
                has_scanner=device.has_scanner,
                has_fax=device.has_fax,
                toner_cyan=device.toner_cyan,
                toner_magenta=device.toner_magenta,
                toner_yellow=device.toner_yellow,
                toner_black=device.toner_black,
                status=PrinterStatus(device.status)
            )
            registered_count += 1
            
        except Exception as e:
            errors.append(f"Failed to register {device.ip_address}: {str(e)}")
    
    message = f"Registered {registered_count} printer(s), skipped {skipped_count} existing"
    if errors:
        message += f". Errors: {'; '.join(errors)}"
    
    return MessageResponse(
        success=True,
        message=message
    )


@router.post("/check-printer", status_code=status.HTTP_200_OK)
async def check_single_printer(
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Verifica una sola impresora por IP y puerto SNMP
    Retorna información de la impresora si está disponible
    """
    ip_address = request.get('ip_address')
    snmp_port = request.get('snmp_port', 161)
    
    if not ip_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IP address is required"
        )
    
    try:
        scanner = NetworkScanner(timeout=2.0)
        
        # Verificar una sola IP
        device_info = await scanner.check_single_device(ip_address, snmp_port)
        
        if not device_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se pudo conectar con la impresora en {ip_address}"
            )
        
        return device_info
        
    except Exception as e:
        logger.error(f"Error checking printer {ip_address}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar impresora: {str(e)}"
        )


@router.post("/refresh-snmp/{printer_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def refresh_printer_snmp(
    printer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Refresh printer information.
    Attempts SNMP first, and falls back to scraping Web Image Monitor (WIM)
    to dynamically retrieve toner levels, status, etc.
    """
    # Get printer from database
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Check if SNMP is available
    snmp_client = get_snmp_client()
    if snmp_client:
        try:
            # Query SNMP
            snmp_info = await snmp_client.get_printer_info(printer.ip_address)
            
            # Update printer with SNMP data
            update_data = {}
            
            if snmp_info.model:
                update_data['detected_model'] = snmp_info.model
            if snmp_info.serial_number:
                update_data['serial_number'] = snmp_info.serial_number
            if snmp_info.location:
                update_data['location'] = snmp_info.location
            
            # Update toner levels
            if snmp_info.toner_black is not None:
                update_data['toner_black'] = snmp_info.toner_black
            if snmp_info.toner_cyan is not None:
                update_data['toner_cyan'] = snmp_info.toner_cyan
            if snmp_info.toner_magenta is not None:
                update_data['toner_magenta'] = snmp_info.toner_magenta
            if snmp_info.toner_yellow is not None:
                update_data['toner_yellow'] = snmp_info.toner_yellow
            
            # Update in database
            if update_data:
                PrinterRepository.update(db, printer_id, **update_data)
                
                # Invalidate dashboard cache so changes reflect instantly
                try:
                    from services.redis_service import redis_service
                    redis_service.invalidate_pattern("dashboard:*")
                except Exception as cache_err:
                    logger.warning(f"Failed to invalidate dashboard cache: {cache_err}")

                return MessageResponse(
                    success=True,
                    message=f"Printer {printer.hostname} updated via SNMP"
                )
            else:
                return MessageResponse(
                    success=False,
                    message="No SNMP data available for this printer"
                )
                
        except Exception as e:
            logger.warning(f"SNMP query failed for {printer.ip_address}, falling back to Web Image Monitor: {e}")
            
    # Web Image Monitor scraping fallback (SNMP is disabled or failed)
    try:
        from services.parsers import get_printer_toner_levels
        import asyncio
        
        loop = asyncio.get_event_loop()
        # Run synchronous scraping in an executor to avoid blocking the event loop
        toner_data = await loop.run_in_executor(None, get_printer_toner_levels, printer.ip_address)
        
        if toner_data.get('success'):
            update_data = {
                'toner_cyan': toner_data.get('cyan', 0),
                'toner_magenta': toner_data.get('magenta', 0),
                'toner_yellow': toner_data.get('yellow', 0),
                'toner_black': toner_data.get('black', 0),
                'status': PrinterStatus.ONLINE
            }
            PrinterRepository.update(db, printer_id, **update_data)
            
            # Invalidate dashboard cache so changes reflect instantly
            try:
                from services.redis_service import redis_service
                redis_service.invalidate_pattern("dashboard:*")
            except Exception as cache_err:
                logger.warning(f"Failed to invalidate dashboard cache: {cache_err}")

            return MessageResponse(
                success=True,
                message=f"Niveles de tóner de {printer.hostname} actualizados desde Web Image Monitor: Negro={update_data['toner_black']}%, Cian={update_data['toner_cyan']}%, Magenta={update_data['toner_magenta']}%, Amarillo={update_data['toner_yellow']}%."
            )
        else:
            return MessageResponse(
                success=False,
                message=f"No se pudo leer la información de tóners desde la web de la impresora: {toner_data.get('message')}"
            )
    except Exception as e:
        logger.error(f"Error scraping toner levels for printer {printer.ip_address}: {e}")
        return MessageResponse(
            success=False,
            message=f"Error al intentar obtener niveles de tóner desde la web: {str(e)}"
        )



@router.get("/user-details", status_code=status.HTTP_200_OK)
async def get_user_details_endpoint(
    printer_ip: str,
    entry_index: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene los detalles (permisos) de un usuario específico en una impresora
    Utilizado para Lazy Loading desde el Frontend
    """
    from services.ricoh_web_client import get_ricoh_web_client
    
    try:
        # Resolve printer password
        printer = PrinterRepository.get_by_ip(db, printer_ip)
        # Si la impresora no tiene contraseña en DB → pasar "" (vacía) para que el scraper
        # intente primero sin contraseña (fábrica). Si tiene contraseña → usarla primero.
        printer_pwd = printer.admin_password if (printer and printer.admin_password) else ""

        ricoh_client = get_ricoh_web_client()
        # No reseteamos sesión aquí para aprovechar cookies si ya existen
        details = ricoh_client._get_user_details(printer_ip, entry_index, fast_sync=False, admin_password=printer_pwd)
        
        if not details:
            # Scraper no pudo obtener datos (sin contraseña o sesión expirada).
            # Devolvemos los permisos guardados en DB como fallback.
            if printer and entry_index:
                from db.models import UserPrinterAssignment, User as UserModel
                assignment = db.query(UserPrinterAssignment).filter(
                    UserPrinterAssignment.printer_id == printer.id,
                    UserPrinterAssignment.entry_index == entry_index
                ).first()
                if assignment:
                    permisos_db = {
                        'copiadora': assignment.func_copier or False,
                        'copiadora_color': assignment.func_copier_color or False,
                        'impresora': assignment.func_printer or False,
                        'impresora_color': assignment.func_printer_color or False,
                        'document_server': assignment.func_document_server or False,
                        'fax': assignment.func_fax or False,
                        'escaner': assignment.func_scanner or False,
                        'navegador': assignment.func_browser or False,
                    }
                    tiene_alguno = any(permisos_db.values())
                    # Si tiene al menos 1 permiso en DB → el usuario está activo
                    from db.models import User as UserModel
                    user_obj = db.query(UserModel).filter(UserModel.id == assignment.user_id).first()
                    if tiene_alguno and user_obj and not user_obj.is_active:
                        user_obj.is_active = True
                        assignment.is_active = True
                        db.commit()
                        logger.info(f"🔄 Usuario ID {assignment.user_id} reactivado por permisos en DB (impresora {printer_ip} sin acceso de scraper)")
                    carpeta = user_obj.smb_path if user_obj else ''
                    logger.warning(f"⚠️  Scraper no pudo acceder a {printer_ip} - devolviendo permisos desde DB (entry: {entry_index})")
                    return {
                        "success": True,
                        "ip": printer_ip,
                        "entry_index": entry_index,
                        "permisos": permisos_db,
                        "carpeta": carpeta or '',
                        "fuente": "db_fallback"
                    }
            raise HTTPException(status_code=404, detail=f"No se pudieron obtener los detalles del usuario en {printer_ip}")
            
        # ACTUALIZACIÓN PERSISTENTE EN DB (cuando el scraper SÍ pudo):
        if printer and entry_index and details.get('permisos'):
            from db.models import UserPrinterAssignment
            assignment = db.query(UserPrinterAssignment).filter(
                UserPrinterAssignment.printer_id == printer.id,
                UserPrinterAssignment.entry_index == entry_index
            ).first()
            if assignment:
                from db.repository import AssignmentRepository
                from db.models import User as UserModel
                AssignmentRepository.update_assignment_state(
                    db=db,
                    user_id=assignment.user_id,
                    printer_id=printer.id,
                    permissions=details['permisos'],
                    entry_index=entry_index
                )
                
                # También actualizar carpeta SMB si viene en los detalles
                if details.get('carpeta'):
                    user_obj = db.query(UserModel).filter(UserModel.id == assignment.user_id).first()
                    if user_obj:
                        user_obj.smb_path = details['carpeta']
                        db.commit()
                logger.info(f"💾 Guardados permisos reales en DB + usuario reactivado. User ID: {assignment.user_id}, Printer: {printer.ip_address}")
            
        return {
            "success": True,
            "ip": printer_ip,
            "entry_index": entry_index,
            "permisos": details.get('permisos', {}),
            "carpeta": details.get('carpeta', '')
        }
    except HTTPException:
        # Re-lanzar HTTPExceptions sin convertirlas en 500
        raise
    except Exception as e:
        logger.error(f"Error inesperado obteniendo detalles de {printer_ip}: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/sync-users-from-printers", status_code=status.HTTP_200_OK)
async def sync_users_from_printers(
    user_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lee usuarios desde todas las impresoras físicas y los agrupa por código de usuario
    
    Args:
        user_code: Código de usuario específico a buscar (opcional). Si se proporciona,
                   solo busca ese usuario en todas las impresoras.
    
    Returns:
        Lista de usuarios únicos con información de en qué impresoras están registrados
    """
    from services.ricoh_web_client import get_ricoh_web_client
    from services.ricoh_selenium_client import close_selenium_client
    from db.repository import UserRepository
    
    logger.info("=" * 70)
    logger.info("🔄 INICIANDO SINCRONIZACIÓN DE USUARIOS")
    logger.info(f"   User code: {user_code if user_code else 'TODOS'}")
    logger.info("=" * 70)
    
    try:
        # Obtener todas las impresoras activas
        logger.info("📋 Obteniendo impresoras de la base de datos...")
        printers = PrinterRepository.get_all(db)
        logger.info(f"   Encontradas {len(printers)} impresoras")
        
        if not printers:
            logger.warning("⚠️ No hay impresoras registradas")
            return {
                "success": False,
                "message": "No hay impresoras registradas",
                "users": [],
                "users_by_printer": []
            }
        
        # Obtener el cliente web
        ricoh_client = get_ricoh_web_client()
        
        # Determinar modo de búsqueda
        if user_code:
            logger.info(f"🔍 Buscando usuario específico: {user_code}")
            mode = "specific"
        else:
            logger.info(f"📋 Sincronizando todos los usuarios")
            mode = "all"
        
        users_dict = {}  # Diccionario para agrupar usuarios por código
        errors = []
        printers_scanned = []
        
        for printer in printers:
            # Omitir impresoras Kyocera (.248 y .249) - no tienen usuarios registrados
            if printer.ip_address in ['192.168.91.248', '192.168.91.249']:
                printers_scanned.append({
                    'id': printer.id,
                    'hostname': printer.hostname,
                    'ip': printer.ip_address,
                    'users_count': 0,
                    'skipped': True,
                    'reason': 'Kyocera - sin usuarios'
                })
                continue
            
            try:
                # IMPORTANTE: Resetear sesión ANTES de cada impresora para evitar conflictos de cookies
                ricoh_client.reset_session()
                logger.info(f"🔄 Sesión reseteada para impresora {printer.hostname} ({printer.ip_address})")
                
                if mode == "specific" and user_code is not None:
                    # Buscar usuario específico (Incluye detalles/permisos automáticamente)
                    logger.info(f"🎯 Llamando a find_specific_user para {printer.ip_address}, usuario {user_code}")
                    user_found = ricoh_client.find_specific_user(printer.ip_address, user_code, admin_password=printer.admin_password)
                    logger.info(f"📋 Resultado de find_specific_user: {user_found}")
                    if user_found:
                        printer_users = [user_found]
                    else:
                        printer_users = []
                else:
                    # Leer todos los usuarios de la impresora (MODO RÁPIDO - sin permisos)
                    # Los permisos se cargan bajo demanda cuando se abre el usuario
                    logger.info(f"📋 Leyendo lista de usuarios de {printer.ip_address}...")
                    printer_users = ricoh_client.read_users_from_printer(printer.ip_address, fast_list=True, admin_password=printer.admin_password)
                
                printers_scanned.append({
                    'id': printer.id,
                    'hostname': printer.hostname,
                    'ip': printer.ip_address,
                    'users_count': len(printer_users)
                })
                
                for user in printer_users:
                    codigo = user['codigo']
                    
                    # Si buscamos usuario específico, verificar que coincida
                    if mode == "specific" and codigo != user_code:
                        continue
                    
                    # Si el usuario no existe en el diccionario, crearlo
                    if codigo not in users_dict:
                        # Verificar si ya existe en DB
                        existing = db.query(User).filter(
                            User.codigo_de_usuario == codigo
                        ).first()
                        
                        # ACTUALIZACIÓN DE PERSISTENCIA:
                        # Si ya existe en DB, actualizamos sus permisos reales para esta impresora.
                        # IMPORTANTE: En modo fast_list los permisos vienen todos en False (no se consultaron
                        # del hardware). Solo actualizamos permisos cuando hay datos reales del hardware,
                        # es decir cuando al menos un permiso está en True O cuando es modo specific.
                        if existing:
                            from db.repository import AssignmentRepository
                            permisos_del_usuario = user.get('permisos', {})
                            tiene_permisos_reales = (
                                mode == "specific" or
                                any(permisos_del_usuario.values())
                            )
                            if tiene_permisos_reales:
                                # Permisos reales del hardware → actualizar en BD
                                AssignmentRepository.update_assignment_state(
                                    db=db, 
                                    user_id=existing.id, 
                                    printer_id=printer.id, 
                                    entry_index=user.get('entry_index', ''), 
                                    permissions=permisos_del_usuario
                                )
                            else:
                                # Modo fast_list sin permisos reales → solo crear asignación si no existe,
                                # preservando los permisos ya guardados en BD
                                existing_assignment = db.query(UserPrinterAssignment).filter(
                                    UserPrinterAssignment.user_id == existing.id,
                                    UserPrinterAssignment.printer_id == printer.id
                                ).first()
                                if not existing_assignment:
                                    # Crear nueva asignación con permisos básicos activos por defecto (usuario descubierto activo físicamente)
                                    new_assignment = UserPrinterAssignment(
                                        user_id=existing.id,
                                        printer_id=printer.id,
                                        entry_index=user.get('entry_index', ''),
                                        is_active=True,
                                        func_copier=True,
                                        func_printer=True,
                                        func_scanner=True
                                    )
                                    db.add(new_assignment)
                                    db.commit()
                                    logger.info(f"   ➕ Nueva asignación creada con permisos activos por defecto para usuario {codigo} en impresora {printer.hostname}")
                                else:
                                    # Asignación ya existe: reactivar pero NO tocar los permisos
                                    if not existing_assignment.is_active:
                                        existing_assignment.is_active = True
                                        db.commit()
                                    logger.debug(f"   🔒 Preservando permisos existentes de {codigo} en {printer.hostname} (modo fast_list)")

                        users_dict[codigo] = {
                            'nombre': user['nombre'],
                            'codigo': codigo,
                            'empresa': user.get('empresa', ''),
                            'permisos': user['permisos'],
                            'carpeta': user['carpeta'],
                            'en_db': existing is not None,
                            'impresoras': []  # Lista de impresoras donde está registrado
                        }
                    
                    # Agregar esta impresora a la lista del usuario con sus permisos específicos
                    # IMPORTANTE: Verificar que no esté duplicada (mismo printer_id)
                    impresora_ya_existe = any(
                        imp['printer_id'] == printer.id 
                        for imp in users_dict[codigo]['impresoras']
                    )
                    
                    if not impresora_ya_existe:
                        logger.debug(f"   ➕ Agregando {codigo} a impresora {printer.hostname} ({printer.ip_address})")
                        users_dict[codigo]['impresoras'].append({
                            'printer_id': printer.id,
                            'printer_name': printer.hostname,
                            'printer_ip': printer.ip_address,
                            'entry_index': user.get('entry_index'),
                            'permisos': user['permisos'],
                            'carpeta': user['carpeta']
                        })
                    else:
                        logger.debug(f"   🔄 Actualizando {codigo} en impresora {printer.hostname} (ya existía)")
                        # Si ya existe, actualizar con el entry_index más reciente
                        for imp in users_dict[codigo]['impresoras']:
                            if imp['printer_id'] == printer.id:
                                # Actualizar con datos más recientes
                                imp['entry_index'] = user.get('entry_index')
                                imp['permisos'] = user['permisos']
                                imp['carpeta'] = user['carpeta']
                                break
                    
                    # Actualizar campos globales si aún no están definidos o para reflejar el estado más completo
                    # (Esto ayuda a pre-poblar el formulario de edición en el front)
                    if not any(users_dict[codigo]['permisos'].values()):
                         users_dict[codigo]['permisos'] = user['permisos']
                    if not users_dict[codigo]['carpeta']:
                         users_dict[codigo]['carpeta'] = user['carpeta']
                
            except Exception as e:
                errors.append(f"Error en {printer.hostname} ({printer.ip_address}): {str(e)}")
                printers_scanned.append({
                    'id': printer.id,
                    'hostname': printer.hostname,
                    'ip': printer.ip_address,
                    'users_count': 0,
                    'error': str(e)
                })
                continue
        
        # Cerrar el cliente Selenium si se usó
        close_selenium_client()
        
        # Convertir diccionario a lista
        users_list = list(users_dict.values())
        
        # Calcular estadísticas
        total_usuarios_unicos = len(users_list)
        usuarios_en_db = sum(1 for u in users_list if u['en_db'])
        usuarios_solo_impresoras = total_usuarios_unicos - usuarios_en_db
        
        if mode == "specific":
            if total_usuarios_unicos > 0:
                user = users_list[0]
                message = f"✅ Usuario '{user_code}' encontrado: {user['nombre']}"
                message += f" | Registrado en {len(user['impresoras'])} impresora(s)"
                if user['en_db']:
                    message += f" | 💾 Existe en DB"
                else:
                    message += f" | 🖨️ Solo en impresoras"
            else:
                message = f"❌ Usuario '{user_code}' no encontrado en ninguna impresora"
        else:
            message = f"✅ Se encontraron {total_usuarios_unicos} usuarios únicos en {len(printers_scanned)} impresora(s)"
            message += f" | 💾 {usuarios_en_db} en DB | 🖨️ {usuarios_solo_impresoras} solo en impresoras"
        
        if errors:
            message += f" | ⚠️ Errores: {len(errors)}"
        
        return {
            "success": True,
            "message": message,
            "users": users_list,
            "printers_scanned": printers_scanned,
            "total_printers": len(printers_scanned),
            "total_usuarios_unicos": total_usuarios_unicos,
            "usuarios_en_db": usuarios_en_db,
            "usuarios_solo_impresoras": usuarios_solo_impresoras,
            "search_mode": mode,
            "user_code_searched": user_code if mode == "specific" else None,
            "errors": errors if errors else []
        }
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error("❌ ERROR EN SINCRONIZACIÓN")
        logger.error(f"   Tipo: {type(e).__name__}")
        logger.error(f"   Mensaje: {str(e)}")
        logger.error("=" * 70)
        
        # Asegurar que se cierre Selenium en caso de error
        from services.ricoh_selenium_client import close_selenium_client
        close_selenium_client()
        
        # Log del traceback completo
        import traceback
        logger.error("Traceback completo:")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sincronizando usuarios: {str(e)}"
        )


@router.get("/printer/{printer_id}/live-diagnostics", status_code=status.HTTP_200_OK)
async def get_printer_live_diagnostics(
    printer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Realiza un escaneo y diagnóstico completo en vivo de una impresora desde el servidor:
    1. Verifica la existencia de la impresora en la base de datos.
    2. Realiza un escaneo paralelo de puertos de red relevantes (FTP, SSH, Telnet, HTTP, etc.).
    3. Intenta obtener los niveles de tóner en vivo vía scraping.
    4. Intenta consultar los contadores físicos generales (Copia, Impresión, Escáner, etc.).
    5. Intenta leer la cantidad de usuarios registrados en el equipo.
    """
    from datetime import datetime
    import socket
    from concurrent.futures import ThreadPoolExecutor
    from db.repository import PrinterRepository
    
    # 1. Obtener la impresora
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    ip = printer.ip_address
    
    # 2. Escaneo de puertos en paralelo
    ports = {
        21: "FTP",
        22: "SSH/SFTP",
        23: "Telnet",
        80: "HTTP (Web Image Monitor)",
        443: "HTTPS (Web Image Monitor SSL)",
        445: "SMB (Direct Directory)",
        515: "LPR (Line Printer Daemon)",
        631: "IPP (Internet Printing Protocol)",
        9100: "RAW (Direct Print)"
    }
    
    def check_port(port_num):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            res = s.connect_ex((ip, port_num))
            s.close()
            return port_num, (res == 0)
        except Exception:
            return port_num, False
            
    ports_status = {}
    with ThreadPoolExecutor(max_workers=len(ports)) as executor:
        futures = [executor.submit(check_port, p) for p in ports.keys()]
        for future in futures:
            p_num, is_open = future.result()
            ports_status[f"port_{p_num}_{ports[p_num].split(' ')[0].replace('/', '_').lower()}"] = {
                "port": p_num,
                "service": ports[p_num],
                "open": is_open
            }

    # 3. Consultar tóner en vivo
    toner_levels = {}
    toner_success = False
    try:
        from services.parsers import get_printer_toner_levels
        toner_data = get_printer_toner_levels(ip)
        if toner_data.get('success'):
            toner_levels = {
                "cyan": toner_data.get('cyan', 0),
                "magenta": toner_data.get('magenta', 0),
                "yellow": toner_data.get('yellow', 0),
                "black": toner_data.get('black', 0)
            }
            toner_success = True
        else:
            toner_levels = {"error": toner_data.get('message', 'Failed to retrieve')}
    except Exception as e:
        toner_levels = {"error": str(e)}

    # 4. Consultar contadores en vivo
    general_counters = {}
    counters_success = False
    try:
        from services.parsers import get_printer_counters
        counters_data = get_printer_counters(ip)
        if counters_data:
            general_counters = {
                "total": counters_data.get('total', 0),
                "copier_black": counters_data.get('copiadora', {}).get('blanco_negro', 0),
                "copier_color": counters_data.get('copiadora', {}).get('color', 0),
                "printer_black": counters_data.get('impresora', {}).get('blanco_negro', 0),
                "printer_color": counters_data.get('impresora', {}).get('color', 0),
                "fax": counters_data.get('fax', {}).get('blanco_negro', 0),
                "scanner_black": counters_data.get('envio_escaner', {}).get('blanco_negro', 0),
                "scanner_color": counters_data.get('envio_escaner', {}).get('color', 0)
            }
            counters_success = True
    except Exception as e:
        general_counters = {"error": str(e)}

    # 5. Obtener total de usuarios registrados
    users_registered_count = None
    users_success = False
    try:
        # Solo intentar si el puerto HTTP (80) está abierto
        if ports_status["port_80_http"]["open"]:
            from services.ricoh_web_client import get_ricoh_web_client
            ricoh_client = get_ricoh_web_client()
            # Reset session to avoid conflicts
            ricoh_client.reset_session()
            users_list = ricoh_client.read_users_from_printer(ip, fast_list=True, admin_password=printer.admin_password)
            users_registered_count = len(users_list)
            users_success = True
    except Exception as e:
        logger.warning(f"Failed to read users from printer {ip} during diagnostics: {e}")

    # 6. Compilar diagnóstico
    status_summary = "online" if ports_status["port_80_http"]["open"] else "offline"
    if status_summary == "online" and (not toner_success or not counters_success):
        status_summary = "limited" # HTTP responde pero falló lectura de contadores/tóners

    return {
        "success": True,
        "printer_id": printer.id,
        "hostname": printer.hostname,
        "ip_address": ip,
        "live_status": status_summary,
        "ports_diagnostics": ports_status,
        "toner_diagnostics": {
            "success": toner_success,
            "levels": toner_levels
        },
        "counter_diagnostics": {
            "success": counters_success,
            "counters": general_counters
        },
        "address_book_diagnostics": {
            "success": users_success,
            "registered_users_count": users_registered_count
        },
        "timestamp": datetime.now()
    }


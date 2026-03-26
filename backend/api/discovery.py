"""
Network discovery API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os
import logging

from db.database import get_db
from db.repository import PrinterRepository
from db.models import PrinterStatus, User
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
    Refresh printer information via SNMP
    Updates toner levels, model, serial number, etc.
    
    Note: Currently SNMP is disabled, returns informational message
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
    if not snmp_client:
        return MessageResponse(
            success=False,
            message="SNMP functionality is currently disabled. Printer data cannot be refreshed automatically."
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SNMP query failed: {str(e)}"
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
        ricoh_client = get_ricoh_web_client()
        # No reseteamos sesión aquí para aprovechar cookies si ya existen
        details = ricoh_client._get_user_details(printer_ip, entry_index, fast_sync=False)
        
        if not details:
            raise HTTPException(status_code=404, detail="No se pudieron obtener los detalles del usuario")
            
        return {
            "success": True,
            "ip": printer_ip,
            "entry_index": entry_index,
            "permisos": details.get('permisos', {}),
            "carpeta": details.get('carpeta', '')
        }
    except Exception as e:
        logger.error(f"Error obteniendo detalles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-users-from-printers", status_code=status.HTTP_200_OK)
async def sync_users_from_printers(
    user_code: str = None,
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
                
                if mode == "specific":
                    # Buscar usuario específico (Incluye detalles/permisos automáticamente)
                    logger.info(f"🎯 Llamando a find_specific_user para {printer.ip_address}, usuario {user_code}")
                    user_found = ricoh_client.find_specific_user(printer.ip_address, user_code)
                    logger.info(f"📋 Resultado de find_specific_user: {user_found}")
                    if user_found:
                        printer_users = [user_found]
                    else:
                        printer_users = []
                else:
                    # Leer todos los usuarios de la impresora (MODO RÁPIDO - sin permisos)
                    # Los permisos se cargan bajo demanda cuando se abre el usuario
                    logger.info(f"📋 Leyendo lista de usuarios de {printer.ip_address}...")
                    printer_users = ricoh_client.read_users_from_printer(printer.ip_address, fast_list=True)
                
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
                        # Si ya existe en DB, actualizamos sus permisos reales para esta impresora
                        if existing:
                            from db.repository import AssignmentRepository
                            AssignmentRepository.update_assignment_state(
                                db=db, 
                                user_id=existing.id, 
                                printer_id=printer.id, 
                                entry_index=user.get('entry_index', ''), 
                                permissions=user['permisos']
                            )

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

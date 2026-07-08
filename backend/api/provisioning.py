"""
Provisioning API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session
from typing import Optional

from db.database import get_db
from services.provisioning import ProvisioningService
from .schemas import (
    ProvisionRequest,
    ProvisionResponse,
    UserProvisioningStatus,
    PrinterUsersResponse,
    MessageResponse,
    UpdateUserFunctionsRequest,
    UpdateUserFunctionsResponse,
    UpdateAssignmentRequest
)

router = APIRouter(prefix="/provisioning", tags=["provisioning"])


@router.post("/provision", response_model=ProvisionResponse)
async def provision_user(
    provision_request: ProvisionRequest,
    db: Session = Depends(get_db)
):
    """
    Provision a user to multiple printers
    Creates assignments between user and printers
    """
    import logging
    logger = logging.getLogger(__name__)
    
    print("="*70)
    print("📥 PETICIÓN DE APROVISIONAMIENTO RECIBIDA")
    print(f"   User ID: {provision_request.user_id}")
    print(f"   Printer IDs: {provision_request.printer_ids}")
    print("="*70)
    
    logger.info(f"📥 Recibida petición de aprovisionamiento:")
    logger.info(f"   User ID: {provision_request.user_id}")
    logger.info(f"   Printer IDs: {provision_request.printer_ids}")
    logger.info(f"   Cantidad de impresoras: {len(provision_request.printer_ids)}")
    
    try:
        result = ProvisioningService.provision_user_to_printers(
            db,
            provision_request.user_id,
            provision_request.printer_ids
        )
        return ProvisionResponse(**result)
    except ValueError as e:
        logger.error(f"❌ Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error durante aprovisionamiento: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provisioning failed: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=UserProvisioningStatus)
async def get_user_provisioning(user_id: int, db: Session = Depends(get_db)):
    """
    Get provisioning status for a user
    Returns user info and all assigned printers
    """
    try:
        status_data = ProvisioningService.get_user_provisioning_status(db, user_id)
        return UserProvisioningStatus(**status_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provisioning status: {str(e)}"
        )


@router.get("/printer/{printer_id}", response_model=PrinterUsersResponse)
async def get_printer_users(printer_id: int, db: Session = Depends(get_db)):
    """
    Get all users provisioned to a printer
    """
    try:
        users_data = ProvisioningService.get_printer_users(db, printer_id)
        return PrinterUsersResponse(**users_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get printer users: {str(e)}"
        )


@router.patch("/update-assignment")
async def update_assignment_permissions(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update permissions for a specific user-printer assignment
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Leer el body manualmente
        body = await request.json()
        
        user_id = body.get('user_id')
        printer_id = body.get('printer_id')
        permissions = body.get('permissions')
        entry_index = body.get('entry_index')
        
        if not user_id or not printer_id or not permissions:
            raise HTTPException(status_code=400, detail="Faltan parámetros requeridos: user_id, printer_id, permissions")
        
        logger.info(f"📝 Actualizando permisos de asignación:")
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Printer ID: {printer_id}")
        logger.info(f"   Entry Index: {entry_index}")
        logger.info(f"   Permissions: {permissions}")
        
        from db.repository import AssignmentRepository
        
        # Actualizar en DB
        success = AssignmentRepository.update_assignment_state(
            db, 
            user_id, 
            printer_id, 
            permissions=permissions,
            entry_index=entry_index
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
            
        # Intentar actualizar en HARDWARE
        assignment = AssignmentRepository.get_by_user_and_printer(db, user_id, printer_id)
        if assignment:
            from db.repository import UserRepository, PrinterRepository
            from services.ricoh_web_client import get_ricoh_web_client
            
            user = UserRepository.get_by_id(db, user_id)
            printer = PrinterRepository.get_by_id(db, printer_id)
            
            if user and printer:
                client = get_ricoh_web_client()
                resolved_entry_index = assignment.entry_index
                
                # 1. Si no tiene entry_index en DB, intentar buscar al usuario en la impresora por su código
                if not resolved_entry_index:
                    logger.info(f"   🔍 [{printer.ip_address}] entry_index no registrado en DB para usuario {user.codigo_de_usuario}. Buscando en el equipo...")
                    user_in_printer = client.find_specific_user(printer.ip_address, user.codigo_de_usuario, admin_password=printer.admin_password)
                    if user_in_printer and user_in_printer.get('entry_index'):
                        resolved_entry_index = user_in_printer['entry_index']
                        # Guardar entry_index en DB
                        assignment.entry_index = resolved_entry_index
                        db.commit()
                        logger.info(f"   ✅ [{printer.ip_address}] Usuario encontrado en slot: {resolved_entry_index}")
                
                # 2. Si aún no tiene entry_index, significa que no existe en el equipo, aprovisionarlo
                if not resolved_entry_index:
                    logger.info(f"   ➕ [{printer.ip_address}] Usuario {user.codigo_de_usuario} no registrado en la impresora. Aprovisionando automáticamente...")
                    try:
                        from services.provisioning import ProvisioningService
                        # provision_user_to_printers creará la asignación física y actualizará la DB
                        ProvisioningService.provision_user_to_printers(db, user_id, [printer_id], reconcile=False)
                        db.refresh(assignment)
                        resolved_entry_index = assignment.entry_index
                        logger.info(f"   ✅ [{printer.ip_address}] Aprovisionamiento automático completado: slot {resolved_entry_index}")
                    except Exception as prov_err:
                        logger.error(f"   ❌ [{printer.ip_address}] Error al aprovisionar automáticamente: {prov_err}")
                
                # 3. Si logramos resolver el slot, aplicar los permisos en la impresora
                if resolved_entry_index:
                    logger.info(f"   📤 [{printer.ip_address}] Sincronizando funciones en slot {resolved_entry_index}...")
                    
                    import time
                    attempts = 0
                    max_attempts = 4
                    delay = 5.0
                    sync_success = False
                    last_res = None
                    
                    while attempts < max_attempts:
                        attempts += 1
                        logger.info(f"   [{printer.ip_address}] Intento {attempts} de {max_attempts} para sincronizar permisos...")
                        res = client.set_user_functions(
                            printer.ip_address, 
                            resolved_entry_index, 
                            permissions, 
                            admin_password=printer.admin_password
                        )
                        
                        if res is True:
                            sync_success = True
                            break
                        elif res in ["BUSY", "TIMEOUT"]:
                            last_res = res
                            logger.warning(f"   [{printer.ip_address}] Impresora ocupada o timeout (intento {attempts}/{max_attempts}). Esperando {delay}s...")
                            if attempts < max_attempts:
                                time.sleep(delay)
                        else:
                            last_res = res
                            break
                            
                    if not sync_success:
                        err_msg = "falló la sincronización con la impresora"
                        if last_res == "BUSY":
                            err_msg = "este dispositivo está siendo utilizado por otras funciones. Inténtelo de nuevo posteriormente."
                        elif last_res == "TIMEOUT":
                            err_msg = "tiempo de espera agotado al conectar con la impresora"
                        return {"success": False, "message": f"Guardado en DB, pero {err_msg} en {printer.ip_address} (tras {attempts} intentos)."}
                else:
                    return {"success": False, "message": f"Guardado en DB, pero no se pudo encontrar ni registrar al usuario en la impresora {printer.ip_address}"}
        
        return {"success": True, "message": "Permisos actualizados y sincronizados correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"❌ Error en update_assignment: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remove", response_model=MessageResponse)
async def remove_user_from_printers(
    request_data: ProvisionRequest,
    db: Session = Depends(get_db)
):
    """
    Remove user from specified printers
    """
    try:
        result = ProvisioningService.remove_user_from_printers(
            db,
            request_data.user_id,
            request_data.printer_ids
        )
        return MessageResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove assignments: {str(e)}"
        )


@router.put("/printers/{printer_ip}/users/{user_code}/functions", response_model=UpdateUserFunctionsResponse)
async def update_user_functions(
    printer_ip: str,
    user_code: str,
    functions: UpdateUserFunctionsRequest,
    db: Session = Depends(get_db)
):
    """
    Actualiza las funciones de un usuario en una impresora específica.
    
    Este endpoint:
    1. Busca el usuario por código
    2. Busca la impresora por IP
    3. Busca la asignación (assignment) entre usuario e impresora
    4. Actualiza las funciones en la impresora física usando ricoh_web_client
    5. Actualiza las funciones en la base de datos
    
    Args:
        printer_ip: IP de la impresora
        user_code: Código del usuario (ej: "7104")
        functions: Funciones a habilitar/deshabilitar
        
    Returns:
        UpdateUserFunctionsResponse con el resultado de la operación
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📝 Actualizando funciones para usuario {user_code} en impresora {printer_ip}")
    
    try:
        from db.repository import UserRepository, PrinterRepository, AssignmentRepository
        from services.ricoh_web_client import get_ricoh_web_client
        
        # 1. Buscar usuario por código
        user = UserRepository.get_by_codigo(db, user_code)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con código {user_code} no encontrado"
            )
        
        # 2. Buscar impresora por IP
        printer = PrinterRepository.get_by_ip(db, printer_ip)
        if not printer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Impresora con IP {printer_ip} no encontrada"
            )
        
        # 3. Buscar asignación
        assignment = AssignmentRepository.get_by_user_and_printer(db, user.id, printer.id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe asignación entre usuario {user_code} e impresora {printer_ip}"
            )
        
        if not assignment.entry_index:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario no tiene entry_index en la impresora. Debe ser provisionado primero."
            )
        
        # 4. Preparar permisos en formato esperado por ricoh_web_client
        permissions = {
            'copiadora': functions.copiadora,
            'copiadora_color': functions.copiadora_color,
            'impresora': functions.impresora,
            'impresora_color': functions.impresora_color,
            'escaner': functions.escaner,
            'document_server': functions.document_server,
            'fax': functions.fax,
            'navegador': functions.navegador
        }
        
        logger.info(f"   Permisos a aplicar: {permissions}")
        
        # 5. Actualizar en la impresora física
        client = get_ricoh_web_client()
        success = client.set_user_functions(printer_ip, assignment.entry_index, permissions)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar funciones en la impresora física"
            )
        
        logger.info(f"   ✅ Funciones actualizadas en impresora física")
        
        # 6. Actualizar en la base de datos
        update_success = AssignmentRepository.update_assignment_state(
            db,
            user.id,
            printer.id,
            permissions=permissions
        )
        
        if not update_success:
            logger.warning(f"   ⚠️ Funciones actualizadas en impresora pero no en DB")
        else:
            logger.info(f"   ✅ Funciones actualizadas en base de datos")
        
        return UpdateUserFunctionsResponse(
            success=True,
            message="Funciones actualizadas correctamente",
            user_code=user_code,
            printer_ip=printer_ip,
            functions_updated=permissions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando funciones: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar funciones: {str(e)}"
        )


@router.post("/printers/{printer_ip}/sync", response_model=MessageResponse)
async def sync_printer_users(
    printer_ip: str,
    fast_list: bool = True,
    db: Session = Depends(get_db)
):
    """
    Sincroniza todos los usuarios de una impresora.
    
    Lee todos los usuarios desde la impresora física y actualiza
    sus funciones reales en la base de datos.
    
    Args:
        printer_ip: IP de la impresora
        fast_list: Si es True, hace sincronización rápida sin cargar permisos individuales
        
    Returns:
        MessageResponse con el resultado de la sincronización
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔄 Sincronizando usuarios de impresora {printer_ip} (fast_list={fast_list})")
    
    try:
        from db.repository import PrinterRepository, AssignmentRepository
        from services.ricoh_web_client import get_ricoh_web_client
        
        # 1. Buscar impresora
        printer = PrinterRepository.get_by_ip(db, printer_ip)
        if not printer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Impresora con IP {printer_ip} no encontrada"
            )
        
        # 2. Leer usuarios desde la impresora
        client = get_ricoh_web_client()
        users_from_printer = client.read_users_from_printer(printer_ip, fast_list=fast_list, admin_password=printer.admin_password)
        
        if not users_from_printer:
            return MessageResponse(
                success=True,
                message=f"No se encontraron usuarios en la impresora {printer_ip}"
            )
        
        logger.info(f"   Encontrados {len(users_from_printer)} usuarios en la impresora")
        
        # 3. Actualizar funciones en DB para cada usuario
        updated_count = 0
        for user_data in users_from_printer:
            user_code = user_data.get('codigo')
            entry_index = user_data.get('entry_index')
            permisos = user_data.get('permisos', {})
            
            if not user_code or not entry_index:
                continue
            
            # Buscar usuario en DB por código
            from db.repository import UserRepository
            user = UserRepository.get_by_codigo(db, user_code)
            
            if not user:
                logger.debug(f"   Usuario {user_code} no existe en DB, saltando...")
                continue
            
            # Buscar o crear asignación durante la sincronización
            # No saltar si no existe la asignación, ya que update_assignment_state la creará
            # Actualizar funciones en DB (solo si no es fast_list)
            if user_data.get('lazy'):
                permissions = None
            else:
                permissions = {
                    'copiadora': permisos.get('copiadora', False),
                    'copiadora_color': permisos.get('copiadora_color', False),
                    'impresora': permisos.get('impresora', False),
                    'impresora_color': permisos.get('impresora_color', False),
                    'escaner': permisos.get('escaner', False),
                    'document_server': permisos.get('document_server', False),
                    'fax': permisos.get('fax', False),
                    'navegador': permisos.get('navegador', False)
                }
            
            success = AssignmentRepository.update_assignment_state(
                db,
                user.id,
                printer.id,
                permissions=permissions,
                entry_index=entry_index
            )
            
            if success:
                updated_count += 1
        
        logger.info(f"   ✅ Sincronizados {updated_count} usuarios")
        
        return MessageResponse(
            success=True,
            message=f"Sincronizados {updated_count} de {len(users_from_printer)} usuarios"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error sincronizando usuarios: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar usuarios: {str(e)}"
        )


@router.put("/users/{user_id}/sync-to-all-printers", response_model=MessageResponse)
async def sync_user_to_all_printers(
    user_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Sincroniza los datos del usuario (carpeta, credenciales) a las impresoras especificadas en paralelo.
    
    IMPORTANTE: Solo sincroniza nombre, código, carpeta y credenciales.
    NO modifica los permisos (cada impresora mantiene sus permisos actuales).
    """
    import logging
    from concurrent.futures import ThreadPoolExecutor
    logger = logging.getLogger(__name__)
    
    try:
        from db.repository import UserRepository, AssignmentRepository, PrinterRepository
        from services.ricoh_web_client import get_ricoh_web_client
        
        # 1. Obtener usuario
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado"
            )
        
        printer_ips = request.get('printer_ips', [])
        sync_permissions = request.get('sync_permissions', False)
        
        if not printer_ips:
            return MessageResponse(
                success=True,
                message="No se especificaron impresoras para sincronizar"
            )
        
        logger.info(f"🔄 Sincronizando usuario {user.codigo_de_usuario} a {len(printer_ips)} impresoras EN PARALELO")
        logger.info(f"   IPs: {printer_ips}")
        logger.info(f"   Solo sincronizando: nombre, código, carpeta, usuario_red")
        logger.info(f"   Permisos: {'Sincronizando permisos base' if sync_permissions else 'se mantienen los actuales de cada impresora'}")
        
        # 2. Pre-cargar datos de impresoras y asignaciones en el hilo principal
        printers_to_sync = []
        for printer_ip in printer_ips:
            printer = PrinterRepository.get_by_ip(db, printer_ip)
            if not printer:
                logger.warning(f"   ⚠️  Impresora {printer_ip} no encontrada en DB, omitiendo")
                continue
            
            assignment = AssignmentRepository.get_by_user_and_printer(db, user_id, printer.id)
            entry_index = assignment.entry_index if assignment else None
            
            printers_to_sync.append({
                'printer_id': printer.id,
                'printer_ip': printer.ip_address,
                'printer_name': printer.hostname,
                'admin_password': printer.admin_password,
                'entry_index': entry_index,
                'has_assignment': assignment is not None,
                'has_color': printer.has_color
            })
            
        if not printers_to_sync:
            return MessageResponse(
                success=False,
                message="Ninguna de las impresoras especificadas existe en la base de datos"
            )
            
        # 3. Definir la función worker que ejecutará los llamadas de red lentas
        # Esta función corre en hilos separados y NO debe hacer escrituras en la DB usando la sesión compartida
        def sync_printer_worker(p_data):
            from services.ricoh_web_client import create_ricoh_web_client
            client = create_ricoh_web_client()
            printer_ip = p_data['printer_ip']
            entry_index = p_data['entry_index']
            admin_password = p_data['admin_password']
            
            resolved_permissions = None
            resolved_entry_index = entry_index
            assignment_needs_update = False
            
            try:
                # A. Si no tiene entry_index en DB, buscar el usuario en la impresora física
                if not resolved_entry_index:
                    logger.info(f"   🔍 [{printer_ip}] Buscando usuario {user.codigo_de_usuario} en el equipo...")
                    user_in_printer = client.find_specific_user(printer_ip, user.codigo_de_usuario, admin_password=admin_password)
                    if user_in_printer and user_in_printer.get('entry_index'):
                        resolved_entry_index = user_in_printer['entry_index']
                        resolved_permissions = user_in_printer.get('permisos', {})
                        assignment_needs_update = True
                        logger.info(f"   ✅ [{printer_ip}] Usuario encontrado con entry_index: {resolved_entry_index}")
                    else:
                        return {
                            'ip': printer_ip,
                            'success': False,
                            'error': "Usuario no registrado en esta impresora"
                        }
                
                # B. Preparar datos de sincronización
                user_data = {
                    'entry_index': resolved_entry_index,
                    'nombre': user.name,
                    'codigo': user.codigo_de_usuario,
                    'carpeta': user.smb_path,
                    'usuario_red': user.network_username,
                }
                
                if sync_permissions:
                    # Adaptar color según capacidades de la impresora
                    has_color = p_data.get('has_color', False)
                    user_data['permisos'] = {
                        'copiadora': user.func_copier,
                        'copiadora_color': user.func_copier_color if has_color else False,
                        'impresora': user.func_printer,
                        'impresora_color': user.func_printer_color if has_color else False,
                        'escaner': user.func_scanner,
                        'document_server': user.func_document_server,
                        'fax': user.func_fax,
                        'navegador': user.func_browser
                    }
                
                # C. Actualizar datos en la impresora física con reintentos para BUSY/TIMEOUT
                logger.info(f"   📤 [{printer_ip}] Enviando datos de carpeta/perfil...")
                
                import time
                attempts = 0
                max_attempts = 12
                delay = 4.0
                sync_success = False
                last_result = None
                
                while attempts < max_attempts:
                    attempts += 1
                    logger.info(f"   [{printer_ip}] Intento {attempts} de {max_attempts} para actualizar carpeta/perfil...")
                    result = client.update_user_in_printer(printer_ip, user_data, admin_password=admin_password)
                    
                    if result is True:
                        sync_success = True
                        break
                    elif result in ["BUSY", "TIMEOUT"]:
                        last_result = result
                        logger.warning(f"   [{printer_ip}] Impresora ocupada o timeout (intento {attempts}/{max_attempts}). Esperando {delay}s...")
                        if attempts < max_attempts:
                            time.sleep(delay)
                    else:
                        last_result = result
                        break
                        
                if sync_success:
                    logger.info(f"   ✅ [{printer_ip}] Actualización física exitosa")
                    return {
                        'ip': printer_ip,
                        'success': True,
                        'printer_id': p_data['printer_id'],
                        'entry_index': resolved_entry_index,
                        'permissions': resolved_permissions,
                        'assignment_needs_update': assignment_needs_update
                    }
                else:
                    err_msg = "Error devuelto por la interfaz web de la impresora"
                    if last_result == "BUSY":
                        err_msg = "este dispositivo está siendo utilizado por otras funciones. Inténtelo de nuevo posteriormente."
                    elif last_result == "TIMEOUT":
                        err_msg = "tiempo de espera agotado al conectar con la impresora"
                    return {
                        'ip': printer_ip,
                        'success': False,
                        'error': err_msg
                    }
                    
            except Exception as e:
                return {
                    'ip': printer_ip,
                    'success': False,
                    'error': f"Excepción de conexión: {str(e)}"
                }
                
        # 4. Disparar el pool de hilos paralelos
        logger.info(f"🚀 Iniciando ThreadPoolExecutor para {len(printers_to_sync)} impresoras...")
        with ThreadPoolExecutor(max_workers=min(len(printers_to_sync), 10)) as executor:
            worker_results = list(executor.map(sync_printer_worker, printers_to_sync))
            
        # 5. Procesar los resultados y guardar en DB en el hilo principal
        success_count = 0
        error_count = 0
        errors = []
        
        for res in worker_results:
            printer_ip = res['ip']
            if res['success']:
                success_count += 1
                if sync_permissions or res['assignment_needs_update']:
                    try:
                        logger.info(f"   💾 Guardando asignación en DB para {printer_ip}...")
                        
                        # Si sincronizamos permisos, usamos los que se mandaron a la impresora
                        if sync_permissions:
                            p_info = next((p for p in printers_to_sync if p['printer_ip'] == printer_ip), {})
                            has_color = p_info.get('has_color', False)
                            perms_to_save = {
                                'copiadora': user.func_copier,
                                'copiadora_color': user.func_copier_color if has_color else False,
                                'impresora': user.func_printer,
                                'impresora_color': user.func_printer_color if has_color else False,
                                'escaner': user.func_scanner,
                                'document_server': user.func_document_server,
                                'fax': user.func_fax,
                                'navegador': user.func_browser
                            }
                        else:
                            perms_to_save = res['permissions'] or {}

                        AssignmentRepository.update_assignment_state(
                            db=db,
                            user_id=user_id,
                            printer_id=res['printer_id'],
                            entry_index=res['entry_index'],
                            permissions=perms_to_save
                        )
                    except Exception as db_err:
                        logger.error(f"   ❌ Error guardando asignación en DB para {printer_ip}: {db_err}")
            else:
                error_count += 1
                errors.append(f"{printer_ip}: {res['error']}")
                
        # Devolver respuesta final
        message = f"Sincronizado en {success_count} de {len(printer_ips)} impresoras"
        if error_count > 0:
            message += f" ({error_count} errores: {', '.join(errors)})"
            
        return MessageResponse(
            success=success_count > 0,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error sincronizando usuario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar usuario: {str(e)}"
        )

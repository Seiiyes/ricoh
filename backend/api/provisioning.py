"""
Provisioning API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
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
    UpdateUserFunctionsResponse
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


@router.patch("/update-assignment", response_model=MessageResponse)
async def update_assignment_permissions(
    user_id: int,
    printer_id: int,
    permissions: dict,
    entry_index: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update permissions for a specific user-printer assignment
    """
    try:
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
            
        # Intentar actualizar en HARDWARE si el usuario tiene entry_index
        assignment = AssignmentRepository.get_by_user_and_printer(db, user_id, printer_id)
        if assignment and assignment.entry_index:
            from services.ricoh_web_client import get_ricoh_web_client
            from db.repository import PrinterRepository
            
            printer = PrinterRepository.get_by_id(db, printer_id)
            if printer:
                client = get_ricoh_web_client()
                # Ejecutar sincronización física y verificar resultado
                sync_success = client.set_user_functions(printer.ip_address, assignment.entry_index, permissions)
                
                if not sync_success:
                    return {"success": False, "message": f"Guardado en DB, pero falló la sincronización con la impresora {printer.ip_address}"}
        
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
    user_id: int,
    printer_ids: list[int],
    db: Session = Depends(get_db)
):
    """
    Remove user from specified printers
    """
    try:
        result = ProvisioningService.remove_user_from_printers(
            db,
            user_id,
            printer_ids
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
    db: Session = Depends(get_db)
):
    """
    Sincroniza todos los usuarios de una impresora.
    
    Lee todos los usuarios desde la impresora física y actualiza
    sus funciones reales en la base de datos.
    
    Args:
        printer_ip: IP de la impresora
        
    Returns:
        MessageResponse con el resultado de la sincronización
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔄 Sincronizando usuarios de impresora {printer_ip}")
    
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
        users_from_printer = client.read_users_from_printer(printer_ip, fast_list=False)
        
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
            
            # Buscar asignación
            assignment = AssignmentRepository.get_by_user_and_printer(db, user.id, printer.id)
            
            if not assignment:
                logger.debug(f"   No hay asignación para usuario {user_code}, saltando...")
                continue
            
            # Actualizar funciones en DB
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
    Sincroniza los datos del usuario (carpeta, credenciales) a las impresoras especificadas
    
    IMPORTANTE: Solo sincroniza nombre, código, carpeta y credenciales.
    NO modifica los permisos (cada impresora mantiene sus permisos actuales).
    
    Args:
        user_id: ID del usuario
        request: Body con {"printer_ips": ["192.168.91.251", "192.168.91.252", ...]}
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from db.repository import UserRepository, AssignmentRepository, PrinterRepository
        from services.ricoh_web_client import RicohWebClient
        
        # 1. Obtener usuario
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado"
            )
        
        printer_ips = request.get('printer_ips', [])
        
        if not printer_ips:
            return MessageResponse(
                success=True,
                message="No se especificaron impresoras para sincronizar"
            )
        
        logger.info(f"🔄 Sincronizando usuario {user.codigo_de_usuario} a {len(printer_ips)} impresoras")
        logger.info(f"   IPs: {printer_ips}")
        logger.info(f"   Solo sincronizando: nombre, código, carpeta, usuario_red")
        logger.info(f"   Permisos: se mantienen los actuales de cada impresora")
        
        # 2. Actualizar en cada impresora física
        client = RicohWebClient()
        success_count = 0
        error_count = 0
        
        for printer_ip in printer_ips:
            try:
                # Buscar la impresora en la DB por IP
                printer = PrinterRepository.get_by_ip(db, printer_ip)
                if not printer:
                    logger.warning(f"   ⚠️  Impresora {printer_ip} no encontrada en DB")
                    error_count += 1
                    continue
                
                # Obtener la asignación para obtener el entry_index
                assignment = AssignmentRepository.get_by_user_and_printer(db, user_id, printer.id)
                
                # Si no hay assignment o no tiene entry_index, buscar el usuario en la impresora
                entry_index = None
                if assignment and assignment.entry_index:
                    entry_index = assignment.entry_index
                else:
                    logger.info(f"   🔍 No hay assignment, buscando usuario {user.codigo_de_usuario} en {printer_ip}...")
                    try:
                        # Buscar el usuario directamente en la impresora
                        user_in_printer = client.find_specific_user(printer_ip, user.codigo_de_usuario)
                        if user_in_printer and user_in_printer.get('entry_index'):
                            entry_index = user_in_printer['entry_index']
                            logger.info(f"   ✅ Usuario encontrado en impresora con entry_index: {entry_index}")
                            
                            # Crear o actualizar el assignment en la DB
                            logger.info(f"   📝 {'Creando' if not assignment else 'Actualizando'} assignment en DB...")
                            AssignmentRepository.update_assignment_state(
                                db=db,
                                user_id=user_id,
                                printer_id=printer.id,
                                entry_index=entry_index,
                                permissions=user_in_printer.get('permisos', {})
                            )
                        else:
                            logger.warning(f"   ⚠️  Usuario {user.codigo_de_usuario} no encontrado en {printer_ip}")
                            error_count += 1
                            continue
                    except Exception as search_error:
                        logger.error(f"   ❌ Error buscando usuario en impresora: {search_error}")
                        error_count += 1
                        continue
                
                if not entry_index:
                    logger.warning(f"   ⚠️  No se pudo obtener entry_index para {printer.hostname} ({printer_ip})")
                    error_count += 1
                    continue
                
                # Preparar datos del usuario SIN permisos (para que mantenga los actuales)
                user_data = {
                    'entry_index': entry_index,
                    'nombre': user.name,
                    'codigo': user.codigo_de_usuario,
                    'carpeta': user.smb_path,
                    'usuario_red': user.network_username,
                    # NO incluir 'permisos' - el método update_user_in_printer leerá y mantendrá los actuales
                }
                
                # Actualizar en la impresora física
                result = client.update_user_in_printer(printer.ip_address, user_data)
                
                if result:
                    logger.info(f"   ✅ Actualizado en {printer.hostname} ({printer.ip_address})")
                    success_count += 1
                else:
                    logger.error(f"   ❌ Error actualizando en {printer.hostname}")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"   ❌ Error en {printer_ip}: {e}")
                error_count += 1
        
        message = f"Sincronizado en {success_count} de {len(printer_ips)} impresoras"
        if error_count > 0:
            message += f" ({error_count} errores)"
        
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

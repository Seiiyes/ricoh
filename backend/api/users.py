"""
User management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import logging

from db.database import get_db
from db.repository import UserRepository, PrinterRepository
from db.models import User, UserPrinterAssignment
from services.encryption_service import EncryptionService
from services.provisioning import ProvisioningService
from services.sanitization_service import SanitizationService
from .schemas import UserCreate, UserUpdate, UserResponse, UserListResponse, MessageResponse, UserCreateResponse

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/debug", status_code=200)
async def debug_user_creation(request: Request):
    """Debug endpoint to see what data is being sent"""
    body = await request.body()
    logger.info("=" * 80)
    logger.info("DEBUG: User creation request")
    logger.info("=" * 80)
    logger.info(f"Raw body: {body.decode('utf-8')}")
    
    try:
        import json
        data = json.loads(body)
        logger.info("Parsed JSON:")
        for key, value in data.items():
            logger.info(f"  {key}: {value} (type: {type(value).__name__})")
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
    
    return {"received": body.decode('utf-8')}


@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with optional automatic provisioning to printers
    Accepts both nested and flat data structures
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📥 Received user creation request")
    
    # Sanitizar inputs de texto
    sanitized_name = SanitizationService.sanitize_string(user.name)
    sanitized_codigo = SanitizationService.sanitize_string(user.codigo_de_usuario)
    
    logger.info(f"   Name: {sanitized_name}")
    logger.info(f"   Código: {sanitized_codigo}")
    logger.info(f"   Empresa: {user.empresa}")
    logger.info(f"   Centro costos: {user.centro_costos}")
    
    # Validate printer IDs if provided
    if user.printer_ids:
        logger.info(f"   Printer IDs: {user.printer_ids}")
        for printer_id in user.printer_ids:
            printer = PrinterRepository.get_by_id(db, printer_id)
            if not printer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Printer with ID {printer_id} not found"
                )
    
    # Check if codigo_de_usuario already exists
    existing_codigo = UserRepository.get_by_codigo(db, sanitized_codigo)
    if existing_codigo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with código de usuario {sanitized_codigo} already exists"
        )
    
    # Extract network credentials (nested or flat) y sanitizar
    if user.network_credentials:
        logger.info("   Using nested network_credentials")
        network_username = SanitizationService.sanitize_string(user.network_credentials.username)
        raw_password = user.network_credentials.password or ""
    else:
        logger.info("   Using flat network fields")
        network_username = SanitizationService.sanitize_string(user.network_username or "reliteltda\\scaner")
        raw_password = user.network_password or ""
    
    logger.info(f"   Network username: {network_username}")
    
    # Extract SMB configuration (nested or flat) y sanitizar
    if user.smb_config:
        logger.info("   Using nested smb_config")
        smb_server = SanitizationService.sanitize_string(user.smb_config.server)
        smb_port = user.smb_config.port
        smb_path = SanitizationService.sanitize_string(user.smb_config.path or "")
    else:
        logger.info("   Using flat SMB fields")
        smb_server = SanitizationService.sanitize_string(user.smb_server or "")
        smb_port = user.smb_port or 21
        smb_path = SanitizationService.sanitize_string(user.smb_path or "")
    
    logger.info(f"   SMB: {smb_server}:{smb_port} -> {smb_path}")
    
    # Extract available functions (nested or flat)
    if user.available_functions:
        logger.info("   Using nested available_functions")
        func_copier = user.available_functions.copier
        func_copier_color = user.available_functions.copier_color
        func_printer = user.available_functions.printer
        func_printer_color = user.available_functions.printer_color
        func_document_server = user.available_functions.document_server
        func_fax = user.available_functions.fax
        func_scanner = user.available_functions.scanner
        func_browser = user.available_functions.browser
    else:
        logger.info("   Using flat function fields")
        func_copier = user.func_copier or False
        func_copier_color = user.func_copier_color or False
        func_printer = user.func_printer or False
        func_printer_color = user.func_printer_color or False
        func_document_server = user.func_document_server or False
        func_fax = user.func_fax or False
        func_scanner = user.func_scanner or False
        func_browser = user.func_browser or False
    
    logger.info(f"   Functions: copier={func_copier}, scanner={func_scanner}, printer={func_printer}")
    
    # Encrypt network password
    encrypted_password = EncryptionService.encrypt(raw_password)
    
    try:
        # Create user in database con datos sanitizados
        new_user = UserRepository.create(
            db,
            name=sanitized_name,
            codigo_de_usuario=sanitized_codigo,
            network_username=network_username,
            network_password_encrypted=encrypted_password,
            smb_server=smb_server,
            smb_port=smb_port,
            smb_path=smb_path,
            func_copier=func_copier,
            func_copier_color=func_copier_color,
            func_printer=func_printer,
            func_printer_color=func_printer_color,
            func_document_server=func_document_server,
            func_fax=func_fax,
            func_scanner=func_scanner,
            func_browser=func_browser,
            empresa=user.empresa,
            centro_costos=user.centro_costos
        )
        logger.info(f"✅ User created successfully: ID={new_user.id}")
        
        # Automatic provisioning if printer IDs provided
        provisioning_results = None
        if user.printer_ids:
            logger.info(f"🔄 Starting automatic provisioning to {len(user.printer_ids)} printer(s)...")
            try:
                provisioning_results = ProvisioningService.provision_user_to_printers(
                    db=db,
                    user_id=new_user.id,
                    printer_ids=user.printer_ids
                )
                logger.info(f"✅ Provisioning completed: {provisioning_results['successful_count']}/{provisioning_results['total_printers']} successful")
            except Exception as prov_error:
                logger.error(f"❌ Provisioning error: {prov_error}")
                # Don't fail user creation if provisioning fails
                provisioning_results = {
                    "overall_success": False,
                    "total_printers": len(user.printer_ids),
                    "successful_count": 0,
                    "failed_count": len(user.printer_ids),
                    "results": [],
                    "summary_message": f"Error durante aprovisionamiento: {str(prov_error)}"
                }
        
        # Build response using Pydantic model for proper serialization
        user_response = UserResponse.model_validate(new_user)
        return UserCreateResponse(
            **user_response.model_dump(),
            provisioning_results=provisioning_results
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"❌ Error creating user: {type(e).__name__}")
        logger.error(f"Error details: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {type(e).__name__}"
        )


@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=10000, description="Items per page"),
    active_only: bool = True,
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination and search
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **active_only**: Filter only active users (default: True)
    - **search**: Search term for nombre or codigo_de_usuario
    """
    # Build query with eager loading of printer assignments and printers to prevent N+1 queries
    from sqlalchemy.orm import joinedload
    query = db.query(User).options(
        joinedload(User.printer_assignments).joinedload(UserPrinterAssignment.printer)
    )
    
    # Apply active filter
    if active_only:
        query = query.filter(User.is_active == True)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_pattern),
                User.codigo_de_usuario.ilike(search_pattern)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    import math
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get paginated results
    users = query.order_by(User.name).offset(offset).limit(page_size).all()
    
    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID
    """
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information
    """
    # Check if user exists
    existing_user = UserRepository.get_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle empresa field: convert empresa name to empresa_id
    if 'empresa' in update_data:
        empresa_value = update_data.pop('empresa')  # Remove empresa from update_data
        
        if empresa_value:
            # Import Empresa model
            from db.models_auth import Empresa
            
            # Try to find empresa by razon_social or nit
            empresa_obj = db.query(Empresa).filter(
                or_(
                    Empresa.razon_social == empresa_value,
                    Empresa.nit == empresa_value
                )
            ).first()
            
            if empresa_obj:
                update_data['empresa_id'] = empresa_obj.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Empresa '{empresa_value}' not found"
                )
        else:
            # If empresa is None or empty, set empresa_id to None
            update_data['empresa_id'] = None
    
    try:
        updated_user = UserRepository.update(db, user_id, **update_data)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


def deactivate_user_printers_task(user_id: int, printers_to_deactivate: List[dict]):
    """
    Background task to deactivate permissions on physical printers.
    Retries multiple times in case the printers are busy.
    """
    from db.database import SessionLocal
    from db.models import UserPrinterAssignment
    from services.ricoh_web_client import get_ricoh_web_client
    from concurrent.futures import ThreadPoolExecutor
    import time
    
    logger.info(f"🚀 [BACKGROUND TASK] Starting physical deactivation for user ID {user_id} on {len(printers_to_deactivate)} printers...")
    
    def deactivate_printer_worker(p_data):
        client = get_ricoh_web_client()
        printer_ip = p_data['printer_ip']
        entry_index = p_data['entry_index']
        admin_password = p_data['admin_password']
        codigo = p_data['codigo_de_usuario']
        
        resolved_entry_index = entry_index
        disabled_permissions = {
            'copiadora': False,
            'copiadora_color': False,
            'escaner': False,
            'impresora': False,
            'impresora_color': False,
            'document_server': False,
            'fax': False,
            'navegador': False
        }
        
        try:
            # If no entry_index is recorded in DB, try to find the user on the printer
            if not resolved_entry_index:
                user_in_printer = client.find_specific_user(printer_ip, codigo, admin_password=admin_password)
                if user_in_printer and user_in_printer.get('entry_index'):
                    resolved_entry_index = user_in_printer['entry_index']
            
            if resolved_entry_index:
                logger.info(f"   🚫 [{printer_ip}] [BACKGROUND] Deshabilitando funciones para slot {resolved_entry_index}...")
                
                attempts = 0
                max_attempts = 30  # Retry up to 30 times (around 5 minutes total) to handle busy printers!
                delay = 10.0      # Wait 10 seconds between attempts
                sync_success = False
                last_res = None
                
                while attempts < max_attempts:
                    attempts += 1
                    logger.info(f"   [{printer_ip}] [BACKGROUND] Intento {attempts} de {max_attempts} para deshabilitar funciones...")
                    res = client.set_user_functions(
                        printer_ip, 
                        resolved_entry_index, 
                        disabled_permissions, 
                        admin_password=admin_password,
                        set_password=False
                    )
                    
                    if res is True:
                        sync_success = True
                        break
                    elif res in ["BUSY", "TIMEOUT"]:
                        last_res = res
                        logger.warning(f"   [{printer_ip}] [BACKGROUND] Impresora ocupada o timeout (intento {attempts}/{max_attempts}). Esperando {delay}s...")
                        if attempts < max_attempts:
                            time.sleep(delay)
                    else:
                        last_res = res
                        break
                        
                if sync_success:
                    return {
                        'assignment_id': p_data['assignment_id'],
                        'success': True,
                        'entry_index': resolved_entry_index,
                        'error': None
                    }
                else:
                    err_msg = "Error de respuesta de la interfaz web de la impresora"
                    if last_res == "BUSY":
                        err_msg = "este dispositivo está siendo utilizado por otras funciones. Inténtelo de nuevo posteriormente."
                    elif last_res == "TIMEOUT":
                        err_msg = "tiempo de espera agotado al conectar con la impresora"
                    return {
                        'assignment_id': p_data['assignment_id'],
                        'success': False,
                        'entry_index': resolved_entry_index,
                        'error': err_msg
                    }
            else:
                return {
                    'assignment_id': p_data['assignment_id'],
                    'success': True,  # Treat as success since they are not on the printer anyway
                    'entry_index': None,
                    'error': "Usuario no encontrado en la impresora"
                }
        except Exception as e:
            return {
                'assignment_id': p_data['assignment_id'],
                'success': False,
                'entry_index': resolved_entry_index,
                'error': f"Excepción de conexión: {str(e)}"
            }

    with ThreadPoolExecutor(max_workers=min(len(printers_to_deactivate), 10)) as executor:
        worker_results = list(executor.map(deactivate_printer_worker, printers_to_deactivate))
        
    # Update DB records inside the background task using a dedicated session
    db_bg = SessionLocal()
    try:
        for res in worker_results:
            assignment = db_bg.query(UserPrinterAssignment).filter(
                UserPrinterAssignment.id == res['assignment_id']
            ).first()
            if assignment:
                # Set all permissions to False in DB to reflect physical printer state
                assignment.func_copier = False
                assignment.func_copier_color = False
                assignment.func_printer = False
                assignment.func_printer_color = False
                assignment.func_document_server = False
                assignment.func_fax = False
                assignment.func_scanner = False
                assignment.func_browser = False
                
                # Keep assignment active but with no permissions to preserve the list
                # assignment.is_active = False
                
                if res['entry_index']:
                    assignment.entry_index = res['entry_index']
                
                if not res['success']:
                    logger.warning(f"⚠️ [BACKGROUND] Error deshabilitando permisos en Impresora {assignment.printer.ip_address}: {res['error']}")
        db_bg.commit()
        logger.info(f"✅ [BACKGROUND TASK] Finished physical deactivation for user ID {user_id}.")
    except Exception as e:
        logger.error(f"❌ [BACKGROUND TASK] Error updating DB assignments: {e}")
        db_bg.rollback()
    finally:
        db_bg.close()


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Delete user (soft delete)
    Deactivates user in DB instantly and disables all permissions on all assigned printers in parallel in the background.
    """
    from db.models import UserPrinterAssignment
    
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # 1. Get all printer assignments for the user to ensure we clean up all printers
    assignments = db.query(UserPrinterAssignment).filter(
        UserPrinterAssignment.user_id == user_id
    ).all()
    
    printers_to_deactivate = []
    for a in assignments:
        printer = a.printer
        if printer:
            printers_to_deactivate.append({
                'assignment_id': a.id,
                'printer_id': printer.id,
                'printer_ip': printer.ip_address,
                'admin_password': printer.admin_password,
                'entry_index': a.entry_index,
                'codigo_de_usuario': user.codigo_de_usuario
            })
            
    # 2. Soft delete the user in database immediately
    success = UserRepository.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user in database"
        )
        
    # 3. Schedule physical deactivation in background
    if printers_to_deactivate:
        background_tasks.add_task(
            deactivate_user_printers_task,
            user_id=user_id,
            printers_to_deactivate=printers_to_deactivate
        )
        
    return MessageResponse(
        success=True,
        message=f"Usuario '{user.name}' desactivado del sistema. La actualización física en los equipos se está procesando en segundo plano."
    )


@router.get("/search/{query}", response_model=List[UserResponse])
async def search_users(query: str, db: Session = Depends(get_db)):
    """
    Search users by name or email
    """
    users = UserRepository.search(db, query)
    return users

"""
User management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import logging

from db.database import get_db
from db.repository import UserRepository, PrinterRepository
from db.models import User
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
        
        # Build response
        response_data = {
            **new_user.__dict__,
            "provisioning_results": provisioning_results
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
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
    # Build query
    query = db.query(User)
    
    # Apply active filter
    if active_only:
        query = query.filter(User.is_active == True)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.nombre.ilike(search_pattern),
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
    
    try:
        updated_user = UserRepository.update(db, user_id, **update_data)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete user (soft delete)
    """
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    success = UserRepository.delete(db, user_id)
    if success:
        return MessageResponse(
            success=True,
            message=f"User '{user.name}' deleted successfully"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/search/{query}", response_model=List[UserResponse])
async def search_users(query: str, db: Session = Depends(get_db)):
    """
    Search users by name or email
    """
    users = UserRepository.search(db, query)
    return users

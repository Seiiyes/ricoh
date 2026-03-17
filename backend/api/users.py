"""
User management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import logging

from db.database import get_db
from db.repository import UserRepository, PrinterRepository
from services.encryption import get_encryption_service
from services.provisioning import ProvisioningService
from .schemas import UserCreate, UserUpdate, UserResponse, MessageResponse, UserCreateResponse

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
    logger.info(f"   Name: {user.name}")
    logger.info(f"   Código: {user.codigo_de_usuario}")
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
    existing_codigo = UserRepository.get_by_codigo(db, user.codigo_de_usuario)
    if existing_codigo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with código de usuario {user.codigo_de_usuario} already exists"
        )
    
    # Extract network credentials (nested or flat)
    if user.network_credentials:
        logger.info("   Using nested network_credentials")
        network_username = user.network_credentials.username
        raw_password = user.network_credentials.password or ""
    else:
        logger.info("   Using flat network fields")
        network_username = user.network_username or "reliteltda\\scaner"
        raw_password = user.network_password or ""
    
    logger.info(f"   Network username: {network_username}")
    
    # Extract SMB configuration (nested or flat)
    if user.smb_config:
        logger.info("   Using nested smb_config")
        smb_server = user.smb_config.server
        smb_port = user.smb_config.port
        smb_path = user.smb_config.path or ""  # Allow empty
    else:
        logger.info("   Using flat SMB fields")
        smb_server = user.smb_server or ""
        smb_port = user.smb_port or 21
        smb_path = user.smb_path or ""  # Allow empty
    
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
    encryption_service = get_encryption_service()
    encrypted_password = encryption_service.encrypt(raw_password)
    
    try:
        # Create user in database
        new_user = UserRepository.create(
            db,
            name=user.name,
            codigo_de_usuario=user.codigo_de_usuario,
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


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination
    """
    users = UserRepository.get_all(db, skip=skip, limit=limit, active_only=active_only)
    return users


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

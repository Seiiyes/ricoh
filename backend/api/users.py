"""
User management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.repository import UserRepository
from services.encryption import get_encryption_service
from .schemas import UserCreate, UserUpdate, UserResponse, MessageResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with complete configuration
    """
    # Check if email already exists
    if user.email:
        existing = UserRepository.get_by_email(db, user.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user.email} already exists"
            )
    
    # Check if codigo_de_usuario already exists
    existing_codigo = UserRepository.get_by_codigo(db, user.codigo_de_usuario)
    if existing_codigo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with código de usuario {user.codigo_de_usuario} already exists"
        )
    
    # Encrypt network password
    encryption_service = get_encryption_service()
    encrypted_password = encryption_service.encrypt(user.network_credentials.password)
    
    try:
        new_user = UserRepository.create(
            db,
            name=user.name,
            codigo_de_usuario=user.codigo_de_usuario,
            network_username=user.network_credentials.username,
            network_password_encrypted=encrypted_password,
            smb_server=user.smb_config.server,
            smb_port=user.smb_config.port,
            smb_path=user.smb_config.path,
            func_copier=user.available_functions.copier,
            func_printer=user.available_functions.printer,
            func_document_server=user.available_functions.document_server,
            func_fax=user.available_functions.fax,
            func_scanner=user.available_functions.scanner,
            func_browser=user.available_functions.browser,
            email=user.email,
            department=user.department
        )
        return new_user
    except Exception as e:
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

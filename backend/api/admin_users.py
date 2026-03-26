"""
Admin Users Endpoints
Endpoints CRUD para gestión de usuarios administradores (solo superadmin)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
import math

from db.database import get_db
from db.models_auth import AdminUser, AdminSession, Empresa
from api.admin_user_schemas import (
    AdminUserCreate, AdminUserUpdate, AdminUserResponse, AdminUserListResponse
)
from api.auth_schemas import SuccessResponse, ErrorResponse
from middleware.auth_middleware import get_current_superadmin, get_client_ip, get_user_agent
from services.password_service import PasswordService
from services.audit_service import AuditService


router = APIRouter(prefix="/admin-users", tags=["Admin Users"])


@router.get(
    "",
    response_model=AdminUserListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of admin users", "model": AdminUserListResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse}
    },
    summary="List Admin Users",
    description="Get paginated list of admin users with optional filters. Only accessible by superadmin."
)
async def list_admin_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by username, nombre_completo, or email"),
    rol: Optional[str] = Query(None, description="Filter by rol"),
    empresa_id: Optional[int] = Query(None, description="Filter by empresa_id"),
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    List all admin users with pagination, search, and filters
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **search**: Search term for username, nombre_completo, or email
    - **rol**: Filter by rol (superadmin, admin, viewer, operator)
    - **empresa_id**: Filter by empresa_id
    
    Only accessible by superadmin.
    """
    # Build query
    query = db.query(AdminUser)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                AdminUser.username.ilike(search_pattern),
                AdminUser.nombre_completo.ilike(search_pattern),
                AdminUser.email.ilike(search_pattern)
            )
        )
    
    # Apply rol filter
    if rol:
        query = query.filter(AdminUser.rol == rol)
    
    # Apply empresa_id filter
    if empresa_id is not None:
        query = query.filter(AdminUser.empresa_id == empresa_id)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    
    # Get paginated results
    admin_users = query.order_by(AdminUser.username).offset(offset).limit(page_size).all()
    
    return AdminUserListResponse(
        items=[AdminUserResponse.model_validate(u) for u in admin_users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post(
    "",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Admin user created", "model": AdminUserResponse},
        400: {"description": "Validation error", "model": ErrorResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        409: {"description": "Admin user already exists", "model": ErrorResponse}
    },
    summary="Create Admin User",
    description="Create a new admin user. Only accessible by superadmin."
)
async def create_admin_user(
    request: Request,
    user_data: AdminUserCreate,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Create a new admin user
    
    Validates:
    - Uniqueness of username and email
    - Password strength
    - empresa_id based on rol (superadmin must have NULL, others must have NOT NULL)
    
    Only accessible by superadmin.
    """
    # Check if username already exists
    existing_username = db.query(AdminUser).filter(
        AdminUser.username == user_data.username
    ).first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ADMIN_USER_USERNAME_EXISTS",
                "message": f"Admin user with username '{user_data.username}' already exists",
                "field": "username"
            }
        )
    
    # Check if email already exists
    existing_email = db.query(AdminUser).filter(
        AdminUser.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ADMIN_USER_EMAIL_EXISTS",
                "message": f"Admin user with email '{user_data.email}' already exists",
                "field": "email"
            }
        )
    
    # Validate empresa exists (if empresa_id provided)
    if user_data.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == user_data.empresa_id).first()
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "EMPRESA_NOT_FOUND",
                    "message": f"Empresa with ID {user_data.empresa_id} not found",
                    "field": "empresa_id"
                }
            )
    
    # Hash password
    password_hash = PasswordService.hash_password(user_data.password)
    
    # Create admin user
    admin_user = AdminUser(
        username=user_data.username,
        password_hash=password_hash,
        nombre_completo=user_data.nombre_completo,
        email=user_data.email,
        rol=user_data.rol,
        empresa_id=user_data.empresa_id
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # Log audit
    AuditService.log_action(
        db=db,
        user=current_user,
        accion="crear",
        modulo="admin_users",
        resultado=AuditService.RESULTADO_EXITO,
        entidad_tipo="admin_user",
        entidad_id=admin_user.id,
        detalles={
            "username": admin_user.username,
            "rol": admin_user.rol,
            "empresa_id": admin_user.empresa_id
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return AdminUserResponse.model_validate(admin_user)


@router.get(
    "/{user_id}",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Admin user details", "model": AdminUserResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        404: {"description": "Admin user not found", "model": ErrorResponse}
    },
    summary="Get Admin User",
    description="Get admin user by ID. Only accessible by superadmin."
)
async def get_admin_user(
    user_id: int,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Get admin user by ID
    
    Only accessible by superadmin.
    """
    admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ADMIN_USER_NOT_FOUND",
                "message": f"Admin user with ID {user_id} not found"
            }
        )
    
    return AdminUserResponse.model_validate(admin_user)


@router.put(
    "/{user_id}",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Admin user updated", "model": AdminUserResponse},
        400: {"description": "Validation error", "model": ErrorResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        404: {"description": "Admin user not found", "model": ErrorResponse},
        409: {"description": "Email already exists", "model": ErrorResponse}
    },
    summary="Update Admin User",
    description="Update admin user by ID. Username cannot be changed. Only accessible by superadmin."
)
async def update_admin_user(
    request: Request,
    user_id: int,
    user_data: AdminUserUpdate,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Update admin user by ID
    
    Username cannot be changed.
    Validates uniqueness of email (if changed).
    
    Only accessible by superadmin.
    """
    # Find admin user
    admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ADMIN_USER_NOT_FOUND",
                "message": f"Admin user with ID {user_id} not found"
            }
        )
    
    # Check if email already exists (if changed)
    if user_data.email and user_data.email != admin_user.email:
        existing_email = db.query(AdminUser).filter(
            AdminUser.email == user_data.email,
            AdminUser.id != user_id
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "ADMIN_USER_EMAIL_EXISTS",
                    "message": f"Admin user with email '{user_data.email}' already exists",
                    "field": "email"
                }
            )
    
    # Validate empresa exists (if empresa_id changed)
    if user_data.empresa_id is not None and user_data.empresa_id != admin_user.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == user_data.empresa_id).first()
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "EMPRESA_NOT_FOUND",
                    "message": f"Empresa with ID {user_data.empresa_id} not found",
                    "field": "empresa_id"
                }
            )
    
    # Validate empresa_id based on rol (if rol is being changed)
    if user_data.rol:
        if user_data.rol == 'superadmin' and user_data.empresa_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "VALIDATION_ERROR",
                    "message": "superadmin must not have empresa_id (must be NULL)",
                    "field": "empresa_id"
                }
            )
        elif user_data.rol in ['admin', 'viewer', 'operator'] and user_data.empresa_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "VALIDATION_ERROR",
                    "message": f"{user_data.rol} must have empresa_id (cannot be NULL)",
                    "field": "empresa_id"
                }
            )
    
    # Update admin user
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(admin_user, field, value)
    
    db.commit()
    db.refresh(admin_user)
    
    # Log audit
    AuditService.log_action(
        db=db,
        user=current_user,
        accion="editar",
        modulo="admin_users",
        resultado=AuditService.RESULTADO_EXITO,
        entidad_tipo="admin_user",
        entidad_id=admin_user.id,
        detalles={
            "username": admin_user.username,
            "updated_fields": list(update_data.keys())
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return AdminUserResponse.model_validate(admin_user)


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Admin user deactivated", "model": SuccessResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        404: {"description": "Admin user not found", "model": ErrorResponse}
    },
    summary="Delete Admin User",
    description="Soft delete admin user (set is_active=False) and invalidate all sessions. Only accessible by superadmin."
)
async def delete_admin_user(
    request: Request,
    user_id: int,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Soft delete admin user (set is_active=False)
    
    Also invalidates all active sessions for the user.
    
    Only accessible by superadmin.
    """
    # Find admin user
    admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ADMIN_USER_NOT_FOUND",
                "message": f"Admin user with ID {user_id} not found"
            }
        )
    
    # Soft delete (set is_active=False)
    admin_user.is_active = False
    
    # Invalidate all active sessions
    db.query(AdminSession).filter(AdminSession.admin_user_id == user_id).delete()
    
    db.commit()
    
    # Log audit
    AuditService.log_action(
        db=db,
        user=current_user,
        accion="eliminar",
        modulo="admin_users",
        resultado=AuditService.RESULTADO_EXITO,
        entidad_tipo="admin_user",
        entidad_id=admin_user.id,
        detalles={
            "username": admin_user.username,
            "rol": admin_user.rol
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return SuccessResponse(
        success=True,
        message=f"Admin user '{admin_user.username}' desactivado exitosamente"
    )

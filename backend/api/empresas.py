"""
Empresas Endpoints
Endpoints CRUD para gestión de empresas (solo superadmin)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
import math

from db.database import get_db
from db.models_auth import AdminUser, Empresa
from api.empresa_schemas import (
    EmpresaCreate, EmpresaUpdate, EmpresaResponse, EmpresaListResponse
)
from api.auth_schemas import SuccessResponse, ErrorResponse
from middleware.auth_middleware import get_current_superadmin, get_client_ip, get_user_agent
from services.audit_service import AuditService


router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get(
    "",
    response_model=EmpresaListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of empresas", "model": EmpresaListResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse}
    },
    summary="List Empresas",
    description="Get paginated list of empresas with optional search. Only accessible by superadmin."
)
async def list_empresas(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by razon_social or nombre_comercial"),
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    List all empresas with pagination and search
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **search**: Search term for razon_social or nombre_comercial
    
    Only accessible by superadmin.
    """
    # Build query
    query = db.query(Empresa)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Empresa.razon_social.ilike(search_pattern),
                Empresa.nombre_comercial.ilike(search_pattern)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    
    # Get paginated results
    empresas = query.order_by(Empresa.razon_social).offset(offset).limit(page_size).all()
    
    return EmpresaListResponse(
        items=[EmpresaResponse.model_validate(e) for e in empresas],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post(
    "",
    response_model=EmpresaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Empresa created", "model": EmpresaResponse},
        400: {"description": "Validation error", "model": ErrorResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        409: {"description": "Empresa already exists", "model": ErrorResponse}
    },
    summary="Create Empresa",
    description="Create a new empresa. Only accessible by superadmin."
)
async def create_empresa(
    request: Request,
    empresa_data: EmpresaCreate,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Create a new empresa
    
    Validates uniqueness of razon_social and nombre_comercial.
    
    Only accessible by superadmin.
    """
    # Check if razon_social already exists
    existing_razon = db.query(Empresa).filter(
        Empresa.razon_social == empresa_data.razon_social
    ).first()
    
    if existing_razon:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "EMPRESA_RAZON_SOCIAL_EXISTS",
                "message": f"Empresa with razon_social '{empresa_data.razon_social}' already exists",
                "field": "razon_social"
            }
        )
    
    # Check if nombre_comercial already exists
    existing_nombre = db.query(Empresa).filter(
        Empresa.nombre_comercial == empresa_data.nombre_comercial
    ).first()
    
    if existing_nombre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "EMPRESA_NOMBRE_COMERCIAL_EXISTS",
                "message": f"Empresa with nombre_comercial '{empresa_data.nombre_comercial}' already exists",
                "field": "nombre_comercial"
            }
        )
    
    # Create empresa
    empresa = Empresa(**empresa_data.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    
    # Log audit
    AuditService.log_action(
        db=db,
        user=current_user,
        accion="crear",
        modulo="empresas",
        resultado=AuditService.RESULTADO_EXITO,
        entidad_tipo="empresa",
        entidad_id=empresa.id,
        detalles={
            "razon_social": empresa.razon_social,
            "nombre_comercial": empresa.nombre_comercial
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return EmpresaResponse.model_validate(empresa)


@router.get(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Empresa details", "model": EmpresaResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        404: {"description": "Empresa not found", "model": ErrorResponse}
    },
    summary="Get Empresa",
    description="Get empresa by ID. Only accessible by superadmin."
)
async def get_empresa(
    empresa_id: int,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Get empresa by ID
    
    Only accessible by superadmin.
    """
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "EMPRESA_NOT_FOUND",
                "message": f"Empresa with ID {empresa_id} not found"
            }
        )
    
    return EmpresaResponse.model_validate(empresa)


@router.put(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Empresa updated", "model": EmpresaResponse},
        400: {"description": "Validation error", "model": ErrorResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        404: {"description": "Empresa not found", "model": ErrorResponse},
        409: {"description": "Empresa already exists", "model": ErrorResponse}
    },
    summary="Update Empresa",
    description="Update empresa by ID. Only accessible by superadmin."
)
async def update_empresa(
    request: Request,
    empresa_id: int,
    empresa_data: EmpresaUpdate,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Update empresa by ID
    
    Validates uniqueness of razon_social and nombre_comercial.
    
    Only accessible by superadmin.
    """
    # Find empresa
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "EMPRESA_NOT_FOUND",
                "message": f"Empresa with ID {empresa_id} not found"
            }
        )
    
    # Check if razon_social already exists (if changed)
    if empresa_data.razon_social and empresa_data.razon_social != empresa.razon_social:
        existing_razon = db.query(Empresa).filter(
            Empresa.razon_social == empresa_data.razon_social,
            Empresa.id != empresa_id
        ).first()
        
        if existing_razon:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "EMPRESA_RAZON_SOCIAL_EXISTS",
                    "message": f"Empresa with razon_social '{empresa_data.razon_social}' already exists",
                    "field": "razon_social"
                }
            )
    
    # Check if nombre_comercial already exists (if changed)
    if empresa_data.nombre_comercial != empresa.nombre_comercial:
        existing_nombre = db.query(Empresa).filter(
            Empresa.nombre_comercial == empresa_data.nombre_comercial,
            Empresa.id != empresa_id
        ).first()
        
        if existing_nombre:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "EMPRESA_NOMBRE_COMERCIAL_EXISTS",
                    "message": f"Empresa with nombre_comercial '{empresa_data.nombre_comercial}' already exists",
                    "field": "nombre_comercial"
                }
            )
    
    # Update empresa
    update_data = empresa_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(empresa, field, value)
    
    db.commit()
    db.refresh(empresa)
    
    # Log audit
    AuditService.log_action(
        db=db,
        user=current_user,
        accion="editar",
        modulo="empresas",
        resultado=AuditService.RESULTADO_EXITO,
        entidad_tipo="empresa",
        entidad_id=empresa.id,
        detalles={
            "razon_social": empresa.razon_social,
            "nombre_comercial": empresa.nombre_comercial,
            "updated_fields": list(update_data.keys())
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return EmpresaResponse.model_validate(empresa)


@router.delete(
    "/{empresa_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Empresa deactivated", "model": SuccessResponse},
        400: {"description": "Empresa has active resources", "model": ErrorResponse},
        403: {"description": "Insufficient permissions", "model": ErrorResponse},
        404: {"description": "Empresa not found", "model": ErrorResponse}
    },
    summary="Delete Empresa",
    description="Soft delete empresa (set is_active=False). Only accessible by superadmin."
)
async def delete_empresa(
    request: Request,
    empresa_id: int,
    current_user: AdminUser = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Soft delete empresa (set is_active=False)
    
    Validates that empresa has no active resources (printers, users, admin_users).
    
    Only accessible by superadmin.
    """
    # Find empresa
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "EMPRESA_NOT_FOUND",
                "message": f"Empresa with ID {empresa_id} not found"
            }
        )
    
    # Check if empresa has active resources
    from db.models import Printer, User
    
    active_printers = db.query(func.count(Printer.id)).filter(
        Printer.empresa_id == empresa_id
    ).scalar()
    
    active_users = db.query(func.count(User.id)).filter(
        User.empresa_id == empresa_id,
        User.is_active == True
    ).scalar()
    
    active_admin_users = db.query(func.count(AdminUser.id)).filter(
        AdminUser.empresa_id == empresa_id,
        AdminUser.is_active == True
    ).scalar()
    
    if active_printers > 0 or active_users > 0 or active_admin_users > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "EMPRESA_HAS_ACTIVE_RESOURCES",
                "message": "Cannot deactivate empresa with active resources",
                "details": {
                    "active_printers": active_printers,
                    "active_users": active_users,
                    "active_admin_users": active_admin_users
                }
            }
        )
    
    # Soft delete (set is_active=False)
    empresa.is_active = False
    db.commit()
    
    # Log audit
    AuditService.log_action(
        db=db,
        user=current_user,
        accion="eliminar",
        modulo="empresas",
        resultado=AuditService.RESULTADO_EXITO,
        entidad_tipo="empresa",
        entidad_id=empresa.id,
        detalles={
            "razon_social": empresa.razon_social,
            "nombre_comercial": empresa.nombre_comercial
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return SuccessResponse(
        success=True,
        message=f"Empresa '{empresa.razon_social}' desactivada exitosamente"
    )

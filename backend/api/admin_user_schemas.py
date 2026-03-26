"""
Admin User Schemas
Schemas Pydantic para endpoints de gestión de usuarios administradores
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re

from services.password_service import PasswordService


class AdminUserBase(BaseModel):
    """Base schema for AdminUser"""
    username: str = Field(..., min_length=3, max_length=100, description="Username (lowercase alphanumeric with underscores/hyphens)")
    nombre_completo: str = Field(..., min_length=1, max_length=255, description="Nombre completo")
    email: str = Field(..., max_length=255, description="Email")
    rol: str = Field(..., description="Rol (superadmin, admin, viewer, operator)")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format (lowercase alphanumeric with underscores/hyphens)"""
        if not re.match(r'^[a-z0-9_-]+$', v):
            raise ValueError(
                "username must contain only lowercase letters, numbers, underscores, and hyphens"
            )
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v
    
    @field_validator('rol')
    @classmethod
    def validate_rol(cls, v: str) -> str:
        """Validate rol is one of the allowed values"""
        allowed_roles = ['superadmin', 'admin', 'viewer', 'operator']
        if v not in allowed_roles:
            raise ValueError(f"rol must be one of: {', '.join(allowed_roles)}")
        return v


class AdminUserCreate(AdminUserBase):
    """Schema for creating a new admin user"""
    password: str = Field(..., min_length=8, description="Password (must meet strength requirements)")
    empresa_id: Optional[int] = Field(None, description="Empresa ID (required for non-superadmin roles)")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements"""
        validation_result = PasswordService.validate_password_strength(v)
        if not validation_result.is_valid:
            raise ValueError("; ".join(validation_result.errors))
        return v
    
    @field_validator('empresa_id')
    @classmethod
    def validate_empresa_id_based_on_rol(cls, v: Optional[int], info) -> Optional[int]:
        """Validate empresa_id based on rol"""
        # Get rol from values (if available)
        rol = info.data.get('rol')
        
        if rol == 'superadmin':
            if v is not None:
                raise ValueError("superadmin must not have empresa_id (must be NULL)")
        elif rol in ['admin', 'viewer', 'operator']:
            if v is None:
                raise ValueError(f"{rol} must have empresa_id (cannot be NULL)")
        
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "username": "nuevo_admin",
            "password": "SecurePass123!",
            "nombre_completo": "Nuevo Administrador",
            "email": "nuevo@empresa.com",
            "rol": "admin",
            "empresa_id": 1
        }
    })


class AdminUserUpdate(BaseModel):
    """Schema for updating an admin user (all fields optional)"""
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    rol: Optional[str] = None
    empresa_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format"""
        if v is None:
            return v
        
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v
    
    @field_validator('rol')
    @classmethod
    def validate_rol(cls, v: Optional[str]) -> Optional[str]:
        """Validate rol is one of the allowed values"""
        if v is None:
            return v
        
        allowed_roles = ['superadmin', 'admin', 'viewer', 'operator']
        if v not in allowed_roles:
            raise ValueError(f"rol must be one of: {', '.join(allowed_roles)}")
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "nombre_completo": "Administrador Actualizado",
            "email": "actualizado@empresa.com",
            "rol": "admin",
            "empresa_id": 1,
            "is_active": True
        }
    })


class EmpresaInfoSimple(BaseModel):
    """Simple empresa information for responses"""
    id: int
    razon_social: str
    nombre_comercial: str
    
    model_config = ConfigDict(from_attributes=True)


class AdminUserResponse(BaseModel):
    """Schema for admin user response (without password_hash)"""
    id: int
    username: str
    nombre_completo: str
    email: str
    rol: str
    empresa_id: Optional[int] = None
    empresa: Optional[EmpresaInfoSimple] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "username": "admin_empresa1",
                "nombre_completo": "Admin Empresa 1",
                "email": "admin@empresa1.com",
                "rol": "admin",
                "empresa_id": 1,
                "empresa": {
                    "id": 1,
                    "razon_social": "Empresa Demo S.A.",
                    "nombre_comercial": "empresa-demo"
                },
                "is_active": True,
                "last_login": "2026-03-20T09:15:00Z",
                "created_at": "2026-01-20T11:00:00Z",
                "updated_at": None
            }
        }
    )


class AdminUserListResponse(BaseModel):
    """Schema for paginated admin user list response"""
    items: list[AdminUserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "items": [
                {
                    "id": 2,
                    "username": "admin_empresa1",
                    "nombre_completo": "Admin Empresa 1",
                    "email": "admin@empresa1.com",
                    "rol": "admin",
                    "empresa_id": 1,
                    "empresa": {
                        "id": 1,
                        "razon_social": "Empresa Demo S.A.",
                        "nombre_comercial": "empresa-demo"
                    },
                    "is_active": True,
                    "last_login": "2026-03-20T09:15:00Z",
                    "created_at": "2026-01-20T11:00:00Z",
                    "updated_at": None
                }
            ],
            "total": 25,
            "page": 1,
            "page_size": 20,
            "total_pages": 2
        }
    })

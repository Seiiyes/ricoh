"""
Empresa Schemas
Schemas Pydantic para endpoints de gestión de empresas
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re


class EmpresaBase(BaseModel):
    """Base schema for Empresa"""
    razon_social: str = Field(..., min_length=1, max_length=255, description="Razón social (nombre legal)")
    nombre_comercial: str = Field(..., min_length=1, max_length=50, description="Nombre comercial (formato kebab-case)")
    nit: Optional[str] = Field(None, max_length=20, description="NIT (Número de Identificación Tributaria)")
    direccion: Optional[str] = Field(None, description="Dirección física")
    telefono: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=255, description="Email de contacto")
    contacto_nombre: Optional[str] = Field(None, max_length=255, description="Nombre del contacto principal")
    contacto_cargo: Optional[str] = Field(None, max_length=100, description="Cargo del contacto principal")
    logo_url: Optional[str] = Field(None, max_length=500, description="URL del logo de la empresa")
    
    @field_validator('nombre_comercial')
    @classmethod
    def validate_nombre_comercial(cls, v: str) -> str:
        """Validate nombre_comercial is in kebab-case format"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError(
                "nombre_comercial must be in kebab-case format (lowercase letters, numbers, and hyphens only)"
            )
        return v
    
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


class EmpresaCreate(EmpresaBase):
    """Schema for creating a new empresa"""
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "razon_social": "Nueva Empresa S.A.S.",
            "nombre_comercial": "nueva-empresa",
            "nit": "900987654-3",
            "direccion": "Avenida 45 #12-34",
            "telefono": "+57 1 987 6543",
            "email": "info@nuevaempresa.com",
            "contacto_nombre": "María García",
            "contacto_cargo": "Directora Administrativa"
        }
    })


class EmpresaUpdate(BaseModel):
    """Schema for updating an empresa (all fields optional except nombre_comercial)"""
    razon_social: Optional[str] = Field(None, min_length=1, max_length=255)
    nombre_comercial: str = Field(..., min_length=1, max_length=50, description="Nombre comercial (requerido)")
    nit: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    contacto_nombre: Optional[str] = Field(None, max_length=255)
    contacto_cargo: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    
    @field_validator('nombre_comercial')
    @classmethod
    def validate_nombre_comercial(cls, v: str) -> str:
        """Validate nombre_comercial is in kebab-case format"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError(
                "nombre_comercial must be in kebab-case format (lowercase letters, numbers, and hyphens only)"
            )
        return v
    
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
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "razon_social": "Empresa Actualizada S.A.S.",
            "nombre_comercial": "empresa-actualizada",
            "nit": "900123456-7",
            "direccion": "Calle 123 #45-67",
            "telefono": "+57 1 234 5678",
            "email": "contacto@empresa.com",
            "contacto_nombre": "Juan Pérez",
            "contacto_cargo": "Gerente TI",
            "is_active": True
        }
    })


class EmpresaResponse(EmpresaBase):
    """Schema for empresa response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "razon_social": "Empresa Demo S.A.",
                "nombre_comercial": "empresa-demo",
                "nit": "900123456-7",
                "direccion": "Calle 123 #45-67",
                "telefono": "+57 1 234 5678",
                "email": "contacto@empresa.com",
                "contacto_nombre": "Juan Pérez",
                "contacto_cargo": "Gerente TI",
                "logo_url": None,
                "is_active": True,
                "created_at": "2026-01-15T10:30:00Z",
                "updated_at": "2026-03-20T14:20:00Z"
            }
        }
    )


class EmpresaListResponse(BaseModel):
    """Schema for paginated empresa list response"""
    items: list[EmpresaResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "items": [
                {
                    "id": 1,
                    "razon_social": "Empresa Demo S.A.",
                    "nombre_comercial": "empresa-demo",
                    "nit": "900123456-7",
                    "direccion": "Calle 123 #45-67",
                    "telefono": "+57 1 234 5678",
                    "email": "contacto@empresa.com",
                    "contacto_nombre": "Juan Pérez",
                    "contacto_cargo": "Gerente TI",
                    "logo_url": None,
                    "is_active": True,
                    "created_at": "2026-01-15T10:30:00Z",
                    "updated_at": "2026-03-20T14:20:00Z"
                }
            ],
            "total": 15,
            "page": 1,
            "page_size": 20,
            "total_pages": 1
        }
    })

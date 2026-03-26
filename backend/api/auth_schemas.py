"""
Authentication Schemas
Schemas Pydantic para endpoints de autenticación
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

from services.password_service import PasswordService


class LoginRequest(BaseModel):
    """Request schema for login"""
    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=1, description="Password")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "username": "admin",
            "password": "SecurePass123!"
        }
    })


class EmpresaInfo(BaseModel):
    """Empresa information for responses"""
    id: int
    razon_social: str
    nombre_comercial: str
    
    model_config = ConfigDict(from_attributes=True)


class AdminUserResponse(BaseModel):
    """Admin user response (without password_hash)"""
    id: int
    username: str
    nombre_completo: str
    email: str
    rol: str
    empresa_id: Optional[int] = None
    empresa: Optional[EmpresaInfo] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    """Response schema for login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: AdminUserResponse
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGc...",
            "refresh_token": "eyJhbGc...",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": 1,
                "username": "admin",
                "nombre_completo": "Administrador Principal",
                "email": "admin@empresa.com",
                "rol": "admin",
                "empresa_id": 1,
                "empresa": {
                    "id": 1,
                    "razon_social": "Empresa Demo S.A.",
                    "nombre_comercial": "empresa-demo"
                },
                "is_active": True,
                "last_login": "2026-03-20T10:30:00Z",
                "created_at": "2026-01-15T08:00:00Z"
            }
        }
    })


class RefreshRequest(BaseModel):
    """Request schema for refresh token"""
    refresh_token: str = Field(..., min_length=1, description="Refresh token")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "refresh_token": "eyJhbGc..."
        }
    })


class RefreshResponse(BaseModel):
    """Response schema for refresh token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration in seconds")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "expires_in": 1800
        }
    })


class RotateTokenResponse(BaseModel):
    """Response schema for rotate token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration in seconds")
    rotated: bool = Field(..., description="True if token was rotated, False if not needed yet")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "expires_in": 1800,
            "rotated": True
        }
    })


class ChangePasswordRequest(BaseModel):
    """Request schema for change password"""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements"""
        validation_result = PasswordService.validate_password_strength(v)
        if not validation_result.is_valid:
            raise ValueError("; ".join(validation_result.errors))
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "current_password": "OldPass123!",
            "new_password": "NewPass456!"
        }
    })


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Operation completed successfully"
        }
    })


class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    message: str
    details: Optional[dict] = None
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "error": "AUTH_INVALID_CREDENTIALS",
            "message": "Invalid credentials",
            "details": None
        }
    })

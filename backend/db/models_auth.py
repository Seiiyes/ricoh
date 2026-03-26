"""
SQLAlchemy ORM Models for Authentication System
Modelos para el sistema de autenticación con roles y multi-tenancy
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Optional

from .database import Base


class Empresa(Base):
    """
    Empresa/Tenant model
    Representa una organización cliente que usa Ricoh Suite
    """
    __tablename__ = "empresas"

    # Identity
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(255), nullable=False, unique=True, index=True)
    nombre_comercial = Column(String(50), nullable=False, unique=True, index=True)
    nit = Column(String(20), unique=True, nullable=True)
    
    # Contact Information
    direccion = Column(Text, nullable=True)
    telefono = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    contacto_nombre = Column(String(255), nullable=True)
    contacto_cargo = Column(String(100), nullable=True)
    
    # Configuration
    logo_url = Column(String(500), nullable=True)
    config_json = Column(JSON, default={}, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    admin_users = relationship("AdminUser", back_populates="empresa")
    printers = relationship("Printer", back_populates="empresa")
    users = relationship("User", back_populates="empresa")

    def __repr__(self):
        return f"<Empresa(id={self.id}, razon_social='{self.razon_social}', nombre_comercial='{self.nombre_comercial}')>"


class AdminUser(Base):
    """
    Admin user model for authentication
    Usuarios administradores del sistema (NO usuarios de impresoras)
    """
    __tablename__ = "admin_users"

    # Identity
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Authorization
    rol = Column(String(20), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    empresa = relationship("Empresa", back_populates="admin_users")
    sessions = relationship("AdminSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AdminAuditLog", back_populates="user")

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}', rol='{self.rol}')>"
    
    def is_superadmin(self) -> bool:
        """Check if user is superadmin"""
        return self.rol == "superadmin"
    
    def is_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.locked_until is None:
            return False
        return self.locked_until > datetime.now(timezone.utc)


class AdminSession(Base):
    """
    Admin session model for JWT token management
    Sesiones activas de usuarios administradores
    """
    __tablename__ = "admin_sessions"

    # Identity
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tokens
    token = Column(String(500), nullable=False, unique=True, index=True)
    refresh_token = Column(String(500), unique=True, nullable=True)
    
    # Client Information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    refresh_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("AdminUser", back_populates="sessions")

    def __repr__(self):
        return f"<AdminSession(id={self.id}, user_id={self.admin_user_id}, expires_at='{self.expires_at}')>"
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return self.expires_at < datetime.now(timezone.utc)


class AdminAuditLog(Base):
    """
    Admin audit log model
    Registro inmutable de auditoría de todas las acciones administrativas
    """
    __tablename__ = "admin_audit_log"

    # Identity
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Action Details
    accion = Column(String(100), nullable=False, index=True)
    modulo = Column(String(50), nullable=False, index=True)
    entidad_tipo = Column(String(50), nullable=True, index=True)
    entidad_id = Column(Integer, nullable=True)
    detalles = Column(JSON, nullable=True)
    resultado = Column(String(20), nullable=False)
    
    # Client Information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("AdminUser", back_populates="audit_logs")

    def __repr__(self):
        return f"<AdminAuditLog(id={self.id}, accion='{self.accion}', modulo='{self.modulo}', resultado='{self.resultado}')>"

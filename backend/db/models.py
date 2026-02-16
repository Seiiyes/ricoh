"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .database import Base


class PrinterStatus(str, enum.Enum):
    """Printer status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class User(Base):
    """
    User model for printer provisioning
    Stores user credentials and SMB configuration
    """
    __tablename__ = "users"

    # Identity
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # Nombre
    
    # Authentication
    codigo_de_usuario = Column(String(8), nullable=False, index=True)  # Código de usuario (renamed from 'pin')
    
    # Network Credentials (Autenticación de carpeta)
    network_username = Column(String(255), nullable=False, default="reliteltda\\scaner")  # Nombre de usuario de inicio de sesión
    network_password_encrypted = Column(Text, nullable=False)  # Contraseña de inicio de sesión (encrypted)
    
    # SMB Configuration (Carpeta SMB)
    smb_server = Column(String(255), nullable=False)  # Nombre de servidor
    smb_port = Column(Integer, default=21, nullable=False)  # Puerto
    smb_path = Column(String(500), nullable=False)  # Ruta (e.g., \\server\folder)
    
    # Available Functions (Funciones disponibles)
    func_copier = Column(Boolean, default=False, nullable=False)  # Copiadora
    func_printer = Column(Boolean, default=False, nullable=False)  # Impresora
    func_document_server = Column(Boolean, default=False, nullable=False)  # Document Server
    func_fax = Column(Boolean, default=False, nullable=False)  # Fax
    func_scanner = Column(Boolean, default=False, nullable=False)  # Escáner
    func_browser = Column(Boolean, default=False, nullable=False)  # Navegador
    
    # Optional Fields
    email = Column(String(255), nullable=True, unique=True, index=True)
    department = Column(String(100), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    printer_assignments = relationship(
        "UserPrinterAssignment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class Printer(Base):
    """
    Printer model for fleet management
    Stores printer information and status
    """
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, unique=True, index=True)  # IPv4/IPv6
    location = Column(String(255), nullable=True)
    status = Column(Enum(PrinterStatus), default=PrinterStatus.OFFLINE)
    detected_model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True, unique=True)
    
    # Capabilities
    has_color = Column(Boolean, default=False)
    has_scanner = Column(Boolean, default=False)
    has_fax = Column(Boolean, default=False)
    
    # Toner levels (0-100)
    toner_cyan = Column(Integer, default=0)
    toner_magenta = Column(Integer, default=0)
    toner_yellow = Column(Integer, default=0)
    toner_black = Column(Integer, default=0)
    
    # Metadata
    last_seen = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_assignments = relationship(
        "UserPrinterAssignment",
        back_populates="printer",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Printer(id={self.id}, hostname='{self.hostname}', ip='{self.ip_address}', status='{self.status}')>"


class UserPrinterAssignment(Base):
    """
    Many-to-many relationship between Users and Printers
    Tracks which users are provisioned on which printers
    """
    __tablename__ = "user_printer_assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False)
    
    # Assignment metadata
    provisioned_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="printer_assignments")
    printer = relationship("Printer", back_populates="user_assignments")

    def __repr__(self):
        return f"<UserPrinterAssignment(user_id={self.user_id}, printer_id={self.printer_id})>"

"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
import enum
import json
from typing import Optional

from .database import Base

# Import authentication models
from .models_auth import Empresa, AdminUser, AdminSession, AdminAuditLog


class PrinterStatus(str, enum.Enum):
    """Printer status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SMBServer(Base):
    """SMB Server configuration (normalized)"""
    __tablename__ = "smb_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    server_address = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False, default=21)
    description = Column(String(500))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="smb_server_rel")


class NetworkCredential(Base):
    """Network credentials (normalized)"""
    __tablename__ = "network_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    password_encrypted = Column(Text, nullable=False)
    description = Column(String(500))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="network_credential_rel")


class CentroCosto(Base):
    """
    CentroCosto model associated with Empresa
    Stores the normalized cost center names
    """
    __tablename__ = "centro_costos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    empresa = relationship("Empresa", back_populates="centros_costo")
    users = relationship("User", back_populates="centro_costo_rel")


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
    func_copier_color = Column(Boolean, default=False, nullable=False)  # Copiadora Color
    func_printer = Column(Boolean, default=False, nullable=False)  # Impresora
    func_printer_color = Column(Boolean, default=False, nullable=False)  # Impresora Color
    func_document_server = Column(Boolean, default=False, nullable=False)  # Document Server
    func_fax = Column(Boolean, default=False, nullable=False)  # Fax
    func_scanner = Column(Boolean, default=False, nullable=False)  # Escáner
    func_browser = Column(Boolean, default=False, nullable=False)  # Navegador
    
    # Optional Fields
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=True, index=True)
    centro_costo_id = Column(Integer, ForeignKey("centro_costos.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Normalized Foreign Keys (new schema)
    smb_server_id = Column(Integer, ForeignKey("smb_servers.id", ondelete="RESTRICT"), nullable=False)
    network_credential_id = Column(Integer, ForeignKey("network_credentials.id", ondelete="RESTRICT"), nullable=False)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    empresa = relationship("Empresa", back_populates="users")
    centro_costo_rel = relationship("CentroCosto", back_populates="users")
    smb_server_rel = relationship("SMBServer", back_populates="users")
    network_credential_rel = relationship("NetworkCredential", back_populates="users")
    printer_assignments = relationship(
        "UserPrinterAssignment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    @property
    def centro_costos(self) -> Optional[str]:
        """Propiedad híbrida para mantener compatibilidad string hacia atrás"""
        return self.centro_costo_rel.nombre if self.centro_costo_rel else None
    
    @property
    def impresoras(self) -> list:
        res = []
        for assoc in self.printer_assignments:
            res.append({
                "printer_id": assoc.printer.id,
                "printer_name": assoc.printer.hostname,
                "printer_ip": assoc.printer.ip_address,
                "printer_location": assoc.printer.location,
                "entry_index": assoc.entry_index,
                "is_active": assoc.is_active,
                "permisos": {
                    "copiadora": assoc.func_copier,
                    "copiadora_color": assoc.func_copier_color,
                    "impresora": assoc.func_printer,
                    "impresora_color": assoc.func_printer_color,
                    "document_server": assoc.func_document_server,
                    "fax": assoc.func_fax,
                    "escaner": assoc.func_scanner,
                    "navegador": assoc.func_browser,
                }
            })
        return res
    
    def set_network_password(self, password: str):
        """
        Encriptar y guardar password de red
        
        Args:
            password: Password en texto plano
        """
        # Import aquí para evitar circular dependency
        from services.encryption_service import EncryptionService
        self.network_password_encrypted = EncryptionService.encrypt(password)
    
    def get_network_password(self) -> Optional[str]:
        """
        Obtener password de red desencriptado
        
        Returns:
            Password en texto plano o None si no existe
        """
        if self.network_password_encrypted:
            try:
                # Import aquí para evitar circular dependency
                from services.encryption_service import EncryptionService
                return EncryptionService.decrypt(self.network_password_encrypted)
            except Exception:
                # Si falla la desencriptación, retornar None
                return None
        return None
    
    @property
    def network_password(self) -> Optional[str]:
        """Property para acceso transparente al password"""
        return self.get_network_password()
    
    @network_password.setter
    def network_password(self, value: str):
        """Property setter para encriptar automáticamente"""
        self.set_network_password(value)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', empresa_id={self.empresa_id})>"


class Printer(Base):
    """
    Printer model for equipment management
    Stores printer information and status
    """
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, unique=True, index=True)  # IPv4/IPv6
    location = Column(String(255), nullable=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(Enum(PrinterStatus), default=PrinterStatus.OFFLINE)
    detected_model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True, index=True)  # Unique constraint removed to allow NULL duplicates
    
    # Capabilities
    has_color = Column(Boolean, default=False)
    has_scanner = Column(Boolean, default=False)
    has_fax = Column(Boolean, default=False)
    
    # Counter capabilities
    tiene_contador_usuario = Column(Boolean, default=True, nullable=False)  # Tiene getUserCounter.cgi
    usar_contador_ecologico = Column(Boolean, default=False, nullable=False)  # Usar getEcoCounter.cgi para usuarios
    formato_contadores = Column(String(50), default='estandar', nullable=False)  # Formato: 'estandar' (18 cols), 'simplificado' (13 cols), 'ecologico'
    
    # Capabilities JSON (new field from migration 010)
    capabilities_json = Column(JSONB, nullable=True)
    inconsistency_count = Column(Integer, default=0, nullable=False)
    
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

    # Printer admin password (encrypted)
    admin_password_encrypted = Column("admin_password", String(255), nullable=True)

    # Relationships
    empresa = relationship("Empresa", back_populates="printers")
    user_assignments = relationship(
        "UserPrinterAssignment",
        back_populates="printer",
        cascade="all, delete-orphan"
    )

    def set_admin_password(self, password: str):
        """Encriptar y guardar password de admin"""
        if not password:
            self.admin_password_encrypted = None
            return
        from services.encryption_service import EncryptionService
        self.admin_password_encrypted = EncryptionService.encrypt(password)

    def get_admin_password(self) -> Optional[str]:
        """Obtener password de admin desencriptado"""
        if self.admin_password_encrypted:
            try:
                from services.encryption_service import EncryptionService
                return EncryptionService.decrypt(self.admin_password_encrypted)
            except Exception:
                return None
        return None

    @property
    def admin_password(self) -> Optional[str]:
        return self.get_admin_password()

    @admin_password.setter
    def admin_password(self, value: str):
        self.set_admin_password(value)

    @property
    def capabilities(self) -> Optional[dict]:
        """
        Get printer capabilities from capabilities_json field
        
        Returns:
            Optional[dict]: Capabilities dictionary or None if not set
        """
        if self.capabilities_json:
            return self.capabilities_json
        return None
    
    def update_capabilities(self, new_capabilities: dict, manual: bool = False) -> None:
        """
        Update printer capabilities with merge logic
        
        If manual=False (automatic detection):
        - Respects manual_override flag (won't update if manual_override=True)
        - Merges with existing capabilities (preserves True values)
        
        If manual=True (manual update):
        - Always updates capabilities
        - Sets manual_override=True
        
        Args:
            new_capabilities: New capabilities dictionary
            manual: Whether this is a manual update
        """
        from models.capabilities import Capabilities
        
        if manual:
            # Manual update: always apply and set manual_override
            new_capabilities['manual_override'] = True
            self.capabilities_json = new_capabilities
            self.updated_at = datetime.utcnow()
        else:
            # Automatic update: respect manual_override and merge
            if self.capabilities_json and self.capabilities_json.get('manual_override', False):
                # Don't update if manual_override is set
                return
            
            if self.capabilities_json:
                # Merge with existing capabilities
                existing = Capabilities.from_json(self.capabilities_json)
                new = Capabilities.from_json(new_capabilities)
                merged = existing.merge(new)
                self.capabilities_json = merged.to_json()
            else:
                # First time: just set the capabilities
                self.capabilities_json = new_capabilities
            
            self.updated_at = datetime.utcnow()

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
    
    # Per-Printer Functions (Estado real en este dispositivo)
    entry_index = Column(String(10), nullable=True) # ID físico en la impresora
    func_copier = Column(Boolean, default=False, nullable=False)
    func_copier_color = Column(Boolean, default=False, nullable=False)
    func_printer = Column(Boolean, default=False, nullable=False)
    func_printer_color = Column(Boolean, default=False, nullable=False)
    func_document_server = Column(Boolean, default=False, nullable=False)
    func_fax = Column(Boolean, default=False, nullable=False)
    func_scanner = Column(Boolean, default=False, nullable=False)
    func_browser = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="printer_assignments")
    printer = relationship("Printer", back_populates="user_assignments")

    def __repr__(self):
        return f"<UserPrinterAssignment(user_id={self.user_id}, printer_id={self.printer_id})>"


class ContadorImpresora(Base):
    """
    Contador total de la impresora (getUnificationCounter.cgi)
    Almacena los contadores totales por impresora
    """
    __tablename__ = "contadores_impresora"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Contador total
    total = Column(Integer, default=0, nullable=False)
    
    # Copiadora
    copiadora_bn = Column(Integer, default=0, nullable=False)
    copiadora_color = Column(Integer, default=0, nullable=False)
    copiadora_color_personalizado = Column(Integer, default=0, nullable=False)
    copiadora_dos_colores = Column(Integer, default=0, nullable=False)
    
    # Impresora
    impresora_bn = Column(Integer, default=0, nullable=False)
    impresora_color = Column(Integer, default=0, nullable=False)
    impresora_color_personalizado = Column(Integer, default=0, nullable=False)
    impresora_dos_colores = Column(Integer, default=0, nullable=False)
    
    # Fax
    fax_bn = Column(Integer, default=0, nullable=False)
    
    # Enviar/TX Total
    enviar_total_bn = Column(Integer, default=0, nullable=False)
    enviar_total_color = Column(Integer, default=0, nullable=False)
    
    # Transmisión por fax
    transmision_fax_total = Column(Integer, default=0, nullable=False)
    
    # Envío por escáner
    envio_escaner_bn = Column(Integer, default=0, nullable=False)
    envio_escaner_color = Column(Integer, default=0, nullable=False)
    
    # Otras funciones
    otras_a3_dlt = Column(Integer, default=0, nullable=False)
    otras_duplex = Column(Integer, default=0, nullable=False)
    
    # Metadata
    fecha_lectura = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    printer = relationship("Printer")

    def __repr__(self):
        return f"<ContadorImpresora(printer_id={self.printer_id}, total={self.total}, fecha={self.fecha_lectura})>"


class ContadorUsuario(Base):
    """
    Contador por usuario (getUserCounter.cgi o getEcoCounter.cgi)
    Almacena los contadores individuales por usuario
    """
    __tablename__ = "contadores_usuario"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usuario (normalizado) - ÚNICO CAMPO DE REFERENCIA
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True)
    
    # Total impresiones
    total_paginas = Column(Integer, default=0, nullable=False)
    total_bn = Column(Integer, default=0, nullable=False)
    total_color = Column(Integer, default=0, nullable=False)
    
    # Copiadora (getUserCounter)
    copiadora_bn = Column(Integer, default=0, nullable=False)
    copiadora_mono_color = Column(Integer, default=0, nullable=False)
    copiadora_dos_colores = Column(Integer, default=0, nullable=False)
    copiadora_todo_color = Column(Integer, default=0, nullable=False)
    copiadora_hojas_2_caras = Column(Integer, default=0, nullable=False)  # Impresora 252
    copiadora_paginas_combinadas = Column(Integer, default=0, nullable=False)  # Impresora 252
    
    # Impresora (getUserCounter)
    impresora_bn = Column(Integer, default=0, nullable=False)
    impresora_mono_color = Column(Integer, default=0, nullable=False)
    impresora_dos_colores = Column(Integer, default=0, nullable=False)
    impresora_color = Column(Integer, default=0, nullable=False)
    impresora_hojas_2_caras = Column(Integer, default=0, nullable=False)  # Impresora 252
    impresora_paginas_combinadas = Column(Integer, default=0, nullable=False)  # Impresora 252
    
    # Escáner (getUserCounter)
    escaner_bn = Column(Integer, default=0, nullable=False)
    escaner_todo_color = Column(Integer, default=0, nullable=False)
    
    # Fax (getUserCounter)
    fax_bn = Column(Integer, default=0, nullable=False)
    fax_paginas_transmitidas = Column(Integer, default=0, nullable=False)
    
    # Revelado (getUserCounter)
    revelado_negro = Column(Integer, default=0, nullable=False)
    revelado_color_ymc = Column(Integer, default=0, nullable=False)
    
    # Métricas ecológicas (getEcoCounter) - almacenadas como texto
    eco_uso_2_caras = Column(String(50), nullable=True)
    eco_uso_combinar = Column(String(50), nullable=True)
    eco_reduccion_papel = Column(String(50), nullable=True)
    
    # Tipo de contador usado
    tipo_contador = Column(String(20), nullable=False, default="usuario")  # "usuario" o "ecologico"
    
    # Metadata
    fecha_lectura = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    printer = relationship("Printer")
    user = relationship("User")  # ← NUEVO

    def __repr__(self):
        return f"<ContadorUsuario(printer_id={self.printer_id}, user_id={self.user_id}, total={self.total_paginas})>"


class CierreMensual(Base):
    """
    Cierre de contadores (diario, semanal, mensual, personalizado)
    Almacena snapshots inmutables para auditoría y comparación
    """
    __tablename__ = "cierres_mensuales"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Fechas del período
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    
    # Período (mantener para compatibilidad con cierres mensuales)
    anio = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)  # 1-12
    
    # Contadores totales al cierre
    total_paginas = Column(Integer, default=0, nullable=False)
    total_copiadora = Column(Integer, default=0, nullable=False)
    total_impresora = Column(Integer, default=0, nullable=False)
    total_escaner = Column(Integer, default=0, nullable=False)
    total_fax = Column(Integer, default=0, nullable=False)
    
    # Diferencia con cierre anterior
    diferencia_total = Column(Integer, default=0, nullable=False)
    diferencia_copiadora = Column(Integer, default=0, nullable=False)
    diferencia_impresora = Column(Integer, default=0, nullable=False)
    diferencia_escaner = Column(Integer, default=0, nullable=False)
    diferencia_fax = Column(Integer, default=0, nullable=False)
    
    # Metadata
    fecha_cierre = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cerrado_por = Column(String(100), nullable=True)  # Usuario que hizo el cierre
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Auditoría (agregado en migración 007)
    modified_at = Column(DateTime(timezone=True), nullable=True)
    modified_by = Column(String(100), nullable=True)
    hash_verificacion = Column(String(64), nullable=True)

    # Relationships
    printer = relationship("Printer")
    usuarios = relationship("CierreMensualUsuario", back_populates="cierre", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CierreMensual(printer_id={self.printer_id}, periodo={self.fecha_inicio} a {self.fecha_fin}, total={self.total_paginas})>"


class CierreMensualUsuario(Base):
    """
    Snapshot de contadores por usuario al momento del cierre mensual
    Permite auditoría y facturación sin depender de datos históricos
    """
    __tablename__ = "cierres_mensuales_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    cierre_mensual_id = Column(Integer, ForeignKey("cierres_mensuales.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usuario (normalizado) - ÚNICO CAMPO DE REFERENCIA
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True)
    
    # Contadores al cierre (snapshot inmutable)
    total_paginas = Column(Integer, nullable=False)
    total_bn = Column(Integer, nullable=False)
    total_color = Column(Integer, nullable=False)
    
    # Desglose por función
    copiadora_bn = Column(Integer, nullable=False)
    copiadora_color = Column(Integer, nullable=False)
    impresora_bn = Column(Integer, nullable=False)
    impresora_color = Column(Integer, nullable=False)
    escaner_bn = Column(Integer, nullable=False)
    escaner_color = Column(Integer, nullable=False)
    fax_bn = Column(Integer, nullable=False)
    
    # Consumo del mes (diferencia con mes anterior)
    consumo_total = Column(Integer, nullable=False)
    consumo_copiadora = Column(Integer, nullable=False)
    consumo_impresora = Column(Integer, nullable=False)
    consumo_escaner = Column(Integer, nullable=False)
    consumo_fax = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    cierre = relationship("CierreMensual", back_populates="usuarios")
    user = relationship("User")  # ← NUEVO

    def __repr__(self):
        return f"<CierreMensualUsuario(cierre_id={self.cierre_mensual_id}, user_id={self.user_id}, consumo={self.consumo_total})>"


class ComparacionGuardada(Base):
    """
    Model for saving close comparisons
    """
    __tablename__ = "comparaciones_guardadas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    cierre1_id = Column(Integer, ForeignKey("cierres_mensuales.id", ondelete="CASCADE"), nullable=False, index=True)
    cierre2_id = Column(Integer, ForeignKey("cierres_mensuales.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_json = Column(JSONB, nullable=False)
    creado_por = Column(String(100), nullable=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    cierre1 = relationship("CierreMensual", foreign_keys=[cierre1_id])
    cierre2 = relationship("CierreMensual", foreign_keys=[cierre2_id])
    admin_user = relationship("AdminUser")
    empresa = relationship("Empresa")

    def __repr__(self):
        return f"<ComparacionGuardada(id={self.id}, titulo='{self.titulo}')>"


class ScheduledClosure(Base):
    """
    Programación de cierres masivos.
    Permite automatizar lecturas de contadores periódicas de forma diaria, semanal, mensual o una sola vez.
    """
    __tablename__ = "scheduled_closures"

    id = Column(Integer, primary_key=True, index=True)
    frequency = Column(String(50), nullable=False)  # "once", "daily", "weekly", "monthly"
    scheduled_time = Column(String(5), nullable=False)  # Formato "HH:MM" (24h), ej: "18:00"
    
    # Para "once" (ejecución única)
    specific_date = Column(Date, nullable=True)
    
    # Para "weekly" (0=Lunes, 6=Domingo)
    day_of_week = Column(Integer, nullable=True)
    
    # Para "monthly" (1 a 31)
    day_of_month = Column(Integer, nullable=True)
    
    # Filtro opcional por empresa
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=False)
    
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)  # Siguiente ejecución precalculada
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación
    empresa = relationship("Empresa")

    def __repr__(self):
        return f"<ScheduledClosure(id={self.id}, frequency='{self.frequency}', time='{self.scheduled_time}')>"



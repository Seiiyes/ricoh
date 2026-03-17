"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Literal
from datetime import datetime
import ipaddress


# ============================================================================
# User Schemas
# ============================================================================

class AvailableFunctions(BaseModel):
    """Available printer functions"""
    copier: bool = False
    copier_color: bool = False
    printer: bool = False
    printer_color: bool = False
    document_server: bool = False
    fax: bool = False
    scanner: bool = False
    browser: bool = False
    
    # Remove specific cross-field validator that causes issues in parallel validation


class SMBConfiguration(BaseModel):
    """SMB folder configuration"""
    server: str = Field(..., min_length=1, max_length=255, description="Server name or IP")
    port: int = Field(21, ge=1, le=65535, description="SMB port")
    path: str = Field(..., max_length=500, description="UNC path")
    
    @validator('path')
    def validate_unc_path(cls, v):
        """Validate UNC path format"""
        # Allow empty path
        if not v or len(v) == 0:
            return v
        # If not empty, must start with \\
        if not v.startswith('\\\\'):
            raise ValueError("Path must start with \\\\ (UNC format)")
        return v


class NetworkCredentials(BaseModel):
    """Network authentication credentials"""
    username: str = Field(default="reliteltda\\scaner", min_length=1, max_length=255, description="Network username")
    password: Optional[str] = Field(None, max_length=255, description="Network password")


class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Full name (Nombre)")
    empresa: Optional[str] = Field(None, max_length=255, description="Empresa")
    centro_costos: Optional[str] = Field(None, max_length=100, description="Centro de costos")


class UserCreate(UserBase):
    """Schema for creating a user"""
    codigo_de_usuario: str = Field(..., min_length=4, max_length=8, description="Numeric authentication code")
    
    # NEW: Optional printer selection for automatic provisioning
    printer_ids: Optional[List[int]] = Field(
        None, 
        description="List of printer IDs to provision user to"
    )
    
    # Network credentials - can be nested or flat
    network_credentials: Optional[NetworkCredentials] = None
    network_username: Optional[str] = Field(None, max_length=255)
    network_password: Optional[str] = Field(None, max_length=255)
    
    # SMB configuration - can be nested or flat
    smb_config: Optional[SMBConfiguration] = None
    smb_server: Optional[str] = Field(None, max_length=255)
    smb_port: Optional[int] = Field(None, ge=1, le=65535)
    smb_path: Optional[str] = Field(None, max_length=500)
    
    # Available functions - can be nested or flat
    available_functions: Optional[AvailableFunctions] = None
    func_copier: Optional[bool] = None
    func_copier_color: Optional[bool] = None
    func_printer: Optional[bool] = None
    func_printer_color: Optional[bool] = None
    func_document_server: Optional[bool] = None
    func_fax: Optional[bool] = None
    func_scanner: Optional[bool] = None
    func_browser: Optional[bool] = None
    
    @validator('codigo_de_usuario')
    def validate_codigo(cls, v):
        """Ensure codigo_de_usuario is numeric"""
        if not v.isdigit():
            raise ValueError("Código de usuario must contain only digits")
        return v
    
    @validator('printer_ids')
    def validate_printer_ids(cls, v):
        """Ensure all printer IDs are positive"""
        if v is not None:
            if not all(pid > 0 for pid in v):
                raise ValueError("All printer IDs must be positive integers")
        return v
    
    @validator('smb_path')
    def validate_unc_path_flat(cls, v):
        """Validate UNC path format for flat structure"""
        if v and len(v) > 0 and not v.startswith('\\\\'):
            raise ValueError("Path must start with \\\\ (UNC format)")
        return v
    
    @validator('network_username')
    def validate_network_username(cls, v):
        """Validate network username is not empty string"""
        if v is not None and len(v) == 0:
            return None  # Convert empty string to None
        return v
    
    @validator('smb_server')
    def validate_smb_server(cls, v):
        """Validate SMB server is not empty string"""
        if v is not None and len(v) == 0:
            return None  # Convert empty string to None
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    codigo_de_usuario: Optional[str] = Field(None, min_length=4, max_length=8)
    network_username: Optional[str] = Field(None, min_length=1, max_length=255)
    network_password: Optional[str] = Field(None, min_length=1, max_length=255)
    smb_server: Optional[str] = Field(None, min_length=1, max_length=255)
    smb_port: Optional[int] = Field(None, ge=1, le=65535)
    smb_path: Optional[str] = Field(None, min_length=1, max_length=500)
    func_copier: Optional[bool] = None
    func_copier_color: Optional[bool] = None
    func_printer: Optional[bool] = None
    func_printer_color: Optional[bool] = None
    func_document_server: Optional[bool] = None
    func_fax: Optional[bool] = None
    func_scanner: Optional[bool] = None
    func_browser: Optional[bool] = None
    empresa: Optional[str] = Field(None, max_length=255)
    centro_costos: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (excludes password)"""
    id: int
    codigo_de_usuario: str
    
    # Network username only (no password)
    network_username: str
    
    # SMB configuration
    smb_server: str
    smb_port: int
    smb_path: str
    
    # Available functions
    func_copier: bool
    func_copier_color: bool
    func_printer: bool
    func_printer_color: bool
    func_document_server: bool
    func_fax: bool
    func_scanner: bool
    func_browser: bool
    
    # Metadata
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# Printer Capabilities Schemas
# ============================================================================

class CapabilitiesResponse(BaseModel):
    """Schema for printer capabilities response"""
    formato_contadores: str = Field(..., description="Counter format: 'estandar', 'simplificado', 'ecologico'")
    has_color: bool = Field(..., description="Supports color printing")
    has_hojas_2_caras: bool = Field(..., description="Supports duplex printing")
    has_paginas_combinadas: bool = Field(..., description="Supports multiple pages per sheet")
    has_mono_color: bool = Field(..., description="Supports single color printing")
    has_dos_colores: bool = Field(..., description="Supports two-color printing")
    detected_at: str = Field(..., description="ISO 8601 timestamp of detection")
    manual_override: bool = Field(default=False, description="Manually configured capabilities")
    
    class Config:
        from_attributes = True


class CapabilitiesUpdate(BaseModel):
    """Schema for updating printer capabilities manually"""
    formato_contadores: Optional[str] = Field(None, description="Counter format")
    has_color: Optional[bool] = Field(None, description="Supports color printing")
    has_hojas_2_caras: Optional[bool] = Field(None, description="Supports duplex printing")
    has_paginas_combinadas: Optional[bool] = Field(None, description="Supports multiple pages per sheet")
    has_mono_color: Optional[bool] = Field(None, description="Supports single color printing")
    has_dos_colores: Optional[bool] = Field(None, description="Supports two-color printing")
    
    @validator('formato_contadores')
    def validate_formato(cls, v):
        """Validate counter format"""
        if v is not None and v not in ['estandar', 'simplificado', 'ecologico']:
            raise ValueError("formato_contadores must be 'estandar', 'simplificado', or 'ecologico'")
        return v


# ============================================================================
# Printer Schemas
# ============================================================================

class PrinterBase(BaseModel):
    """Base printer schema"""
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., description="IPv4 or IPv6 address")
    location: Optional[str] = Field(None, max_length=255)
    empresa: Optional[str] = Field(None, max_length=255, description="Company/Organization")
    
    @validator('ip_address')
    def validate_ip(cls, v):
        """Validate IP address format"""
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError("Invalid IP address format")


class PrinterCreate(PrinterBase):
    """Schema for creating a printer"""
    detected_model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    has_color: bool = False
    has_scanner: bool = False
    has_fax: bool = False
    toner_cyan: int = Field(0, ge=0, le=100)
    toner_magenta: int = Field(0, ge=0, le=100)
    toner_yellow: int = Field(0, ge=0, le=100)
    toner_black: int = Field(0, ge=0, le=100)


class PrinterUpdate(BaseModel):
    """Schema for updating a printer"""
    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    empresa: Optional[str] = Field(None, max_length=255)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[Literal['online', 'offline', 'error', 'maintenance']] = None
    toner_cyan: Optional[int] = Field(None, ge=0, le=100)
    toner_magenta: Optional[int] = Field(None, ge=0, le=100)
    toner_yellow: Optional[int] = Field(None, ge=0, le=100)
    toner_black: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class PrinterResponse(PrinterBase):
    """Schema for printer response"""
    id: int
    empresa: Optional[str]
    status: str
    detected_model: Optional[str]
    serial_number: Optional[str]
    has_color: bool
    has_scanner: bool
    has_fax: bool
    toner_cyan: int
    toner_magenta: int
    toner_yellow: int
    toner_black: int
    last_seen: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Capabilities
    capabilities: Optional[CapabilitiesResponse] = Field(None, description="Printer capabilities")
    
    class Config:
        from_attributes = True


# ============================================================================
# Discovery Schemas
# ============================================================================

class ScanRequest(BaseModel):
    """Request schema for network scan"""
    ip_range: str = Field(
        ...,
        description="IP range in CIDR notation (e.g., 192.168.1.0/24)",
        example="192.168.1.0/24"
    )
    
    @validator('ip_range')
    def validate_ip_range(cls, v):
        """Validate CIDR notation"""
        try:
            ipaddress.ip_network(v, strict=False)
            return v
        except ValueError:
            raise ValueError("Invalid IP range format. Use CIDR notation (e.g., 192.168.1.0/24)")


class DiscoveredDevice(BaseModel):
    """Schema for discovered device"""
    hostname: str
    ip_address: str
    status: str
    detected_model: Optional[str]
    has_color: bool
    has_scanner: bool
    has_fax: bool
    toner_cyan: int
    toner_magenta: int
    toner_yellow: int
    toner_black: int
    location: Optional[str]


class ScanResponse(BaseModel):
    """Response schema for network scan"""
    devices: List[DiscoveredDevice]
    total_scanned: int
    total_found: int
    scan_duration_seconds: float
    timestamp: datetime


# ============================================================================
# Provisioning Schemas
# ============================================================================

class ProvisionRequest(BaseModel):
    """Request schema for provisioning"""
    user_id: int = Field(..., gt=0, description="User ID to provision")
    printer_ids: List[int] = Field(..., min_items=1, description="List of printer IDs")
    
    @validator('printer_ids')
    def validate_printer_ids(cls, v):
        """Ensure all printer IDs are positive"""
        if not all(pid > 0 for pid in v):
            raise ValueError("All printer IDs must be positive integers")
        return v


class ProvisionResponse(BaseModel):
    """Response schema for provisioning"""
    success: bool
    user_id: int
    user_name: str
    printers_provisioned: int
    printer_ids: List[int]
    provisioned_at: str
    message: str


class UserProvisioningStatus(BaseModel):
    """Schema for user provisioning status"""
    user_id: int
    user_name: str
    empresa: Optional[str]
    smb_path: Optional[str]
    total_printers: int
    printers: List[dict]


class PrinterUsersResponse(BaseModel):
    """Schema for printer users response"""
    printer_id: int
    hostname: str
    ip_address: str
    total_users: int
    users: List[dict]


# ============================================================================
# WebSocket Event Schemas
# ============================================================================

class LogEvent(BaseModel):
    """Schema for log events"""
    id: str
    timestamp: str
    message: str
    type: Literal['info', 'success', 'error', 'warning']
    user_id: Optional[int] = None
    printer_id: Optional[int] = None


# ============================================================================
# Common Response Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None


# ============================================================================
# User Functions Update Schemas
# ============================================================================

class UpdateUserFunctionsRequest(BaseModel):
    """Request schema for updating user functions on a printer"""
    copiadora: bool = False
    copiadora_color: bool = False
    impresora: bool = False
    impresora_color: bool = False
    escaner: bool = False
    document_server: bool = False
    fax: bool = False
    navegador: bool = False


class UpdateUserFunctionsResponse(BaseModel):
    """Response schema for updating user functions"""
    success: bool
    message: str
    user_code: str
    printer_ip: str
    functions_updated: dict



# ============================================================================
# Automatic Provisioning Schemas
# ============================================================================

class PrinterProvisioningResult(BaseModel):
    """Result of provisioning to a single printer"""
    printer_id: int
    hostname: str
    ip_address: str
    status: Literal['success', 'failed']
    error_message: Optional[str] = None
    retry_attempts: int = 0
    provisioned_at: Optional[str] = None


class ProvisioningResults(BaseModel):
    """Detailed provisioning results"""
    overall_success: bool
    total_printers: int
    successful_count: int
    failed_count: int
    results: List[PrinterProvisioningResult]
    summary_message: str


class UserCreateResponse(UserResponse):
    """Extended response for user creation with provisioning"""
    provisioning_results: Optional[ProvisioningResults] = None

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
    printer: bool = False
    document_server: bool = False
    fax: bool = False
    scanner: bool = False
    browser: bool = False
    
    @validator('copier', 'printer', 'document_server', 'fax', 'scanner', 'browser')
    def at_least_one_function(cls, v, values):
        """Ensure at least one function is enabled"""
        # Check if at least one function is True
        if not any(values.values()) and not v:
            raise ValueError("At least one function must be enabled")
        return v


class SMBConfiguration(BaseModel):
    """SMB folder configuration"""
    server: str = Field(..., min_length=1, max_length=255, description="Server name or IP")
    port: int = Field(21, ge=1, le=65535, description="SMB port")
    path: str = Field(..., min_length=1, max_length=500, description="UNC path")
    
    @validator('path')
    def validate_unc_path(cls, v):
        """Validate UNC path format"""
        if not v.startswith('\\\\'):
            raise ValueError("Path must start with \\\\ (UNC format)")
        return v


class NetworkCredentials(BaseModel):
    """Network authentication credentials"""
    username: str = Field(default="reliteltda\\scaner", min_length=1, max_length=255, description="Network username")
    password: str = Field(..., min_length=1, max_length=255, description="Network password")


class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Full name (Nombre)")
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user"""
    codigo_de_usuario: str = Field(..., min_length=4, max_length=8, description="Numeric authentication code")
    
    # Network credentials
    network_credentials: NetworkCredentials
    
    # SMB configuration
    smb_config: SMBConfiguration
    
    # Available functions
    available_functions: AvailableFunctions
    
    @validator('codigo_de_usuario')
    def validate_codigo(cls, v):
        """Ensure codigo_de_usuario is numeric"""
        if not v.isdigit():
            raise ValueError("Código de usuario must contain only digits")
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
    func_printer: Optional[bool] = None
    func_document_server: Optional[bool] = None
    func_fax: Optional[bool] = None
    func_scanner: Optional[bool] = None
    func_browser: Optional[bool] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=100)
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
    func_printer: bool
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
# Printer Schemas
# ============================================================================

class PrinterBase(BaseModel):
    """Base printer schema"""
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., description="IPv4 or IPv6 address")
    location: Optional[str] = Field(None, max_length=255)
    
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
    status: Optional[Literal['online', 'offline', 'error', 'maintenance']] = None
    toner_cyan: Optional[int] = Field(None, ge=0, le=100)
    toner_magenta: Optional[int] = Field(None, ge=0, le=100)
    toner_yellow: Optional[int] = Field(None, ge=0, le=100)
    toner_black: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class PrinterResponse(PrinterBase):
    """Schema for printer response"""
    id: int
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
    email: Optional[str]
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

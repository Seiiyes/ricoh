# Design Document: Ricoh User Provisioning

## Overview

This design extends the existing Ricoh printer provisioning system to support complete user configuration with all fields required by Ricoh printers. The system currently captures only basic information (name, PIN, SMB path) and needs to be enhanced to support network credentials, available functions, complete SMB configuration, and proper Spanish terminology.

The architecture follows a three-tier pattern:
- **Frontend**: React TypeScript application (to be implemented)
- **Backend**: Python FastAPI application with PostgreSQL database
- **Printer Communication**: SNMP-based communication with Ricoh printers

Key design decisions:
- Use AES-256 encryption for network passwords stored in the database
- Rename "pin" to "codigo_de_usuario" throughout the system for consistency with Ricoh terminology
- Store available functions as individual boolean columns for query flexibility
- Parse existing "smb_path" into separate server/port/path components during migration
- Let the printer auto-generate Nº_de_registro and Visualización_tecla (not stored in our system)

## Architecture

### System Components

```
┌─────────────────┐
│   Frontend      │
│  (React + TS)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Backend API   │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│  DB    │ │  Ricoh   │
│ (PG)   │ │ Printers │
└────────┘ └──────────┘
```

### Data Flow

1. **User Creation Flow**:
   - Frontend submits complete user form → Backend validates → Encrypt password → Store in DB → Return user object

2. **Provisioning Flow**:
   - Frontend requests provisioning → Backend retrieves user → Decrypt password → Format Ricoh payload → Send via SNMP → Update assignment table → Return success

3. **Migration Flow**:
   - Run migration script → Read existing users → Parse smb_path → Rename pin column → Set default values → Update records

## Components and Interfaces

### Database Schema

#### Extended User Model

```python
class User(Base):
    __tablename__ = "users"
    
    # Identity
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # Nombre
    
    # Authentication
    codigo_de_usuario = Column(String(8), nullable=False, index=True)  # Renamed from 'pin'
    
    # Network Credentials (Autenticación de carpeta)
    network_username = Column(String(255), nullable=False)  # Nombre de usuario de inicio de sesión
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
    printer_assignments = relationship("UserPrinterAssignment", back_populates="user", cascade="all, delete-orphan")
```

**Migration Notes**:
- Rename `pin` column to `codigo_de_usuario`
- Parse existing `smb_path` (e.g., "\\\\192.168.1.100\\scans") into:
  - `smb_server`: "192.168.1.100"
  - `smb_port`: 21 (default)
  - `smb_path`: "\\\\192.168.1.100\\scans" (keep full path)
- Add new columns with defaults:
  - `network_username`: empty string (to be filled by admin)
  - `network_password_encrypted`: empty string (to be filled by admin)
  - All `func_*` columns: False (to be configured by admin)

### API Schemas

#### UserCreate Schema

```python
class AvailableFunctions(BaseModel):
    """Available printer functions"""
    copier: bool = False
    printer: bool = False
    document_server: bool = False
    fax: bool = False
    scanner: bool = False
    browser: bool = False
    
    @validator('*')
    def at_least_one_function(cls, v, values):
        """Ensure at least one function is enabled"""
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
    username: str = Field(..., min_length=1, max_length=255, description="Network username")
    password: str = Field(..., min_length=1, max_length=255, description="Network password")


class UserCreate(BaseModel):
    """Schema for creating a user"""
    # Basic info
    name: str = Field(..., min_length=1, max_length=100, description="Full name (Nombre)")
    codigo_de_usuario: str = Field(..., min_length=4, max_length=8, regex=r'^\d+$', description="Numeric authentication code")
    
    # Network credentials
    network_credentials: NetworkCredentials
    
    # SMB configuration
    smb_config: SMBConfiguration
    
    # Available functions
    available_functions: AvailableFunctions
    
    # Optional fields
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=100)
    
    @validator('codigo_de_usuario')
    def validate_codigo(cls, v):
        """Ensure codigo_de_usuario is numeric"""
        if not v.isdigit():
            raise ValueError("Código de usuario must contain only digits")
        return v
```

#### UserResponse Schema

```python
class UserResponse(BaseModel):
    """Schema for user response (excludes password)"""
    id: int
    name: str
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
    
    # Optional fields
    email: Optional[str]
    department: Optional[str]
    
    # Metadata
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

### Backend Services

#### Password Encryption Service

```python
class PasswordEncryptionService:
    """
    Service for encrypting/decrypting network passwords
    Uses AES-256-GCM for authenticated encryption
    """
    
    def __init__(self, encryption_key: bytes):
        """
        Initialize with encryption key from environment
        Key should be 32 bytes for AES-256
        """
        self.key = encryption_key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext password
        Returns base64-encoded ciphertext with nonce
        """
        # Implementation uses cryptography.fernet or similar
        pass
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext password
        Returns plaintext password
        """
        pass
```

**Key Management**:
- Store encryption key in environment variable `ENCRYPTION_KEY`
- Generate key using: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- Never commit key to version control
- Use different keys for dev/staging/production

#### Ricoh Provisioning Service

```python
class RicohProvisioningService:
    """
    Service for provisioning users to Ricoh printers via SNMP
    """
    
    def __init__(self, snmp_client: SNMPClient, password_service: PasswordEncryptionService):
        self.snmp = snmp_client
        self.password_service = password_service
    
    def provision_user(self, user: User, printer: Printer) -> bool:
        """
        Provision a user to a Ricoh printer
        
        Args:
            user: User object with all configuration
            printer: Printer object with IP address
            
        Returns:
            True if successful, False otherwise
        """
        # Decrypt password in memory only
        network_password = self.password_service.decrypt(user.network_password_encrypted)
        
        # Build Ricoh payload
        payload = {
            "nombre": user.name,
            "codigo_de_usuario": user.codigo_de_usuario,
            "nombre_usuario_inicio_sesion": user.network_username,
            "contrasena_inicio_sesion": network_password,
            "funciones_disponibles": {
                "copiadora": user.func_copier,
                "impresora": user.func_printer,
                "document_server": user.func_document_server,
                "fax": user.func_fax,
                "escaner": user.func_scanner,
                "navegador": user.func_browser
            },
            "carpeta_smb": {
                "protocolo": "SMB",
                "servidor": user.smb_server,
                "puerto": user.smb_port,
                "ruta": user.smb_path
            }
            # Note: No nº_de_registro or visualización_tecla - printer auto-generates these
        }
        
        # Send via SNMP
        return self.snmp.set_user_configuration(printer.ip_address, payload)
```

### Frontend Components

#### User Form Component

```typescript
interface UserFormData {
  // Basic info
  name: string;
  codigoDeUsuario: string;
  
  // Network credentials
  networkUsername: string;
  networkPassword: string;
  
  // SMB configuration
  smbServer: string;
  smbPort: number;
  smbPath: string;
  
  // Available functions
  funcCopier: boolean;
  funcPrinter: boolean;
  funcDocumentServer: boolean;
  funcFax: boolean;
  funcScanner: boolean;
  funcBrowser: boolean;
  
  // Optional
  email?: string;
  department?: string;
}

const UserProvisioningForm: React.FC = () => {
  // Form state management
  // Validation logic
  // Submit handler
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Basic Information Section */}
      <section>
        <h3>Información Básica</h3>
        <input label="Nombre Completo" name="name" required />
        <input label="Código de usuario" name="codigoDeUsuario" pattern="[0-9]{4,8}" required />
      </section>
      
      {/* Network Credentials Section */}
      <section>
        <h3>Autenticación de Carpeta</h3>
        <input label="Nombre de usuario de inicio de sesión" name="networkUsername" required />
        <input type="password" label="Contraseña de inicio de sesión" name="networkPassword" required />
      </section>
      
      {/* Available Functions Section */}
      <section>
        <h3>Funciones Disponibles</h3>
        <checkbox label="Copiadora" name="funcCopier" />
        <checkbox label="Impresora" name="funcPrinter" />
        <checkbox label="Document Server" name="funcDocumentServer" />
        <checkbox label="Fax" name="funcFax" />
        <checkbox label="Escáner" name="funcScanner" />
        <checkbox label="Navegador" name="funcBrowser" />
      </section>
      
      {/* SMB Configuration Section */}
      <section>
        <h3>Carpeta SMB</h3>
        <input label="Nombre de servidor" name="smbServer" required />
        <input type="number" label="Puerto" name="smbPort" defaultValue={21} required />
        <input label="Ruta" name="smbPath" placeholder="\\servidor\carpeta" required />
      </section>
      
      {/* Optional Fields Section */}
      <section>
        <h3>Información Adicional (Opcional)</h3>
        <input type="email" label="Correo electrónico" name="email" />
        <input label="Departamento" name="department" />
      </section>
      
      <button type="submit">Crear Usuario</button>
    </form>
  );
};
```

## Data Models

### User Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| name | String(100) | NOT NULL, Indexed | Full name (Nombre) |
| codigo_de_usuario | String(8) | NOT NULL, Indexed | Numeric auth code (4-8 digits) |
| network_username | String(255) | NOT NULL | Network login username |
| network_password_encrypted | Text | NOT NULL | AES-256 encrypted password |
| smb_server | String(255) | NOT NULL | SMB server name/IP |
| smb_port | Integer | NOT NULL, Default: 21 | SMB port number |
| smb_path | String(500) | NOT NULL | UNC path to folder |
| func_copier | Boolean | NOT NULL, Default: False | Copier function enabled |
| func_printer | Boolean | NOT NULL, Default: False | Printer function enabled |
| func_document_server | Boolean | NOT NULL, Default: False | Document server enabled |
| func_fax | Boolean | NOT NULL, Default: False | Fax function enabled |
| func_scanner | Boolean | NOT NULL, Default: False | Scanner function enabled |
| func_browser | Boolean | NOT NULL, Default: False | Browser function enabled |
| email | String(255) | UNIQUE, Indexed | Email address (optional) |
| department | String(100) | NULL | Department name (optional) |
| is_active | Boolean | NOT NULL, Default: True | Active status |
| created_at | DateTime | NOT NULL, Auto | Creation timestamp |
| updated_at | DateTime | NULL, Auto | Last update timestamp |

### Ricoh Printer Payload Format

```json
{
  "nombre": "Juan Pérez",
  "codigo_de_usuario": "1014",
  "nombre_usuario_inicio_sesion": "jperez",
  "contrasena_inicio_sesion": "SecurePass123",
  "funciones_disponibles": {
    "copiadora": true,
    "impresora": true,
    "document_server": false,
    "fax": false,
    "escaner": true,
    "navegador": false
  },
  "carpeta_smb": {
    "protocolo": "SMB",
    "servidor": "192.168.1.100",
    "puerto": 21,
    "ruta": "\\\\192.168.1.100\\scans\\jperez"
  }
}
```

**Note**: The printer will automatically:
- Generate `nº_de_registro` (auto-incremental)
- Set `visualización_tecla` = `nombre` (copy from name field)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


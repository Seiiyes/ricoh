# Design Document - Sistema de Autenticación y Gestión de Empresas

## Overview

Este documento describe el diseño técnico completo para implementar un sistema de autenticación con roles y multi-tenancy basado en empresas para Ricoh Suite. El sistema transformará la aplicación actual (sin autenticación) en una plataforma segura multi-tenant con control de acceso basado en roles.

### Objetivos del Sistema

1. **Normalización de Datos**: Convertir campos VARCHAR de empresa en tabla normalizada con integridad referencial
2. **Autenticación Segura**: Implementar sistema JWT con bcrypt para hashing de contraseñas
3. **Multi-Tenancy**: Aislamiento completo de datos entre empresas
4. **Control de Acceso**: Roles (superadmin, admin, viewer, operator) con permisos granulares
5. **Auditoría Completa**: Registro inmutable de todas las acciones administrativas
6. **Seguridad**: Rate limiting, HTTPS, CORS, protección contra ataques comunes

### Alcance

**Incluye:**
- Migración de base de datos (normalización de empresas)
- Backend: Endpoints de autenticación, middleware, filtrado automático
- Frontend: Login, gestión de empresas, gestión de usuarios admin, protección de rutas
- Seguridad: JWT, bcrypt, rate limiting, CORS, HTTPS

**No Incluye:**
- Autenticación de dos factores (2FA) - fase futura
- Single Sign-On (SSO) - fase futura
- Permisos granulares por módulo (tabla admin_permissions) - opcional
- Notificaciones por email - fase futura


## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend - React + TypeScript"
        A[Login Page] --> B[Protected Routes]
        B --> C[Dashboard]
        B --> D[Empresas Module]
        B --> E[Admin Users Module]
        B --> F[Existing Modules]
        G[Auth Context] --> B
        H[API Client] --> G
    end
    
    subgraph "Backend - FastAPI"
        I[Auth Endpoints] --> J[Auth Middleware]
        J --> K[Role Validator]
        K --> L[Business Logic]
        L --> M[Company Filter]
        M --> N[Repository Layer]
    end
    
    subgraph "Database - PostgreSQL"
        O[(empresas)]
        P[(admin_users)]
        Q[(admin_sessions)]
        R[(admin_audit_log)]
        S[(printers)]
        T[(users)]
        U[(contadores)]
    end
    
    H -->|JWT Token| I
    N --> O
    N --> P
    N --> Q
    N --> R
    N --> S
    N --> T
    N --> U
    
    O -->|FK| S
    O -->|FK| T
    P -->|FK| O
    Q -->|FK| P
    R -->|FK| P
```

### Component Architecture


```mermaid
graph LR
    subgraph "Presentation Layer"
        A[React Components]
        B[Zustand Store]
        C[API Service]
    end
    
    subgraph "API Layer"
        D[Auth Routes]
        E[Empresa Routes]
        F[Admin User Routes]
        G[Existing Routes]
    end
    
    subgraph "Business Logic Layer"
        H[Auth Service]
        I[JWT Service]
        J[Password Service]
        K[Company Filter Service]
    end
    
    subgraph "Data Access Layer"
        L[Empresa Repository]
        M[Admin User Repository]
        N[Session Repository]
        O[Audit Repository]
        P[Existing Repositories]
    end
    
    subgraph "Database Layer"
        Q[(PostgreSQL)]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    D --> H
    E --> H
    F --> H
    G --> K
    H --> I
    H --> J
    H --> L
    H --> M
    H --> N
    H --> O
    K --> P
    L --> Q
    M --> Q
    N --> Q
    O --> Q
    P --> Q
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth API
    participant M as Middleware
    participant DB as Database
    
    U->>F: Enter credentials
    F->>A: POST /auth/login
    A->>DB: Validate user
    DB-->>A: User data
    A->>A: Verify password (bcrypt)
    A->>A: Generate JWT tokens
    A->>DB: Create session
    A->>DB: Log audit event
    A-->>F: {access_token, refresh_token, user}
    F->>F: Store tokens in localStorage
    F->>F: Redirect to /dashboard
    
    Note over F,A: Subsequent Requests
    F->>A: GET /api/resource (with token)
    A->>M: Validate JWT
    M->>DB: Check session
    M->>M: Check user active
    M->>M: Apply company filter
    M-->>A: Authorized request
    A-->>F: Resource data
```

### Multi-Tenancy Architecture

```mermaid
graph TB
    subgraph "Superadmin View"
        SA[Superadmin User] --> ALL[All Companies Data]
        ALL --> E1[Empresa A]
        ALL --> E2[Empresa B]
        ALL --> E3[Empresa C]
    end
    
    subgraph "Admin View - Empresa A"
        AA[Admin User A] --> FA[Company Filter]
        FA --> DA[Only Empresa A Data]
        DA --> PA[Printers A]
        DA --> UA[Users A]
        DA --> CA[Counters A]
    end
    
    subgraph "Admin View - Empresa B"
        AB[Admin User B] --> FB[Company Filter]
        FB --> DB[Only Empresa B Data]
        DB --> PB[Printers B]
        DB --> UB[Users B]
        DB --> CB[Counters B]
    end
    
    style SA fill:#ff6b6b
    style AA fill:#4ecdc4
    style AB fill:#95e1d3
```


## Components and Interfaces

### Backend Components

#### 1. Authentication Service

**Responsabilidad**: Gestionar autenticación, generación de tokens, validación de credenciales

```python
class AuthService:
    """Service for authentication operations"""
    
    def login(self, username: str, password: str, ip_address: str, user_agent: str) -> LoginResponse:
        """
        Authenticate user and create session
        
        Args:
            username: Username
            password: Plain text password
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            LoginResponse with tokens and user info
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            AccountLockedError: If account is locked
            AccountDisabledError: If account is disabled
        """
        pass
    
    def logout(self, token: str) -> None:
        """Invalidate session"""
        pass
    
    def refresh_token(self, refresh_token: str) -> RefreshResponse:
        """Generate new access token from refresh token"""
        pass
    
    def validate_token(self, token: str) -> AdminUser:
        """Validate JWT and return user"""
        pass
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Change user password"""
        pass
```

#### 2. JWT Service

**Responsabilidad**: Generación y validación de tokens JWT

```python
class JWTService:
    """Service for JWT operations"""
    
    def create_access_token(self, user: AdminUser) -> str:
        """
        Create access token (30 min expiration)
        
        Payload:
            - user_id: int
            - username: str
            - rol: str
            - empresa_id: Optional[int]
            - exp: datetime (30 minutes)
            - iat: datetime
        """
        pass
    
    def create_refresh_token(self, user: AdminUser) -> str:
        """
        Create refresh token (7 days expiration)
        
        Payload:
            - user_id: int
            - type: "refresh"
            - exp: datetime (7 days)
            - iat: datetime
        """
        pass
    
    def decode_token(self, token: str) -> dict:
        """
        Decode and validate JWT
        
        Raises:
            InvalidTokenError: If signature is invalid
            ExpiredTokenError: If token is expired
        """
        pass
    
    def verify_signature(self, token: str) -> bool:
        """Verify JWT signature"""
        pass
```

#### 3. Password Service

**Responsabilidad**: Hashing y validación de contraseñas

```python
class PasswordService:
    """Service for password operations"""
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt (12 rounds)
        
        Args:
            password: Plain text password
            
        Returns:
            Bcrypt hash (60 characters)
        """
        pass
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        pass
    
    def validate_password_strength(self, password: str) -> ValidationResult:
        """
        Validate password meets requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        - At least 1 special character
        """
        pass
    
    def generate_temporary_password(self) -> str:
        """Generate secure random password (16 characters)"""
        pass
```

#### 4. Company Filter Service

**Responsabilidad**: Aplicar filtrado automático por empresa según rol

```python
class CompanyFilterService:
    """Service for automatic company filtering"""
    
    def apply_filter(self, query: Query, user: AdminUser) -> Query:
        """
        Apply company filter to SQLAlchemy query
        
        Logic:
            - If user.rol == "superadmin": No filter (return all)
            - If user.rol in ["admin", "viewer", "operator"]: Filter by user.empresa_id
        
        Args:
            query: SQLAlchemy query
            user: Authenticated user
            
        Returns:
            Filtered query
        """
        pass
    
    def validate_company_access(self, user: AdminUser, empresa_id: int) -> bool:
        """
        Validate if user can access empresa
        
        Returns:
            True if superadmin or empresa_id matches user.empresa_id
        """
        pass
    
    def enforce_company_on_create(self, user: AdminUser, data: dict) -> dict:
        """
        Enforce empresa_id on resource creation
        
        Logic:
            - If user.rol == "superadmin": Allow any empresa_id
            - If user.rol == "admin": Force empresa_id = user.empresa_id
        """
        pass
```


#### 5. Audit Service

**Responsabilidad**: Registrar todas las acciones administrativas

```python
class AuditService:
    """Service for audit logging"""
    
    def log_action(
        self,
        user: AdminUser,
        accion: str,
        modulo: str,
        resultado: str,
        entidad_tipo: Optional[str] = None,
        entidad_id: Optional[int] = None,
        detalles: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Create audit log entry
        
        Args:
            user: User performing action
            accion: Action name (login, logout, crear, editar, eliminar, etc.)
            modulo: Module name (auth, empresas, admin_users, printers, etc.)
            resultado: Result (exito, error, denegado)
            entidad_tipo: Entity type (empresa, admin_user, printer, etc.)
            entidad_id: Entity ID
            detalles: Additional details (JSON)
            ip_address: Client IP
            user_agent: Client user agent
        """
        pass
    
    def get_user_activity(self, user_id: int, limit: int = 100) -> List[AuditLog]:
        """Get recent activity for user"""
        pass
    
    def get_entity_history(self, entidad_tipo: str, entidad_id: int) -> List[AuditLog]:
        """Get audit history for specific entity"""
        pass
```

#### 6. Rate Limiter Service

**Responsabilidad**: Limitar requests para prevenir ataques

```python
class RateLimiterService:
    """Service for rate limiting"""
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> RateLimitResult:
        """
        Check if request is within rate limit
        
        Args:
            key: Unique key (e.g., IP address, user ID)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            RateLimitResult with allowed status and remaining count
        """
        pass
    
    def increment_counter(self, key: str, window_seconds: int) -> int:
        """Increment request counter"""
        pass
    
    def reset_counter(self, key: str) -> None:
        """Reset request counter"""
        pass
```

### Backend API Endpoints

#### Authentication Endpoints

```python
# POST /auth/login
Request:
{
    "username": "admin",
    "password": "SecurePass123!"
}

Response (200):
{
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
        }
    }
}

Errors:
- 401: Invalid credentials
- 403: Account locked or disabled
- 429: Too many requests

# POST /auth/logout
Headers:
    Authorization: Bearer {access_token}

Response (200):
{
    "success": true,
    "message": "Sesión cerrada exitosamente"
}

# POST /auth/refresh
Request:
{
    "refresh_token": "eyJhbGc..."
}

Response (200):
{
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
}

# GET /auth/me
Headers:
    Authorization: Bearer {access_token}

Response (200):
{
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
    "permisos": ["governance", "contadores", "cierres", "usuarios", "fleet"]
}

# POST /auth/change-password
Headers:
    Authorization: Bearer {access_token}

Request:
{
    "current_password": "OldPass123!",
    "new_password": "NewPass456!"
}

Response (200):
{
    "success": true,
    "message": "Contraseña actualizada exitosamente"
}
```


#### Empresa Endpoints (Superadmin only)

```python
# GET /empresas
Headers:
    Authorization: Bearer {access_token}

Query Params:
    page: int = 1
    page_size: int = 20
    search: Optional[str]

Response (200):
{
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
            "is_active": true,
            "created_at": "2026-01-15T10:30:00Z",
            "updated_at": "2026-03-20T14:20:00Z"
        }
    ],
    "total": 15,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
}

# POST /empresas
Headers:
    Authorization: Bearer {access_token}

Request:
{
    "razon_social": "Nueva Empresa S.A.S.",
    "nombre_comercial": "nueva-empresa",
    "nit": "900987654-3",
    "direccion": "Avenida 45 #12-34",
    "telefono": "+57 1 987 6543",
    "email": "info@nuevaempresa.com",
    "contacto_nombre": "María García",
    "contacto_cargo": "Directora Administrativa"
}

Response (201):
{
    "id": 16,
    "razon_social": "Nueva Empresa S.A.S.",
    "nombre_comercial": "nueva-empresa",
    ...
}

# GET /empresas/{id}
# PUT /empresas/{id}
# DELETE /empresas/{id} (soft delete)
```

#### Admin User Endpoints (Superadmin only)

```python
# GET /admin-users
Headers:
    Authorization: Bearer {access_token}

Query Params:
    page: int = 1
    page_size: int = 20
    search: Optional[str]
    rol: Optional[str]
    empresa_id: Optional[int]

Response (200):
{
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
            "is_active": true,
            "last_login": "2026-03-20T09:15:00Z",
            "created_at": "2026-01-20T11:00:00Z"
        }
    ],
    "total": 25,
    "page": 1,
    "page_size": 20,
    "total_pages": 2
}

# POST /admin-users
Headers:
    Authorization: Bearer {access_token}

Request:
{
    "username": "nuevo_admin",
    "password": "SecurePass123!",
    "nombre_completo": "Nuevo Administrador",
    "email": "nuevo@empresa.com",
    "rol": "admin",
    "empresa_id": 1
}

Response (201):
{
    "id": 26,
    "username": "nuevo_admin",
    "nombre_completo": "Nuevo Administrador",
    "email": "nuevo@empresa.com",
    "rol": "admin",
    "empresa_id": 1,
    "is_active": true,
    "created_at": "2026-03-20T15:30:00Z"
}

# GET /admin-users/{id}
# PUT /admin-users/{id}
# DELETE /admin-users/{id} (soft delete)
```

### Frontend Components

#### 1. Login Page Component

```typescript
interface LoginPageProps {}

interface LoginFormData {
    username: string;
    password: string;
    rememberMe: boolean;
}

const LoginPage: React.FC<LoginPageProps> = () => {
    const [formData, setFormData] = useState<LoginFormData>({
        username: '',
        password: '',
        rememberMe: false
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showPassword, setShowPassword] = useState(false);
    
    const handleSubmit = async (e: React.FormEvent) => {
        // Validate form
        // Call API /auth/login
        // Store tokens in localStorage
        // Redirect to /dashboard
    };
    
    return (
        // Login form UI
    );
};
```

#### 2. Protected Route Component

```typescript
interface ProtectedRouteProps {
    children: React.ReactNode;
    requiredRole?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
    children, 
    requiredRole 
}) => {
    const { user, isAuthenticated, loading } = useAuth();
    const navigate = useNavigate();
    
    useEffect(() => {
        if (!loading && !isAuthenticated) {
            navigate('/login');
        }
        
        if (requiredRole && user && !requiredRole.includes(user.rol)) {
            navigate('/unauthorized');
        }
    }, [isAuthenticated, loading, user, requiredRole]);
    
    if (loading) {
        return <LoadingSpinner />;
    }
    
    return isAuthenticated ? <>{children}</> : null;
};
```


#### 3. Auth Context Provider

```typescript
interface AuthContextType {
    user: AdminUser | null;
    isAuthenticated: boolean;
    loading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<AdminUser | null>(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        // Check if token exists in localStorage
        // Validate token with /auth/me
        // Set user if valid
        // Set up token refresh interval
    }, []);
    
    const login = async (username: string, password: string) => {
        const response = await authAPI.login(username, password);
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        setUser(response.user);
    };
    
    const logout = async () => {
        await authAPI.logout();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };
    
    const refreshToken = async () => {
        const refresh_token = localStorage.getItem('refresh_token');
        if (!refresh_token) throw new Error('No refresh token');
        
        const response = await authAPI.refresh(refresh_token);
        localStorage.setItem('access_token', response.access_token);
    };
    
    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, login, logout, refreshToken }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
};
```

#### 4. API Client with Interceptors

```typescript
import axios from 'axios';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor: Add token to all requests
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor: Handle 401 and refresh token
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        
        // If 401 and not already retried
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                const refresh_token = localStorage.getItem('refresh_token');
                const response = await axios.post('/auth/refresh', { refresh_token });
                
                localStorage.setItem('access_token', response.data.access_token);
                originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
                
                return apiClient(originalRequest);
            } catch (refreshError) {
                // Refresh failed, redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
);

export default apiClient;
```

#### 5. Empresas Management Component

```typescript
interface EmpresasPageProps {}

const EmpresasPage: React.FC<EmpresasPageProps> = () => {
    const [empresas, setEmpresas] = useState<Empresa[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [selectedEmpresa, setSelectedEmpresa] = useState<Empresa | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [page, setPage] = useState(1);
    
    useEffect(() => {
        loadEmpresas();
    }, [page, searchTerm]);
    
    const loadEmpresas = async () => {
        const response = await empresaAPI.getAll({ page, search: searchTerm });
        setEmpresas(response.items);
    };
    
    const handleCreate = () => {
        setSelectedEmpresa(null);
        setShowModal(true);
    };
    
    const handleEdit = (empresa: Empresa) => {
        setSelectedEmpresa(empresa);
        setShowModal(true);
    };
    
    const handleDelete = async (id: number) => {
        if (confirm('¿Está seguro de desactivar esta empresa?')) {
            await empresaAPI.delete(id);
            loadEmpresas();
        }
    };
    
    return (
        <div>
            <Header title="Gestión de Empresas" />
            <SearchBar value={searchTerm} onChange={setSearchTerm} />
            <Button onClick={handleCreate}>Nueva Empresa</Button>
            <EmpresasTable 
                empresas={empresas}
                onEdit={handleEdit}
                onDelete={handleDelete}
            />
            <Pagination page={page} onChange={setPage} />
            {showModal && (
                <EmpresaModal
                    empresa={selectedEmpresa}
                    onClose={() => setShowModal(false)}
                    onSave={loadEmpresas}
                />
            )}
        </div>
    );
};
```


## Data Models

### Database Schema

#### Entity Relationship Diagram

```mermaid
erDiagram
    empresas ||--o{ admin_users : "tiene"
    empresas ||--o{ printers : "posee"
    empresas ||--o{ users : "gestiona"
    admin_users ||--o{ admin_sessions : "crea"
    admin_users ||--o{ admin_audit_log : "registra"
    
    empresas {
        int id PK
        varchar razon_social UK
        varchar nombre_comercial UK
        varchar nit UK
        text direccion
        varchar telefono
        varchar email
        varchar contacto_nombre
        varchar contacto_cargo
        varchar logo_url
        jsonb config_json
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    admin_users {
        int id PK
        varchar username UK
        varchar password_hash
        varchar nombre_completo
        varchar email UK
        varchar rol
        int empresa_id FK
        boolean is_active
        timestamp created_at
        timestamp updated_at
        timestamp last_login
        int failed_login_attempts
        timestamp locked_until
    }
    
    admin_sessions {
        int id PK
        int admin_user_id FK
        varchar token UK
        varchar refresh_token UK
        varchar ip_address
        text user_agent
        timestamp expires_at
        timestamp refresh_expires_at
        timestamp created_at
        timestamp last_activity
    }
    
    admin_audit_log {
        int id PK
        int admin_user_id FK
        varchar accion
        varchar modulo
        varchar entidad_tipo
        int entidad_id
        jsonb detalles
        varchar resultado
        varchar ip_address
        text user_agent
        timestamp created_at
    }
    
    printers {
        int id PK
        int empresa_id FK
        varchar hostname
        varchar ip_address UK
        varchar location
        varchar status
        varchar detected_model
        varchar serial_number
        boolean has_color
        boolean has_scanner
        boolean has_fax
        timestamp created_at
        timestamp updated_at
    }
    
    users {
        int id PK
        int empresa_id FK
        varchar name
        varchar codigo_de_usuario
        varchar network_username
        text network_password_encrypted
        varchar smb_server
        int smb_port
        varchar smb_path
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
```

### Table Definitions

#### 1. empresas

```sql
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    razon_social VARCHAR(255) NOT NULL UNIQUE,
    nombre_comercial VARCHAR(50) NOT NULL UNIQUE,
    nit VARCHAR(20) UNIQUE,
    direccion TEXT,
    telefono VARCHAR(50),
    email VARCHAR(255),
    contacto_nombre VARCHAR(255),
    contacto_cargo VARCHAR(100),
    logo_url VARCHAR(500),
    config_json JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_razon_social_no_vacia CHECK (LENGTH(TRIM(razon_social)) > 0),
    CONSTRAINT chk_nombre_comercial_formato CHECK (nombre_comercial ~ '^[a-z0-9-]+$'),
    CONSTRAINT chk_email_formato CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_empresas_razon_social ON empresas(razon_social);
CREATE INDEX idx_empresas_nombre_comercial ON empresas(nombre_comercial);
CREATE INDEX idx_empresas_active ON empresas(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_empresas_config ON empresas USING gin(config_json);

COMMENT ON TABLE empresas IS 'Empresas/organizaciones del sistema (tenants)';
COMMENT ON COLUMN empresas.nombre_comercial IS 'Identificador único en formato kebab-case para URLs';
COMMENT ON COLUMN empresas.config_json IS 'Configuración: max_usuarios, max_impresoras, modulos_habilitados, etc.';
```

#### 2. admin_users

```sql
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    rol VARCHAR(20) NOT NULL,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_rol_valido CHECK (rol IN ('superadmin', 'admin', 'viewer', 'operator')),
    CONSTRAINT chk_superadmin_sin_empresa CHECK (
        (rol = 'superadmin' AND empresa_id IS NULL) OR
        (rol != 'superadmin' AND empresa_id IS NOT NULL)
    ),
    CONSTRAINT chk_email_formato CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_username_formato CHECK (username ~ '^[a-z0-9_-]{3,}$'),
    CONSTRAINT chk_password_hash_length CHECK (LENGTH(password_hash) >= 60)
);

CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_empresa_id ON admin_users(empresa_id);
CREATE INDEX idx_admin_users_rol ON admin_users(rol);
CREATE INDEX idx_admin_users_active ON admin_users(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE admin_users IS 'Usuarios administradores del sistema (para login)';
COMMENT ON COLUMN admin_users.rol IS 'Roles: superadmin (sin empresa), admin, viewer, operator';
COMMENT ON COLUMN admin_users.failed_login_attempts IS 'Contador de intentos fallidos (reset al login exitoso)';
COMMENT ON COLUMN admin_users.locked_until IS 'Cuenta bloqueada hasta esta fecha (por intentos fallidos)';
```


#### 3. admin_sessions

```sql
CREATE TABLE admin_sessions (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    refresh_token VARCHAR(500) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    refresh_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_expires_future CHECK (expires_at > created_at)
);

CREATE INDEX idx_sessions_admin_user_id ON admin_sessions(admin_user_id);
CREATE INDEX idx_sessions_token ON admin_sessions(token);
CREATE INDEX idx_sessions_expires ON admin_sessions(expires_at);
CREATE INDEX idx_sessions_active ON admin_sessions(admin_user_id, expires_at) 
WHERE expires_at > NOW();

COMMENT ON TABLE admin_sessions IS 'Sesiones activas de usuarios administradores (JWT tokens)';
COMMENT ON COLUMN admin_sessions.token IS 'Access token JWT (hash para búsqueda rápida)';
COMMENT ON COLUMN admin_sessions.refresh_token IS 'Refresh token JWT';
```

#### 4. admin_audit_log

```sql
CREATE TABLE admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL,
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    entidad_tipo VARCHAR(50),
    entidad_id INTEGER,
    detalles JSONB,
    resultado VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_resultado_valido CHECK (resultado IN ('exito', 'error', 'denegado'))
);

CREATE INDEX idx_audit_admin_user_id ON admin_audit_log(admin_user_id);
CREATE INDEX idx_audit_accion ON admin_audit_log(accion);
CREATE INDEX idx_audit_modulo ON admin_audit_log(modulo);
CREATE INDEX idx_audit_created_at ON admin_audit_log(created_at DESC);
CREATE INDEX idx_audit_entidad ON admin_audit_log(entidad_tipo, entidad_id);
CREATE INDEX idx_audit_detalles ON admin_audit_log USING gin(detalles);

COMMENT ON TABLE admin_audit_log IS 'Log de auditoría de todas las acciones de administradores';
COMMENT ON COLUMN admin_audit_log.detalles IS 'JSON con detalles de la acción (valores anteriores, nuevos, etc.)';
COMMENT ON COLUMN admin_audit_log.accion IS 'Acciones: login, logout, crear, editar, eliminar, exportar, ver';
```

### Migration Scripts

#### Migration 010: Create empresas table and normalize

```sql
-- Migration 010: Normalización de empresas
-- Fecha: 2026-03-20
-- Descripción: Crear tabla empresas y migrar campos VARCHAR

BEGIN;

-- 1. Crear tabla empresas
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    razon_social VARCHAR(255) NOT NULL UNIQUE,
    nombre_comercial VARCHAR(50) NOT NULL UNIQUE,
    nit VARCHAR(20) UNIQUE,
    direccion TEXT,
    telefono VARCHAR(50),
    email VARCHAR(255),
    contacto_nombre VARCHAR(255),
    contacto_cargo VARCHAR(100),
    logo_url VARCHAR(500),
    config_json JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_razon_social_no_vacia CHECK (LENGTH(TRIM(razon_social)) > 0),
    CONSTRAINT chk_nombre_comercial_formato CHECK (nombre_comercial ~ '^[a-z0-9-]+$'),
    CONSTRAINT chk_email_formato CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 2. Crear índices
CREATE INDEX idx_empresas_razon_social ON empresas(razon_social);
CREATE INDEX idx_empresas_nombre_comercial ON empresas(nombre_comercial);
CREATE INDEX idx_empresas_active ON empresas(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_empresas_config ON empresas USING gin(config_json);

-- 3. Crear trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_empresas_updated_at 
BEFORE UPDATE ON empresas
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 4. Insertar empresas únicas desde printers y users
INSERT INTO empresas (razon_social, nombre_comercial, is_active)
SELECT DISTINCT 
    COALESCE(empresa, 'Sin Asignar') as razon_social,
    LOWER(REGEXP_REPLACE(COALESCE(empresa, 'sin-asignar'), '[^a-zA-Z0-9]+', '-', 'g')) as nombre_comercial,
    TRUE as is_active
FROM (
    SELECT DISTINCT empresa FROM printers WHERE empresa IS NOT NULL
    UNION
    SELECT DISTINCT empresa FROM users WHERE empresa IS NOT NULL
) AS empresas_unicas
ON CONFLICT (razon_social) DO NOTHING;

-- 5. Agregar empresa_id a printers
ALTER TABLE printers ADD COLUMN empresa_id INTEGER;

UPDATE printers p
SET empresa_id = e.id
FROM empresas e
WHERE COALESCE(p.empresa, 'Sin Asignar') = e.razon_social;

ALTER TABLE printers 
    ALTER COLUMN empresa_id SET NOT NULL,
    ADD CONSTRAINT fk_printers_empresa 
        FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE RESTRICT;

CREATE INDEX idx_printers_empresa_id ON printers(empresa_id);

-- 6. Eliminar columna empresa antigua de printers
ALTER TABLE printers DROP COLUMN empresa;

-- 7. Agregar empresa_id a users
ALTER TABLE users ADD COLUMN empresa_id INTEGER;

UPDATE users u
SET empresa_id = e.id
FROM empresas e
WHERE COALESCE(u.empresa, 'Sin Asignar') = e.razon_social;

-- empresa_id puede ser NULL en users (usuarios sin empresa asignada)
ALTER TABLE users 
    ADD CONSTRAINT fk_users_empresa 
        FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE RESTRICT;

CREATE INDEX idx_users_empresa_id ON users(empresa_id);

ALTER TABLE users DROP COLUMN empresa;

-- 8. Comentarios
COMMENT ON TABLE empresas IS 'Empresas/organizaciones del sistema (tenants)';
COMMENT ON COLUMN empresas.nombre_comercial IS 'Identificador único en formato kebab-case para URLs';
COMMENT ON COLUMN empresas.config_json IS 'Configuración: max_usuarios, max_impresoras, modulos_habilitados, etc.';

COMMIT;
```


#### Migration 011: Create authentication tables

```sql
-- Migration 011: Tablas de autenticación
-- Fecha: 2026-03-20
-- Descripción: Crear tablas admin_users, admin_sessions, admin_audit_log

BEGIN;

-- 1. Crear tabla admin_users
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    rol VARCHAR(20) NOT NULL,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_rol_valido CHECK (rol IN ('superadmin', 'admin', 'viewer', 'operator')),
    CONSTRAINT chk_superadmin_sin_empresa CHECK (
        (rol = 'superadmin' AND empresa_id IS NULL) OR
        (rol != 'superadmin' AND empresa_id IS NOT NULL)
    ),
    CONSTRAINT chk_email_formato CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_username_formato CHECK (username ~ '^[a-z0-9_-]{3,}$'),
    CONSTRAINT chk_password_hash_length CHECK (LENGTH(password_hash) >= 60)
);

CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_empresa_id ON admin_users(empresa_id);
CREATE INDEX idx_admin_users_rol ON admin_users(rol);
CREATE INDEX idx_admin_users_active ON admin_users(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_admin_users_updated_at 
BEFORE UPDATE ON admin_users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 2. Crear tabla admin_sessions
CREATE TABLE admin_sessions (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    refresh_token VARCHAR(500) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    refresh_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_expires_future CHECK (expires_at > created_at)
);

CREATE INDEX idx_sessions_admin_user_id ON admin_sessions(admin_user_id);
CREATE INDEX idx_sessions_token ON admin_sessions(token);
CREATE INDEX idx_sessions_expires ON admin_sessions(expires_at);
CREATE INDEX idx_sessions_active ON admin_sessions(admin_user_id, expires_at) 
WHERE expires_at > NOW();

-- 3. Crear tabla admin_audit_log
CREATE TABLE admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL,
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    entidad_tipo VARCHAR(50),
    entidad_id INTEGER,
    detalles JSONB,
    resultado VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_resultado_valido CHECK (resultado IN ('exito', 'error', 'denegado'))
);

CREATE INDEX idx_audit_admin_user_id ON admin_audit_log(admin_user_id);
CREATE INDEX idx_audit_accion ON admin_audit_log(accion);
CREATE INDEX idx_audit_modulo ON admin_audit_log(modulo);
CREATE INDEX idx_audit_created_at ON admin_audit_log(created_at DESC);
CREATE INDEX idx_audit_entidad ON admin_audit_log(entidad_tipo, entidad_id);
CREATE INDEX idx_audit_detalles ON admin_audit_log USING gin(detalles);

-- 4. Insertar superadmin inicial
DO $$
DECLARE
    temp_password TEXT;
    password_hash TEXT;
BEGIN
    -- Generar contraseña temporal aleatoria
    temp_password := encode(gen_random_bytes(12), 'base64');
    
    -- Hashear contraseña (esto debe hacerse en Python con bcrypt, aquí es placeholder)
    -- En la implementación real, esto se hará desde Python
    password_hash := '$2b$12$placeholder_hash_to_be_replaced_by_python_script';
    
    INSERT INTO admin_users (
        username, 
        password_hash, 
        nombre_completo, 
        email, 
        rol, 
        empresa_id,
        is_active
    ) VALUES (
        'superadmin',
        password_hash,
        'Super Administrador',
        'admin@ricoh-suite.local',
        'superadmin',
        NULL,
        TRUE
    );
    
    RAISE NOTICE 'Superadmin creado. Contraseña temporal: %', temp_password;
    RAISE NOTICE 'IMPORTANTE: Cambiar contraseña en el primer login';
END $$;

-- 5. Comentarios
COMMENT ON TABLE admin_users IS 'Usuarios administradores del sistema (para login)';
COMMENT ON TABLE admin_sessions IS 'Sesiones activas de usuarios administradores (JWT tokens)';
COMMENT ON TABLE admin_audit_log IS 'Log de auditoría de todas las acciones de administradores';

COMMIT;
```

### SQLAlchemy Models

#### Empresa Model

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Empresa(Base):
    """Empresa/Tenant model"""
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(255), nullable=False, unique=True, index=True)
    nombre_comercial = Column(String(50), nullable=False, unique=True, index=True)
    nit = Column(String(20), unique=True, nullable=True)
    direccion = Column(Text, nullable=True)
    telefono = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    contacto_nombre = Column(String(255), nullable=True)
    contacto_cargo = Column(String(100), nullable=True)
    logo_url = Column(String(500), nullable=True)
    config_json = Column(JSONB, default={}, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    admin_users = relationship("AdminUser", back_populates="empresa")
    printers = relationship("Printer", back_populates="empresa")
    users = relationship("User", back_populates="empresa")

    def __repr__(self):
        return f"<Empresa(id={self.id}, razon_social='{self.razon_social}')>"
```


#### AdminUser Model

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class AdminUser(Base):
    """Admin user model for authentication"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    rol = Column(String(20), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    empresa = relationship("Empresa", back_populates="admin_users")
    sessions = relationship("AdminSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AdminAuditLog", back_populates="user")

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}', rol='{self.rol}')>"
    
    def is_superadmin(self) -> bool:
        return self.rol == "superadmin"
    
    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return self.locked_until > datetime.now(timezone.utc)
```

#### AdminSession Model

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class AdminSession(Base):
    """Admin session model for JWT token management"""
    __tablename__ = "admin_sessions"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), nullable=False, unique=True, index=True)
    refresh_token = Column(String(500), unique=True, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    refresh_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("AdminUser", back_populates="sessions")

    def __repr__(self):
        return f"<AdminSession(id={self.id}, user_id={self.admin_user_id})>"
    
    def is_expired(self) -> bool:
        return self.expires_at < datetime.now(timezone.utc)
```

#### AdminAuditLog Model

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class AdminAuditLog(Base):
    """Admin audit log model"""
    __tablename__ = "admin_audit_log"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, index=True)
    accion = Column(String(100), nullable=False, index=True)
    modulo = Column(String(50), nullable=False, index=True)
    entidad_tipo = Column(String(50), nullable=True, index=True)
    entidad_id = Column(Integer, nullable=True)
    detalles = Column(JSONB, nullable=True)
    resultado = Column(String(20), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("AdminUser", back_populates="audit_logs")

    def __repr__(self):
        return f"<AdminAuditLog(id={self.id}, accion='{self.accion}', resultado='{self.resultado}')>"
```

### Pydantic Schemas

#### Auth Schemas

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes
    user: "AdminUserResponse"

class RefreshRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str

class RefreshResponse(BaseModel):
    """Refresh token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800

class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
```


#### Empresa Schemas

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime

class EmpresaBase(BaseModel):
    """Base empresa schema"""
    razon_social: str = Field(..., min_length=1, max_length=255)
    nombre_comercial: str = Field(..., min_length=1, max_length=50)
    nit: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    contacto_nombre: Optional[str] = Field(None, max_length=255)
    contacto_cargo: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    
    @validator('nombre_comercial')
    def validate_nombre_comercial(cls, v):
        if not v.islower() or not all(c.isalnum() or c == '-' for c in v):
            raise ValueError('nombre_comercial must be lowercase alphanumeric with hyphens only')
        return v

class EmpresaCreate(EmpresaBase):
    """Schema for creating empresa"""
    pass

class EmpresaUpdate(BaseModel):
    """Schema for updating empresa"""
    razon_social: Optional[str] = Field(None, min_length=1, max_length=255)
    nit: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    contacto_nombre: Optional[str] = Field(None, max_length=255)
    contacto_cargo: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class EmpresaResponse(EmpresaBase):
    """Schema for empresa response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

#### AdminUser Schemas

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Literal
from datetime import datetime

class AdminUserBase(BaseModel):
    """Base admin user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    rol: Literal['superadmin', 'admin', 'viewer', 'operator']
    
    @validator('username')
    def validate_username(cls, v):
        if not v.islower() or not all(c.isalnum() or c in '_-' for c in v):
            raise ValueError('username must be lowercase alphanumeric with underscores/hyphens only')
        return v

class AdminUserCreate(AdminUserBase):
    """Schema for creating admin user"""
    password: str = Field(..., min_length=8)
    empresa_id: Optional[int] = None
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('empresa_id')
    def validate_empresa_id(cls, v, values):
        rol = values.get('rol')
        if rol == 'superadmin' and v is not None:
            raise ValueError('superadmin cannot have empresa_id')
        if rol != 'superadmin' and v is None:
            raise ValueError('non-superadmin must have empresa_id')
        return v

class AdminUserUpdate(BaseModel):
    """Schema for updating admin user"""
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    rol: Optional[Literal['superadmin', 'admin', 'viewer', 'operator']] = None
    empresa_id: Optional[int] = None
    is_active: Optional[bool] = None

class AdminUserResponse(AdminUserBase):
    """Schema for admin user response"""
    id: int
    empresa_id: Optional[int]
    empresa: Optional["EmpresaResponse"]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

## Correctness Properties

Before writing the correctness properties, I need to analyze the acceptance criteria from the requirements document to determine which are testable as properties, examples, or edge cases.


### Property Reflection

After analyzing all acceptance criteria, I've identified the following testable properties. Now I'll perform reflection to eliminate redundancy:

**Identified Properties:**
1. nombre_comercial format validation (kebab-case)
2. username format validation
3. email format validation
4. Password hashing with bcrypt
5. Password strength validation
6. API responses never contain password_hash
7. Password update generates new hash
8. Correct password verification
9. Failed login attempts reset on success
10. JWT token generation on successful login
11. Session creation on successful login
12. Audit log creation for login attempts
13. Refresh token generates new access token
14. Refresh token doesn't rotate
15. Invalid JWT signature rejection
16. last_activity update on authenticated requests
17. Superadmin sees all empresa data
18. Admin sees only their empresa data
19. Admin cannot access other empresa resources
20. Admin-created resources have correct empresa_id
21. Non-superadmin cannot access empresa endpoints
22. Duplicate razon_social rejection
23. Duplicate username/email rejection
24. Role-based empresa_id validation
25. User deactivation invalidates sessions
26. Password change invalidates other sessions

**Redundancy Analysis:**

- Properties 4 and 7 can be combined: "Password hashing always uses bcrypt and generates unique hashes"
- Properties 6 and 18 are identical: "API responses never contain password_hash" (keep one)
- Properties 17, 18, 19 can be combined into one comprehensive multi-tenancy property
- Properties 22 and 23 are similar uniqueness validations, but test different entities (keep both)
- Properties 11 and 12 both test side effects of login, but are distinct (session vs audit)
- Properties 25 and 26 both test session invalidation, can be combined

**Final Property List (after removing redundancy):**
1. Format validation (nombre_comercial, username, email)
2. Password hashing and uniqueness
3. Password strength validation
4. API responses never contain password_hash
5. Password verification
6. Failed login attempts management
7. Successful login creates tokens, session, and audit log
8. Refresh token behavior
9. JWT signature validation
10. Session activity tracking
11. Multi-tenancy data isolation
12. Role-based access control
13. Uniqueness constraints
14. Session invalidation on security events

Now I'll write the formal correctness properties:


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Format Validation Consistency

*For any* input string being validated as nombre_comercial, username, or email, the validation function should consistently accept valid formats and reject invalid formats according to the specified regex patterns.

**Validates: Requirements 1.3, 2.2, 2.3**

### Property 2: Password Hashing Uniqueness and Verification

*For any* plain text password, hashing it with bcrypt should produce a hash that: (a) is at least 60 characters long, (b) starts with "$2b$12$", (c) verifies correctly against the original password, and (d) produces a different hash when hashed again (salted uniqueness).

**Validates: Requirements 3.1, 3.4, 3.10**

### Property 3: Password Strength Requirements

*For any* password string, the validation function should reject it if it lacks any of: uppercase letter, lowercase letter, digit, special character, or is less than 8 characters; and accept it if it meets all requirements.

**Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6**

### Property 4: Password Hash Exclusion from API Responses

*For any* API endpoint that returns user data (AdminUser), the response JSON should never contain the field "password_hash" or its value.

**Validates: Requirements 3.9, 12.18**

### Property 5: Password Verification Correctness

*For any* stored password hash and input password, bcrypt verification should return true if and only if the input password matches the original password that was hashed.

**Validates: Requirements 6.7**

### Property 6: Failed Login Attempts Management

*For any* user account, after 5 consecutive failed login attempts, the account should be locked (locked_until set to NOW() + 15 minutes), and after a successful login, failed_login_attempts should be reset to 0.

**Validates: Requirements 6.8, 6.9, 6.10**

### Property 7: Successful Login Side Effects

*For any* successful login with valid credentials, the system should: (a) generate a valid access_token JWT with 30-minute expiration, (b) generate a valid refresh_token JWT with 7-day expiration, (c) create a record in admin_sessions, (d) update last_login timestamp, and (e) create an audit log entry with accion="login" and resultado="exito".

**Validates: Requirements 6.11, 6.12, 6.13, 6.14, 6.15**

### Property 8: Refresh Token Behavior

*For any* valid refresh_token, calling the refresh endpoint should: (a) return a new access_token with 30-minute expiration, (b) keep the same refresh_token unchanged, and (c) update last_activity in the session.

**Validates: Requirements 8.6, 8.10**

### Property 9: JWT Signature Validation

*For any* JWT token, if the signature is invalid (tampered or signed with wrong key), the validation should fail and return 401 error; if the signature is valid but the token is expired, it should return 401 error with "Token expirado" message.

**Validates: Requirements 9.6, 9.7, 9.8**

### Property 10: Session Activity Tracking

*For any* authenticated request with a valid token, the system should update the last_activity timestamp in the corresponding admin_sessions record to the current time.

**Validates: Requirements 9.16**

### Property 11: Multi-Tenancy Data Isolation

*For any* query to resources with empresa_id (printers, users, contadores, cierres), if the authenticated user has rol="superadmin", all records should be returned; if the user has rol="admin", only records where empresa_id matches the user's empresa_id should be returned; and if an admin attempts to access a resource with a different empresa_id, a 403 error should be returned.

**Validates: Requirements 10.2, 10.3, 10.4, 10.6**

### Property 12: Empresa ID Enforcement on Resource Creation

*For any* resource creation request (printer, user, contador) by an admin user, the system should automatically set empresa_id to the admin's empresa_id, regardless of what empresa_id was provided in the request.

**Validates: Requirements 10.9**

### Property 13: Role-Based Access Control for Empresa Endpoints

*For any* request to empresa management endpoints (/empresas/*), if the authenticated user's rol is not "superadmin", the system should return 403 error.

**Validates: Requirements 11.6**

### Property 14: Uniqueness Constraint Enforcement

*For any* attempt to create an empresa with duplicate razon_social or nombre_comercial, or an admin_user with duplicate username or email, the system should reject the request with an appropriate error indicating which field violates uniqueness.

**Validates: Requirements 11.7, 12.6, 12.7**

### Property 15: Role-Based Empresa ID Validation

*For any* admin_user creation or update, if rol="superadmin" then empresa_id must be NULL, and if rol in ["admin", "viewer", "operator"] then empresa_id must NOT be NULL; violations should be rejected with validation error.

**Validates: Requirements 2.6, 2.7, 12.10, 12.11**

### Property 16: Session Invalidation on Security Events

*For any* user account, when the user is deactivated (is_active set to FALSE) or changes their password, all active sessions for that user (except the current session in case of password change) should be deleted from admin_sessions.

**Validates: Requirements 12.16, 26.10**

### Property 17: Audit Log Immutability and Completeness

*For any* administrative action (login, logout, crear, editar, eliminar), an audit log entry should be created with the correct accion, modulo, resultado, and detalles; and once created, audit log entries should never be modified or deleted.

**Validates: Requirements 5.7, 5.10, 6.15, 6.16**


## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
    "detail": "Error message",
    "error_code": "ERROR_CODE",
    "timestamp": "2026-03-20T15:30:00Z"
}
```

### HTTP Status Codes

| Status Code | Usage |
|-------------|-------|
| 200 | Successful request |
| 201 | Resource created successfully |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (invalid/missing/expired token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Resource not found |
| 409 | Conflict (duplicate resource) |
| 422 | Unprocessable entity (validation error) |
| 429 | Too many requests (rate limit exceeded) |
| 500 | Internal server error |

### Error Codes and Messages

#### Authentication Errors (AUTH_*)

```python
AUTH_INVALID_CREDENTIALS = {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Credenciales inválidas",
    "status": 401
}

AUTH_ACCOUNT_LOCKED = {
    "code": "AUTH_ACCOUNT_LOCKED",
    "message": "Cuenta bloqueada temporalmente. Intente nuevamente en {minutes} minutos",
    "status": 403
}

AUTH_ACCOUNT_DISABLED = {
    "code": "AUTH_ACCOUNT_DISABLED",
    "message": "Cuenta desactivada. Contacte al administrador",
    "status": 403
}

AUTH_TOKEN_MISSING = {
    "code": "AUTH_TOKEN_MISSING",
    "message": "Token no proporcionado",
    "status": 401
}

AUTH_TOKEN_INVALID = {
    "code": "AUTH_TOKEN_INVALID",
    "message": "Token inválido",
    "status": 401
}

AUTH_TOKEN_EXPIRED = {
    "code": "AUTH_TOKEN_EXPIRED",
    "message": "Token expirado",
    "status": 401
}

AUTH_SESSION_INVALID = {
    "code": "AUTH_SESSION_INVALID",
    "message": "Sesión inválida",
    "status": 401
}

AUTH_REFRESH_TOKEN_INVALID = {
    "code": "AUTH_REFRESH_TOKEN_INVALID",
    "message": "Refresh token inválido o expirado",
    "status": 401
}
```

#### Authorization Errors (AUTHZ_*)

```python
AUTHZ_INSUFFICIENT_PERMISSIONS = {
    "code": "AUTHZ_INSUFFICIENT_PERMISSIONS",
    "message": "Permisos insuficientes para realizar esta acción",
    "status": 403
}

AUTHZ_EMPRESA_ACCESS_DENIED = {
    "code": "AUTHZ_EMPRESA_ACCESS_DENIED",
    "message": "Acceso denegado a recursos de otra empresa",
    "status": 403
}

AUTHZ_SUPERADMIN_REQUIRED = {
    "code": "AUTHZ_SUPERADMIN_REQUIRED",
    "message": "Esta acción requiere rol de superadmin",
    "status": 403
}
```

#### Validation Errors (VAL_*)

```python
VAL_PASSWORD_WEAK = {
    "code": "VAL_PASSWORD_WEAK",
    "message": "La contraseña no cumple con los requisitos de seguridad",
    "details": {
        "requirements": [
            "Mínimo 8 caracteres",
            "Al menos una mayúscula",
            "Al menos una minúscula",
            "Al menos un número",
            "Al menos un carácter especial"
        ]
    },
    "status": 400
}

VAL_PASSWORD_SAME = {
    "code": "VAL_PASSWORD_SAME",
    "message": "La nueva contraseña debe ser diferente de la actual",
    "status": 400
}

VAL_PASSWORD_INCORRECT = {
    "code": "VAL_PASSWORD_INCORRECT",
    "message": "Contraseña actual incorrecta",
    "status": 400
}

VAL_USERNAME_FORMAT = {
    "code": "VAL_USERNAME_FORMAT",
    "message": "Username debe contener solo letras minúsculas, números, guiones y guiones bajos",
    "status": 400
}

VAL_EMAIL_FORMAT = {
    "code": "VAL_EMAIL_FORMAT",
    "message": "Formato de email inválido",
    "status": 400
}

VAL_NOMBRE_COMERCIAL_FORMAT = {
    "code": "VAL_NOMBRE_COMERCIAL_FORMAT",
    "message": "nombre_comercial debe estar en formato kebab-case (minúsculas, números y guiones)",
    "status": 400
}
```

#### Resource Errors (RES_*)

```python
RES_NOT_FOUND = {
    "code": "RES_NOT_FOUND",
    "message": "{resource_type} no encontrado",
    "status": 404
}

RES_DUPLICATE = {
    "code": "RES_DUPLICATE",
    "message": "{field} ya existe",
    "status": 409
}

RES_HAS_DEPENDENCIES = {
    "code": "RES_HAS_DEPENDENCIES",
    "message": "No se puede eliminar {resource_type} porque tiene {dependency_type} activos",
    "status": 400
}
```

#### Rate Limiting Errors (RATE_*)

```python
RATE_LIMIT_EXCEEDED = {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Demasiados intentos. Intente nuevamente en {seconds} segundos",
    "status": 429,
    "headers": {
        "X-RateLimit-Limit": "5",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1679328600"
    }
}
```

### Error Handling Strategy

#### 1. Input Validation

```python
# Use Pydantic for automatic validation
from pydantic import BaseModel, validator

class LoginRequest(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v
```

#### 2. Business Logic Errors

```python
# Use custom exceptions
class AuthenticationError(Exception):
    def __init__(self, error_code: dict):
        self.error_code = error_code
        super().__init__(error_code['message'])

# In service layer
if not user:
    raise AuthenticationError(AUTH_INVALID_CREDENTIALS)
```

#### 3. Database Errors

```python
from sqlalchemy.exc import IntegrityError

try:
    db.add(empresa)
    db.commit()
except IntegrityError as e:
    if 'unique constraint' in str(e).lower():
        raise ResourceDuplicateError(field='razon_social')
    raise
```

#### 4. Global Exception Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=exc.error_code['status'],
        content={
            "detail": exc.error_code['message'],
            "error_code": exc.error_code['code'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
```

### Logging Strategy

#### Log Levels

- **DEBUG**: Detailed information for debugging (token validation steps, query details)
- **INFO**: General informational messages (successful login, resource created)
- **WARNING**: Warning messages (failed login attempt, rate limit approaching)
- **ERROR**: Error messages (authentication failed, database error)
- **CRITICAL**: Critical errors (database connection lost, service unavailable)

#### Log Format

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
)

# Example logs
logger.info(f"User {username} logged in successfully", extra={"request_id": request_id})
logger.warning(f"Failed login attempt for user {username} from IP {ip_address}")
logger.error(f"Database error: {str(e)}", exc_info=True)
```

#### Sensitive Data Handling

```python
# Never log passwords or tokens
logger.info(f"Login attempt for user {username}")  # ✅ Good
logger.info(f"Login with password {password}")     # ❌ Bad

# Mask sensitive data in logs
def mask_token(token: str) -> str:
    if len(token) < 10:
        return "***"
    return f"{token[:4]}...{token[-4:]}"

logger.debug(f"Validating token {mask_token(token)}")
```


## Testing Strategy

### Dual Testing Approach

This system requires both unit tests and property-based tests for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property-based tests**: Verify universal properties across all inputs through randomization

Both approaches are complementary and necessary. Unit tests catch concrete bugs and validate specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Property-Based Testing Configuration

**Library**: We will use **Hypothesis** for Python (backend) and **fast-check** for TypeScript (frontend)

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: sistema-autenticacion-empresas, Property {number}: {property_text}`

**Example Property Test**:

```python
from hypothesis import given, strategies as st
import pytest

# Feature: sistema-autenticacion-empresas, Property 2: Password Hashing Uniqueness and Verification
@given(password=st.text(min_size=8, max_size=100))
def test_password_hashing_uniqueness_and_verification(password):
    """
    For any plain text password, hashing it with bcrypt should produce a hash that:
    (a) is at least 60 characters long
    (b) starts with "$2b$12$"
    (c) verifies correctly against the original password
    (d) produces a different hash when hashed again (salted uniqueness)
    """
    from services.password_service import PasswordService
    
    service = PasswordService()
    
    # Hash the password
    hash1 = service.hash_password(password)
    hash2 = service.hash_password(password)
    
    # (a) Check length
    assert len(hash1) >= 60, "Hash should be at least 60 characters"
    
    # (b) Check prefix
    assert hash1.startswith("$2b$12$"), "Hash should start with $2b$12$"
    
    # (c) Verify correctness
    assert service.verify_password(password, hash1), "Hash should verify against original password"
    
    # (d) Check uniqueness (salted)
    assert hash1 != hash2, "Two hashes of same password should be different (salted)"
```

### Unit Testing Strategy

#### Backend Unit Tests

**Test Organization**:
```
backend/tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_auth/
│   ├── test_auth_service.py
│   ├── test_jwt_service.py
│   ├── test_password_service.py
│   └── test_auth_endpoints.py
├── test_empresa/
│   ├── test_empresa_service.py
│   └── test_empresa_endpoints.py
├── test_admin_user/
│   ├── test_admin_user_service.py
│   └── test_admin_user_endpoints.py
├── test_middleware/
│   ├── test_auth_middleware.py
│   └── test_company_filter.py
└── test_properties/            # Property-based tests
    ├── test_password_properties.py
    ├── test_validation_properties.py
    ├── test_multitenancy_properties.py
    └── test_session_properties.py
```

**Example Unit Tests**:

```python
# test_auth_service.py
import pytest
from services.auth_service import AuthService
from exceptions import AuthenticationError, AccountLockedError

def test_login_with_valid_credentials(db_session, test_user):
    """Test successful login with valid credentials"""
    service = AuthService(db_session)
    
    result = service.login(
        username="testuser",
        password="ValidPass123!",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )
    
    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.user.username == "testuser"
    
    # Verify session was created
    session = db_session.query(AdminSession).filter_by(
        admin_user_id=result.user.id
    ).first()
    assert session is not None
    
    # Verify audit log was created
    audit = db_session.query(AdminAuditLog).filter_by(
        admin_user_id=result.user.id,
        accion="login"
    ).first()
    assert audit is not None
    assert audit.resultado == "exito"

def test_login_with_invalid_password(db_session, test_user):
    """Test login fails with incorrect password"""
    service = AuthService(db_session)
    
    with pytest.raises(AuthenticationError) as exc_info:
        service.login(
            username="testuser",
            password="WrongPassword",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
    
    assert exc_info.value.error_code['code'] == "AUTH_INVALID_CREDENTIALS"
    
    # Verify failed_login_attempts was incremented
    user = db_session.query(AdminUser).filter_by(username="testuser").first()
    assert user.failed_login_attempts == 1

def test_account_locked_after_5_failed_attempts(db_session, test_user):
    """Test account is locked after 5 failed login attempts"""
    service = AuthService(db_session)
    
    # Make 5 failed attempts
    for i in range(5):
        with pytest.raises(AuthenticationError):
            service.login(
                username="testuser",
                password="WrongPassword",
                ip_address="192.168.1.1",
                user_agent="Mozilla/5.0"
            )
    
    # 6th attempt should raise AccountLockedError
    with pytest.raises(AccountLockedError) as exc_info:
        service.login(
            username="testuser",
            password="WrongPassword",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
    
    assert "bloqueada temporalmente" in str(exc_info.value)
    
    # Verify locked_until is set
    user = db_session.query(AdminUser).filter_by(username="testuser").first()
    assert user.locked_until is not None
    assert user.locked_until > datetime.now(timezone.utc)
```

**Example Integration Tests**:

```python
# test_auth_endpoints.py
from fastapi.testclient import TestClient

def test_login_endpoint_success(client: TestClient, test_user):
    """Test POST /auth/login with valid credentials"""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "ValidPass123!"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800
    assert data["user"]["username"] == "testuser"
    assert "password_hash" not in data["user"]  # Should never be returned

def test_login_endpoint_invalid_credentials(client: TestClient):
    """Test POST /auth/login with invalid credentials"""
    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "WrongPassword"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "AUTH_INVALID_CREDENTIALS"

def test_protected_endpoint_without_token(client: TestClient):
    """Test accessing protected endpoint without token"""
    response = client.get("/empresas")
    
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "AUTH_TOKEN_MISSING"

def test_protected_endpoint_with_valid_token(client: TestClient, auth_headers):
    """Test accessing protected endpoint with valid token"""
    response = client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "password_hash" not in data
```


#### Frontend Unit Tests

**Test Organization**:
```
frontend/src/tests/
├── auth/
│   ├── LoginPage.test.tsx
│   ├── AuthContext.test.tsx
│   └── ProtectedRoute.test.tsx
├── empresas/
│   ├── EmpresasPage.test.tsx
│   └── EmpresaModal.test.tsx
├── admin-users/
│   ├── AdminUsersPage.test.tsx
│   └── AdminUserModal.test.tsx
└── utils/
    ├── apiClient.test.ts
    └── validation.test.ts
```

**Example Frontend Tests**:

```typescript
// LoginPage.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginPage } from './LoginPage';
import { authAPI } from '../services/authAPI';

jest.mock('../services/authAPI');

describe('LoginPage', () => {
    it('should render login form', () => {
        render(<LoginPage />);
        
        expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
    });
    
    it('should call login API on form submit', async () => {
        const mockLogin = jest.fn().mockResolvedValue({
            access_token: 'token123',
            refresh_token: 'refresh123',
            user: { username: 'testuser', rol: 'admin' }
        });
        (authAPI.login as jest.Mock) = mockLogin;
        
        render(<LoginPage />);
        
        fireEvent.change(screen.getByLabelText(/username/i), {
            target: { value: 'testuser' }
        });
        fireEvent.change(screen.getByLabelText(/password/i), {
            target: { value: 'ValidPass123!' }
        });
        fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
        
        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('testuser', 'ValidPass123!');
        });
    });
    
    it('should display error message on login failure', async () => {
        const mockLogin = jest.fn().mockRejectedValue({
            response: { data: { detail: 'Credenciales inválidas' } }
        });
        (authAPI.login as jest.Mock) = mockLogin;
        
        render(<LoginPage />);
        
        fireEvent.change(screen.getByLabelText(/username/i), {
            target: { value: 'testuser' }
        });
        fireEvent.change(screen.getByLabelText(/password/i), {
            target: { value: 'wrong' }
        });
        fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
        
        await waitFor(() => {
            expect(screen.getByText(/credenciales inválidas/i)).toBeInTheDocument();
        });
    });
});
```

### Property-Based Tests

#### Backend Property Tests

```python
# test_validation_properties.py
from hypothesis import given, strategies as st
import pytest

# Feature: sistema-autenticacion-empresas, Property 1: Format Validation Consistency
@given(nombre_comercial=st.text(min_size=1, max_size=50))
def test_nombre_comercial_validation_consistency(nombre_comercial):
    """
    For any input string being validated as nombre_comercial,
    the validation should consistently accept valid kebab-case formats
    and reject invalid formats.
    """
    from services.validation_service import ValidationService
    
    service = ValidationService()
    is_valid = service.validate_nombre_comercial(nombre_comercial)
    
    # Valid format: lowercase alphanumeric with hyphens
    expected_valid = (
        nombre_comercial.islower() and
        all(c.isalnum() or c == '-' for c in nombre_comercial) and
        not nombre_comercial.startswith('-') and
        not nombre_comercial.endswith('-')
    )
    
    assert is_valid == expected_valid, \
        f"Validation inconsistent for '{nombre_comercial}': got {is_valid}, expected {expected_valid}"

# Feature: sistema-autenticacion-empresas, Property 3: Password Strength Requirements
@given(password=st.text(min_size=1, max_size=100))
def test_password_strength_validation(password):
    """
    For any password string, the validation should reject it if it lacks
    any required component, and accept it if it meets all requirements.
    """
    from services.password_service import PasswordService
    
    service = PasswordService()
    result = service.validate_password_strength(password)
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    is_long_enough = len(password) >= 8
    
    expected_valid = has_upper and has_lower and has_digit and has_special and is_long_enough
    
    assert result.is_valid == expected_valid, \
        f"Password validation inconsistent for '{password}': got {result.is_valid}, expected {expected_valid}"

# Feature: sistema-autenticacion-empresas, Property 11: Multi-Tenancy Data Isolation
@given(
    user_rol=st.sampled_from(['superadmin', 'admin']),
    user_empresa_id=st.integers(min_value=1, max_value=10),
    resource_empresa_id=st.integers(min_value=1, max_value=10)
)
def test_multitenancy_data_isolation(user_rol, user_empresa_id, resource_empresa_id, db_session):
    """
    For any query to resources with empresa_id, superadmin should see all records,
    admin should only see records from their empresa, and admin should get 403
    when accessing other empresa resources.
    """
    from services.company_filter_service import CompanyFilterService
    from models import AdminUser, Printer
    
    # Create test user
    user = AdminUser(
        username="testuser",
        rol=user_rol,
        empresa_id=None if user_rol == 'superadmin' else user_empresa_id
    )
    
    # Create test printer
    printer = Printer(
        hostname="test-printer",
        ip_address="192.168.1.100",
        empresa_id=resource_empresa_id
    )
    db_session.add(printer)
    db_session.commit()
    
    service = CompanyFilterService()
    
    # Test query filtering
    query = db_session.query(Printer)
    filtered_query = service.apply_filter(query, user)
    results = filtered_query.all()
    
    if user_rol == 'superadmin':
        # Superadmin should see all printers
        assert len(results) > 0
    else:
        # Admin should only see printers from their empresa
        for printer in results:
            assert printer.empresa_id == user_empresa_id
    
    # Test access validation
    can_access = service.validate_company_access(user, resource_empresa_id)
    
    if user_rol == 'superadmin':
        assert can_access == True
    else:
        assert can_access == (user_empresa_id == resource_empresa_id)
```

#### Frontend Property Tests

```typescript
// validation.properties.test.ts
import fc from 'fast-check';
import { validateNombreComercial, validateUsername, validateEmail } from '../utils/validation';

// Feature: sistema-autenticacion-empresas, Property 1: Format Validation Consistency
describe('Format Validation Properties', () => {
    it('should consistently validate nombre_comercial format', () => {
        fc.assert(
            fc.property(
                fc.string({ minLength: 1, maxLength: 50 }),
                (nombreComercial) => {
                    const isValid = validateNombreComercial(nombreComercial);
                    
                    // Valid format: lowercase alphanumeric with hyphens
                    const expectedValid = (
                        nombreComercial === nombreComercial.toLowerCase() &&
                        /^[a-z0-9-]+$/.test(nombreComercial) &&
                        !nombreComercial.startsWith('-') &&
                        !nombreComercial.endsWith('-')
                    );
                    
                    expect(isValid).toBe(expectedValid);
                }
            ),
            { numRuns: 100 }
        );
    });
    
    it('should consistently validate username format', () => {
        fc.assert(
            fc.property(
                fc.string({ minLength: 1, maxLength: 100 }),
                (username) => {
                    const isValid = validateUsername(username);
                    
                    // Valid format: lowercase alphanumeric with underscores/hyphens, min 3 chars
                    const expectedValid = (
                        username.length >= 3 &&
                        username === username.toLowerCase() &&
                        /^[a-z0-9_-]+$/.test(username)
                    );
                    
                    expect(isValid).toBe(expectedValid);
                }
            ),
            { numRuns: 100 }
        );
    });
});
```

### Test Coverage Goals

- **Unit Test Coverage**: Minimum 80% code coverage
- **Property Test Coverage**: All 17 correctness properties must have corresponding property tests
- **Integration Test Coverage**: All API endpoints must have integration tests
- **E2E Test Coverage**: Critical user flows (login, empresa management, user management)

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov hypothesis
      - name: Run unit tests
        run: pytest tests/ --cov=. --cov-report=xml
      - name: Run property tests
        run: pytest tests/test_properties/ -v
      - name: Upload coverage
        uses: codecov/codecov-action@v2
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '20'
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Manual Testing Checklist

#### Authentication Flow
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Login with locked account
- [ ] Login with disabled account
- [ ] Logout
- [ ] Token refresh
- [ ] Token expiration handling
- [ ] Password change

#### Multi-Tenancy
- [ ] Superadmin sees all empresas
- [ ] Admin sees only their empresa data
- [ ] Admin cannot access other empresa resources
- [ ] Admin-created resources have correct empresa_id

#### Empresa Management
- [ ] Create empresa
- [ ] Edit empresa
- [ ] Deactivate empresa
- [ ] Cannot delete empresa with active resources
- [ ] Duplicate razon_social rejected

#### Admin User Management
- [ ] Create admin user
- [ ] Create superadmin user
- [ ] Edit admin user
- [ ] Deactivate admin user
- [ ] Duplicate username/email rejected
- [ ] Role-based empresa_id validation

#### Security
- [ ] Rate limiting on login endpoint
- [ ] HTTPS in production
- [ ] CORS configuration
- [ ] Audit logs created for all actions
- [ ] Password hash never returned in API responses


## Implementation Plan

### Phase 1: Database Migration (Week 1)

**Goal**: Normalize empresa data and create authentication tables

**Tasks**:
1. Create backup of production database
2. Test migration scripts in development environment
3. Create migration 010: empresas table and normalization
4. Create migration 011: authentication tables (admin_users, admin_sessions, admin_audit_log)
5. Create initial superadmin user with temporary password
6. Verify data integrity after migration
7. Update SQLAlchemy models
8. Run tests to ensure existing functionality still works

**Deliverables**:
- Migration scripts (010, 011)
- Updated SQLAlchemy models
- Migration verification report

### Phase 2: Backend Authentication (Week 2-3)

**Goal**: Implement authentication services and endpoints

**Tasks**:
1. Implement PasswordService (bcrypt hashing, validation)
2. Implement JWTService (token generation, validation)
3. Implement AuthService (login, logout, refresh, change password)
4. Implement AuditService (audit logging)
5. Implement RateLimiterService (rate limiting)
6. Create authentication endpoints (/auth/login, /auth/logout, /auth/refresh, /auth/me, /auth/change-password)
7. Create authentication middleware
8. Write unit tests for all services
9. Write property-based tests for password and JWT properties
10. Write integration tests for authentication endpoints

**Deliverables**:
- Authentication services
- Authentication endpoints
- Middleware
- Comprehensive test suite (80%+ coverage)

### Phase 3: Backend Multi-Tenancy (Week 3-4)

**Goal**: Implement company filtering and role-based access control

**Tasks**:
1. Implement CompanyFilterService (automatic filtering)
2. Create role-based access control decorator (@require_role)
3. Update existing endpoints to apply company filtering
4. Create empresa endpoints (/empresas/*)
5. Create admin_user endpoints (/admin-users/*)
6. Write unit tests for company filtering
7. Write property-based tests for multi-tenancy properties
8. Write integration tests for empresa and admin_user endpoints

**Deliverables**:
- CompanyFilterService
- Role-based access control
- Empresa and admin_user endpoints
- Updated existing endpoints with filtering
- Comprehensive test suite

### Phase 4: Frontend Authentication (Week 4-5)

**Goal**: Implement login page and authentication context

**Tasks**:
1. Create LoginPage component
2. Create AuthContext and AuthProvider
3. Create ProtectedRoute component
4. Implement API client with interceptors (token injection, refresh)
5. Update routing to use ProtectedRoute
6. Create Navbar with user info and logout
7. Write unit tests for authentication components
8. Write E2E tests for login flow

**Deliverables**:
- Login page
- Authentication context
- Protected routes
- API client with interceptors
- Comprehensive test suite

### Phase 5: Frontend Multi-Tenancy (Week 5-6)

**Goal**: Implement empresa and admin user management

**Tasks**:
1. Create EmpresasPage component
2. Create EmpresaModal component (create/edit)
3. Create AdminUsersPage component
4. Create AdminUserModal component (create/edit)
5. Update existing modules to show empresa filter
6. Add empresa selector for superadmin
7. Write unit tests for all components
8. Write E2E tests for empresa and admin user management

**Deliverables**:
- Empresa management module
- Admin user management module
- Updated existing modules with empresa context
- Comprehensive test suite

### Phase 6: Security Hardening (Week 6)

**Goal**: Implement security features and conduct security audit

**Tasks**:
1. Implement rate limiting on all authentication endpoints
2. Configure CORS for production
3. Set up HTTPS redirect in production
4. Add security headers (HSTS, X-Content-Type-Options, etc.)
5. Conduct security audit
6. Perform penetration testing
7. Fix any security issues found
8. Document security configuration

**Deliverables**:
- Rate limiting implementation
- CORS configuration
- HTTPS configuration
- Security headers
- Security audit report
- Penetration testing report

### Phase 7: Documentation and Deployment (Week 7)

**Goal**: Complete documentation and deploy to production

**Tasks**:
1. Update API documentation (Swagger/OpenAPI)
2. Write user guide for admin users
3. Write deployment guide
4. Create runbook for common operations
5. Deploy to staging environment
6. Conduct user acceptance testing (UAT)
7. Deploy to production
8. Monitor for issues
9. Train users

**Deliverables**:
- Complete API documentation
- User guide
- Deployment guide
- Runbook
- Production deployment
- Training materials

## Deployment Considerations

### Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/ricoh_fleet
SECRET_KEY=your-secret-key-min-32-chars
REFRESH_SECRET_KEY=your-refresh-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=https://app.ricoh-suite.com,https://admin.ricoh-suite.com
RATE_LIMIT_LOGIN=5
RATE_LIMIT_WINDOW=60
ENVIRONMENT=production

# Frontend (.env)
VITE_API_URL=https://api.ricoh-suite.com
VITE_ENVIRONMENT=production
```

### Database Backup Strategy

1. **Before Migration**: Full backup of database
2. **Daily Backups**: Automated daily backups at 2 AM
3. **Retention**: Keep backups for 30 days
4. **Testing**: Test restore procedure monthly

### Monitoring and Alerting

**Metrics to Monitor**:
- Failed login attempts per minute
- Active sessions count
- Token refresh rate
- API response times
- Database connection pool usage
- Error rate by endpoint

**Alerts**:
- Failed login attempts > 100/minute (potential attack)
- Error rate > 5% (system issue)
- Database connection pool > 80% (scaling needed)
- Disk space < 20% (cleanup needed)

### Rollback Plan

If issues are discovered after deployment:

1. **Immediate**: Revert to previous version using Docker image tag
2. **Database**: Restore from backup if database changes are problematic
3. **Communication**: Notify users of rollback and expected downtime
4. **Investigation**: Analyze logs to identify root cause
5. **Fix**: Develop fix in development environment
6. **Retest**: Thoroughly test fix before redeployment

### Performance Optimization

**Database**:
- Ensure all foreign keys have indexes
- Use connection pooling (10-20 connections)
- Enable query logging in development to identify slow queries
- Consider read replicas for reporting queries

**Backend**:
- Use async/await for I/O operations
- Implement caching for frequently accessed data (Redis)
- Use database connection pooling
- Optimize JWT validation (cache public keys)

**Frontend**:
- Implement code splitting
- Lazy load routes
- Use React.memo for expensive components
- Implement virtual scrolling for large lists

## Security Considerations

### OWASP Top 10 Mitigation

1. **Injection**: Use parameterized queries (SQLAlchemy ORM)
2. **Broken Authentication**: Implement secure JWT, bcrypt, rate limiting
3. **Sensitive Data Exposure**: Never return password_hash, use HTTPS
4. **XML External Entities**: Not applicable (no XML processing)
5. **Broken Access Control**: Implement role-based access control, company filtering
6. **Security Misconfiguration**: Use security headers, disable debug in production
7. **Cross-Site Scripting (XSS)**: Sanitize inputs, use React (auto-escaping)
8. **Insecure Deserialization**: Validate all inputs with Pydantic
9. **Using Components with Known Vulnerabilities**: Keep dependencies updated
10. **Insufficient Logging & Monitoring**: Implement comprehensive audit logging

### Additional Security Measures

**Password Policy**:
- Minimum 8 characters
- Require uppercase, lowercase, number, special character
- Hash with bcrypt (12 rounds)
- Never store plain text passwords

**Session Management**:
- Short-lived access tokens (30 minutes)
- Long-lived refresh tokens (7 days)
- Invalidate sessions on logout
- Invalidate all sessions on password change

**Rate Limiting**:
- Login: 5 attempts per minute per IP
- Refresh: 10 attempts per minute per user
- API endpoints: 100 requests per minute per user

**Audit Logging**:
- Log all authentication events
- Log all administrative actions
- Include IP address and user agent
- Store logs immutably (no updates/deletes)

**HTTPS**:
- Require HTTPS in production
- Redirect HTTP to HTTPS
- Use HSTS header
- Use valid SSL certificate

## Maintenance and Operations

### Regular Maintenance Tasks

**Daily**:
- Monitor error logs
- Check failed login attempts
- Verify backup completion

**Weekly**:
- Review audit logs for suspicious activity
- Check disk space usage
- Review performance metrics

**Monthly**:
- Update dependencies
- Review and rotate logs
- Test backup restore procedure
- Review user access and remove inactive users

**Quarterly**:
- Security audit
- Performance review
- Capacity planning
- User training refresher

### Common Operations

**Create Superadmin User**:
```python
from services.password_service import PasswordService
from models import AdminUser
from db.database import SessionLocal

db = SessionLocal()
password_service = PasswordService()

user = AdminUser(
    username="newsuperadmin",
    password_hash=password_service.hash_password("TempPass123!"),
    nombre_completo="New Super Admin",
    email="newsuperadmin@ricoh-suite.com",
    rol="superadmin",
    empresa_id=None,
    is_active=True
)

db.add(user)
db.commit()
print(f"Superadmin created: {user.username}")
```

**Reset User Password**:
```python
from services.password_service import PasswordService
from models import AdminUser
from db.database import SessionLocal

db = SessionLocal()
password_service = PasswordService()

user = db.query(AdminUser).filter_by(username="targetuser").first()
if user:
    new_password = password_service.generate_temporary_password()
    user.password_hash = password_service.hash_password(new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    print(f"Password reset for {user.username}: {new_password}")
```

**Clean Expired Sessions**:
```python
from models import AdminSession
from db.database import SessionLocal
from datetime import datetime, timezone

db = SessionLocal()

deleted = db.query(AdminSession).filter(
    AdminSession.expires_at < datetime.now(timezone.utc)
).delete()

db.commit()
print(f"Deleted {deleted} expired sessions")
```

## Conclusion

This design document provides a comprehensive blueprint for implementing a secure, scalable authentication and multi-tenancy system for Ricoh Suite. The system will transform the application from an unauthenticated single-tenant system to a secure multi-tenant platform with role-based access control.

Key features include:
- Normalized empresa data with referential integrity
- Secure JWT-based authentication with bcrypt password hashing
- Complete data isolation between empresas
- Role-based access control (superadmin, admin, viewer, operator)
- Comprehensive audit logging
- Rate limiting and security hardening
- Property-based testing for correctness guarantees

The implementation plan spans 7 weeks and includes database migration, backend development, frontend development, security hardening, and deployment. The system is designed to be maintainable, scalable, and secure, following industry best practices and OWASP guidelines.

---

**Document Version**: 1.0  
**Created**: 2026-03-19  
**Feature**: sistema-autenticacion-empresas  
**Workflow**: requirements-first  
**Status**: Ready for implementation

# Diseño de Corrección de Vulnerabilidades de Seguridad

## Overview

Este diseño especifica las correcciones técnicas para 11 vulnerabilidades de seguridad identificadas en la auditoría del sistema Ricoh Equipment Management. Las vulnerabilidades se organizan en tres categorías: gestión de secretos y configuración (4 vulnerabilidades), exposición de información sensible en logs (3 vulnerabilidades), y configuración de seguridad permisiva (4 vulnerabilidades).

El enfoque de corrección es incremental y preserva toda la funcionalidad existente del sistema. Cada corrección se implementa de forma que:
- Rechaza configuraciones inseguras con mensajes claros
- Mantiene compatibilidad con configuraciones válidas existentes
- No rompe flujos de autenticación, encriptación o integración con impresoras
- Proporciona mensajes de error instructivos para facilitar la configuración correcta

## Glossary

- **Bug_Condition (C)**: Condición que identifica configuraciones inseguras o exposición de datos sensibles
- **Property (P)**: Comportamiento esperado después de la corrección - rechazo de configuraciones inseguras con mensajes instructivos
- **Preservation**: Funcionalidad existente que debe mantenerse sin cambios - autenticación, encriptación, integración con impresoras
- **ENCRYPTION_KEY**: Clave Fernet (AES-128) para encriptar datos sensibles en base de datos (contraseñas de red, credenciales)
- **SECRET_KEY**: Clave para firmar tokens JWT, debe tener alta entropía
- **wimToken**: Token de sesión web usado por impresoras Ricoh para prevenir CSRF
- **Entropía**: Medida de complejidad de una clave basada en variedad de caracteres (mayúsculas, minúsculas, dígitos, especiales)
- **Redis**: Sistema de almacenamiento en memoria distribuido para tokens CSRF y rate limiting en despliegues multi-instancia

## Bug Details

### Bug Condition

Las vulnerabilidades se manifiestan en tres escenarios principales:


**1. Configuración de Secretos Insegura**: El sistema acepta o genera configuraciones de secretos que comprometen la seguridad de datos encriptados y tokens JWT.

**2. Exposición de Información Sensible**: Los logs y la consola exponen tokens JWT, contraseñas temporales y wimTokens en texto plano o parcialmente enmascarados de forma insuficiente.

**3. Configuración de Seguridad Permisiva**: El sistema usa configuraciones por defecto que permiten ataques CSRF, CORS permisivo, y almacenamiento en memoria que no funciona en producción multi-instancia.

**Formal Specification:**
```
FUNCTION isBugCondition_SecretConfig(config)
  INPUT: config of type SystemConfiguration
  OUTPUT: boolean
  
  RETURN (
    config.ENCRYPTION_KEY = NULL OR
    config.SECRET_KEY.length < 32 OR
    NOT hasMinimumEntropy(config.SECRET_KEY, min_categories=3) OR
    config.RICOH_ADMIN_PASSWORD = "" OR
    config.DATABASE_URL contains "ricoh_admin:ricoh_secure_2024"
  )
END FUNCTION

FUNCTION isBugCondition_SensitiveExposure(logEntry)
  INPUT: logEntry of type LogEntry
  OUTPUT: boolean
  
  RETURN (
    (logEntry.contains_jwt_token AND logEntry.exposed_chars > 8) OR
    (logEntry.contains_password AND logEntry.format = "plaintext") OR
    (logEntry.contains_wimToken AND logEntry.exposed_chars > 8)
  )
END FUNCTION

FUNCTION isBugCondition_PermissiveConfig(securityConfig)
  INPUT: securityConfig of type SecurityConfiguration
  OUTPUT: boolean
  
  RETURN (
    securityConfig.CORS.allowMethods = ["*"] OR
    securityConfig.CORS.allowHeaders = ["*"] OR
    (securityConfig.environment = "production" AND securityConfig.CSRF.enabled = false) OR
    securityConfig.CSRF.storage = "memory" OR
    securityConfig.rateLimit.storage = "memory"
  )
END FUNCTION

FUNCTION hasMinimumEntropy(key, min_categories)
  INPUT: key of type string, min_categories of type integer
  OUTPUT: boolean
  
  has_upper ← key contains uppercase letters
  has_lower ← key contains lowercase letters
  has_digit ← key contains digits
  has_special ← key contains special characters
  
  categories_count ← count(has_upper, has_lower, has_digit, has_special)
  
  RETURN categories_count >= min_categories
END FUNCTION
```

### Examples

**Ejemplo 1: ENCRYPTION_KEY no configurada en desarrollo**
```python
# Configuración actual (vulnerable)
os.environ["ENVIRONMENT"] = "development"
os.environ.pop("ENCRYPTION_KEY", None)

# Comportamiento actual: Genera clave temporal
# WARNING: ENCRYPTION_KEY no configurada, generando clave temporal
# Clave temporal generada: gAAAAABh...

# Comportamiento esperado: Rechazar con error instructivo
# ValueError: ENCRYPTION_KEY must be set in all environments.
# Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

**Ejemplo 2: SECRET_KEY con baja entropía**
```python
# Configuración actual (vulnerable)
os.environ["SECRET_KEY"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # 32 chars, solo minúsculas

# Comportamiento actual: Acepta la clave
# Token JWT generado exitosamente

# Comportamiento esperado: Rechazar con error instructivo
# ValueError: SECRET_KEY has insufficient entropy. Must contain at least 3 of: uppercase, lowercase, digits, special characters
```

**Ejemplo 3: Token JWT en logs**
```python
# Log actual (vulnerable)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
logger.info(f"Token: {token[:20]}...")
# Output: Token: eyJhbGciOiJIUzI1NiIsI...

# Log esperado (seguro)
logger.info(f"Token: {token[:4]}...{token[-4:]}")
# Output: Token: eyJh...R8U
```

**Ejemplo 4: CORS permisivo**
```python
# Configuración actual (vulnerable)
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Comportamiento esperado (restrictivo)
app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "X-Request-ID"]
)
```

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Encriptación y desencriptación de datos sensibles con ENCRYPTION_KEY válida debe continuar funcionando
- Generación y validación de tokens JWT con SECRET_KEY válida debe continuar funcionando
- Autenticación con impresoras Ricoh usando credenciales válidas debe continuar funcionando
- Procesamiento de peticiones CORS de orígenes permitidos debe continuar funcionando
- Validación de tokens CSRF cuando están habilitados debe continuar funcionando
- Rate limiting de peticiones legítimas debe continuar funcionando
- Registro de eventos de auditoría debe continuar funcionando

**Scope:**
Todas las configuraciones válidas y operaciones con datos no sensibles deben ser completamente no afectadas por estas correcciones. Esto incluye:
- Configuraciones con ENCRYPTION_KEY y SECRET_KEY válidas
- Logs que no contienen información sensible
- Peticiones HTTP dentro de límites de rate limiting
- Operaciones CRUD en base de datos
- Integración con impresoras Ricoh usando credenciales configuradas

## Hypothesized Root Cause

Basado en el análisis de la auditoría y el código, las causas raíz son:

1. **Configuración Permisiva en Desarrollo**: El código permite generar claves temporales en modo desarrollo para facilitar el desarrollo local, pero esto causa pérdida de datos al reiniciar y puede filtrarse a producción.

2. **Validación Insuficiente de Entropía**: La validación de SECRET_KEY solo verifica longitud mínima, no la complejidad de la clave, permitiendo claves débiles como "aaaaaaaa...".

3. **Logging de Debugging No Sanitizado**: Los logs de debugging imprimen tokens parciales para facilitar troubleshooting, pero exponen suficiente información para ataques.

4. **Configuraciones por Defecto Inseguras**: CORS, CSRF y rate limiting usan configuraciones permisivas por defecto para facilitar desarrollo, pero estas configuraciones no son apropiadas para producción.

5. **Almacenamiento en Memoria**: CSRF y rate limiting usan diccionarios en memoria por simplicidad, pero esto no funciona en despliegues distribuidos con múltiples instancias.

6. **Credenciales Hardcodeadas**: DATABASE_URL y RICOH_ADMIN_PASSWORD tienen valores por defecto hardcodeados que pueden usarse accidentalmente en producción.

## Correctness Properties

Property 1: Bug Condition - Rechazo de Configuración Insegura de Secretos

_For any_ configuración del sistema donde ENCRYPTION_KEY no está configurada, SECRET_KEY tiene baja entropía, RICOH_ADMIN_PASSWORD está vacía, o DATABASE_URL contiene credenciales hardcodeadas, el sistema corregido SHALL rechazar la configuración con un ValueError que incluye instrucciones claras para generar o configurar el secreto correctamente.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: Bug Condition - Enmascaramiento de Información Sensible

_For any_ entrada de log que contiene tokens JWT, contraseñas, o wimTokens, el sistema corregido SHALL enmascarar la información sensible mostrando solo los primeros 4 y últimos 4 caracteres (formato: XXXX...YYYY), o en el caso de contraseñas, solo la longitud.

**Validates: Requirements 2.5, 2.6, 2.7**

Property 3: Bug Condition - Configuración Restrictiva de Seguridad

_For any_ configuración de seguridad donde CORS permite todos los métodos/headers, CSRF está deshabilitada en producción, o el almacenamiento es en memoria, el sistema corregido SHALL usar configuraciones restrictivas con listas explícitas de métodos/headers permitidos, CSRF habilitada por defecto en producción, y Redis como backend de almacenamiento distribuido.

**Validates: Requirements 2.8, 2.9, 2.10, 2.11**

Property 4: Preservation - Funcionalidad Existente con Configuración Válida

_For any_ configuración válida (ENCRYPTION_KEY configurada, SECRET_KEY con entropía suficiente, credenciales no hardcodeadas) y operaciones que no involucran información sensible en logs, el sistema corregido SHALL producir exactamente el mismo comportamiento que el sistema original, preservando toda la funcionalidad de encriptación, autenticación, integración con impresoras, CORS, CSRF y rate limiting.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14, 3.15, 3.16, 3.17, 3.18**

## Fix Implementation

### Changes Required

Las correcciones se implementarán en 11 archivos del backend, organizadas por categoría:


#### Categoría 1: Gestión de Secretos y Configuración

**File**: `backend/services/encryption_service.py`

**Function**: `EncryptionService.initialize()`

**Specific Changes**:
1. **Eliminar generación de clave temporal**: Remover el bloque que genera clave temporal en modo desarrollo
2. **Forzar configuración obligatoria**: Lanzar ValueError si ENCRYPTION_KEY no está configurada en cualquier entorno
3. **Mensaje instructivo**: Incluir comando para generar clave válida en el mensaje de error

```python
# Cambio específico (líneas 35-40)
# ANTES:
if os.getenv("ENVIRONMENT", "development") == "development":
    logger.warning("⚠️ ENCRYPTION_KEY no configurada, generando clave temporal")
    encryption_key = Fernet.generate_key().decode()

# DESPUÉS:
if not encryption_key:
    raise ValueError(
        "ENCRYPTION_KEY must be set in all environments. "
        "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    )
```

**File**: `backend/services/jwt_service.py`

**Function**: `JWTService._get_secret_key()`

**Specific Changes**:
1. **Agregar validación de entropía**: Implementar función `_validate_secret_key_entropy()` que verifica complejidad
2. **Verificar categorías de caracteres**: Validar presencia de al menos 3 de 4 categorías (mayúsculas, minúsculas, dígitos, especiales)
3. **Rechazar claves débiles**: Lanzar ValueError con mensaje instructivo si la entropía es insuficiente

```python
# Nuevo método a agregar
@classmethod
def _validate_secret_key_entropy(cls, secret_key: str) -> bool:
    """Validate SECRET_KEY has minimum entropy"""
    import string
    
    charset_used = set(secret_key)
    has_upper = any(c in string.ascii_uppercase for c in charset_used)
    has_lower = any(c in string.ascii_lowercase for c in charset_used)
    has_digit = any(c in string.digits for c in charset_used)
    has_special = any(c in string.punctuation for c in charset_used)
    
    categories = sum([has_upper, has_lower, has_digit, has_special])
    return categories >= 3

# Modificar _get_secret_key() para incluir validación
if not cls._validate_secret_key_entropy(secret_key):
    raise ValueError(
        "SECRET_KEY has insufficient entropy. "
        "Must contain at least 3 of: uppercase, lowercase, digits, special characters. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )
```

**File**: `backend/services/ricoh_web_client.py`

**Function**: `RicohWebClient.__init__()`

**Specific Changes**:
1. **Eliminar valor por defecto vacío**: Cambiar `admin_password: str = ""` a `admin_password: str = None`
2. **Validar contraseña requerida**: Lanzar ValueError si admin_password es None o vacío
3. **Obtener de variable de entorno**: Intentar obtener de `RICOH_ADMIN_PASSWORD` si no se proporciona

```python
# Cambio en __init__ (línea 23)
# ANTES:
def __init__(self, timeout: int = 30, admin_user: str = "admin", admin_password: str = ""):

# DESPUÉS:
def __init__(self, timeout: int = 30, admin_user: str = "admin", admin_password: str = None):
    if admin_password is None:
        admin_password = os.getenv("RICOH_ADMIN_PASSWORD")
    
    if not admin_password:
        raise ValueError(
            "RICOH_ADMIN_PASSWORD must be set. "
            "Configure it in environment variables or pass it explicitly."
        )
    
    self.admin_password = admin_password
```

**File**: `backend/db/database.py`

**Function**: Module-level configuration

**Specific Changes**:
1. **Eliminar valor por defecto con credenciales**: Remover el string hardcodeado de DATABASE_URL
2. **Requerir variable de entorno**: Lanzar ValueError si DATABASE_URL no está configurada
3. **Mensaje instructivo**: Incluir ejemplo de formato correcto en el mensaje de error

```python
# Cambio en configuración (líneas 8-11)
# ANTES:
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet"
)

# DESPUÉS:
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL must be set in environment variables. "
        "Example: DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
    )
```

#### Categoría 2: Exposición de Información Sensible en Logs

**File**: `backend/middleware/auth_middleware.py`

**Function**: `get_current_user()`

**Specific Changes**:
1. **Enmascarar tokens en logs**: Cambiar formato de `token[:20]` a `token[:4]...token[-4:]`
2. **Aplicar a todos los logs**: Actualizar tanto print statements como logger.info
3. **Mantener trazabilidad**: Asegurar que los primeros y últimos 4 caracteres sean suficientes para correlacionar logs

```python
# Cambio en logging (líneas 60-61)
# ANTES:
print(f"[AUTH] Autenticación iniciada - Token: {token[:20] if token else 'NONE'}...")
logger.info(f"🔐 Autenticación iniciada - Token: {token[:20] if token else 'NONE'}...")

# DESPUÉS:
token_preview = f"{token[:4]}...{token[-4:]}" if token and len(token) > 8 else "NONE"
print(f"[AUTH] Autenticación iniciada - Token: {token_preview}")
logger.info(f"🔐 Autenticación iniciada - Token: {token_preview}")
```

**File**: `backend/scripts/init_superadmin.py`

**Function**: `main()`

**Specific Changes**:
1. **Ocultar contraseña en output**: No imprimir la contraseña temporal en texto plano
2. **Mostrar solo longitud**: Indicar que se generó una contraseña de N caracteres
3. **Guardar en archivo seguro**: Opcionalmente, guardar en archivo con permisos restrictivos (0600)

```python
# Cambio en output (líneas después de generar contraseña)
# ANTES:
print(f"✅ Contraseña generada: {len(temp_password)} caracteres")
print()
# ... más adelante ...
print(f"   Password: {temp_password}")

# DESPUÉS:
print(f"✅ Contraseña generada: {len(temp_password)} caracteres")
print()
# ... más adelante ...
print(f"   Password: [Saved to secure file: .superadmin_password]")
print(f"   Password length: {len(temp_password)} characters")

# Guardar en archivo con permisos restrictivos
password_file = backend_dir / '.superadmin_password'
password_file.write_text(temp_password)
os.chmod(password_file, 0o600)  # Solo lectura para el propietario
```

**File**: `backend/services/ricoh_web_client.py`

**Function**: Múltiples funciones que loguean wimToken

**Specific Changes**:
1. **Identificar todos los logs de wimToken**: Buscar todos los logger.debug/info que imprimen wimToken
2. **Aplicar enmascaramiento consistente**: Usar formato `token[:4]...token[-4:]` en todos los casos
3. **Actualizar aproximadamente 15 ubicaciones**: Incluyendo `_refresh_wim_token()`, `_authenticate()`, `provision_user()`

```python
# Ejemplo de cambio en _refresh_wim_token() (línea 73)
# ANTES:
logger.debug(f"✅ Nuevo wimToken obtenido: {token}")

# DESPUÉS:
token_preview = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else token
logger.debug(f"✅ Nuevo wimToken obtenido: {token_preview}")
```

#### Categoría 3: Configuración de Seguridad Permisiva

**File**: `backend/main.py`

**Function**: CORS Middleware configuration

**Specific Changes**:
1. **Definir listas explícitas**: Crear constantes ALLOWED_METHODS y ALLOWED_HEADERS
2. **Restringir métodos**: Cambiar `["*"]` a lista específica de métodos HTTP necesarios
3. **Restringir headers**: Cambiar `["*"]` a lista específica de headers requeridos
4. **Agregar expose_headers**: Especificar headers que el cliente puede leer

```python
# Cambio en configuración CORS (líneas 149-155)
# ANTES:
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# DESPUÉS:
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-CSRF-Token",
    "X-Request-ID"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=3600,
)
```

**File**: `backend/main.py`

**Function**: CSRF Protection Middleware initialization

**Specific Changes**:
1. **Habilitar por defecto en producción**: Cambiar lógica para habilitar CSRF si ENVIRONMENT=production
2. **Permitir deshabilitar explícitamente**: Solo deshabilitar si ENABLE_CSRF=false está explícitamente configurado
3. **Logging claro**: Indicar claramente si CSRF está habilitada o deshabilitada y por qué

```python
# Cambio en inicialización CSRF (líneas 162-164)
# ANTES:
if os.getenv("ENABLE_CSRF", "false").lower() == "true":
    logger.info("🛡️ CSRF Protection enabled")
    app.add_middleware(CSRFProtectionMiddleware)

# DESPUÉS:
# Habilitar CSRF por defecto en producción, o si ENABLE_CSRF=true
enable_csrf = (
    os.getenv("ENVIRONMENT") == "production" or
    os.getenv("ENABLE_CSRF", "false").lower() == "true"
)

if enable_csrf:
    logger.info("🛡️ CSRF Protection enabled")
    app.add_middleware(CSRFProtectionMiddleware)
else:
    logger.warning("⚠️ CSRF Protection disabled (not recommended for production)")
```

**File**: `backend/middleware/csrf_protection.py`

**Function**: `CSRFProtectionMiddleware.__init__()` y métodos de almacenamiento

**Specific Changes**:
1. **Agregar soporte para Redis**: Implementar backend de Redis como alternativa a memoria
2. **Detectar configuración**: Usar Redis si REDIS_URL está configurada, memoria en caso contrario
3. **Migrar métodos de almacenamiento**: Actualizar `_store_token()`, `_validate_csrf_token()`, `_cleanup_expired_tokens()` para usar Redis
4. **Mantener compatibilidad**: Permitir modo memoria para desarrollo local

```python
# Cambios en __init__ (línea 35)
# ANTES:
def __init__(self, app, secret_key: str = None):
    super().__init__(app)
    self.secret_key = secret_key or secrets.token_urlsafe(32)
    self._token_cache = {}

# DESPUÉS:
def __init__(self, app, secret_key: str = None, redis_url: str = None):
    super().__init__(app)
    self.secret_key = secret_key or secrets.token_urlsafe(32)
    
    # Usar Redis si está configurado, memoria en caso contrario
    self.redis_url = redis_url or os.getenv("REDIS_URL")
    
    if self.redis_url:
        import redis
        self.redis_client = redis.from_url(self.redis_url)
        self.storage_backend = "redis"
        logger.info("🔴 CSRF usando Redis para almacenamiento distribuido")
    else:
        self._token_cache = {}
        self.storage_backend = "memory"
        logger.warning("⚠️ CSRF usando memoria (no recomendado para producción multi-instancia)")

# Nuevo método para almacenar en Redis
def _store_token_redis(self, token: str, data: dict):
    """Store token in Redis with expiration"""
    import json
    self.redis_client.setex(
        f"csrf:{token}",
        timedelta(hours=self.TOKEN_EXPIRATION_HOURS),
        json.dumps(data)
    )

# Nuevo método para obtener de Redis
def _get_token_redis(self, token: str) -> Optional[dict]:
    """Get token from Redis"""
    import json
    data = self.redis_client.get(f"csrf:{token}")
    return json.loads(data) if data else None

# Nuevo método para eliminar de Redis
def _delete_token_redis(self, token: str):
    """Delete token from Redis"""
    self.redis_client.delete(f"csrf:{token}")
```

**File**: `backend/services/rate_limiter_service.py`

**Function**: `RateLimiterService` class

**Specific Changes**:
1. **Agregar soporte para Redis**: Implementar backend de Redis como alternativa a memoria
2. **Detectar configuración**: Usar Redis si REDIS_URL está configurada, memoria en caso contrario
3. **Migrar métodos de almacenamiento**: Actualizar `check_rate_limit()`, `increment_counter()`, `reset_counter()` para usar Redis
4. **Usar comandos atómicos**: Implementar con INCR y EXPIRE de Redis para operaciones atómicas
5. **Mantener compatibilidad**: Permitir modo memoria para desarrollo local

```python
# Cambios en la clase (inicio del archivo)
# ANTES:
class RateLimiterService:
    """Service for rate limiting using in-memory storage"""
    _storage: Dict[str, Dict] = defaultdict(dict)
    _lock = threading.Lock()

# DESPUÉS:
class RateLimiterService:
    """Service for rate limiting using Redis or in-memory storage"""
    
    # Configuración de backend
    _redis_client = None
    _storage_backend = None
    _storage: Dict[str, Dict] = defaultdict(dict)
    _lock = threading.Lock()
    
    @classmethod
    def initialize(cls):
        """Initialize rate limiter with Redis or memory backend"""
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            import redis
            cls._redis_client = redis.from_url(redis_url)
            cls._storage_backend = "redis"
            logger.info("🔴 Rate Limiter usando Redis para almacenamiento distribuido")
        else:
            cls._storage_backend = "memory"
            logger.warning("⚠️ Rate Limiter usando memoria (no recomendado para producción multi-instancia)")
    
    @classmethod
    def check_rate_limit_redis(cls, key: str, max_requests: int, window_seconds: int) -> RateLimitResult:
        """Check rate limit using Redis"""
        redis_key = f"ratelimit:{key}"
        
        # Usar pipeline para operaciones atómicas
        pipe = cls._redis_client.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, window_seconds)
        results = pipe.execute()
        
        current_count = results[0]
        
        if current_count > max_requests:
            ttl = cls._redis_client.ttl(redis_key)
            reset_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
            return RateLimitResult(allowed=False, remaining=0, reset_at=reset_at)
        
        remaining = max_requests - current_count
        ttl = cls._redis_client.ttl(redis_key)
        reset_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        
        return RateLimitResult(allowed=True, remaining=remaining, reset_at=reset_at)
```

## Testing Strategy

### Validation Approach

La estrategia de testing sigue un enfoque de tres fases: primero, verificar que las configuraciones inseguras son rechazadas (exploratory bug condition checking); segundo, verificar que las configuraciones válidas funcionan correctamente (fix checking); tercero, verificar que toda la funcionalidad existente se preserva (preservation checking).

### Exploratory Bug Condition Checking

**Goal**: Verificar que el código sin corregir acepta configuraciones inseguras y expone información sensible. Confirmar o refutar el análisis de causa raíz.

**Test Plan**: Escribir tests que intenten usar configuraciones inseguras y verifiquen que el código actual las acepta. Ejecutar estos tests en el código UNFIXED para observar fallos.

**Test Cases**:
1. **Test ENCRYPTION_KEY no configurada**: Intentar inicializar EncryptionService sin ENCRYPTION_KEY en desarrollo (fallará en código unfixed - acepta y genera temporal)
2. **Test SECRET_KEY con baja entropía**: Intentar usar SECRET_KEY="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" (fallará en código unfixed - acepta)
3. **Test exposición de tokens en logs**: Capturar logs durante autenticación y verificar que contienen más de 8 caracteres del token (fallará en código unfixed - expone 20 caracteres)
4. **Test CORS permisivo**: Verificar que allow_methods=["*"] está configurado (fallará en código unfixed - está configurado)
5. **Test CSRF deshabilitada**: Verificar que CSRF está deshabilitada por defecto (fallará en código unfixed - está deshabilitada)
6. **Test almacenamiento en memoria**: Verificar que CSRF y rate limiting usan diccionarios en memoria (fallará en código unfixed - usan memoria)

**Expected Counterexamples**:
- EncryptionService acepta ENCRYPTION_KEY=None y genera clave temporal
- JWTService acepta SECRET_KEY con solo minúsculas
- Logs contienen `Token: eyJhbGciOiJIUzI1NiIsI...` (20 caracteres expuestos)
- CORS configurado con `allow_methods=["*"]` y `allow_headers=["*"]`
- CSRF deshabilitada por defecto incluso en producción
- CSRF y rate limiting usan `self._token_cache = {}` y `_storage = defaultdict(dict)`

### Fix Checking

**Goal**: Verificar que para todas las configuraciones inseguras, el código corregido rechaza la configuración con mensajes instructivos.

**Pseudocode:**
```
FOR ALL config WHERE isBugCondition_SecretConfig(config) DO
  result ← validateConfiguration_fixed(config)
  ASSERT result.raises_error = true
  ASSERT result.error_message contains "must be set"
  ASSERT result.error_message contains "Generate one with:"
END FOR

FOR ALL logEntry WHERE isBugCondition_SensitiveExposure(logEntry) DO
  result ← logSensitiveData_fixed(logEntry)
  ASSERT result.format = "XXXX...YYYY"
  ASSERT result.exposed_chars <= 8
END FOR

FOR ALL securityConfig WHERE isBugCondition_PermissiveConfig(securityConfig) DO
  result ← applySecurityConfig_fixed(securityConfig)
  ASSERT result.CORS.allowMethods is explicit list
  ASSERT result.CORS.allowHeaders is explicit list
  ASSERT (result.environment = "production" IMPLIES result.CSRF.enabled = true)
  ASSERT result.CSRF.storage = "redis" OR result.CSRF.storage = "memory" with warning
END FOR
```

**Test Cases**:
1. **Test rechazo de ENCRYPTION_KEY no configurada**: Verificar que lanza ValueError con mensaje instructivo
2. **Test rechazo de SECRET_KEY débil**: Verificar que lanza ValueError indicando entropía insuficiente
3. **Test enmascaramiento de tokens**: Verificar que logs muestran solo 4+4 caracteres
4. **Test CORS restrictivo**: Verificar que solo métodos/headers específicos están permitidos
5. **Test CSRF habilitada en producción**: Verificar que CSRF se habilita automáticamente cuando ENVIRONMENT=production
6. **Test Redis backend**: Verificar que CSRF y rate limiting usan Redis cuando REDIS_URL está configurada

### Preservation Checking

**Goal**: Verificar que para todas las configuraciones válidas y operaciones normales, el código corregido produce exactamente el mismo comportamiento que el código original.

**Pseudocode:**
```
FOR ALL config WHERE NOT isBugCondition_SecretConfig(config) DO
  ASSERT encryptData_original(config, data) = encryptData_fixed(config, data)
  ASSERT decryptData_original(config, encrypted) = decryptData_fixed(config, encrypted)
END FOR

FOR ALL validToken WHERE isValidJWT(validToken) DO
  ASSERT validateToken_original(validToken) = validateToken_fixed(validToken)
END FOR

FOR ALL request WHERE isWithinRateLimit(request) DO
  ASSERT processRequest_original(request) = processRequest_fixed(request)
END FOR
```

**Testing Approach**: Property-based testing es recomendado para preservation checking porque genera muchos casos de prueba automáticamente y captura edge cases que tests manuales podrían perder.

**Test Plan**: Ejecutar tests de funcionalidad existente en código UNFIXED para capturar comportamiento esperado, luego ejecutar los mismos tests en código FIXED para verificar preservación.

**Test Cases**:
1. **Preservation: Encriptación con clave válida**: Verificar que datos encriptados con ENCRYPTION_KEY válida se desencriptan correctamente
2. **Preservation: Autenticación con token válido**: Verificar que tokens JWT válidos se validan correctamente
3. **Preservation: Integración con impresoras**: Verificar que autenticación con impresoras Ricoh funciona con credenciales válidas
4. **Preservation: CORS con orígenes permitidos**: Verificar que peticiones de orígenes permitidos se procesan correctamente
5. **Preservation: CSRF con token válido**: Verificar que peticiones con token CSRF válido se procesan correctamente
6. **Preservation: Rate limiting dentro de límites**: Verificar que peticiones dentro de límites se procesan sin restricciones
7. **Preservation: Auditoría de eventos**: Verificar que eventos críticos se registran correctamente en logs de auditoría

### Unit Tests

- Test de validación de entropía de SECRET_KEY con diferentes combinaciones de caracteres
- Test de enmascaramiento de tokens con diferentes longitudes de token
- Test de configuración CORS con diferentes listas de métodos y headers
- Test de habilitación de CSRF en diferentes entornos (development, production)
- Test de almacenamiento Redis vs memoria para CSRF y rate limiting
- Test de rechazo de configuraciones inseguras con mensajes de error correctos

### Property-Based Tests

- Generar claves aleatorias con diferentes niveles de entropía y verificar validación correcta
- Generar tokens JWT aleatorios y verificar enmascaramiento consistente en logs
- Generar configuraciones de seguridad aleatorias y verificar aplicación de restricciones
- Generar datos sensibles aleatorios y verificar encriptación/desencriptación correcta con claves válidas
- Generar peticiones HTTP aleatorias y verificar rate limiting correcto

### Integration Tests

- Test de flujo completo de autenticación con SECRET_KEY válida de alta entropía
- Test de flujo completo de encriptación/desencriptación con ENCRYPTION_KEY válida
- Test de flujo completo de provisioning de usuarios a impresoras Ricoh con credenciales válidas
- Test de flujo completo de peticiones CORS desde orígenes permitidos
- Test de flujo completo de protección CSRF con tokens válidos
- Test de flujo completo de rate limiting en escenarios de carga normal y alta
- Test de despliegue multi-instancia con Redis para CSRF y rate limiting

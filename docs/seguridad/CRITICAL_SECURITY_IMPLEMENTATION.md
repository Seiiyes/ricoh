# Implementación de Mejoras Críticas de Seguridad

## 📋 Resumen

Se implementaron 5 mejoras críticas de seguridad para el sistema Ricoh Equipment Management:

1. ✅ **Servicio de Encriptación** - Encriptación de datos sensibles en BD
2. ✅ **Servicio de Sanitización** - Protección contra XSS
3. ✅ **Protección CSRF** - Tokens CSRF para requests mutables
4. ✅ **Rotación de Tokens JWT** - Renovación automática de tokens
5. ✅ **Middleware HTTPS** - Redirección HTTP a HTTPS en producción

---

## 1. Servicio de Encriptación

### 📁 Archivo
`backend/services/encryption_service.py`

### 🎯 Funcionalidad
- Encriptación/desencriptación de datos sensibles usando Fernet (AES-128)
- Derivación de claves desde contraseñas con PBKDF2
- Soporte para encriptar campos específicos en diccionarios

### 🔧 Uso

```python
from services.encryption_service import EncryptionService

# Encriptar string
encrypted = EncryptionService.encrypt("mi_password_secreto")

# Desencriptar
decrypted = EncryptionService.decrypt(encrypted)

# Encriptar campos de diccionario
data = {"username": "admin", "password": "secret"}
encrypted_data = EncryptionService.encrypt_dict(data, ["password"])
```

### ⚙️ Configuración

**Desarrollo:**
- Genera clave temporal automáticamente
- No requiere configuración

**Producción:**
```bash
# Generar clave
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# Agregar a .env
ENCRYPTION_KEY=tu_clave_generada_aqui
ENVIRONMENT=production
```

### ✅ Tests
- 10 tests unitarios (100% pasando)
- Archivo: `backend/tests/test_encryption_service.py`

---

## 2. Servicio de Sanitización

### 📁 Archivo
`backend/services/sanitization_service.py`

### 🎯 Funcionalidad
- Sanitización de inputs para prevenir XSS
- Remoción de scripts, event handlers, iframes
- Validación de emails, URLs, nombres de archivo
- Escapado de caracteres HTML

### 🔧 Uso

```python
from services.sanitization_service import SanitizationService, sanitize

# Sanitizar string
clean = SanitizationService.sanitize_string('<script>alert("XSS")</script>')

# Sanitizar diccionario
data = {"name": '<script>alert(1)</script>', "age": 25}
clean_data = SanitizationService.sanitize_dict(data)

# Función de utilidad
clean = sanitize('<script>alert(1)</script>')

# Validar email
is_valid = SanitizationService.validate_email('test@test.com')

# Sanitizar nombre de archivo
safe_filename = SanitizationService.sanitize_filename('../../../etc/passwd')
```

### 🛡️ Protecciones
- Scripts (`<script>`, `javascript:`)
- Event handlers (`onclick`, `onerror`, etc.)
- Iframes y objetos embebidos
- Meta refresh y base tags
- Data URIs peligrosos
- VBScript

### ✅ Tests
- 18 tests unitarios (100% pasando)
- Archivo: `backend/tests/test_sanitization_service.py`

---

## 3. Protección CSRF

### 📁 Archivo
`backend/middleware/csrf_protection.py`

### 🎯 Funcionalidad
- Genera tokens CSRF únicos por sesión
- Valida tokens en requests mutables (POST, PUT, DELETE, PATCH)
- Tokens de un solo uso con expiración de 2 horas

### 🔧 Configuración

**Backend (main.py):**
```python
# Habilitar CSRF protection
ENABLE_CSRF=true  # en .env
```

**Frontend (apiClient.ts):**
```typescript
// El interceptor debe incluir el token CSRF
axios.interceptors.request.use((config) => {
  // Obtener token del header de respuesta anterior
  const csrfToken = localStorage.getItem('csrf_token');
  if (csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method?.toUpperCase())) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});

// Guardar nuevo token de cada respuesta
axios.interceptors.response.use((response) => {
  const newCsrfToken = response.headers['x-csrf-token'];
  if (newCsrfToken) {
    localStorage.setItem('csrf_token', newCsrfToken);
  }
  return response;
});
```

### 🚫 Rutas Excluidas
- `/auth/login`
- `/auth/refresh`
- `/docs`
- `/openapi.json`

### ✅ Tests
- 4 tests de integración
- Archivo: `backend/tests/test_csrf_protection.py`

---

## 4. Rotación de Tokens JWT

### 📁 Archivos
- `backend/services/jwt_service.py` (métodos agregados)
- `backend/api/auth.py` (endpoint `/auth/rotate-token`)
- `backend/api/auth_schemas.py` (schema `RotateTokenResponse`)

### 🎯 Funcionalidad
- Verifica si un token está cerca de expirar
- Genera nuevo token si está dentro del threshold (5 minutos)
- Mantiene sesiones activas sin interrupciones

### 🔧 Uso

**Backend:**
```python
from services.jwt_service import JWTService

# Verificar si debe rotarse
should_rotate = JWTService.should_rotate_token(token, rotation_threshold_minutes=5)

# Rotar token
new_token = JWTService.rotate_access_token(current_token, user)
```

**Frontend (apiClient.ts):**
```typescript
// Interceptor para rotación automática
axios.interceptors.response.use(async (response) => {
  // Verificar si el token está cerca de expirar
  const token = localStorage.getItem('access_token');
  const expiration = getTokenExpiration(token);
  
  if (expiration && isWithinMinutes(expiration, 5)) {
    // Rotar token
    const rotateResponse = await axios.post('/auth/rotate-token');
    if (rotateResponse.data.rotated) {
      localStorage.setItem('access_token', rotateResponse.data.access_token);
    }
  }
  
  return response;
});
```

**Endpoint:**
```bash
POST /auth/rotate-token
Authorization: Bearer <access_token>

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "rotated": true
}
```

### ✅ Tests
- 6 tests unitarios (100% pasando)
- Archivo: `backend/tests/test_token_rotation.py`

---

## 5. Middleware HTTPS Redirect

### 📁 Archivo
`backend/middleware/https_redirect.py`

### 🎯 Funcionalidad
- Redirige automáticamente HTTP a HTTPS en producción
- Solo activo cuando `ENVIRONMENT=production` y `FORCE_HTTPS=true`

### 🔧 Configuración

**Producción (.env):**
```bash
ENVIRONMENT=production
FORCE_HTTPS=true
```

**Desarrollo:**
```bash
ENVIRONMENT=development
# FORCE_HTTPS no es necesario (deshabilitado por defecto)
```

### 📝 Comportamiento
- Requests HTTP → Redirect 301 a HTTPS
- Requests HTTPS → Continúa normalmente
- Desarrollo → No hace nada (permite HTTP)

---

## 📊 Resumen de Tests

| Componente | Tests | Estado |
|------------|-------|--------|
| Encryption Service | 10 | ✅ 100% |
| Sanitization Service | 18 | ✅ 100% |
| CSRF Protection | 4 | ✅ 100% |
| Token Rotation | 6 | ✅ 100% |
| **TOTAL** | **38** | **✅ 100%** |

---

## 🚀 Integración en main.py

```python
# Import middleware
from middleware.ddos_protection import DDoSProtectionMiddleware
from middleware.https_redirect import HTTPSRedirectMiddleware
from middleware.csrf_protection import CSRFProtectionMiddleware

# Add middlewares
app.add_middleware(DDoSProtectionMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)

# CSRF Protection (opcional, habilitar con ENABLE_CSRF=true)
if os.getenv("ENABLE_CSRF", "false").lower() == "true":
    logger.info("🛡️ CSRF Protection enabled")
    app.add_middleware(CSRFProtectionMiddleware)
```

---

## 📦 Dependencias Nuevas

```bash
pip install cryptography
```

Ya incluida en `requirements.txt`.

---

## 🔐 Variables de Entorno

### Desarrollo
```bash
ENVIRONMENT=development
# No requiere ENCRYPTION_KEY (se genera temporal)
# FORCE_HTTPS no es necesario
# ENABLE_CSRF=false (opcional)
```

### Producción
```bash
ENVIRONMENT=production
ENCRYPTION_KEY=<clave_generada>
FORCE_HTTPS=true
ENABLE_CSRF=true  # Recomendado
SECRET_KEY=<clave_jwt>
```

---

## 📝 Próximos Pasos (Opcional)

### Integración en el Código Existente

1. **Encriptar network_password en modelo User:**
```python
# En db/models.py
from services.encryption_service import EncryptionService

class User(Base):
    network_password = Column(String(500))
    
    def set_network_password(self, password: str):
        self.network_password = EncryptionService.encrypt(password)
    
    def get_network_password(self) -> str:
        return EncryptionService.decrypt(self.network_password)
```

2. **Sanitizar inputs en endpoints:**
```python
# En api/printers.py
from services.sanitization_service import sanitize

@router.post("/printers")
async def create_printer(printer_data: PrinterCreate):
    # Sanitizar inputs
    clean_data = sanitize(printer_data.dict())
    # Continuar con lógica...
```

3. **Actualizar frontend para CSRF:**
- Modificar `src/services/apiClient.ts`
- Agregar interceptores para tokens CSRF
- Guardar tokens en localStorage

4. **Implementar rotación automática:**
- Agregar interceptor en `apiClient.ts`
- Verificar expiración en cada request
- Rotar token automáticamente

---

## 🎯 Beneficios de Seguridad

| Mejora | Protege Contra | Impacto |
|--------|----------------|---------|
| Encriptación | Exposición de datos sensibles | 🔴 Crítico |
| Sanitización | XSS, Injection attacks | 🔴 Crítico |
| CSRF Protection | Cross-Site Request Forgery | 🟡 Alto |
| Token Rotation | Session hijacking | 🟡 Alto |
| HTTPS Redirect | Man-in-the-middle | 🔴 Crítico |

---

## ✅ Checklist de Implementación

- [x] Servicio de encriptación implementado
- [x] Servicio de sanitización implementado
- [x] Middleware CSRF implementado
- [x] Rotación de tokens JWT implementada
- [x] Middleware HTTPS redirect implementado
- [x] Tests unitarios (38 tests, 100% pasando)
- [x] Documentación completa
- [x] Integración en main.py
- [ ] Actualizar frontend para CSRF (pendiente)
- [ ] Integrar encriptación en modelos (pendiente)
- [ ] Integrar sanitización en endpoints (pendiente)
- [ ] Configurar ENCRYPTION_KEY en producción (pendiente)

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Cryptography Documentation](https://cryptography.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Fecha de Implementación:** 20 de Marzo de 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Completado

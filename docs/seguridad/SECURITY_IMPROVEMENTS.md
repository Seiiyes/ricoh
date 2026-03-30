# Mejoras de Seguridad Adicionales

> **🎉 ACTUALIZACIÓN (20 de Marzo de 2026):**  
> Las 5 mejoras críticas de Nivel 1 han sido completamente implementadas.  
> Ver detalles en: [`docs/CRITICAL_SECURITY_IMPLEMENTATION.md`](./CRITICAL_SECURITY_IMPLEMENTATION.md)

---

## Estado Actual de Seguridad ✅

### Ya Implementado (17 controles)
1. ✅ **Autenticación JWT** - Tokens seguros con expiración
2. ✅ **Hashing de Contraseñas** - bcrypt con 12 rounds
3. ✅ **Validación de Fortaleza de Contraseñas** - Requisitos estrictos
4. ✅ **Rate Limiting** - Por IP y por endpoint
5. ✅ **Protección DDoS** - 6 capas de defensa
6. ✅ **Multi-tenancy** - Aislamiento de datos por empresa
7. ✅ **CORS** - Control de orígenes permitidos
8. ✅ **Security Headers** - HSTS, X-Frame-Options, etc.
9. ✅ **Audit Logging** - Registro de acciones administrativas
10. ✅ **Session Management** - Control de sesiones activas
11. ✅ **Input Validation** - Pydantic schemas con validadores
12. ✅ **SQL Injection Protection** - ORM con queries parametrizadas
13. ✅ **🆕 Encryption Service** - Encriptación de datos sensibles con Fernet (AES-128)
14. ✅ **🆕 Sanitization Service** - Protección contra XSS
15. ✅ **🆕 CSRF Protection** - Tokens CSRF para requests mutables
16. ✅ **🆕 Token Rotation** - Renovación automática de tokens JWT
17. ✅ **🆕 HTTPS Redirect** - Redirección HTTP a HTTPS en producción

---

## Mejoras de Seguridad Adicionales Propuestas

> **Nota:** Las mejoras de Nivel 1 (Críticas) ya están implementadas.  
> Las siguientes son mejoras adicionales recomendadas para fortalecer aún más la seguridad.

### 🔐 Nivel 1: Críticas ✅ COMPLETADO

1. ✅ **HTTPS/TLS Obligatorio** - Implementado en `middleware/https_redirect.py`
2. ✅ **Rotación Automática de Tokens JWT** - Implementado en `services/jwt_service.py` + endpoint `/auth/rotate-token`
3. ✅ **Encriptación de Datos Sensibles** - Implementado en `services/encryption_service.py`
4. ✅ **Protección CSRF** - Implementado en `middleware/csrf_protection.py`
5. ✅ **Sanitización de Inputs (XSS)** - Implementado en `services/sanitization_service.py`

**Ver documentación completa:** [`docs/CRITICAL_SECURITY_IMPLEMENTATION.md`](./CRITICAL_SECURITY_IMPLEMENTATION.md)

---

### 🔐 Nivel 2: Importantes (Media Prioridad)

Las siguientes mejoras están documentadas a continuación para implementación futura:

---

## Mejoras de Seguridad Propuestas (Nivel 2+)

### 🔐 Nivel 1: Críticas (Alta Prioridad) - ✅ COMPLETADO

#### 1. HTTPS/TLS Obligatorio ✅
**Estado**: ✅ Implementado
**Archivo**: `backend/middleware/https_redirect.py`

**Implementación**:
```python
# middleware/https_redirect.py
from fastapi import Request
from fastapi.responses import RedirectResponse

@app.middleware("http")
async def https_redirect(request: Request, call_next):
    if os.getenv("ENVIRONMENT") == "production":
        if request.url.scheme != "https":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url, status_code=301)
    return await call_next(request)
```

**Beneficios**:
- Encriptación de tráfico
- Protección contra man-in-the-middle
- Confianza del usuario

---

#### 2. Rotación Automática de Tokens JWT
**Estado**: ❌ No implementado
**Riesgo**: Tokens robados válidos indefinidamente

**Implementación**:
```python
# services/jwt_service.py
class JWTService:
    @classmethod
    def rotate_token(cls, old_token: str) -> dict:
        """Rotar token antes de expiración"""
        decoded = cls.decode_token(old_token)
        
        # Verificar que está cerca de expirar (últimos 5 minutos)
        exp = datetime.fromtimestamp(decoded['exp'])
        now = datetime.now(timezone.utc)
        time_left = (exp - now).total_seconds()
        
        if time_left < 300:  # 5 minutos
            # Crear nuevo token
            user = get_user_from_token(decoded)
            return {
                "access_token": cls.create_access_token(user),
                "rotated": True
            }
        
        return {"rotated": False}
```

**Beneficios**:
- Reduce ventana de ataque
- Tokens de corta duración
- Mejor control de sesiones

---

#### 3. Encriptación de Datos Sensibles en Base de Datos
**Estado**: ⚠️ Parcial (solo passwords hasheados)
**Riesgo**: Exposición de datos en caso de breach

**Implementación**:
```python
# services/encryption_service.py
from cryptography.fernet import Fernet
import os
import base64

class EncryptionService:
    """Servicio para encriptar/desencriptar datos sensibles"""
    
    _key = None
    _cipher = None
    
    @classmethod
    def initialize(cls):
        """Inicializar con clave de encriptación"""
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            # Generar clave si no existe
            key = Fernet.generate_key()
            logger.warning("⚠️ Generando nueva clave de encriptación")
        
        cls._key = key if isinstance(key, bytes) else key.encode()
        cls._cipher = Fernet(cls._key)
    
    @classmethod
    def encrypt(cls, data: str) -> str:
        """Encriptar datos"""
        if not cls._cipher:
            cls.initialize()
        
        encrypted = cls._cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    @classmethod
    def decrypt(cls, encrypted_data: str) -> str:
        """Desencriptar datos"""
        if not cls._cipher:
            cls.initialize()
        
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = cls._cipher.decrypt(decoded)
        return decrypted.decode()

# Uso en modelos
class User(Base):
    network_password = Column(String(500))  # Encriptado
    
    def set_network_password(self, password: str):
        self.network_password = EncryptionService.encrypt(password)
    
    def get_network_password(self) -> str:
        return EncryptionService.decrypt(self.network_password)
```

**Datos a encriptar**:
- Contraseñas de red (network_password)
- Tokens de API externos
- Información personal sensible
- Configuraciones con credenciales

**Beneficios**:
- Protección en caso de dump de BD
- Cumplimiento de regulaciones (GDPR, etc.)
- Defensa en profundidad

---

#### 4. Protección CSRF para Operaciones Críticas
**Estado**: ❌ No implementado
**Riesgo**: Cross-Site Request Forgery

**Implementación**:
```python
# middleware/csrf_protection.py
from fastapi import Request, HTTPException
import secrets
from datetime import datetime, timedelta

class CSRFProtection:
    """Protección contra CSRF"""
    
    _tokens = {}  # {token: expiry}
    
    @classmethod
    def generate_token(cls, session_id: str) -> str:
        """Generar token CSRF"""
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=1)
        cls._tokens[token] = {
            "session_id": session_id,
            "expiry": expiry
        }
        return token
    
    @classmethod
    def validate_token(cls, token: str, session_id: str) -> bool:
        """Validar token CSRF"""
        if token not in cls._tokens:
            return False
        
        data = cls._tokens[token]
        
        # Verificar expiración
        if datetime.utcnow() > data["expiry"]:
            del cls._tokens[token]
            return False
        
        # Verificar sesión
        if data["session_id"] != session_id:
            return False
        
        return True

@app.middleware("http")
async def csrf_protection(request: Request, call_next):
    """Middleware de protección CSRF"""
    
    # Solo para métodos que modifican datos
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        # Excepto login y endpoints públicos
        if not request.url.path.startswith("/auth/login"):
            csrf_token = request.headers.get("X-CSRF-Token")
            session_id = request.cookies.get("session_id")
            
            if not csrf_token or not CSRFProtection.validate_token(csrf_token, session_id):
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or missing CSRF token"
                )
    
    return await call_next(request)
```

**Beneficios**:
- Previene ataques CSRF
- Protege operaciones críticas
- Estándar de seguridad web

---

#### 5. Sanitización de Inputs (XSS Prevention)
**Estado**: ⚠️ Parcial (validación básica)
**Riesgo**: Cross-Site Scripting

**Implementación**:
```python
# services/sanitization_service.py
import html
import re
from typing import Any, Dict

class SanitizationService:
    """Servicio para sanitizar inputs y prevenir XSS"""
    
    # Patrones peligrosos
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',  # onclick, onload, etc.
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
    ]
    
    @classmethod
    def sanitize_string(cls, text: str) -> str:
        """Sanitizar string para prevenir XSS"""
        if not text:
            return text
        
        # Escapar HTML
        sanitized = html.escape(text)
        
        # Remover patrones peligrosos
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizar diccionario recursivamente"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_string(v) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized

# Uso en endpoints
@router.post("/users")
async def create_user(user_data: UserCreate):
    # Sanitizar antes de guardar
    sanitized_data = SanitizationService.sanitize_dict(user_data.dict())
    # ... guardar en BD
```

**Beneficios**:
- Previene XSS
- Protege contra inyección de HTML
- Datos limpios en BD

---

### 🔒 Nivel 2: Importantes (Media Prioridad)

#### 6. Autenticación de Dos Factores (2FA)
**Estado**: ❌ No implementado
**Riesgo**: Acceso con credenciales robadas

**Implementación**:
```python
# services/totp_service.py
import pyotp
import qrcode
from io import BytesIO

class TOTPService:
    """Servicio para autenticación de dos factores"""
    
    @classmethod
    def generate_secret(cls) -> str:
        """Generar secreto para TOTP"""
        return pyotp.random_base32()
    
    @classmethod
    def generate_qr_code(cls, username: str, secret: str) -> bytes:
        """Generar código QR para configurar 2FA"""
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=username,
            issuer_name="Ricoh Fleet Management"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @classmethod
    def verify_token(cls, secret: str, token: str) -> bool:
        """Verificar token TOTP"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

# Agregar a modelo AdminUser
class AdminUser(Base):
    totp_secret = Column(String(32), nullable=True)
    totp_enabled = Column(Boolean, default=False)
```

**Beneficios**:
- Seguridad adicional
- Protección contra phishing
- Estándar en aplicaciones empresariales

---

#### 7. Detección de Anomalías en Login
**Estado**: ⚠️ Básico (solo failed attempts)
**Riesgo**: Accesos no autorizados no detectados

**Implementación**:
```python
# services/anomaly_detection_service.py
from datetime import datetime, timedelta
from collections import defaultdict

class AnomalyDetectionService:
    """Detectar comportamientos anómalos"""
    
    _user_patterns = defaultdict(lambda: {
        "usual_ips": set(),
        "usual_hours": set(),
        "usual_user_agents": set(),
        "last_locations": []
    })
    
    @classmethod
    def check_login_anomaly(cls, user_id: int, ip: str, 
                           user_agent: str, hour: int) -> dict:
        """Detectar anomalías en login"""
        pattern = cls._user_patterns[user_id]
        anomalies = []
        risk_score = 0
        
        # IP nueva
        if ip not in pattern["usual_ips"]:
            anomalies.append("new_ip")
            risk_score += 30
            
            # Si tiene IPs conocidas, es más sospechoso
            if len(pattern["usual_ips"]) > 0:
                risk_score += 20
        
        # Hora inusual
        if hour not in pattern["usual_hours"]:
            anomalies.append("unusual_hour")
            risk_score += 10
        
        # User agent nuevo
        if user_agent not in pattern["usual_user_agents"]:
            anomalies.append("new_user_agent")
            risk_score += 15
        
        # Actualizar patrones si es login exitoso
        pattern["usual_ips"].add(ip)
        pattern["usual_hours"].add(hour)
        pattern["usual_user_agents"].add(user_agent)
        
        return {
            "is_anomalous": risk_score > 40,
            "risk_score": risk_score,
            "anomalies": anomalies,
            "requires_verification": risk_score > 60
        }
```

**Acciones según riesgo**:
- **Bajo (0-40)**: Login normal
- **Medio (41-60)**: Notificar al usuario por email
- **Alto (61+)**: Requerir 2FA o verificación adicional

**Beneficios**:
- Detección temprana de accesos no autorizados
- Alertas proactivas
- Análisis de comportamiento

---

#### 8. Política de Contraseñas Avanzada
**Estado**: ✅ Básico implementado
**Mejora**: Agregar más controles

**Implementación**:
```python
# services/password_policy_service.py
class PasswordPolicyService:
    """Política avanzada de contraseñas"""
    
    # Historial de contraseñas
    PASSWORD_HISTORY_SIZE = 5
    
    # Expiración
    PASSWORD_MAX_AGE_DAYS = 90
    
    # Diccionario de contraseñas comunes
    COMMON_PASSWORDS = set([
        "password", "123456", "qwerty", "admin", 
        "letmein", "welcome", # ... más
    ])
    
    @classmethod
    def check_password_reuse(cls, user_id: int, new_password: str, 
                            db: Session) -> bool:
        """Verificar que no se reutilice contraseña"""
        history = db.query(PasswordHistory)\
            .filter(PasswordHistory.user_id == user_id)\
            .order_by(PasswordHistory.created_at.desc())\
            .limit(cls.PASSWORD_HISTORY_SIZE)\
            .all()
        
        for old_hash in history:
            if PasswordService.verify_password(new_password, old_hash.password_hash):
                return False  # Contraseña ya usada
        
        return True
    
    @classmethod
    def check_common_password(cls, password: str) -> bool:
        """Verificar que no sea contraseña común"""
        return password.lower() not in cls.COMMON_PASSWORDS
    
    @classmethod
    def check_password_expiration(cls, user: AdminUser) -> bool:
        """Verificar si contraseña expiró"""
        if not user.password_changed_at:
            return False
        
        age = datetime.utcnow() - user.password_changed_at
        return age.days > cls.PASSWORD_MAX_AGE_DAYS
    
    @classmethod
    def check_username_in_password(cls, username: str, password: str) -> bool:
        """Verificar que contraseña no contenga username"""
        return username.lower() not in password.lower()

# Agregar a modelo
class PasswordHistory(Base):
    __tablename__ = "password_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("admin_users.id"))
    password_hash = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Beneficios**:
- Previene reutilización de contraseñas
- Fuerza cambios periódicos
- Evita contraseñas débiles comunes

---

#### 9. Logging de Seguridad Mejorado
**Estado**: ✅ Básico implementado
**Mejora**: Más detallado y estructurado

**Implementación**:
```python
# services/security_logger.py
import json
from datetime import datetime
from enum import Enum

class SecurityEventType(Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    ADMIN_ACTION = "admin_action"

class SecurityLogger:
    """Logger especializado para eventos de seguridad"""
    
    @classmethod
    def log_event(cls, event_type: SecurityEventType, user_id: int = None,
                  ip: str = None, details: dict = None):
        """Registrar evento de seguridad"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "ip": ip,
            "details": details or {}
        }
        
        # Log estructurado
        logger.info(f"SECURITY_EVENT: {json.dumps(event)}")
        
        # Guardar en BD para análisis
        # db.add(SecurityEvent(**event))
        
        # Alertar si es crítico
        if event_type in [SecurityEventType.SUSPICIOUS_ACTIVITY]:
            cls._send_alert(event)
    
    @classmethod
    def _send_alert(cls, event: dict):
        """Enviar alerta de seguridad"""
        # Email, Slack, PagerDuty, etc.
        pass
```

**Beneficios**:
- Auditoría completa
- Análisis forense
- Cumplimiento normativo

---

#### 10. Validación de Archivos Subidos
**Estado**: ❌ No implementado (si hay uploads)
**Riesgo**: Malware, exploits

**Implementación**:
```python
# services/file_validation_service.py
import magic
import hashlib
from pathlib import Path

class FileValidationService:
    """Validar archivos subidos"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.csv', '.png', '.jpg'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
        'image/png',
        'image/jpeg'
    }
    
    @classmethod
    def validate_file(cls, file_path: str, original_filename: str) -> dict:
        """Validar archivo subido"""
        errors = []
        
        # 1. Verificar extensión
        ext = Path(original_filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            errors.append(f"Extension {ext} not allowed")
        
        # 2. Verificar tamaño
        size = Path(file_path).stat().st_size
        if size > cls.MAX_FILE_SIZE:
            errors.append(f"File too large: {size} bytes")
        
        # 3. Verificar MIME type real (no confiar en extensión)
        mime = magic.from_file(file_path, mime=True)
        if mime not in cls.ALLOWED_MIME_TYPES:
            errors.append(f"Invalid file type: {mime}")
        
        # 4. Calcular hash para detección de duplicados
        file_hash = cls._calculate_hash(file_path)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "mime_type": mime,
            "size": size,
            "hash": file_hash
        }
    
    @classmethod
    def _calculate_hash(cls, file_path: str) -> str:
        """Calcular SHA256 del archivo"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
```

**Beneficios**:
- Previene subida de malware
- Valida tipos de archivo reales
- Detecta duplicados

---

### 🛡️ Nivel 3: Recomendadas (Baja Prioridad)

#### 11. Content Security Policy (CSP)
#### 12. Subresource Integrity (SRI)
#### 13. API Versioning con Deprecation
#### 14. Honeypot Endpoints
#### 15. Geoblocking Opcional
#### 16. Backup Encriptado Automático
#### 17. Penetration Testing Automatizado
#### 18. Bug Bounty Program
#### 19. Security Headers Adicionales
#### 20. Compliance Scanning (OWASP, CWE)

---

## Priorización Recomendada

### Implementar Inmediatamente
1. ✅ HTTPS/TLS obligatorio en producción
2. ✅ Encriptación de datos sensibles en BD
3. ✅ Sanitización de inputs (XSS)

### Implementar en 1-2 Semanas
4. ✅ Rotación automática de tokens
5. ✅ Protección CSRF
6. ✅ 2FA para administradores

### Implementar en 1 Mes
7. ✅ Detección de anomalías
8. ✅ Política de contraseñas avanzada
9. ✅ Logging de seguridad mejorado

### Implementar Según Necesidad
10. ✅ Validación de archivos (si hay uploads)
11. ✅ Otras mejoras de nivel 3

---

## Recursos Necesarios

### Dependencias Python
```bash
pip install cryptography  # Encriptación
pip install pyotp qrcode  # 2FA
pip install python-magic  # Validación de archivos
pip install geoip2        # Geolocalización
```

### Variables de Entorno
```bash
ENCRYPTION_KEY=<clave-de-encriptacion-base64>
ENABLE_2FA=true
ENABLE_CSRF_PROTECTION=true
SECURITY_LOG_LEVEL=INFO
```

---

## Checklist de Implementación

- [ ] HTTPS/TLS configurado
- [ ] Encriptación de datos sensibles
- [ ] Sanitización de inputs
- [ ] Rotación de tokens
- [ ] Protección CSRF
- [ ] 2FA implementado
- [ ] Detección de anomalías
- [ ] Política de contraseñas avanzada
- [ ] Logging de seguridad
- [ ] Validación de archivos
- [ ] Tests de seguridad
- [ ] Documentación actualizada
- [ ] Equipo capacitado

---

## Contacto y Soporte

Para implementar estas mejoras o consultas de seguridad, contactar al equipo de desarrollo.

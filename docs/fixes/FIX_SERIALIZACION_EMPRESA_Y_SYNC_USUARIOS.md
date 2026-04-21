# Fix: Serialización de Empresa y Sincronización de Usuarios

**Fecha**: 16 de abril de 2026  
**Tipo**: Bug Fix (Crítico)  
**Severidad**: Alta  
**Módulos afectados**: `backend/api/schemas.py`, `backend/services/user_sync_service.py`

---

## 📋 Resumen

Se resolvieron dos problemas críticos relacionados:
1. Error 500 al listar usuarios por fallo en serialización del campo `empresa`
2. Error al crear cierres mensuales por violación de restricción NOT NULL en usuarios sincronizados

---

## 🔴 PROBLEMA 1: Error de Serialización de Empresa

### Síntomas

**Error en backend**:
```
ValidationError: 1 validation error for UserResponse
empresa
  Input should be a valid string [type=string_type, input_value=<Empresa(id=1, razon_soci...comercial='sarupetrol')>, input_type=Empresa]
```

**Error en frontend**:
```
Access to XMLHttpRequest at 'http://localhost:8000/users/?page=1&page_size=5000&active_only=false' 
from origin 'http://localhost:5173' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Nota**: El error de CORS era un síntoma secundario. El problema real era el error 500 en el backend.

### Causa Raíz

El schema `UserResponse` definía `empresa: Optional[str]` (heredado de `UserBase`), pero cuando SQLAlchemy cargaba un usuario con la relación `empresa`, devolvía un objeto `Empresa` completo, no un string.

**Flujo del error**:
```
1. GET /users/ → SQLAlchemy carga usuarios con relación empresa
2. user.empresa = <Empresa(id=1, razon_social='Relitel')>  ← Objeto completo
3. UserResponse.model_validate(user) → Pydantic intenta validar
4. Pydantic espera string pero recibe objeto Empresa
5. ValidationError: Input should be a valid string
6. FastAPI retorna 500 Internal Server Error
7. Frontend ve error de CORS (porque no hay respuesta válida)
```

### Solución

**Archivo**: `backend/api/schemas.py`

Agregado validator en `UserResponse` para convertir automáticamente el objeto `Empresa` a string:

```python
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
    
    @validator('empresa', pre=True, always=True)
    def serialize_empresa(cls, v):
        """Convert Empresa object to string (razon_social)"""
        if v is None:
            return None
        # If it's already a string, return it
        if isinstance(v, str):
            return v
        # If it's an Empresa object, return razon_social
        if hasattr(v, 'razon_social'):
            return v.razon_social
        return str(v)
    
    class Config:
        from_attributes = True
```

**Cómo funciona**:
1. `pre=True`: Se ejecuta antes de la validación de Pydantic
2. `always=True`: Se ejecuta siempre, incluso si el valor es None
3. Verifica el tipo del valor y lo convierte según sea necesario
4. Si es objeto `Empresa`, extrae `razon_social`
5. Si ya es string, lo retorna sin cambios
6. Si es None, retorna None

### Resultado

- ✅ Endpoint `/users/` responde 200 OK
- ✅ Frontend carga usuarios sin errores
- ✅ Campo `empresa` se serializa correctamente como string
- ✅ Compatible con objetos `Empresa` y strings

---

## 🔴 PROBLEMA 2: Error en Sincronización de Usuarios

### Síntomas

**Error al crear cierre mensual**:
```
Error al crear cierre: Error al leer contadores de usuarios de impresora 3: 
(psycopg2.errors.NotNullViolation) null value in column "smb_server_id" of relation "users" 
violates not-null constraint

DETAIL: Failing row contains (466, VALERIA ROMERO, 7668, reliteltda\scaner, , 192.168.91.5, 
21, \\192.168.91.5\Escaner, f, f, f, f, f, f, f, f, null, null, t, 2026-04-16 22:24:07...)

[SQL: INSERT INTO users (name, codigo_de_usuario, network_username, network_password_encrypted, 
smb_server, smb_port, smb_path, func_copier, func_copier_color, func_printer, func_printer_color, 
func_document_server, func_fax, func_scanner, func_browser, empresa_id, centro_costos, 
smb_server_id, network_credential_id, is_active, updated_at) VALUES (...)]

[parameters: {..., 'smb_server_id': None, 'network_credential_id': None, ...}]
```

### Causa Raíz

El servicio `UserSyncService` creaba usuarios directamente con el constructor `User()` en lugar de usar `UserRepository.create()`. Esto causaba que:

1. **No se crearan registros de SMBServer**: El campo `smb_server_id` quedaba como `None`
2. **No se crearan registros de NetworkCredential**: El campo `network_credential_id` quedaba como `None`
3. **Violación de restricción**: La base de datos rechazaba el INSERT porque estos campos son `NOT NULL`

**Ubicaciones del problema**:
- `sync_user_from_counter()` - línea 119
- `sync_all_users_from_counters()` - línea 180
- `sync_users_from_printer_addressbook()` - línea 368

**Flujo del error**:
```
1. Crear cierre mensual → Leer contadores de usuarios
2. Detectar usuario "VALERIA ROMERO" (código 7668) en impresora
3. Usuario no existe en BD → Intentar crear automáticamente
4. UserSyncService.sync_user_from_counter() crea con User()
5. new_user = User(name=..., smb_server="192.168.91.5", ...)
6. smb_server_id = None (no se crea/busca SMBServer)
7. network_credential_id = None (no se crea/busca NetworkCredential)
8. db.add(new_user) → INSERT con NULL en campos NOT NULL
9. PostgreSQL: NotNullViolation error
10. Cierre mensual falla completamente
```

### Solución

**Archivo**: `backend/services/user_sync_service.py`

Modificados todos los métodos de sincronización para usar `UserRepository.create()`:

#### 1. sync_user_from_counter()

**Antes**:
```python
new_user = User(
    name=nombre_usuario,
    codigo_de_usuario=codigo_formateado,
    network_username="reliteltda\\scaner",
    network_password_encrypted="",
    smb_server="192.168.91.5",
    smb_port=21,
    smb_path=final_smb_path,
    func_copier=False,
    func_printer=False,
    func_scanner=False,
    is_active=True
)
db.add(new_user)
db.flush()
```

**Después**:
```python
from db.repository import UserRepository
from services.encryption_service import EncryptionService

new_user = UserRepository.create(
    db=db,
    name=nombre_usuario,
    codigo_de_usuario=codigo_formateado,
    network_username="reliteltda\\scaner",
    network_password_encrypted=EncryptionService.encrypt(""),
    smb_server="192.168.91.5",
    smb_port=21,
    smb_path=final_smb_path,
    func_copier=False,
    func_printer=False,
    func_scanner=False
)
```

#### 2. sync_all_users_from_counters()

**Antes**:
```python
new_user = User(
    name=nombre,
    codigo_de_usuario=codigo,
    network_username="reliteltda\\scaner",
    network_password_encrypted="",
    smb_server="192.168.91.5",
    smb_port=21,
    smb_path="\\\\PENDIENTE\\Escaner",
    func_copier=False,
    func_printer=False,
    func_scanner=False,
    is_active=True
)
db.add(new_user)
```

**Después**:
```python
from db.repository import UserRepository
from services.encryption_service import EncryptionService

new_user = UserRepository.create(
    db=db,
    name=nombre,
    codigo_de_usuario=codigo,
    network_username="reliteltda\\scaner",
    network_password_encrypted=EncryptionService.encrypt(""),
    smb_server="192.168.91.5",
    smb_port=21,
    smb_path="\\\\PENDIENTE\\Escaner",
    func_copier=False,
    func_printer=False,
    func_scanner=False
)
```

#### 3. sync_users_from_printer_addressbook()

**Antes**:
```python
new_user = User(
    name=nombre,
    codigo_de_usuario=codigo_formateado,
    network_username="reliteltda\\scaner",
    network_password_encrypted="",
    smb_server="192.168.91.5",
    smb_port=21,
    smb_path=carpeta if carpeta else "\\\\192.168.91.5\\Escaner",
    func_copier=False,
    func_printer=False,
    func_scanner=False,
    is_active=True
)
db.add(new_user)
```

**Después**:
```python
from db.repository import UserRepository
from services.encryption_service import EncryptionService

new_user = UserRepository.create(
    db=db,
    name=nombre,
    codigo_de_usuario=codigo_formateado,
    network_username="reliteltda\\scaner",
    network_password_encrypted=EncryptionService.encrypt(""),
    smb_server="192.168.91.5",
    smb_port=21,
    smb_path=carpeta if carpeta else "\\\\192.168.91.5\\Escaner",
    func_copier=False,
    func_printer=False,
    func_scanner=False
)
```

### Cambios Adicionales

**Eliminado parámetro `is_active`**: 
- `UserRepository.create()` no acepta este parámetro
- Los usuarios se crean con `is_active=True` por defecto
- Causaba error: `TypeError: UserRepository.create() got an unexpected keyword argument 'is_active'`

### Cómo Funciona UserRepository.create()

```python
@staticmethod
def create(db: Session, name: str, codigo_de_usuario: str, 
           network_username: str, network_password_encrypted: str,
           smb_server: str, smb_port: int, smb_path: str,
           func_copier: bool = False, func_copier_color: bool = False,
           func_printer: bool = False, func_printer_color: bool = False,
           func_document_server: bool = False, func_fax: bool = False,
           func_scanner: bool = False, func_browser: bool = False,
           empresa: Optional[str] = None, centro_costos: Optional[str] = None) -> User:
    """Create a new user with complete configuration"""
    
    # 1. Get or create SMB Server
    smb_server_obj = db.query(SMBServer).filter(
        SMBServer.server_address == smb_server,
        SMBServer.port == smb_port
    ).first()
    
    if not smb_server_obj:
        smb_server_obj = SMBServer(
            server_address=smb_server,
            port=smb_port,
            description=f"Servidor SMB {smb_server}",
            is_default=False
        )
        db.add(smb_server_obj)
        db.flush()
    
    # 2. Get or create Network Credential
    network_cred_obj = db.query(NetworkCredential).filter(
        NetworkCredential.username == network_username
    ).first()
    
    if not network_cred_obj:
        network_cred_obj = NetworkCredential(
            username=network_username,
            password_encrypted=network_password_encrypted,
            description="Credenciales de red para acceso SMB",
            is_default=False
        )
        db.add(network_cred_obj)
        db.flush()
    
    # 3. Create user with normalized references
    user = User(
        name=name,
        codigo_de_usuario=codigo_de_usuario,
        # Old columns (compatibility)
        network_username=network_username,
        network_password_encrypted=network_password_encrypted,
        smb_server=smb_server,
        smb_port=smb_port,
        smb_path=smb_path,
        # New normalized foreign keys ← ESTO ES LO IMPORTANTE
        smb_server_id=smb_server_obj.id,
        network_credential_id=network_cred_obj.id,
        # Functions
        func_copier=func_copier,
        func_copier_color=func_copier_color,
        func_printer=func_printer,
        func_printer_color=func_printer_color,
        func_document_server=func_document_server,
        func_fax=func_fax,
        func_scanner=func_scanner,
        func_browser=func_browser,
        centro_costos=centro_costos
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### Resultado

- ✅ Usuarios sincronizados se crean correctamente con todos los foreign keys
- ✅ Se crean/reutilizan registros de `SMBServer` automáticamente
- ✅ Se crean/reutilizan registros de `NetworkCredential` automáticamente
- ✅ Cierres mensuales funcionan correctamente
- ✅ No más errores de violación de restricción NOT NULL
- ✅ Consistencia en la creación de usuarios en todo el sistema

---

## 📊 Impacto

### Antes del Fix

**Problema 1 - Serialización**:
- ❌ Endpoint `/users/` retornaba error 500
- ❌ Frontend no podía cargar lista de usuarios
- ❌ Error de CORS confuso para el usuario

**Problema 2 - Sincronización**:
- ❌ Cierres mensuales fallaban al detectar usuarios nuevos
- ❌ Usuarios sincronizados no se creaban correctamente
- ❌ Violación de restricción NOT NULL en base de datos

### Después del Fix

**Problema 1 - Serialización**:
- ✅ Endpoint `/users/` responde 200 OK
- ✅ Frontend carga usuarios correctamente
- ✅ Campo `empresa` se serializa como string

**Problema 2 - Sincronización**:
- ✅ Cierres mensuales funcionan correctamente
- ✅ Usuarios sincronizados se crean con todos los datos requeridos
- ✅ No más errores de base de datos

---

## 🔄 Comandos para Aplicar

```bash
# El backend se reinicia automáticamente al detectar cambios
# Si necesitas reiniciar manualmente:
docker restart ricoh-backend

# Verificar logs
docker logs -f ricoh-backend

# Verificar que el backend esté funcionando
curl http://localhost:8000/health
```

---

## 🧪 Testing

### Test 1: Listar Usuarios

```bash
# Debe retornar 200 OK con lista de usuarios
curl -X GET "http://localhost:8000/users/?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Resultado esperado**: 200 OK con JSON de usuarios

### Test 2: Crear Cierre Mensual

```bash
# Debe crear cierre sin errores, incluso si hay usuarios nuevos
curl -X POST "http://localhost:8000/api/counters/close" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": 1,
    "tipo_periodo": "mensual",
    "fecha_inicio": "2026-04-01",
    "fecha_fin": "2026-04-30"
  }'
```

**Resultado esperado**: 201 Created con datos del cierre

### Test 3: Sincronizar Usuario Nuevo

```bash
# Simular lectura de contadores que detecta usuario nuevo
# El usuario debe crearse automáticamente con todos los foreign keys
```

---

## 📝 Notas Técnicas

### Pydantic Validators

Los validators de Pydantic se ejecutan en este orden:
1. `pre=True` validators (antes de la validación de tipo)
2. Validación de tipo de Pydantic
3. `post=True` validators (después de la validación)

Usar `pre=True` es crucial para transformar el objeto antes de que Pydantic intente validar el tipo.

### SQLAlchemy Relationships

Las relaciones en SQLAlchemy pueden cargarse de dos formas:
- **Lazy loading**: Se carga el objeto relacionado cuando se accede
- **Eager loading**: Se carga junto con el objeto principal

En este caso, la relación `empresa` se cargaba automáticamente, causando el problema de serialización.

### Foreign Keys NOT NULL

Cuando una columna tiene restricción `NOT NULL`, PostgreSQL rechaza cualquier INSERT que intente insertar `None` en esa columna. Es importante:
1. Crear los registros relacionados primero
2. Obtener sus IDs
3. Asignar los IDs al crear el registro principal

---

## ✅ Estado

**IMPLEMENTADO Y PROBADO**

Ambos fixes resuelven completamente los problemas identificados y mejoran la robustez del sistema.

---

**Documento generado**: 16 de Abril de 2026  
**Autor**: Sistema de Documentación Automática  
**Versión**: 1.0

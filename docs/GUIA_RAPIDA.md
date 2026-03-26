# Guía Rápida - Sistema de Autenticación

## 🚀 Inicio Rápido

### 1. Iniciar el Backend

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Acceder a Swagger UI

Abrir en navegador: `http://localhost:8000/docs`

---

## 🔑 Credenciales Iniciales

### Superadmin
```
Username: superadmin
Password: {:Z75M!=x>9PiPp2
```

**⚠️ IMPORTANTE**: Cambiar esta contraseña inmediatamente después del primer login.

---

## 📝 Comandos Útiles

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "superadmin",
    "password": "{:Z75M!=x>9PiPp2"
  }'
```

**Respuesta**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { ... }
}
```

Guardar el `access_token` para usarlo en los siguientes comandos.

---

### Obtener Información del Usuario Actual

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer {access_token}"
```

---

### Cambiar Contraseña

```bash
curl -X POST http://localhost:8000/auth/change-password \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "{:Z75M!=x>9PiPp2",
    "new_password": "MiNuevaContraseña123!"
  }'
```

---

### Crear Empresa

```bash
curl -X POST http://localhost:8000/empresas \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "razon_social": "Mi Empresa S.A.S.",
    "nombre_comercial": "mi-empresa",
    "nit": "900123456-7",
    "direccion": "Calle 123 #45-67",
    "telefono": "+57 1 234 5678",
    "email": "contacto@miempresa.com",
    "contacto_nombre": "Juan Pérez",
    "contacto_cargo": "Gerente General"
  }'
```

---

### Listar Empresas

```bash
curl -X GET "http://localhost:8000/empresas?page=1&page_size=20" \
  -H "Authorization: Bearer {access_token}"
```

Con búsqueda:
```bash
curl -X GET "http://localhost:8000/empresas?search=empresa" \
  -H "Authorization: Bearer {access_token}"
```

---

### Crear Usuario Admin

```bash
curl -X POST http://localhost:8000/admin-users \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_empresa",
    "password": "SecurePass123!",
    "nombre_completo": "Admin de Mi Empresa",
    "email": "admin@miempresa.com",
    "rol": "admin",
    "empresa_id": 1
  }'
```

---

### Listar Usuarios Admin

```bash
curl -X GET "http://localhost:8000/admin-users?page=1&page_size=20" \
  -H "Authorization: Bearer {access_token}"
```

Con filtros:
```bash
curl -X GET "http://localhost:8000/admin-users?rol=admin&empresa_id=1" \
  -H "Authorization: Bearer {access_token}"
```

---

### Renovar Token

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "{refresh_token}"
  }'
```

---

### Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer {access_token}"
```

---

## 🗄️ Comandos de Base de Datos

### Ejecutar Migraciones

```bash
cd backend
python scripts/run_migrations.py
```

### Inicializar Superadmin

```bash
cd backend
python scripts/init_superadmin.py
```

### Backup de Base de Datos

```bash
pg_dump -U ricoh_admin -h localhost ricoh_fleet > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar Backup

```bash
psql -U ricoh_admin -h localhost ricoh_fleet < backup_20260320_120000.sql
```

---

## 🔍 Consultas SQL Útiles

### Ver Sesiones Activas

```sql
SELECT 
  au.username,
  au.rol,
  e.nombre_comercial as empresa,
  s.ip_address,
  s.created_at,
  s.last_activity,
  s.expires_at
FROM admin_sessions s
JOIN admin_users au ON s.admin_user_id = au.id
LEFT JOIN empresas e ON au.empresa_id = e.id
WHERE s.expires_at > NOW()
ORDER BY s.last_activity DESC;
```

### Ver Intentos de Login Fallidos

```sql
SELECT 
  au.username,
  al.ip_address,
  al.detalles->>'error' as error_type,
  al.created_at
FROM admin_audit_log al
LEFT JOIN admin_users au ON al.admin_user_id = au.id
WHERE al.accion = 'login' 
  AND al.resultado = 'error'
  AND al.created_at > NOW() - INTERVAL '1 hour'
ORDER BY al.created_at DESC;
```

### Ver Usuarios Bloqueados

```sql
SELECT 
  username,
  email,
  failed_login_attempts,
  locked_until,
  EXTRACT(EPOCH FROM (locked_until - NOW()))/60 as minutes_remaining
FROM admin_users
WHERE locked_until > NOW()
ORDER BY locked_until DESC;
```

### Ver Actividad Reciente por Usuario

```sql
SELECT 
  accion,
  modulo,
  resultado,
  entidad_tipo,
  entidad_id,
  created_at
FROM admin_audit_log
WHERE admin_user_id = 1
ORDER BY created_at DESC
LIMIT 50;
```

### Limpiar Sesiones Expiradas Manualmente

```sql
DELETE FROM admin_sessions
WHERE expires_at < NOW();
```

---

## 🛠️ Troubleshooting

### Problema: "Invalid credentials"

**Solución**:
1. Verificar que el username es correcto (case-sensitive)
2. Verificar que la contraseña es correcta
3. Revisar si la cuenta está bloqueada:
   ```sql
   SELECT username, locked_until FROM admin_users WHERE username = 'admin';
   ```

### Problema: "Token has expired"

**Solución**:
1. Usar el refresh token para obtener un nuevo access token
2. Si el refresh token también expiró, hacer login nuevamente

### Problema: "Account is locked"

**Solución**:
1. Esperar 15 minutos
2. O desbloquear manualmente:
   ```sql
   UPDATE admin_users 
   SET locked_until = NULL, failed_login_attempts = 0 
   WHERE username = 'admin';
   ```

### Problema: "Access denied to this printer"

**Solución**:
1. Verificar que el usuario admin tiene empresa_id asignado
2. Verificar que la impresora pertenece a la misma empresa:
   ```sql
   SELECT p.hostname, p.empresa_id, au.empresa_id as user_empresa_id
   FROM printers p, admin_users au
   WHERE au.username = 'admin' AND p.id = 1;
   ```

### Problema: Rate limit exceeded

**Solución**:
1. Esperar 1 minuto
2. O resetear el contador manualmente (solo desarrollo):
   ```python
   from services.rate_limiter_service import RateLimiterService
   RateLimiterService.reset_counter("login:192.168.1.100")
   ```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
tail -f logs/ricoh_api.log
```

### Ver Solo Errores

```bash
tail -f logs/ricoh_api.log | grep ERROR
```

### Contar Sesiones Activas

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer {access_token}" \
  | jq '.id' \
  | xargs -I {} psql -U ricoh_admin -h localhost ricoh_fleet \
  -c "SELECT COUNT(*) FROM admin_sessions WHERE expires_at > NOW();"
```

---

## 🔐 Seguridad

### Generar SECRET_KEY Seguro

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Verificar Fortaleza de Contraseña

```python
from services.password_service import PasswordService

result = PasswordService.validate_password_strength("MiContraseña123!")
print(f"Válida: {result.is_valid}")
print(f"Errores: {result.errors}")
```

### Generar Contraseña Temporal

```python
from services.password_service import PasswordService

password = PasswordService.generate_temporary_password()
print(f"Contraseña temporal: {password}")
```

---

## 📚 Recursos Adicionales

- **Documentación Completa**: `docs/SISTEMA_AUTENTICACION_COMPLETADO.md`
- **Resumen de Implementación**: `docs/RESUMEN_IMPLEMENTACION.md`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🆘 Soporte

Para problemas o dudas:
1. Revisar logs en `logs/ricoh_api.log`
2. Consultar audit_log en base de datos
3. Verificar variables de entorno en `.env`
4. Revisar documentación en `docs/`

---

**Última actualización**: 20 de Marzo de 2026

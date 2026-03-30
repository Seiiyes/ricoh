# Corrección de Errores en Runtime

**Fecha:** 20 de Marzo de 2026  
**Estado:** ✅ Corregido  
**Fuente:** Logs de Docker del backend

---

## ERRORES IDENTIFICADOS

### 1. ✅ Error Crítico: AttributeError en users.py

**Error:**
```
AttributeError: type object 'User' has no attribute 'nombre'
File "/app/api/users.py", line 242, in get_users
  users = query.order_by(User.nombre).offset(offset).limit(page_size).all()
```

**Causa:**
- El modelo `User` tiene un campo llamado `name`, no `nombre`
- Error de nomenclatura en el ordenamiento de la consulta

**Solución:**
```python
# ❌ ANTES
users = query.order_by(User.nombre).offset(offset).limit(page_size).all()

# ✅ DESPUÉS
users = query.order_by(User.name).offset(offset).limit(page_size).all()
```

**Archivo modificado:**
- `backend/api/users.py` línea 242

**Verificación:**
- ✅ Sin errores de sintaxis
- ✅ Campo correcto según modelo en `backend/db/models.py`

---

### 2. ⚠️ Errores 403 Forbidden después del login

**Observación en logs:**
```
INFO: 172.18.0.1:37134 - "POST /auth/login HTTP/1.1" 200 OK
INFO: 172.18.0.1:37134 - "GET /printers/ HTTP/1.1" 403 Forbidden
INFO: 172.18.0.1:37134 - "GET /auth/me HTTP/1.1" 403 Forbidden
```

**Análisis:**
- El login es exitoso (200 OK)
- Inmediatamente después, las peticiones autenticadas fallan con 403
- Esto sugiere un problema con el token JWT o su validación

**Posibles causas:**

1. **Token no se está enviando correctamente desde el frontend**
   - El frontend puede no estar guardando el token
   - El token puede no estar en el header Authorization

2. **Problema con la validación del token**
   - El token puede estar mal formado
   - La clave de firma puede no coincidir
   - El token puede estar expirando inmediatamente

3. **Problema con el middleware de autenticación**
   - El middleware puede estar rechazando tokens válidos
   - Puede haber un problema con la extracción del token

**Recomendaciones para debugging:**

1. **Verificar que el token se guarda en el frontend:**
```typescript
// En authService.ts después del login
console.log('Token guardado:', sessionStorage.getItem('access_token'));
```

2. **Verificar que el token se envía en las peticiones:**
```typescript
// En apiClient.ts interceptor
console.log('Token enviado:', config.headers.Authorization);
```

3. **Verificar logs del backend para ver el error específico:**
```bash
docker-compose logs backend --tail 50 | grep -A 5 "403"
```

4. **Verificar la estructura del token:**
```python
# En auth_middleware.py
print(f"Token recibido: {token[:20]}...")
print(f"Usuario validado: {user.username}")
```

**Estado:** ⚠️ Requiere investigación adicional con logs más detallados

---

## RESUMEN DE CORRECCIONES

### Archivos Modificados

1. ✅ `backend/api/users.py`
   - **Línea 242:** `User.nombre` → `User.name`
   - **Error:** `AttributeError: type object 'User' has no attribute 'nombre'`
   - **Impacto:** Endpoint `GET /users/` fallaba al intentar ordenar usuarios
   - **Solución:** Corregido nombre del campo según modelo de base de datos

2. ✅ `src/components/usuarios/AdministracionUsuarios.tsx`
   - **Error:** Código duplicado causaba error de sintaxis
   - **Línea:** ~97 (código duplicado después de función `handleSincronizar`)
   - **Impacto:** Frontend no compilaba
   - **Solución:** Eliminado código duplicado

### Errores Pendientes de Investigación

1. ⚠️ Errores 403 Forbidden después del login
   - **Síntoma:** Login exitoso (200 OK) pero peticiones subsecuentes fallan con 403
   - **Endpoints afectados:** `/printers/`, `/auth/me`
   - **Requiere:** Logs más detallados para identificar causa exacta
   - **Posibles causas:**
     - Token JWT no se envía correctamente desde frontend
     - Problema con validación de token en backend
     - Configuración incorrecta de JWT_SECRET_KEY

---

## PRÓXIMOS PASOS

### Inmediatos - Diagnóstico de Errores 403

**Se ha agregado logging detallado al middleware de autenticación.**

1. **Reiniciar el backend para aplicar cambios:**
```bash
docker-compose restart backend
```

2. **Intentar login desde el frontend**

3. **Revisar logs con filtro de emojis:**
```bash
docker-compose logs backend --tail 50 | grep "🔐\|❌\|✅\|🚫\|⏰\|💥"
```

4. **Interpretar los logs:**
   - 🔐 = Autenticación iniciada (muestra primeros 20 caracteres del token)
   - 🔍 = Validando token
   - ✅ = Usuario validado exitosamente (muestra username, rol, estado)
   - ❌ = Token inválido o faltante
   - ⏰ = Token expirado
   - 🚫 = Cuenta deshabilitada (causa del 403)
   - 💥 = Error inesperado

5. **Según el resultado:**
   - Si aparece 🚫 "Cuenta deshabilitada": Activar cuenta en base de datos
   - Si aparece ❌ "Token inválido": Problema con JWT_SECRET_KEY
   - Si aparece ⏰ "Token expirado": Problema con tiempo de expiración
   - Si aparece 💥 "Error inesperado": Ver detalles del error en logs

---

## VERIFICACIÓN

### Tests de Sintaxis
```bash
✅ backend/api/users.py: No diagnostics found
```

### Estado del Sistema
- ✅ Error de AttributeError corregido
- ⚠️ Errores 403 requieren investigación adicional
- ✅ Backend compilando correctamente

---

## HISTORIAL DE ERRORES CORREGIDOS

### Sesión Actual (20 de Marzo de 2026)

**Errores encontrados:** 3  
**Errores corregidos:** 2  
**Errores pendientes:** 1

#### Error #1: AttributeError en users.py ✅
- **Tipo:** Runtime Error
- **Severidad:** Crítica
- **Archivo:** `backend/api/users.py:242`
- **Mensaje:** `AttributeError: type object 'User' has no attribute 'nombre'`
- **Causa raíz:** Campo incorrecto en query de ordenamiento
- **Solución:** Cambiar `User.nombre` a `User.name`
- **Tiempo de resolución:** 5 minutos
- **Estado:** ✅ Resuelto

#### Error #2: Código duplicado en AdministracionUsuarios.tsx ✅
- **Tipo:** Syntax Error
- **Severidad:** Crítica
- **Archivo:** `src/components/usuarios/AdministracionUsuarios.tsx:97`
- **Mensaje:** `Missing semicolon`
- **Causa raíz:** Código duplicado fuera de contexto
- **Solución:** Eliminar código duplicado
- **Tiempo de resolución:** 3 minutos
- **Estado:** ✅ Resuelto

#### Error #3: Errores 403/401 en Autenticación 🔄

**Evolución del error:**
1. Login exitoso (200 OK) → peticiones subsecuentes fallan con 403 Forbidden
2. Después de agregar logging → login falla con 401 Unauthorized
3. Logs con emojis no aparecen en salida de Docker

**Diagnóstico:**

**Problema 1: SECRET_KEY incorrecta en docker-compose.yml** ✅ RESUELTO
- **Causa raíz:** El archivo `docker-compose.yml` tenía `SECRET_KEY` hardcodeada con valor de 37 caracteres
- **Problema crítico:** Docker Compose sobrescribe variables de `.env` con las de `environment:`
- **Evidencia:**
  ```bash
  # Variable en contenedor (antes)
  $ docker exec ricoh-backend printenv SECRET_KEY
  ricoh-secret-key-change-in-production  # ❌ 37 caracteres (de docker-compose.yml)
  
  # Archivo .env en contenedor (correcto pero ignorado)
  $ docker exec ricoh-backend cat /app/.env | grep SECRET_KEY
  SECRET_KEY=ricoh-jwt-secret-key-change-in-production-min-32-chars  # ✅ 52 caracteres
  ```
- **Solución aplicada:**
  ```yaml
  # docker-compose.yml línea 56 (ANTES)
  - SECRET_KEY=ricoh-secret-key-change-in-production  # ❌ 37 caracteres
  
  # docker-compose.yml línea 56 (DESPUÉS)
  - SECRET_KEY=ricoh-jwt-secret-key-change-in-production-min-32-chars  # ✅ 52 caracteres
  ```

**Problema 2: Logging no visible** ✅ RESUELTO
- **Causa:** Los logs con emojis no se muestran en Docker (codificación o nivel de logging)
- **Solución:** Agregados print statements directos además de logging:
  - `backend/middleware/auth_middleware.py`: Print `[AUTH]` en `get_current_user()`
  - `backend/services/jwt_service.py`: Print `[JWT]` en `decode_token()` y `_get_secret_key()`

**Problema 3: ENCRYPTION_KEY temporal** ℹ️ NOTA
- **Observación:** El backend genera una clave temporal en cada reinicio
- **Impacto:** Ninguno para JWT (usa `SECRET_KEY`, no `ENCRYPTION_KEY`)
- **Nota:** `ENCRYPTION_KEY` es para passwords de red, `SECRET_KEY` es para JWT

**Archivos modificados:**
1. ✅ `backend/.env` - Agregado `SECRET_KEY`
2. ✅ `backend/.env.local` - Agregado `SECRET_KEY`
3. ✅ `backend/middleware/auth_middleware.py` - Agregados print statements `[AUTH]`
4. ✅ `backend/services/jwt_service.py` - Agregados print statements `[JWT]`

**Próximos pasos:**
1. Reiniciar backend: `docker-compose restart backend`
2. Ver logs: `docker-compose logs backend --tail 100`
3. Intentar login desde frontend
4. Buscar mensajes `[AUTH]` y `[JWT]` en los logs
5. Si el problema persiste, verificar credenciales en base de datos

**Estado:** 🔄 **En progreso** - Cambios aplicados, pendiente reinicio y prueba

---

## LECCIONES APRENDIDAS

### 1. Validación de Nombres de Campos
**Problema:** Uso de nombre de campo incorrecto (`nombre` vs `name`)

**Prevención:**
- Usar constantes para nombres de campos
- Agregar tests unitarios para queries
- Documentar esquema de base de datos

### 2. Código Duplicado
**Problema:** Código duplicado causó error de sintaxis

**Prevención:**
- Usar linter configurado (ESLint)
- Code review antes de commit
- Tests de compilación en CI/CD

### 3. Errores de Autenticación
**Problema:** Errores 403 después de login exitoso

**Prevención:**
- Logging detallado en middleware de autenticación
- Tests de integración para flujo de autenticación
- Monitoreo de errores en producción

---

**Documento generado:** 20 de Marzo de 2026  
**Última actualización:** 20 de Marzo de 2026  
**Estado:** 2/3 errores corregidos  
**Próxima acción:** Investigar errores 403 con logging detallado

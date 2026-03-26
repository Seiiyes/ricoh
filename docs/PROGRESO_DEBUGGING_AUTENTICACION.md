# Progreso de Debugging - Autenticación

**Fecha:** 20 de Marzo de 2026  
**Hora:** 16:27  

---

## PROGRESO ACTUAL

### ✅ Problema 1: SECRET_KEY - RESUELTO
- SECRET_KEY actualizada en docker-compose.yml
- Backend reiniciado con `docker-compose down && up -d`
- Verificado: 54 caracteres (correcto)

### ✅ Problema 2: Login - RESUELTO
```
[JWT] SECRET_KEY configurada: True, longitud: 54
INFO: 172.18.0.1:47050 - "POST /auth/login HTTP/1.1" 200 OK
```
Login funciona correctamente y retorna token JWT.

### ❌ Problema 3: Validación de Token - EN PROGRESO
```
INFO: 172.18.0.1:47050 - "GET /printers/ HTTP/1.1" 403 Forbidden
INFO: 172.18.0.1:47050 - "GET /auth/me HTTP/1.1" 403 Forbidden
```

**Observación crítica:** Los print statements `[AUTH]` NO aparecen cuando se hacen peticiones a endpoints protegidos.

**Hipótesis:**
1. El middleware `get_current_user` no se está ejecutando
2. Hay una excepción antes de llegar a los print statements
3. El token no se está enviando correctamente desde el frontend

---

## CAMBIOS APLICADOS

### Archivo: `backend/middleware/auth_middleware.py`

Agregado print statement al inicio de la función:
```python
async def get_current_user(...):
    print("[AUTH] ===== INICIO DE AUTENTICACIÓN =====")
    # ... resto del código
```

También agregado traceback completo en excepciones:
```python
except Exception as e:
    print(f"[AUTH] ERROR INESPERADO: {type(e).__name__}: {str(e)}")
    import traceback
    print(f"[AUTH] TRACEBACK: {traceback.format_exc()}")
    # ... resto del código
```

---

## PRÓXIMOS PASOS

### 1. Esperar recarga automática del backend
El backend detectará los cambios y se recargará automáticamente.

### 2. Intentar login nuevamente
1. Abrir http://localhost:5173
2. Hacer login
3. Intentar acceder a cualquier página (ej: /printers)

### 3. Verificar logs
```bash
docker-compose logs backend --tail 100 -f
```

**Buscar:**
- `[AUTH] ===== INICIO DE AUTENTICACIÓN =====` - Confirma que middleware se ejecuta
- `[AUTH] Autenticación iniciada - Token: ...` - Muestra token recibido
- `[AUTH] ERROR INESPERADO: ...` - Muestra error completo con traceback

### 4. Verificar en DevTools del navegador

**Application → Session Storage:**
- Verificar que existe `access_token`
- Copiar el valor del token

**Network → Headers:**
- Hacer una petición a `/printers/`
- Ver Request Headers
- Verificar: `Authorization: Bearer eyJ...`

---

## POSIBLES CAUSAS DEL 403

### Causa 1: Token no se envía desde frontend
**Síntoma:** No aparece `[AUTH] ===== INICIO DE AUTENTICACIÓN =====` en logs

**Verificación:**
- DevTools → Network → Request Headers
- Debe existir: `Authorization: Bearer <token>`

**Solución:** Verificar `src/services/apiClient.ts` interceptor

### Causa 2: Token se envía pero middleware falla antes de print
**Síntoma:** Aparece 403 pero no aparecen print statements

**Verificación:**
- Buscar errores de Python en logs
- Buscar excepciones no capturadas

**Solución:** El traceback agregado mostrará el error exacto

### Causa 3: Token inválido o expirado
**Síntoma:** Aparece `[AUTH] ERROR: Token inválido` o `[AUTH] ERROR: Token expirado`

**Verificación:**
- Ver mensaje de error en logs
- Verificar que SECRET_KEY no cambió después del login

**Solución:** Hacer logout y login nuevamente

### Causa 4: Sesión no existe en base de datos
**Síntoma:** Aparece `[AUTH] ERROR: Token inválido: Session not found`

**Verificación:**
```sql
SELECT * FROM admin_sessions WHERE token LIKE 'eyJ%' ORDER BY created_at DESC LIMIT 5;
```

**Solución:** Hacer logout y login nuevamente

---

## COMANDOS ÚTILES

### Ver logs en tiempo real
```bash
docker-compose logs backend --tail 100 -f
```

### Filtrar solo mensajes de autenticación
```bash
docker-compose logs backend -f | Select-String "\[AUTH\]|\[JWT\]"
```

### Verificar SECRET_KEY
```bash
docker exec ricoh-backend printenv SECRET_KEY
```

### Verificar sesiones en base de datos
```bash
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
SELECT id, admin_user_id, LEFT(token, 20) as token_preview, expires_at, created_at 
FROM admin_sessions 
ORDER BY created_at DESC 
LIMIT 5;
```

---

## ESTADO ACTUAL

**Login:** ✅ Funciona (200 OK)  
**Token generado:** ✅ Sí  
**SECRET_KEY:** ✅ Correcta (54 caracteres)  
**Validación de token:** ❌ Falla (403 Forbidden)  
**Print statements:** ❌ No aparecen  

**Próxima acción:** Esperar recarga del backend e intentar login nuevamente

---

**Documento generado:** 20 de Marzo de 2026 16:27  
**Última actualización:** 20 de Marzo de 2026 16:27

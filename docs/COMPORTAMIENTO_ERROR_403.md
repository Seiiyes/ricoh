# Comportamiento del Error 403 - Token Expirado

**Fecha**: 20 de Marzo de 2026  
**Estado**: ✅ COMPORTAMIENTO NORMAL Y ESPERADO

---

## 🔍 ¿Qué es el Error 403?

Cuando ves este error en la consola del navegador:

```
:8000/printers/:1  Failed to load resource: the server responded with a status of 403 (Forbidden)
```

**NO ES UN BUG**. Es el comportamiento normal cuando el token JWT expira.

---

## 🔄 Flujo Completo

### 1. Token Expira (30 minutos después del login)
```
Usuario logueado → 30 minutos pasan → Token expira
```

### 2. Usuario Hace un Request
```
Frontend: GET /printers/
Headers: Authorization: Bearer <token_expirado>
```

### 3. Backend Retorna 403
```
Backend: 403 Forbidden (token inválido)
Navegador: Muestra error en consola ❌
```

### 4. Interceptor Detecta el Error
```
apiClient interceptor: "Detecté un 403, voy a renovar el token"
Console: "🔄 Token expirado, renovando automáticamente..."
```

### 5. Interceptor Renueva el Token
```
Frontend: POST /auth/refresh
Body: { refresh_token: "<refresh_token>" }
Backend: 200 OK { access_token: "<nuevo_token>" }
Console: "✅ Token renovado exitosamente, reintentando request..."
```

### 6. Interceptor Reintenta el Request Original
```
Frontend: GET /printers/
Headers: Authorization: Bearer <nuevo_token>
Backend: 200 OK { data: [...] }
Usuario: Ve los datos correctamente ✅
```

---

## 📊 Logs del Backend

Cuando esto sucede, verás en los logs del backend:

```
INFO: 172.18.0.1:56004 - "GET /printers/ HTTP/1.1" 403 Forbidden
INFO: 172.18.0.1:56016 - "POST /auth/refresh HTTP/1.1" 200 OK
INFO: 172.18.0.1:56004 - "GET /printers/ HTTP/1.1" 200 OK
```

Esto confirma que:
1. ✅ El primer request falló (403)
2. ✅ El token se renovó exitosamente (200)
3. ✅ El request se reintentó y funcionó (200)

---

## 🎯 ¿Por Qué Aparece el Error en la Consola?

El navegador registra el error 403 **antes** de que el interceptor de axios lo maneje. Esto es comportamiento estándar de los navegadores y no se puede evitar.

### Orden de Eventos
1. Navegador hace request → Backend retorna 403
2. **Navegador registra error en consola** ← Aquí ves el error
3. Axios pasa el error al interceptor
4. Interceptor renueva el token
5. Interceptor reintenta el request
6. Request exitoso

---

## ✅ ¿Cómo Saber que Está Funcionando Correctamente?

### Señales de que TODO está bien:

1. **Ves el error 403 en consola** ✅
2. **Inmediatamente después ves estos logs:**
   ```
   🔄 Token expirado, renovando automáticamente...
   ✅ Token renovado exitosamente, reintentando request...
   ```
3. **Los datos aparecen en la pantalla** ✅
4. **NO eres redirigido a la página de login** ✅

### Señales de que algo está MAL:

1. **Ves el error 403** ❌
2. **NO ves los logs de renovación** ❌
3. **Eres redirigido a la página de login** ❌
4. **Los datos NO aparecen** ❌

---

## 🚨 Cuándo Preocuparse

### Caso 1: Refresh Token Expirado (7 días)
Si el refresh token también expiró, verás:
```
❌ Error al renovar token, redirigiendo a login...
```
**Solución**: Hacer login nuevamente. Esto es normal después de 7 días de inactividad.

### Caso 2: Interceptor No Funciona
Si el interceptor no está funcionando, verás:
- Error 403 persistente
- NO ves los logs de renovación
- Los datos NO aparecen
- NO eres redirigido a login

**Solución**: Verificar que el servicio esté usando `apiClient` y no `fetch` directamente.

### Caso 3: Backend No Responde
Si el backend no está corriendo:
```
Network Error
```
**Solución**: Verificar que Docker esté corriendo: `docker-compose ps`

---

## 🔧 Configuración Actual

### Tiempos de Expiración
- **Access Token**: 30 minutos
- **Refresh Token**: 7 días
- **Renovación Automática**: Cada 25 minutos (preventiva)

### Renovación Preventiva
El `AuthContext` renueva el token automáticamente cada 25 minutos para evitar que expire durante el uso activo. Sin embargo, si el usuario está inactivo por más de 30 minutos, el token expirará y verás el error 403.

---

## 📝 Ejemplo Real

### Escenario: Usuario Inactivo por 35 Minutos

```
10:00 AM - Usuario hace login
10:30 AM - Token expira (30 minutos)
10:35 AM - Usuario regresa y hace clic en "Impresoras"

Console:
❌ :8000/printers/:1 Failed to load resource: 403 (Forbidden)
🔄 Token expirado, renovando automáticamente...
✅ Token renovado exitosamente, reintentando request...

Resultado: Usuario ve las impresoras sin necesidad de hacer login nuevamente ✅
```

---

## 🎓 Lecciones Aprendidas

### 1. El Error 403 es Normal
No es un bug, es el mecanismo de seguridad funcionando correctamente.

### 2. El Sistema se Recupera Automáticamente
El usuario no necesita hacer nada, el sistema maneja todo en segundo plano.

### 3. Los Logs son Tus Amigos
Los logs en consola te dicen exactamente qué está pasando:
- 🔄 = Renovando token
- ✅ = Token renovado exitosamente
- ❌ = Error, redirigiendo a login

### 4. Confía en el Interceptor
El interceptor de `apiClient` está diseñado para manejar estos casos automáticamente.

---

## 🔍 Debugging

### Ver Logs en Consola del Navegador
1. Abrir DevTools (F12)
2. Ir a la pestaña "Console"
3. Buscar los emojis: 🔄 ✅ ❌

### Ver Logs del Backend
```bash
docker-compose logs backend --tail=50 -f
```

### Verificar Token en localStorage
```javascript
// En la consola del navegador
console.log('Access Token:', localStorage.getItem('access_token'));
console.log('Refresh Token:', localStorage.getItem('refresh_token'));
```

### Forzar Expiración del Token (Para Testing)
```javascript
// En la consola del navegador
localStorage.setItem('access_token', 'token_invalido');
// Luego hacer un request y ver cómo se recupera automáticamente
```

---

## 📞 FAQ

### P: ¿Por qué veo el error 403 si el sistema funciona?
**R**: El navegador registra el error antes de que el interceptor lo maneje. Es comportamiento estándar.

### P: ¿Puedo ocultar el error 403 de la consola?
**R**: No, es comportamiento del navegador. Pero los logs con emojis te ayudan a entender qué está pasando.

### P: ¿Cada cuánto veo el error 403?
**R**: Solo cuando el token expira (30 minutos) y el usuario está inactivo. Si el usuario está activo, la renovación preventiva (cada 25 minutos) evita que expire.

### P: ¿Debo preocuparme por el error 403?
**R**: No, siempre y cuando veas los logs de renovación (🔄 ✅) y los datos aparezcan correctamente.

### P: ¿Qué pasa si el refresh token también expira?
**R**: El usuario será redirigido a la página de login. Esto es normal después de 7 días de inactividad.

---

## ✅ Conclusión

El error 403 que ves en la consola es:
- ✅ Normal y esperado
- ✅ Parte del mecanismo de seguridad
- ✅ Manejado automáticamente por el interceptor
- ✅ Transparente para el usuario final

**No necesitas hacer nada**. El sistema está funcionando correctamente.

---

**Documentado por**: Kiro AI Assistant  
**Fecha**: 20 de Marzo de 2026  
**Versión**: 1.0

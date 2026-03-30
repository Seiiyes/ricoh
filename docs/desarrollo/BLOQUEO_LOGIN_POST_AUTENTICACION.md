# Bloqueo de Acceso a Login Post-Autenticación

## Problema Identificado

Después de iniciar sesión, los usuarios podían usar el botón "atrás" del navegador y volver a la página de login, lo cual no es el comportamiento esperado en una aplicación con autenticación.

## Solución Implementada

### 1. Redirección Automática en LoginPage

Se agregó un `useEffect` en `LoginPage.tsx` que verifica si el usuario ya está autenticado y lo redirige automáticamente a la página principal:

```typescript
// Redirigir si el usuario ya está autenticado
useEffect(() => {
  if (!authLoading && isAuthenticated) {
    navigate('/', { replace: true });
  }
}, [isAuthenticated, authLoading, navigate]);
```

**Características:**
- Verifica `authLoading` para evitar redirecciones prematuras durante la carga inicial
- Usa `replace: true` para reemplazar la entrada en el historial (evita que el botón "atrás" vuelva al login)
- Se ejecuta cada vez que cambia el estado de autenticación

### 2. Unificación de Almacenamiento de Tokens

Se detectó una inconsistencia crítica donde diferentes partes del código usaban diferentes métodos de almacenamiento:

**Antes:**
- `AuthContext.tsx` → `localStorage`
- `authService.ts` → `sessionStorage`
- `apiClient.ts` → `sessionStorage`

**Después:**
- Todos los archivos ahora usan `localStorage` de forma consistente

**Archivos modificados:**
1. `src/services/authService.ts`
   - `login()` → Guarda tokens en `localStorage`
   - `logout()` → Limpia tokens de `localStorage`
   - `refreshToken()` → Lee/escribe en `localStorage`
   - `hasToken()` → Lee de `localStorage`

2. `src/services/apiClient.ts`
   - Request interceptor → Lee tokens de `localStorage`
   - Response interceptor → Guarda CSRF token en `localStorage`
   - Error handler → Limpia tokens de `localStorage`

## Comportamiento Actual

### Flujo de Autenticación

1. **Usuario no autenticado accede a `/login`**
   - Se muestra el formulario de login normalmente

2. **Usuario inicia sesión exitosamente**
   - Tokens se guardan en `localStorage`
   - Usuario es redirigido a `/`
   - La entrada de `/login` es reemplazada en el historial

3. **Usuario intenta volver a `/login` usando el botón "atrás"**
   - El `useEffect` detecta que `isAuthenticated === true`
   - Usuario es redirigido automáticamente a `/`
   - No puede acceder al formulario de login

4. **Usuario intenta acceder directamente a `/login` (escribiendo la URL)**
   - Mismo comportamiento: redirección automática a `/`

### Persistencia de Sesión

**Con `localStorage`:**
- ✅ La sesión persiste al cerrar la pestaña
- ✅ La sesión persiste al cerrar el navegador
- ✅ La sesión se mantiene entre recargas de página
- ⚠️ La sesión expira según la configuración del backend (30 min access token, 7 días refresh token)

**Ventajas:**
- Mejor experiencia de usuario (no necesita volver a iniciar sesión constantemente)
- Consistente con aplicaciones web modernas
- Los tokens se renuevan automáticamente cada 25 minutos

**Consideraciones de seguridad:**
- Los tokens en `localStorage` son accesibles por JavaScript (riesgo de XSS)
- Mitigación: El backend implementa rate limiting y validación estricta de tokens
- Recomendación: Mantener las dependencias actualizadas para prevenir vulnerabilidades XSS

## Configuración de Duración de Sesiones

### Backend (Python)

Configurado en `backend/api/auth.py` y servicios relacionados:

```python
# Access token: 30 minutos
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Refresh token: 7 días
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### Frontend (TypeScript)

Renovación automática en `AuthContext.tsx`:

```typescript
// Renovar token automáticamente cada 25 minutos
useEffect(() => {
  if (!user) return;
  
  const interval = setInterval(async () => {
    try {
      await authService.refreshToken();
      console.log('Token renovado automáticamente');
    } catch (error) {
      console.error('Error al renovar token:', error);
      await logout();
    }
  }, 25 * 60 * 1000); // 25 minutos
  
  return () => clearInterval(interval);
}, [user]);
```

## Limpieza de Sesiones Expiradas

El backend incluye un job de limpieza en `backend/jobs/cleanup_sessions.py`:

**Funciones:**
- `cleanup_expired_sessions()` → Elimina sesiones con access tokens expirados
- `cleanup_expired_refresh_tokens()` → Elimina sesiones con refresh tokens expirados
- `run_cleanup_job()` → Ejecuta ambas limpiezas

**Ejecución:**
- Actualmente se ejecuta manualmente
- Recomendación: Configurar un scheduler (APScheduler, Celery, cron) para ejecutarlo periódicamente

## Archivos Modificados

1. `src/pages/LoginPage.tsx`
   - Agregado `useEffect` para redirección automática
   - Agregado `authLoading` y `isAuthenticated` del contexto

2. `src/services/authService.ts`
   - Cambiado `sessionStorage` → `localStorage` en todos los métodos

3. `src/services/apiClient.ts`
   - Cambiado `sessionStorage` → `localStorage` en interceptores

## Testing Manual

### Caso 1: Acceso a Login Post-Autenticación
1. Iniciar sesión con credenciales válidas
2. Presionar el botón "atrás" del navegador
3. **Resultado esperado:** Redirección automática a `/`

### Caso 2: Acceso Directo a Login
1. Iniciar sesión con credenciales válidas
2. Escribir `/login` en la barra de direcciones
3. **Resultado esperado:** Redirección automática a `/`

### Caso 3: Persistencia de Sesión
1. Iniciar sesión con credenciales válidas
2. Cerrar la pestaña del navegador
3. Abrir una nueva pestaña y acceder a la aplicación
4. **Resultado esperado:** Usuario sigue autenticado

### Caso 4: Expiración de Sesión
1. Iniciar sesión con credenciales válidas
2. Esperar más de 30 minutos sin actividad
3. Intentar realizar una acción
4. **Resultado esperado:** Redirección automática a `/login`

## Mejoras Futuras (Opcional)

### 1. Opción "Recordarme"
Agregar un checkbox en el login para elegir entre:
- `localStorage` (sesión persistente)
- `sessionStorage` (sesión temporal, se borra al cerrar pestaña)

### 2. Detección de Inactividad
Implementar un timer que cierre la sesión después de X minutos de inactividad del usuario.

### 3. Múltiples Sesiones
Permitir al usuario ver y gestionar sus sesiones activas desde diferentes dispositivos.

### 4. Notificación de Expiración
Mostrar una notificación (usando Sileo) cuando la sesión esté por expirar, dando opción de renovarla.

## Referencias

- [MDN: Window.localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [MDN: Window.sessionStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

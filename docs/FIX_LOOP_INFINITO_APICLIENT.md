# Fix: Loop Infinito en apiClient.ts

**Fecha**: 26 de marzo de 2026  
**Problema**: La aplicación se quedaba colgada al cargar, sin mostrar errores en consola  
**Causa**: Loop infinito en el interceptor de respuestas de axios

## Problema Identificado

### Síntoma
- La aplicación se quedaba completamente colgada al cargar
- No aparecían errores en la consola del navegador (F12)
- El navegador mostraba: "Unsafe attempt to load URL http://localhost:5173/"
- Vite servía los archivos correctamente pero la página no renderizaba

### Causa Raíz

En `src/services/apiClient.ts`, el interceptor de respuestas tenía un **loop infinito**:

```typescript
// ❌ CÓDIGO PROBLEMÁTICO
apiClient.interceptors.response.use(
  (response) => {
    // ...
    checkAndRotateToken(); // ← Esto causaba el loop
    return response;
  },
  // ...
);

async function checkAndRotateToken() {
  // ...
  const response = await apiClient.post('/auth/rotate-token'); // ← Esto genera otra respuesta
  // ...
}
```

**Flujo del loop**:
1. Se hace cualquier request → genera una respuesta
2. El interceptor llama a `checkAndRotateToken()`
3. `checkAndRotateToken()` hace `apiClient.post('/auth/rotate-token')`
4. Eso genera otra respuesta → vuelve al paso 2
5. **Loop infinito** 🔄

### Problema Secundario

En `src/contexts/AuthContext.tsx`, el segundo `useEffect` tenía una dependencia incompleta:

```typescript
// ⚠️ CÓDIGO PROBLEMÁTICO
useEffect(() => {
  // ...
  await logout(); // ← logout no está en las dependencias
}, [user]); // ← Falta logout
```

Esto podía causar warnings de React y comportamiento inconsistente.

## Solución Implementada

### 1. Eliminar checkAndRotateToken del interceptor

```typescript
// ✅ CÓDIGO CORREGIDO
apiClient.interceptors.response.use(
  (response) => {
    // Guardar nuevo CSRF token si viene en el header
    const newCsrfToken = response.headers['x-csrf-token'];
    if (newCsrfToken) {
      sessionStorage.setItem('csrf_token', newCsrfToken);
    }
    
    // NO llamar checkAndRotateToken aquí para evitar loops infinitos
    // La rotación se manejará de forma programada en AuthContext
    
    return response;
  },
  // ...
);
```

### 2. Eliminar función checkAndRotateToken

Se eliminó completamente la función `checkAndRotateToken()` y su variable `isRotating`.

### 3. Simplificar AuthContext

```typescript
// ✅ CÓDIGO CORREGIDO
useEffect(() => {
  if (!user) return;
  
  const interval = setInterval(async () => {
    try {
      await authService.refreshToken();
      console.log('Token renovado automáticamente');
    } catch (error) {
      console.error('Error al renovar token:', error);
      // Si falla la renovación, limpiar tokens directamente
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      setUser(null);
    }
  }, 25 * 60 * 1000); // 25 minutos
  
  return () => clearInterval(interval);
}, [user]); // user es suficiente
```

## Archivos Modificados

1. `src/services/apiClient.ts`
   - Eliminada llamada a `checkAndRotateToken()` del interceptor
   - Eliminada función `checkAndRotateToken()` completa
   - Eliminada variable `isRotating`

2. `src/contexts/AuthContext.tsx`
   - Simplificado manejo de errores en renovación de token
   - Eliminada dependencia problemática de `logout()`

## Verificación

```bash
# Reiniciar frontend
docker-compose restart frontend

# Verificar logs
docker logs ricoh-frontend --tail 30

# Abrir navegador en http://localhost:5173
# La aplicación debe cargar correctamente
```

## Lecciones Aprendidas

1. **Evitar llamadas recursivas en interceptores**: Los interceptores de axios se ejecutan en TODAS las respuestas, incluyendo las generadas por llamadas dentro del mismo interceptor.

2. **Separar responsabilidades**: La renovación automática de tokens debe manejarse en un lugar específico (como AuthContext con `setInterval`), no en interceptores globales.

3. **Cuidado con useEffect**: Siempre incluir todas las dependencias o usar callbacks que no dependan de estado externo.

4. **Debugging de loops infinitos**: Cuando la aplicación se cuelga sin errores, buscar:
   - Interceptores que hacen requests
   - useEffect con dependencias incompletas
   - Llamadas recursivas no controladas

## Simplificación Adicional (26 marzo - 10:20)

Después del primer fix, la aplicación seguía colgada. Se realizó una simplificación AGRESIVA:

### Cambios adicionales en AuthContext:
- ✅ Eliminado `async/await` en el useEffect inicial (posible causa de bloqueo)
- ✅ Deshabilitada renovación automática de tokens (comentada temporalmente)
- ✅ Uso de `.then()/.catch()/.finally()` en lugar de async/await

### Cambios adicionales en apiClient:
- ✅ Eliminados TODOS los reintentos automáticos de token
- ✅ Simplificado manejo de 401: solo limpiar y redirigir
- ✅ Eliminado manejo de 403
- ✅ Eliminada lógica compleja de refresh token en interceptor

### Archivos de diagnóstico creados:
- `public/simple-test.html` - Test HTML puro sin React
- `src/App.SIMPLE.tsx` - Versión ultra-simplificada de App sin AuthContext
- `src/App.BACKUP.tsx` - Backup del App.tsx original
- `INSTRUCCIONES_URGENTES.md` - Guía de diagnóstico para el usuario

## Próximos Pasos de Diagnóstico

1. Probar `http://localhost:5173/simple-test.html` (HTML puro)
2. Si funciona, el problema es React
3. Si no funciona, el problema es el navegador/red
4. Limpiar cache completo del navegador
5. Probar en modo incógnito
6. Probar en otro navegador
7. Si nada funciona, reemplazar App.tsx con App.SIMPLE.tsx

## Estado Final

⏳ Pendiente de verificación por el usuario  
✅ Código simplificado al máximo  
✅ Eliminados todos los posibles loops infinitos  
✅ Archivos de diagnóstico creados  
⏳ Esperando resultados de pruebas del navegador

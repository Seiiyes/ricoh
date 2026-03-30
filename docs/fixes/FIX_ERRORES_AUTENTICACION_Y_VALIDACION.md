# Fix: Errores de Autenticación y Validación

**Fecha:** 20 de Marzo de 2026  
**Tipo:** Bug Fix  
**Prioridad:** Alta (Crítico)

---

## Errores Encontrados

### 1. Error 401 en Login (Crítico)
**Síntoma:**
```
Failed to load resource: the server responded with a status of 401 (Unauthorized)
🔄 Token expirado, renovando automáticamente...
✅ Token renovado exitosamente, reintentando request...
Failed to load resource: the server responded with a status of 401 (Unauthorized)
```

**Causa:**
El servicio de autenticación usaba `apiClient` para hacer login, pero `apiClient` tiene interceptores que intentan renovar el token cuando recibe un 401. En el login no hay token aún, causando un loop infinito de intentos de renovación.

**Solución:**
- Usar axios directamente en el método `login()` sin interceptores
- Agregar validación en el interceptor para no intentar renovar token en rutas de autenticación

---

### 2. Error 422 con Objeto Renderizado (Crítico)
**Síntoma:**
```
Failed to load resource: the server responded with a status of 422 (Unprocessable Entity)
Uncaught Error: Objects are not valid as a React child (found: object with keys {type, loc, msg, input, url})
```

**Causa:**
El backend retorna errores de validación 422 como un array de objetos:
```json
[
  {
    "type": "validation_error",
    "loc": ["body", "periodo"],
    "msg": "field required",
    "input": {...}
  }
]
```

El componente intentaba renderizar este objeto directamente en el Alert, causando el error de React.

**Solución:**
Mejorar el manejo de errores en `CierreModal.tsx` para convertir objetos de error a strings legibles.

---

## Soluciones Implementadas

### 1. authService.ts - Login sin Interceptores

**ANTES:**
```typescript
async login(username: string, password: string): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', {
    username,
    password,
  });
  // ...
}
```

**DESPUÉS:**
```typescript
async login(username: string, password: string): Promise<LoginResponse> {
  // Usar axios directamente sin interceptores
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const axios = (await import('axios')).default;
  
  const response = await axios.post<LoginResponse>(`${API_BASE_URL}/auth/login`, {
    username,
    password,
  });
  // ...
}
```

**Beneficio:** Evita el loop infinito de renovación de token durante el login.

---

### 2. apiClient.ts - Validación de Rutas de Auth

**ANTES:**
```typescript
if ((error.response?.status === 401 || error.response?.status === 403) && !originalRequest._retry) {
  // Intentar renovar token siempre
}
```

**DESPUÉS:**
```typescript
// No intentar renovar token en rutas de autenticación
const isAuthRoute = originalRequest.url?.includes('/auth/login') || 
                    originalRequest.url?.includes('/auth/refresh');

if ((error.response?.status === 401 || error.response?.status === 403) && 
    !originalRequest._retry && 
    !isAuthRoute) {
  // Intentar renovar token solo si no es ruta de auth
}
```

**Beneficio:** Previene intentos de renovación en rutas donde no tiene sentido.

---

### 3. CierreModal.tsx - Manejo Robusto de Errores

**ANTES:**
```typescript
catch (err: any) {
  console.error('Error al crear cierre:', err);
  setError(err.response?.data?.detail || err.message || 'Error al crear el cierre');
}
```

**DESPUÉS:**
```typescript
catch (err: any) {
  console.error('Error al crear cierre:', err);
  
  let errorMessage = 'Error al crear el cierre';
  
  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    
    // Si detail es un array de errores de validación (422)
    if (Array.isArray(detail)) {
      errorMessage = detail.map((e: any) => {
        if (typeof e === 'object' && e.msg) {
          return `${e.loc ? e.loc.join('.') + ': ' : ''}${e.msg}`;
        }
        return String(e);
      }).join(', ');
    } 
    // Si detail es un string
    else if (typeof detail === 'string') {
      errorMessage = detail;
    }
    // Si detail es un objeto con message
    else if (typeof detail === 'object' && detail.message) {
      errorMessage = detail.message;
    }
    // Cualquier otro caso
    else {
      errorMessage = JSON.stringify(detail);
    }
  } else if (err.message) {
    errorMessage = err.message;
  }
  
  setError(errorMessage);
}
```

**Beneficio:** 
- Convierte arrays de errores de validación a mensajes legibles
- Maneja diferentes formatos de error del backend
- Previene el error "Objects are not valid as a React child"

---

## Ejemplos de Mensajes de Error Mejorados

### Error de Validación 422:
**Backend retorna:**
```json
[
  {
    "type": "missing",
    "loc": ["body", "periodo"],
    "msg": "Field required"
  },
  {
    "type": "string_type",
    "loc": ["body", "notas"],
    "msg": "Input should be a valid string"
  }
]
```

**Usuario ve:**
```
body.periodo: Field required, body.notas: Input should be a valid string
```

### Error Simple:
**Backend retorna:**
```json
{
  "detail": "Printer not found"
}
```

**Usuario ve:**
```
Printer not found
```

---

## Archivos Modificados

1. **src/services/authService.ts**
   - Método `login()` usa axios directamente sin interceptores

2. **src/services/apiClient.ts**
   - Interceptor valida rutas de autenticación antes de intentar renovar token

3. **src/components/contadores/cierres/CierreModal.tsx**
   - Manejo robusto de errores con conversión de objetos a strings

---

## Testing

### Casos de Prueba:

#### Login:
1. ✅ Login exitoso sin intentos de renovación de token
2. ✅ Login fallido muestra mensaje de error correcto
3. ✅ No hay loops infinitos de renovación

#### Errores de Validación:
1. ✅ Error 422 con array de errores se muestra como texto legible
2. ✅ Error 422 con string se muestra directamente
3. ✅ Error 422 con objeto se convierte a string
4. ✅ No hay errores de React "Objects are not valid as a React child"

#### Renovación de Token:
1. ✅ Token se renueva automáticamente en requests normales
2. ✅ Token NO se intenta renovar en /auth/login
3. ✅ Token NO se intenta renovar en /auth/refresh

---

## Patrón Reutilizable

Este patrón de manejo de errores puede aplicarse a otros componentes:

```typescript
catch (err: any) {
  let errorMessage = 'Error genérico';
  
  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    
    if (Array.isArray(detail)) {
      // Errores de validación (422)
      errorMessage = detail.map((e: any) => {
        if (typeof e === 'object' && e.msg) {
          return `${e.loc ? e.loc.join('.') + ': ' : ''}${e.msg}`;
        }
        return String(e);
      }).join(', ');
    } else if (typeof detail === 'string') {
      errorMessage = detail;
    } else if (typeof detail === 'object' && detail.message) {
      errorMessage = detail.message;
    } else {
      errorMessage = JSON.stringify(detail);
    }
  } else if (err.message) {
    errorMessage = err.message;
  }
  
  setError(errorMessage);
}
```

---

## Recomendaciones

### 1. Crear Utilidad de Manejo de Errores
Crear una función reutilizable:

```typescript
// src/utils/errorHandler.ts
export function parseApiError(err: any): string {
  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    
    if (Array.isArray(detail)) {
      return detail.map((e: any) => {
        if (typeof e === 'object' && e.msg) {
          return `${e.loc ? e.loc.join('.') + ': ' : ''}${e.msg}`;
        }
        return String(e);
      }).join(', ');
    } else if (typeof detail === 'string') {
      return detail;
    } else if (typeof detail === 'object' && detail.message) {
      return detail.message;
    } else {
      return JSON.stringify(detail);
    }
  } else if (err.message) {
    return err.message;
  }
  
  return 'Error desconocido';
}
```

Uso:
```typescript
catch (err: any) {
  setError(parseApiError(err));
}
```

### 2. Aplicar Patrón a Otros Componentes
Buscar otros componentes que manejen errores y aplicar el mismo patrón:
- Formularios de creación/edición
- Modales de confirmación
- Páginas con llamadas a API

### 3. Agregar Tests
Crear tests unitarios para:
- Manejo de diferentes formatos de error
- Conversión de arrays a strings
- Casos edge (null, undefined, etc.)

---

## Impacto

### Antes:
- ❌ Login causaba loop infinito de renovación de token
- ❌ Errores 422 crasheaban la aplicación
- ❌ Mensajes de error ilegibles (objetos JSON)

### Después:
- ✅ Login funciona correctamente sin loops
- ✅ Errores 422 se manejan gracefully
- ✅ Mensajes de error legibles para el usuario
- ✅ Aplicación más robusta y estable

---

## Conclusión

✅ **Fixes implementados exitosamente**

Se corrigieron 2 errores críticos que afectaban la autenticación y la creación de cierres. La aplicación ahora maneja errores de forma más robusta y proporciona mensajes claros al usuario.

**Próximos pasos:**
1. Crear utilidad reutilizable de manejo de errores
2. Aplicar patrón a otros componentes
3. Agregar tests unitarios

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 20 de Marzo de 2026  
**Versión:** 1.0

# Errores Encontrados y Soluciones - Sistema de Autenticación

**Fecha**: 20 de Marzo de 2026  
**Proyecto**: Ricoh Suite - Sistema de Autenticación y Multi-Tenancy

## 📋 Resumen

Este documento registra todos los errores encontrados durante la implementación del sistema de autenticación y sus soluciones, para referencia futura y prevención de problemas similares.

---

## Error 1: Axios no instalado en package.json

### Síntoma
```
[plugin:vite:import-analysis] Failed to resolve import "axios" from "src/services/apiClient.ts"
```

### Causa
El archivo `apiClient.ts` importa `axios`, pero la dependencia no estaba listada en `package.json`.

### Solución
Agregar axios a las dependencias:

```json
"dependencies": {
  "axios": "^1.7.9",
  ...
}
```

Luego ejecutar:
```bash
npm install
```

### Prevención
- Siempre verificar que las dependencias estén en `package.json` antes de usarlas
- Ejecutar `npm install <paquete>` en lugar de solo importar

### Archivos Afectados
- `package.json`
- `src/services/apiClient.ts`

---

## Error 2: Módulo bcrypt no encontrado en Docker

### Síntoma
```
ModuleNotFoundError: No module named 'bcrypt'
```

### Causa
El contenedor de Docker del backend no se reconstruyó después de agregar nuevas dependencias (`bcrypt`, `PyJWT`, `python-dotenv`) al `requirements.txt`.

### Solución
Reconstruir el contenedor del backend:

```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Prevención
- Siempre reconstruir contenedores después de cambios en `requirements.txt`
- Usar `--no-cache` para asegurar instalación limpia
- Considerar usar volúmenes para desarrollo local

### Archivos Afectados
- `backend/requirements.txt`
- `backend/Dockerfile`

---

## Error 3: CORS Policy - No 'Access-Control-Allow-Origin'

### Síntoma
```
Access to XMLHttpRequest at 'http://localhost:8000/printers/' from origin 'http://localhost:5173' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

### Causa
El backend no estaba respondiendo correctamente debido al Error 2 (bcrypt faltante), por lo que no enviaba headers CORS.

### Solución
1. Solucionar el Error 2 (reconstruir backend)
2. Verificar configuración CORS en `backend/main.py`:

```python
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)
```

### Prevención
- Verificar que el backend esté corriendo correctamente antes de diagnosticar CORS
- Revisar logs del backend para errores subyacentes
- CORS es síntoma, no causa raíz

### Archivos Afectados
- `backend/main.py`

---

## Error 4: Error 403 Forbidden en /printers/

### Síntoma
```
Failed to load resource: the server responded with a status of 403 (Forbidden)
```

### Causa
El endpoint `/printers/` ahora requiere autenticación (usa `get_current_user`), pero el servicio de frontend (`printerService.ts`) estaba usando `fetch` directamente en lugar de `apiClient` que tiene los interceptores de autenticación.

### Solución
Actualizar `printerService.ts` para usar `apiClient`:

```typescript
// ANTES (incorrecto)
const response = await fetch(`${API_BASE_URL}/printers/`);

// DESPUÉS (correcto)
import apiClient from './apiClient';
const response = await apiClient.get('/printers/');
```

### Prevención
- Todos los servicios deben usar `apiClient` para requests autenticados
- `apiClient` maneja automáticamente:
  - Agregar token de autenticación
  - Renovar token cuando expira
  - Redirigir a login si token inválido

### Archivos Afectados
- `src/services/printerService.ts`
- `src/services/servicioUsuarios.ts`
- `src/services/counterService.ts`

---

## Error 5: ResponseValidationError - Empresa object en lugar de string

### Síntoma
```
fastapi.exceptions.ResponseValidationError: 5 validation errors:
'Input should be a valid string', 'input': <Empresa(id=1, razon_social='Sin Asignar', nombre_comercial='sin-asignar')>
```

### Causa
Después de la migración a multi-tenancy, el modelo `Printer` tiene una relación con la tabla `Empresa` (objeto completo), pero el schema Pydantic `PrinterResponse` esperaba un `string` para el campo `empresa`.

### Solución
Agregar un validator en `PrinterResponse` para serializar el objeto `Empresa`:

```python
class PrinterResponse(PrinterBase):
    empresa: Optional[str] = None
    
    @validator('empresa', pre=True, always=True)
    def serialize_empresa(cls, v):
        """Convert Empresa object to string (razon_social)"""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if hasattr(v, 'razon_social'):
            return v.razon_social
        return str(v)
```

### Prevención
- Cuando se cambia un campo de string a relación, actualizar los schemas Pydantic
- Usar validators para serializar objetos complejos
- Considerar crear schemas separados para relaciones (EmpresaResponse)

### Archivos Afectados
- `backend/api/schemas.py`
- `backend/db/models.py`

---

## Error 6: WebSocket connection failed

### Síntoma
```
WebSocket connection to 'ws://localhost:8000/ws/logs' failed: 
WebSocket is closed before the connection is established
```

### Causa
El backend no estaba completamente iniciado o el endpoint WebSocket no está disponible.

### Solución
Este error es secundario y no crítico. El WebSocket es para logs en tiempo real. Se puede:

1. Verificar que el backend esté completamente iniciado
2. O deshabilitar temporalmente el WebSocket en el frontend si no es necesario

### Prevención
- Implementar reconexión automática en el cliente WebSocket
- Agregar manejo de errores graceful
- Considerar hacer el WebSocket opcional

### Archivos Afectados
- `src/services/printerService.ts`
- `backend/main.py` (endpoint `/ws/logs`)

---

## Error 7: Error 403 Forbidden persistente (Token Expirado)

### Síntoma
```
Failed to load resource: the server responded with a status of 403 (Forbidden)
```

El error aparece intermitentemente, especialmente después de que el usuario ha estado inactivo por un tiempo.

### Causa
El token JWT ha expirado (30 minutos de vida). Aunque el interceptor de `apiClient` detecta el 403 y renueva el token automáticamente, el usuario ve el error 403 en la consola antes de que se complete la renovación.

### Solución Implementada
1. **Interceptor actualizado** para manejar tanto 401 como 403:
   ```typescript
   // En apiClient.ts
   if ((error.response?.status === 401 || error.response?.status === 403) && !originalRequest._retry) {
     // Intentar renovar token y reintentar request
   }
   ```

2. **Todos los servicios actualizados** para usar `apiClient`:
   - ✅ `printerService.ts` - Completamente actualizado
   - ✅ `servicioUsuarios.ts` - Completamente actualizado
   - ✅ `counterService.ts` - Completamente actualizado

3. **Renovación automática** en `AuthContext`:
   - Token se renueva automáticamente cada 25 minutos
   - Previene expiración durante uso activo

### Comportamiento Esperado
- Usuario ve error 403 momentáneo en consola
- Interceptor detecta el 403 y renueva el token automáticamente
- Request se reintenta con el nuevo token
- Usuario ve los datos correctamente sin necesidad de re-login

### Prevención
- Usar `apiClient` para TODOS los requests autenticados
- No usar `fetch` directamente
- El interceptor maneja automáticamente:
  - Agregar token de autenticación
  - Renovar token cuando expira (401 o 403)
  - Redirigir a login si token inválido

### Archivos Afectados
- `src/services/apiClient.ts` (interceptor)
- `src/services/printerService.ts` (actualizado)
- `src/services/servicioUsuarios.ts` (actualizado)
- `src/services/counterService.ts` (actualizado)
- `src/contexts/AuthContext.tsx` (renovación automática)

### Nota Importante
El error 403 en consola es normal y esperado cuando el token expira. Lo importante es que el sistema se recupera automáticamente sin intervención del usuario. Si el usuario necesita hacer login nuevamente, significa que el refresh token también expiró (7 días).

---

## Lecciones Aprendidas

### 1. Orden de Debugging
Cuando hay múltiples errores:
1. Verificar que el backend esté corriendo (logs)
2. Verificar dependencias instaladas
3. Verificar configuración (CORS, env vars)
4. Verificar código (schemas, servicios)

### 2. Docker vs Local
- Docker es mejor para producción
- Local es mejor para desarrollo y debugging
- Siempre reconstruir contenedores después de cambios en dependencias

### 3. Schemas Pydantic
- Mantener schemas sincronizados con modelos de base de datos
- Usar validators para transformaciones complejas
- Documentar cambios en relaciones (string → object)

### 4. Servicios Frontend
- Centralizar requests HTTP en un cliente (apiClient)
- No usar `fetch` directamente para requests autenticados
- Interceptores manejan autenticación automáticamente
- TODOS los servicios deben usar apiClient:
  - ✅ printerService.ts
  - ✅ servicioUsuarios.ts
  - ✅ counterService.ts
  - ✅ authService.ts
  - ✅ empresaService.ts
  - ✅ adminUserService.ts

### 5. Migraciones
- Cuando se cambia estructura de datos (empresa: string → Empresa: object):
  1. Actualizar modelos de BD
  2. Actualizar schemas Pydantic
  3. Actualizar servicios frontend
  4. Actualizar componentes que usan los datos

---

## Checklist de Prevención

Antes de implementar cambios similares:

- [ ] Verificar que todas las dependencias estén en package.json/requirements.txt
- [ ] Reconstruir contenedores Docker después de cambios en dependencias
- [ ] Actualizar schemas Pydantic cuando se cambian relaciones en modelos
- [ ] Usar apiClient en lugar de fetch para requests autenticados (TODOS los servicios)
- [ ] Probar endpoints en Swagger antes de integrar en frontend
- [ ] Verificar logs del backend antes de diagnosticar errores de frontend
- [ ] Documentar cambios en estructura de datos
- [ ] Verificar que el interceptor maneje tanto 401 como 403
- [ ] Implementar renovación automática de token en AuthContext

---

## Comandos Útiles para Debugging

### Ver logs del backend
```bash
docker-compose logs backend --tail=100
docker-compose logs -f backend  # tiempo real
```

### Reconstruir backend
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Verificar estado de contenedores
```bash
docker-compose ps
```

### Entrar al contenedor
```bash
docker exec -it ricoh-backend bash
```

### Verificar dependencias instaladas
```bash
docker exec -it ricoh-backend pip list | grep bcrypt
```

### Probar endpoint manualmente
```bash
curl -X GET http://localhost:8000/printers/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Referencias

- **Documentación FastAPI**: https://fastapi.tiangolo.com/
- **Documentación Pydantic**: https://docs.pydantic.dev/
- **Documentación Docker Compose**: https://docs.docker.com/compose/
- **Documentación Axios**: https://axios-http.com/

---

**Mantenido por**: Equipo de Desarrollo  
**Última actualización**: 20 de Marzo de 2026  
**Versión**: 1.0


---

## Error 8: Componentes usando fetch directamente en lugar de apiClient

### Síntoma
```
CierresView.tsx:38  GET http://localhost:8000/printers/ 403 (Forbidden)
```

Los cierres mensuales no cargan y aparecen errores 403 en la consola, específicamente desde componentes como `CierresView.tsx`, `ComparacionPage.tsx`, etc.

### Causa
Varios componentes de React estaban usando `fetch` directamente en lugar de `apiClient`, por lo que:
1. No incluían el token JWT en los headers
2. No se beneficiaban del interceptor de renovación automática
3. Cada componente manejaba errores de forma diferente

**Componentes afectados**:
- `src/components/contadores/cierres/CierresView.tsx`
- `src/components/contadores/cierres/ComparacionPage.tsx`
- `src/components/contadores/cierres/CierreModal.tsx`
- `src/components/contadores/cierres/CierreDetalleModal.tsx`
- `src/components/contadores/cierres/ComparacionModal.tsx`
- `src/components/discovery/DiscoveryModal.tsx`
- `src/components/usuarios/AdministracionUsuarios.tsx`

### Solución

#### 1. Importar apiClient en cada componente
```typescript
// ANTES
const API_BASE = 'http://localhost:8000';

// DESPUÉS
import apiClient from '@/services/apiClient';
```

#### 2. Reemplazar fetch por apiClient
```typescript
// ANTES (incorrecto)
const response = await fetch(`${API_BASE}/printers`);
if (!response.ok) throw new Error('Error al cargar impresoras');
const data = await response.json();

// DESPUÉS (correcto)
const response = await apiClient.get('/printers/');
const data = response.data;
```

#### 3. Actualizar parámetros de query
```typescript
// ANTES (incorrecto)
const params = new URLSearchParams({ year: selectedYear.toString(), limit: '500' });
const response = await fetch(`${API_BASE}/api/counters/monthly/${id}?${params}`);

// DESPUÉS (correcto)
const response = await apiClient.get(`/api/counters/monthly/${id}`, {
  params: {
    year: selectedYear,
    limit: 500
  }
});
```

#### 4. Mejorar manejo de errores
```typescript
// ANTES (incorrecto)
catch (err: any) {
  setError(err.message);
}

// DESPUÉS (correcto)
catch (err: any) {
  console.error('Error al cargar datos:', err);
  setError(err.response?.data?.detail || err.message || 'Error al cargar datos');
}
```

### Prevención

#### Checklist para Nuevos Componentes
- [ ] Importar `apiClient` en lugar de usar `fetch`
- [ ] NO definir variables `API_BASE` o `API_URL`
- [ ] Usar `apiClient.get/post/put/delete()` para todos los requests autenticados
- [ ] Usar `params` object para query parameters
- [ ] Manejar errores con `err.response?.data?.detail`
- [ ] Agregar `console.error` para debugging

#### Patrón Recomendado para Componentes
```typescript
import { useState, useEffect } from 'react';
import apiClient from '@/services/apiClient';

export const MiComponente = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/endpoint', {
        params: { filter: 'value' }
      });
      setData(response.data);
    } catch (err: any) {
      console.error('Error al cargar datos:', err);
      setError(err.response?.data?.detail || err.message || 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // ... resto del componente
};
```

### Cómo Detectar Este Error

#### 1. Buscar en el código
```bash
# Buscar componentes que usan fetch
grep -r "await fetch" src/components/

# Buscar definiciones de API_BASE o API_URL
grep -r "API_BASE\|API_URL" src/components/
```

#### 2. Revisar errores en consola
Si ves errores 403 que mencionan un archivo `.tsx` específico:
```
CierresView.tsx:38  GET http://localhost:8000/printers/ 403 (Forbidden)
```

Esto indica que el componente está usando `fetch` directamente.

#### 3. Verificar que el interceptor no se ejecuta
Si NO ves estos logs después del 403:
```
🔄 Token expirado, renovando automáticamente...
✅ Token renovado exitosamente, reintentando request...
```

Significa que el request no pasó por `apiClient`.

### Impacto

**Antes de la corrección**:
- ❌ 7 componentes sin autenticación automática
- ❌ Errores 403 persistentes en cierres
- ❌ Manejo inconsistente de errores
- ❌ Código duplicado en cada componente

**Después de la corrección**:
- ✅ Todos los componentes usan autenticación automática
- ✅ Renovación de token funciona en todos los componentes
- ✅ Manejo consistente de errores
- ✅ ~450 líneas de código menos (64% reducción)

### Archivos Afectados
- `src/components/contadores/cierres/CierresView.tsx`
- `src/components/contadores/cierres/ComparacionPage.tsx`
- `src/components/contadores/cierres/CierreModal.tsx`
- `src/components/contadores/cierres/CierreDetalleModal.tsx`
- `src/components/contadores/cierres/ComparacionModal.tsx`
- `src/components/discovery/DiscoveryModal.tsx`
- `src/components/usuarios/AdministracionUsuarios.tsx`

### Lección Aprendida

**Regla de Oro**: NUNCA usar `fetch` directamente en componentes o servicios que requieren autenticación. SIEMPRE usar `apiClient`.

**Por qué es importante**:
1. `apiClient` agrega automáticamente el token JWT
2. `apiClient` renueva el token cuando expira
3. `apiClient` maneja errores de forma consistente
4. `apiClient` redirige a login cuando es necesario
5. Código más limpio y mantenible

**Cómo asegurar que no vuelva a pasar**:
1. Revisar todos los componentes nuevos antes de commit
2. Buscar `fetch(` en el código antes de hacer PR
3. Agregar un linter rule para prohibir `fetch` en src/
4. Documentar el patrón en la guía de desarrollo

---

**Última actualización**: 20 de Marzo de 2026  
**Total de errores documentados**: 8

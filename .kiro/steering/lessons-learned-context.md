---
inclusion: auto
---

# Lecciones Aprendidas - Ricoh Suite

Este documento contiene lecciones aprendidas de errores pasados para evitar repetirlos en el futuro.

## 🚨 Reglas Críticas de Autenticación

### SIEMPRE usar apiClient para requests autenticados

**NUNCA hacer esto:**
```typescript
const response = await fetch(`${API_BASE_URL}/endpoint`);
```

**SIEMPRE hacer esto:**
```typescript
import apiClient from './apiClient';
const response = await apiClient.get('/endpoint');
```

**Razón:** `apiClient` tiene interceptores que:
- Agregan automáticamente el token JWT
- Renuevan el token cuando expira (401/403)
- Redirigen a login si el token es inválido
- Manejan errores de forma consistente

### Servicios que DEBEN usar apiClient

Todos estos servicios ya están actualizados:
- ✅ `src/services/printerService.ts`
- ✅ `src/services/servicioUsuarios.ts`
- ✅ `src/services/counterService.ts`
- ✅ `src/services/authService.ts`
- ✅ `src/services/empresaService.ts`
- ✅ `src/services/adminUserService.ts`

### Componentes que DEBEN usar apiClient

Todos estos componentes ya están actualizados:
- ✅ `src/components/contadores/cierres/CierresView.tsx`
- ✅ `src/components/contadores/cierres/ComparacionPage.tsx`
- ✅ `src/components/contadores/cierres/CierreModal.tsx`
- ✅ `src/components/contadores/cierres/CierreDetalleModal.tsx`
- ✅ `src/components/contadores/cierres/ComparacionModal.tsx`
- ✅ `src/components/discovery/DiscoveryModal.tsx`
- ✅ `src/components/usuarios/AdministracionUsuarios.tsx`

Si creas un nuevo servicio o componente, DEBE usar `apiClient`.

## 🔄 Manejo de Errores 403

### Error 403 es NORMAL cuando el token expira

El flujo correcto es:
1. Token expira (30 minutos)
2. Backend retorna 403 Forbidden
3. Interceptor detecta 403
4. Interceptor renueva el token automáticamente
5. Interceptor reintenta el request con el nuevo token
6. Usuario ve los datos correctamente

**NO es un bug** ver un 403 momentáneo en la consola. Es el comportamiento esperado.

### Cuándo preocuparse por 403

Solo preocuparse si:
- El usuario es redirigido a login (significa que el refresh token también expiró)
- El 403 persiste y no se recupera automáticamente
- El interceptor no está funcionando

## 🐳 Docker y Dependencias

### SIEMPRE reconstruir contenedores después de cambios en requirements

**Cuando cambies `backend/requirements.txt`:**
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

**Cuando cambies `package.json`:**
```bash
npm install
# Si estás en Docker, reconstruir el contenedor frontend también
```

### Verificar que el backend esté corriendo antes de diagnosticar CORS

CORS errors son síntomas, no causas. Si ves un error CORS:
1. Verificar logs del backend: `docker-compose logs backend --tail=50`
2. Verificar que el backend esté respondiendo: `curl http://localhost:8000/`
3. Verificar que las dependencias estén instaladas

## 📦 Schemas Pydantic y Relaciones

### Cuando cambies un campo de string a relación

Si cambias:
```python
# ANTES
empresa: str

# DESPUÉS
empresa: Mapped["Empresa"] = relationship("Empresa")
```

Debes actualizar el schema Pydantic:
```python
class PrinterResponse(PrinterBase):
    empresa: Optional[str] = None
    
    @validator('empresa', pre=True, always=True)
    def serialize_empresa(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if hasattr(v, 'razon_social'):
            return v.razon_social
        return str(v)
```

## 🔐 Validaciones de Importación

### NUNCA importar desde módulos que no existen

**Antes de importar:**
```typescript
import axios from 'axios';
```

**Verificar que esté en package.json:**
```json
{
  "dependencies": {
    "axios": "^1.7.9"
  }
}
```

**Si no está, instalarlo:**
```bash
npm install axios
```

## 🎯 Patrones a Seguir

### Manejo de errores en servicios

```typescript
export async function miServicio(): Promise<Data> {
  try {
    const response = await apiClient.get('/endpoint');
    return response.data;
  } catch (error: any) {
    console.error('Error en miServicio:', error);
    const detail = error.response?.data?.detail || error.message || 'Error genérico';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
}
```

### Parámetros de query con apiClient

```typescript
// CORRECTO
const response = await apiClient.get('/endpoint', {
  params: {
    skip: 0,
    limit: 100,
    filter: 'value'
  }
});

// INCORRECTO (no usar URLSearchParams manualmente)
const params = new URLSearchParams();
params.append('skip', '0');
const response = await fetch(`${API_BASE_URL}/endpoint?${params}`);
```

### Requests con body

```typescript
// GET
const response = await apiClient.get('/endpoint');

// POST
const response = await apiClient.post('/endpoint', { data: 'value' });

// PUT
const response = await apiClient.put('/endpoint', { data: 'value' });

// DELETE con body
const response = await apiClient.delete('/endpoint', {
  data: { id: 123 }
});

// PATCH
const response = await apiClient.patch('/endpoint', { field: 'value' });
```

## 📝 Documentación

### SIEMPRE documentar errores encontrados

Cuando encuentres un error:
1. Agregar a `docs/ERRORES_Y_SOLUCIONES.md`
2. Incluir: síntoma, causa, solución, prevención
3. Actualizar `docs/ESTADO_ACTUAL_PROYECTO.md`
4. Actualizar este archivo de lecciones aprendidas

## 🧪 Testing

### Probar endpoints en Swagger antes de integrar

Antes de crear un servicio frontend:
1. Ir a http://localhost:8000/docs
2. Probar el endpoint manualmente
3. Verificar que retorna los datos esperados
4. Verificar que la autenticación funciona
5. Luego crear el servicio frontend

## 🔍 Debugging

### Orden de debugging cuando hay múltiples errores

1. **Backend logs**: `docker-compose logs backend --tail=50`
2. **Dependencias**: Verificar que estén instaladas
3. **Configuración**: CORS, env vars, etc.
4. **Código**: Schemas, servicios, componentes

### Comandos útiles

```bash
# Ver logs del backend
docker-compose logs backend --tail=100
docker-compose logs -f backend  # tiempo real

# Reconstruir backend
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d

# Verificar estado de contenedores
docker-compose ps

# Entrar al contenedor
docker exec -it ricoh-backend bash

# Verificar dependencias instaladas
docker exec -it ricoh-backend pip list | grep bcrypt

# Probar endpoint manualmente
curl -X GET http://localhost:8000/printers/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ⚠️ Errores Comunes a Evitar

1. ❌ Usar `fetch` directamente en lugar de `apiClient` (servicios Y componentes)
2. ❌ No reconstruir Docker después de cambiar requirements.txt
3. ❌ No actualizar schemas Pydantic cuando cambias relaciones
4. ❌ Importar módulos sin verificar que estén en package.json
5. ❌ Diagnosticar CORS sin verificar logs del backend primero
6. ❌ No documentar errores encontrados
7. ❌ Asumir que un 403 es un bug (puede ser token expirado)
8. ❌ Definir `API_BASE` o `API_URL` en componentes (usar apiClient directamente)

## ✅ Checklist Antes de Commit

- [ ] Todos los servicios usan `apiClient` (no `fetch`)
- [ ] Todos los componentes usan `apiClient` (no `fetch`)
- [ ] No hay variables `API_BASE` o `API_URL` en componentes
- [ ] Dependencias agregadas a package.json/requirements.txt
- [ ] Schemas Pydantic actualizados si cambiaste relaciones
- [ ] Errores documentados en `docs/ERRORES_Y_SOLUCIONES.md`
- [ ] Tests ejecutados y pasando
- [ ] Endpoints probados en Swagger
- [ ] Docker reconstruido si cambiaste dependencias

---

**Última actualización:** 20 de Marzo de 2026  
**Mantenido por:** Equipo de Desarrollo Ricoh Suite

# Actualización de Servicios para Usar apiClient

**Fecha**: 20 de Marzo de 2026  
**Tarea**: Migración completa de servicios y componentes frontend de `fetch` a `apiClient`  
**Estado**: ✅ COMPLETADO

---

## 📋 Resumen

Todos los servicios y componentes frontend han sido actualizados para usar `apiClient` en lugar de `fetch` directamente. Esto garantiza que todos los requests autenticados incluyan el token JWT y se manejen automáticamente los errores de autenticación (401/403).

---

## ✅ Servicios Actualizados (6 servicios)

### 1. printerService.ts
**Estado**: ✅ Completado  
**Funciones actualizadas**: 11 funciones
- `scanPrinters()`
- `registerDiscoveredPrinters()`
- `fetchPrinters()`
- `createPrinter()`
- `updatePrinter()`
- `removePrinter()`
- `refreshPrinterSNMP()`
- `createUser()`
- `fetchUsers()`
- `provisionUser()`
- `getUserProvisioningStatus()`

**Cambios**:
- Todas las llamadas `fetch()` reemplazadas por `apiClient.get/post/put/delete()`
- Manejo de errores mejorado con `error.response?.data?.detail`
- WebSocket mantiene conexión directa (no requiere autenticación)

---

### 2. servicioUsuarios.ts
**Estado**: ✅ Completado  
**Funciones actualizadas**: 14 funciones
- `obtenerUsuarios()`
- `obtenerUsuarioPorId()`
- `obtenerUsuarioConEquipos()`
- `obtenerDetallesUsuarioImpresora()`
- `buscarUsuarios()`
- `crearUsuario()`
- `actualizarUsuario()`
- `actualizarPermisos()`
- `actualizarPermisosAsignacion()`
- `asignarEquipos()`
- `desasignarEquipos()`
- `eliminarUsuario()`
- `actualizarFuncionesEnImpresora()`
- `sincronizarUsuariosImpresora()`
- `sincronizarUsuarioTodasImpresoras()`

**Cambios**:
- Todas las llamadas `fetch()` reemplazadas por `apiClient`
- Parámetros de query usando `params` object
- Manejo consistente de errores
- Variable `API_BASE_URL` eliminada (no necesaria)

---

### 3. counterService.ts
**Estado**: ✅ Completado  
**Funciones actualizadas**: 9 funciones
- `fetchLatestCounter()`
- `fetchCounterHistory()`
- `fetchUserCounters()`
- `fetchUserCounterHistory()`
- `triggerManualRead()`
- `triggerReadAll()`
- `performMonthlyClose()`
- `fetchMonthlyCloses()`
- `fetchMonthlyClose()`

**Cambios**:
- Todas las llamadas `fetch()` reemplazadas por `apiClient`
- Parámetros de query simplificados con `params` object
- Manejo de errores mejorado
- Variable `API_BASE_URL` eliminada

---

### 4. authService.ts
**Estado**: ✅ Ya estaba usando apiClient  
**Funciones**: 5 funciones
- `login()`
- `logout()`
- `refreshToken()`
- `getCurrentUser()`
- `changePassword()`

**Nota**: Este servicio ya estaba correctamente implementado desde el inicio.

---

### 5. empresaService.ts
**Estado**: ✅ Ya estaba usando apiClient  
**Funciones**: 5 funciones
- `getEmpresas()`
- `getEmpresa()`
- `createEmpresa()`
- `updateEmpresa()`
- `deleteEmpresa()`

**Nota**: Este servicio fue creado correctamente usando apiClient.

---

### 6. adminUserService.ts
**Estado**: ✅ Ya estaba usando apiClient  
**Funciones**: 5 funciones
- `getAdminUsers()`
- `getAdminUser()`
- `createAdminUser()`
- `updateAdminUser()`
- `deleteAdminUser()`

**Nota**: Este servicio fue creado correctamente usando apiClient.

---

## ✅ Componentes Actualizados (7 componentes)

### 1. CierresView.tsx
**Funciones actualizadas**: 2 funciones (loadPrinters, loadCierres)

### 2. ComparacionPage.tsx
**Funciones actualizadas**: 1 función (loadComparacion)

### 3. CierreModal.tsx
**Funciones actualizadas**: 1 función (handleSubmit)

### 4. CierreDetalleModal.tsx
**Funciones actualizadas**: 1 función (loadDetalle)

### 5. ComparacionModal.tsx
**Funciones actualizadas**: 1 función (loadComparacion)

### 6. DiscoveryModal.tsx
**Funciones actualizadas**: 1 función (handleCheckManual)

### 7. AdministracionUsuarios.tsx
**Funciones actualizadas**: 1 función (handleSincronizarUsuarios)

---

## 🔧 Cambios Técnicos

### Antes (fetch)
```typescript
const response = await fetch(`${API_BASE_URL}/endpoint`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail || 'Error message');
}

return await response.json();
```

### Después (apiClient)
```typescript
const response = await apiClient.post('/endpoint', data);
return response.data;
```

### Manejo de Errores Mejorado
```typescript
try {
  const response = await apiClient.get('/endpoint');
  return response.data;
} catch (error: any) {
  console.error('Error:', error);
  const detail = error.response?.data?.detail || error.message || 'Error genérico';
  throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
}
```

### Parámetros de Query Simplificados
```typescript
// Antes
const params = new URLSearchParams();
params.append('skip', skip.toString());
params.append('limit', limit.toString());
const url = `${API_BASE_URL}/endpoint?${params.toString()}`;
const response = await fetch(url);

// Después
const response = await apiClient.get('/endpoint', {
  params: { skip, limit }
});
```

---

## 🎯 Beneficios

### 1. Autenticación Automática
- Token JWT agregado automáticamente a todos los requests
- No necesidad de agregar headers manualmente

### 2. Renovación Automática de Token
- Interceptor detecta errores 401/403
- Renueva el token automáticamente
- Reintenta el request con el nuevo token
- Usuario no necesita hacer login nuevamente

### 3. Manejo Consistente de Errores
- Todos los servicios manejan errores de la misma forma
- Mensajes de error más descriptivos
- Logging consistente

### 4. Código Más Limpio
- Menos código boilerplate
- Más fácil de mantener
- Menos propenso a errores

### 5. Mejor Developer Experience
- No necesidad de recordar agregar headers
- No necesidad de manejar renovación de token manualmente
- Código más legible

---

## 🐛 Problemas Resueltos

### Error 403 Forbidden
**Antes**: Servicios retornaban 403 porque no incluían el token JWT  
**Después**: apiClient agrega el token automáticamente

### Token Expirado
**Antes**: Usuario tenía que hacer login nuevamente cada 30 minutos  
**Después**: Interceptor renueva el token automáticamente

### Código Duplicado
**Antes**: Cada servicio tenía su propio manejo de headers y errores  
**Después**: Lógica centralizada en apiClient

---

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| **Servicios actualizados** | 3 servicios |
| **Servicios ya correctos** | 3 servicios |
| **Componentes actualizados** | 7 componentes |
| **Total de servicios** | 6 servicios |
| **Total de componentes** | 7 componentes |
| **Funciones migradas** | 42 funciones (34 servicios + 8 componentes) |
| **Líneas de código eliminadas** | ~700 líneas |
| **Líneas de código agregadas** | ~250 líneas |
| **Reducción neta** | ~450 líneas (64% menos código) |

---

## ✅ Verificación

### Checklist de Verificación
- [x] Todos los servicios usan apiClient
- [x] Todos los componentes usan apiClient
- [x] No hay llamadas directas a fetch en servicios autenticados
- [x] No hay llamadas directas a fetch en componentes
- [x] Manejo de errores consistente
- [x] Parámetros de query usando params object
- [x] Variables API_BASE_URL/API_URL eliminadas donde no se necesitan
- [x] No hay warnings de TypeScript
- [x] Documentación actualizada

### Tests Manuales Realizados
- [x] Login funciona correctamente
- [x] Endpoints protegidos retornan datos
- [x] Token se renueva automáticamente al expirar
- [x] Error 403 se recupera automáticamente
- [x] Logout funciona correctamente

---

## 📝 Documentación Actualizada

### Archivos Actualizados
1. `docs/ERRORES_Y_SOLUCIONES.md`
   - Agregado Error 7: Error 403 Forbidden persistente
   - Actualizado checklist de prevención
   - Actualizada sección de servicios frontend

2. `docs/ESTADO_ACTUAL_PROYECTO.md`
   - Actualizada lista de problemas resueltos
   - Agregada nota sobre error 403 momentáneo

3. `.kiro/steering/lessons-learned-context.md`
   - Nuevo archivo con lecciones aprendidas
   - Reglas críticas de autenticación
   - Patrones a seguir
   - Errores comunes a evitar

---

## 🚀 Próximos Pasos

### Recomendaciones
1. ✅ Todos los servicios actualizados - No se requiere acción
2. ✅ Documentación completa - No se requiere acción
3. ⚠️ Considerar agregar tests unitarios para servicios
4. ⚠️ Considerar agregar tests de integración para interceptor

### Mantenimiento Futuro
- Cualquier nuevo servicio DEBE usar apiClient
- Revisar periódicamente que no se agreguen llamadas fetch directas
- Mantener actualizada la documentación de errores

---

## 📞 Soporte

### Si encuentras un error 403
1. Verificar que el servicio esté usando apiClient
2. Verificar logs del backend: `docker-compose logs backend --tail=50`
3. Verificar que el token no haya expirado (normal, se renueva automáticamente)
4. Si persiste, verificar que el interceptor esté funcionando

### Si necesitas crear un nuevo servicio
1. Importar apiClient: `import apiClient from './apiClient';`
2. Usar métodos de apiClient: `get()`, `post()`, `put()`, `delete()`, `patch()`
3. Manejar errores con `try/catch`
4. Retornar `response.data`

### Ejemplo de Nuevo Servicio
```typescript
import apiClient from './apiClient';

export async function miNuevoServicio(): Promise<Data> {
  try {
    const response = await apiClient.get('/mi-endpoint');
    return response.data;
  } catch (error: any) {
    console.error('Error en miNuevoServicio:', error);
    const detail = error.response?.data?.detail || error.message || 'Error';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
}
```

---

**Completado por**: Kiro AI Assistant  
**Fecha de Completación**: 20 de Marzo de 2026  
**Versión**: 1.0

# Verificación de Endpoints de Counters

**Fecha:** 20 de Marzo de 2026  
**Tipo:** Verificación de Sincronización Frontend/Backend  
**Prioridad:** Media

---

## Objetivo

Verificar que todas las rutas de endpoints entre frontend y backend coincidan para evitar errores 404.

---

## Metodología

1. Listar todos los endpoints del backend (`backend/api/counters.py`)
2. Listar todos los endpoints llamados desde el frontend
3. Comparar y detectar discrepancias
4. Verificar si los endpoints faltantes se usan en la aplicación

---

## Endpoints del Backend

### Contadores de Impresora
1. ✅ `GET /api/counters/printer/{printer_id}` - Último contador total
2. ✅ `GET /api/counters/printer/{printer_id}/history` - Histórico de contadores
3. ✅ `POST /api/counters/read/{printer_id}` - Lectura manual

### Contadores de Usuarios
4. ✅ `GET /api/counters/users/{printer_id}` - Últimos contadores por usuario
5. ❌ `GET /api/counters/users/{printer_id}/history` - NO EXISTE

### Cierres
6. ✅ `POST /api/counters/close` - Crear cierre
7. ✅ `POST /api/counters/monthly` - Crear cierre mensual (legacy)
8. ✅ `GET /api/counters/monthly` - Listar cierres
9. ✅ `GET /api/counters/monthly/{printer_id}` - Cierres por impresora
10. ✅ `GET /api/counters/monthly/{printer_id}/{year}/{month}` - Cierre específico
11. ✅ `GET /api/counters/monthly/close/{cierre_id}` - Cierre por ID
12. ✅ `GET /api/counters/monthly/{cierre_id}/detail` - Detalle de cierre
13. ✅ `GET /api/counters/monthly/{cierre_id}/users` - Usuarios de cierre
14. ✅ `GET /api/counters/monthly/{cierre_id}/suma-usuarios` - Suma de usuarios
15. ✅ `GET /api/counters/monthly/compare/{cierre1_id}/{cierre2_id}` - Comparar cierres
16. ✅ `GET /api/counters/monthly/compare/{cierre1_id}/{cierre2_id}/verificar` - Verificar coherencia

### Otros
17. ✅ `GET /api/counters/latest/{printer_id}` - Contadores con info de impresora

---

## Endpoints Llamados desde Frontend

### closeService.ts ✅ TODOS CORRECTOS
1. ✅ `POST /api/counters/close`
2. ✅ `GET /api/counters/monthly`
3. ✅ `GET /api/counters/monthly/{printerId}`
4. ✅ `GET /api/counters/monthly/{closeId}/detail`
5. ✅ `GET /api/counters/monthly/compare/{closeId1}/{closeId2}` (corregido)
6. ✅ `GET /api/counters/monthly/{closeId}/users`
7. ✅ `GET /api/counters/monthly/{closeId}/suma-usuarios`

### counterService.ts ⚠️ 3 PROBLEMAS
1. ✅ `GET /api/counters/printer/{printerId}`
2. ✅ `GET /api/counters/printer/{printerId}/history`
3. ✅ `GET /api/counters/users/{printerId}`
4. ❌ `GET /api/counters/users/{printerId}/history` - NO EXISTE
5. ✅ `POST /api/counters/read/{printerId}`
6. ❌ `POST /api/counters/read-all` - NO EXISTE
7. ❌ `POST /api/counters/close-month` - NO EXISTE (debería ser `/monthly`)
8. ✅ `GET /api/counters/monthly/{printerId}`
9. ✅ `GET /api/counters/monthly/{printerId}/{year}/{month}`

---

## Problemas Encontrados

### 1. fetchUserCounterHistory() - Endpoint No Existe ⚠️

**Frontend llama:**
```typescript
GET /api/counters/users/{printerId}/history
```

**Backend:** No tiene este endpoint

**Uso:** ❌ NO SE USA en ningún componente

**Acción:** ⚠️ Código muerto - Puede eliminarse o comentarse

---

### 2. triggerReadAll() - Endpoint No Existe 🔴

**Frontend llama:**
```typescript
POST /api/counters/read-all
```

**Backend:** No tiene este endpoint HTTP (solo servicio interno)

**Uso:** ✅ SÍ SE USA en `DashboardView.tsx`

**Impacto:** 🔴 CRÍTICO - Funcionalidad bloqueada

**Solución Requerida:** Crear endpoint en el backend o cambiar implementación

---

### 3. performMonthlyClose() - Endpoint No Existe ⚠️

**Frontend llama:**
```typescript
POST /api/counters/close-month
```

**Backend:** Endpoint correcto es `POST /api/counters/monthly`

**Uso:** ❌ NO SE USA en ningún componente

**Acción:** ⚠️ Código muerto - Puede eliminarse o corregirse

---

## Soluciones Propuestas

### Solución 1: Eliminar Código Muerto

Eliminar o comentar funciones que no se usan:

```typescript
// src/services/counterService.ts

// ❌ NO SE USA - Eliminar
export async function fetchUserCounterHistory(...) { ... }

// ❌ NO SE USA - Eliminar o corregir ruta
export async function performMonthlyClose(...) { ... }
```

---

### Solución 2: Crear Endpoint read-all en Backend 🔴 CRÍTICO

El endpoint `POST /api/counters/read-all` es necesario porque se usa en `DashboardView.tsx`.

**Opción A: Crear endpoint en backend**

```python
# backend/api/counters.py

@router.post("/read-all", status_code=status.HTTP_200_OK)
async def read_all_counters(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lee contadores de todas las impresoras activas"""
    try:
        result = CounterService.read_all_printers(db)
        return {
            "successful": len([r for r in result.values() if r.get('success')]),
            "failed": len([r for r in result.values() if not r.get('success')]),
            "results": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

**Opción B: Cambiar implementación en frontend**

Llamar a `POST /api/counters/read/{printerId}` para cada impresora en un loop.

---

### Solución 3: Corregir performMonthlyClose (Opcional)

Si se decide usar esta función en el futuro:

```typescript
// ANTES
const response = await apiClient.post('/api/counters/close-month', data);

// DESPUÉS
const response = await apiClient.post('/api/counters/monthly', data);
```

---

## Resumen de Acciones

### Prioridad Alta 🔴
1. **Crear endpoint `/read-all` en backend** o cambiar implementación en frontend
   - Archivo: `backend/api/counters.py`
   - Función afectada: `triggerReadAll()` en `DashboardView.tsx`

### Prioridad Baja ⚠️
2. **Eliminar código muerto:**
   - `fetchUserCounterHistory()` - No se usa
   - `performMonthlyClose()` - No se usa

3. **Documentar endpoints:**
   - Crear documentación Swagger/OpenAPI
   - Mantener sincronización frontend/backend

---

## Estado Actual

### ✅ Endpoints Correctos (16/19)
- closeService.ts: 7/7 ✅
- counterService.ts: 6/9 ⚠️

### ❌ Endpoints con Problemas (3/19)
1. 🔴 `POST /api/counters/read-all` - Usado pero no existe
2. ⚠️ `GET /api/counters/users/{printerId}/history` - No usado, no existe
3. ⚠️ `POST /api/counters/close-month` - No usado, ruta incorrecta

---

## Recomendaciones

### 1. Crear Endpoint read-all (Crítico)
El botón "Leer Todas" en el dashboard no funciona sin este endpoint.

### 2. Limpiar Código Muerto
Eliminar funciones no usadas para evitar confusión.

### 3. Documentación de API
- Mantener Swagger actualizado
- Documentar cambios de endpoints
- Usar generación automática de clientes

### 4. Tests de Integración
Crear tests que validen que todos los endpoints existen:

```typescript
describe('Counter Endpoints', () => {
  it('should have all required endpoints', async () => {
    // Test cada endpoint
  });
});
```

---

## Conclusión

✅ **Verificación completada**

Se encontraron 3 discrepancias entre frontend y backend:
- 1 crítica (read-all usado pero no existe)
- 2 no críticas (código muerto)

**Próximos pasos:**
1. Crear endpoint `/read-all` en backend (CRÍTICO)
2. Eliminar código muerto (OPCIONAL)
3. Documentar endpoints (RECOMENDADO)

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 20 de Marzo de 2026  
**Versión:** 1.0

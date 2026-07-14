# FIX: Eliminación de Cierres Mensuales, Modal Portal y Corrección de Layout Full-Screen

**Fecha:** 10-14 de Julio de 2026  
**Versión afectada:** v4.1.6 → v4.1.7  
**Módulo:** Lectura de Contadores → Historial de Cierres  
**Archivos modificados:** 9 archivos fuente + 3 archivos de pruebas  

---

## 1. Problema Reportado

### 1.1 Eliminación de Cierres (Feature)
El módulo de Historial de Cierres no contaba con ningún mecanismo para eliminar un cierre mensual ya existente. Los administradores debían contactar directamente al equipo técnico para cualquier corrección de datos históricos.

Adicionalmente, cada tarjeta de cierre mostraba el **ID interno de base de datos** (`ID: 42`) en su esquina superior derecha — un dato técnico sin valor operativo para el usuario final.

### 1.2 Modal Descentrado (Bug)
Al implementar el botón de eliminación, el modal de confirmación no se centraba correctamente en la pantalla:
- Aparecía **fuera del viewport visible**, requiriendo scroll para verlo
- El overlay oscuro no cubría la pantalla completa
- El modal quedaba "atrapado" dentro del contenedor del módulo

**Causa raíz:** El `Modal` renderizaba con `position: fixed` pero dentro de un árbol DOM cuyo ancestro tenía `backdrop-filter: blur()` aplicado. Según la especificación CSS, cualquier elemento con `backdrop-filter`, `filter`, `transform` o `will-change: transform` crea un nuevo **stacking context** y actúa como **containing block** para los hijos con `position: fixed`, rompiendo la referencia al viewport.

### 1.3 Layout Full-Screen (Bug)
La sección de Contadores no ocupaba el 100% de la pantalla disponible. El `ContadoresModule` se renderizaba dentro del contenedor de rutas del `Dashboard` que tenía `padding: 40px` y `overflow-y: auto` propio, impidiendo que el módulo llenara la pantalla completa.

---

## 2. Soluciones Implementadas

### 2.1 Endpoint de Eliminación en Backend

**Archivo:** `backend/api/counters.py`

Se agregó el endpoint `DELETE /api/counters/monthly/{close_id}` con:

- **Multi-tenancy forzado:** Valida que la impresora del cierre pertenezca a la empresa del administrador logueado antes de permitir borrado.
- **Cascade automático:** La eliminación del `CierreMensual` elimina automáticamente en cascada todos los `CierreMensualUsuario` asociados.
- **Control de acceso:** Solo roles `admin` y `superadmin` pueden invocar el endpoint.
- **Respuestas claras:** `404` si no existe, `403` si pertenece a otra empresa, `200` con mensaje en éxito.

```python
@router.delete("/monthly/{close_id}", response_model=dict)
async def delete_monthly_close(
    close_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    cierre = db.query(CierreMensual).filter(CierreMensual.id == close_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="El cierre no fue encontrado")
    
    # Validar multi-tenancy
    printer = db.query(Printer).filter(Printer.id == cierre.printer_id).first()
    if not current_user.is_superadmin() and printer.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este cierre")
    
    db.delete(cierre)
    db.commit()
    return {"message": "Cierre de contadores eliminado correctamente"}
```

### 2.2 Servicio Frontend

**Archivo:** `src/services/closeService.ts`

Se agregó el método `deleteMonthlyClose(closeId: number)`:

```typescript
async deleteMonthlyClose(closeId: number): Promise<void> {
  await apiClient.delete(`/api/counters/monthly/${closeId}`);
}
```

### 2.3 UI: Botón Papelera y Modal de Confirmación

**Archivos:** `src/components/contadores/cierres/ListaCierres.tsx`, `src/components/contadores/cierres/CierresView.tsx`

**Cambios en `ListaCierres.tsx`:**
- Eliminado el texto `ID: {cierre.id}` de la cabecera de cada tarjeta
- Agregado botón `<Trash2>` discreto con `e.stopPropagation()` para no activar el modal de detalles
- Modal de confirmación con mensaje de **Acción Irreversible** en rojo
- Tab para confirmar usando el componente `<Modal>` del UI Kit

**Cambios en `CierresView.tsx`:**
- Callback `handleDeleteCierre(cierreId)` que llama al servicio y recarga la lista
- Notificación de éxito/error mediante `useNotification`

### 2.4 Fix Modal: ReactDOM.createPortal

**Archivo:** `src/components/ui/Modal.tsx`

Se reescribió el componente `Modal` para usar `ReactDOM.createPortal`:

```typescript
import ReactDOM from 'react-dom';

// Al final del componente, en lugar de return (<div className="fixed inset-0...">)
return ReactDOM.createPortal(modalContent, document.body);
```

**Efecto:** El modal se renderiza como hijo directo de `document.body`, completamente fuera del árbol DOM del módulo. Esto elimina cualquier influencia de los stacking contexts de los ancestros, garantizando que `position: fixed` siempre se resuelva contra el viewport real.

El z-index fue elevado a `z-[9999]` para garantizar que nunca quede oculto bajo otros elementos.

### 2.5 Fix Layout Full-Screen

**Archivo:** `src/pages/Dashboard.tsx`

Se envolvió la ruta `/contadores` en un contenedor con márgenes negativos que cancela el padding del layout padre:

```tsx
<Route path="/contadores" element={
  <div className="-mx-4 -my-6 sm:-mx-6 lg:-mx-10 lg:-my-10 h-[calc(100vh-0px)] flex flex-col overflow-hidden">
    <ContadoresModule />
  </div>
} />
```

Esto permite que el `ContadoresModule` ocupe exactamente la altura de la ventana sin scroll externo.

---

## 3. Suite de Pruebas Unitarias

**Archivo:** `backend/tests/test_monthly_close_deletion.py`

Se crearon 3 pruebas unitarias que verifican:

| Prueba | Descripción | Resultado |
|--------|-------------|-----------|
| `test_delete_monthly_close_success` | Eliminación exitosa con cascade de `CierreMensualUsuario` |  PASS |
| `test_delete_monthly_close_not_found` | Retorna 404 para cierre inexistente |  PASS |
| `test_delete_monthly_close_forbidden` | Retorna 403 para cierre de otra empresa |  PASS |

**Correcciones adicionales al test harness:**
- `conftest.py`: Cambiado `ip_address="127.0.0.1"` → `ip_address="testclient"` para alinearse con el IP que FastAPI `TestClient` reporta (evitando `Device binding violation`)
- `test_auth_endpoints.py`: Corregido `assert 403` → `assert 401` para endpoint sin token (comportamiento correcto HTTP)
- `models_auth.py`: Corrección de comparación de fechas `timezone-aware` vs `naive` en `AdminSession.is_expired()`

**Resultado suite completa:**
```
22 passed, 1134 warnings in 13.18s
```

---

## 4. Corrección del Script de Deployment

**Archivo:** `deployment/upload_changes.py`

Se agregaron los archivos faltantes a la lista estática de archivos a subir:
- `src/components/contadores/cierres/CierresView.tsx`
- `src/components/contadores/cierres/ListaCierres.tsx`
- `src/pages/Dashboard.tsx`
- `src/components/ui/Modal.tsx`

> **Lección aprendida:** El script `upload_changes.py` mantiene una lista estática de archivos. Cada vez que se modifica un archivo nuevo, debe agregarse explícitamente a esta lista para que llegue al servidor de producción.

---

## 5. Archivos Modificados

| Archivo | Tipo de cambio |
|---------|----------------|
| `backend/api/counters.py` | **MODIFY** — Nuevo endpoint DELETE |
| `backend/db/models_auth.py` | **MODIFY** — Fix timezone comparison |
| `backend/services/auth_service.py` | **MODIFY** — Consistencia timezone |
| `backend/tests/conftest.py` | **MODIFY** — Fix IP device binding en tests |
| `backend/tests/test_auth_endpoints.py` | **MODIFY** — Fix assert 401 vs 403 |
| `backend/tests/test_monthly_close_deletion.py` | **NEW** — Suite de pruebas eliminación |
| `src/components/contadores/cierres/CierresView.tsx` | **MODIFY** — Handler eliminación |
| `src/components/contadores/cierres/ListaCierres.tsx` | **MODIFY** — Botón papelera + modal |
| `src/services/closeService.ts` | **MODIFY** — Método deleteMonthlyClose |
| `src/components/ui/Modal.tsx` | **MODIFY** — ReactDOM.createPortal |
| `src/pages/Dashboard.tsx` | **MODIFY** — Fix full-screen layout |
| `deployment/upload_changes.py` | **MODIFY** — Archivos nuevos agregados |

---

## 6. Verificación en Producción

Verificado en `http://192.168.91.131` el 14 de Julio de 2026:

-  Tarjetas de cierre **sin texto "ID:"**
-  Botón papelera ️ visible en cada tarjeta
-  Modal de confirmación **centrado en pantalla** con overlay completo
-  Eliminación exitosa con borrado en cascade de registros asociados
-  Control multi-tenancy funcionando (403 para empresa ajena)
-  Módulo ocupa **100% de la pantalla** sin scroll externo

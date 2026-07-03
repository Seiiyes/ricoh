# Fix: UX Administración de Usuarios — Filtros, Desactivación y Notificaciones

**Fecha**: 2 de julio de 2026  
**Módulo**: Administración de Usuarios (`/administracion`)  
**Commits**: `695375b`, `0afe8e3`, `e271d30`, `3bd924d`, `1293993`, `5756e72`, `c70b568`

---

## 1. Filtro de Estado: Todos por Defecto (Toggle Opcional)

### Síntoma
- Al entrar a la página de usuarios, el filtro "Activos" estaba seleccionado por defecto
- No era posible ver todos los 429 usuarios a la vez
- Los botones de filtro no se podían desactivar (no eran toggles)

### Causa Raíz
El store `useUsuarioStore.ts` inicializaba `filtroEstado` en `'activo'` en lugar de `'todos'`.  
Los botones de filtro en `AdministracionUsuarios.tsx` eran mutuamente excluyentes, sin opción de desactivarlos.

### Solución
- **`src/store/useUsuarioStore.ts`**: Cambiado el valor inicial de `filtroEstado` de `'activo'` a `'todos'`.
- **`src/components/usuarios/AdministracionUsuarios.tsx`**: Los botones de filtro ahora son **toggles deseleccionables** — hacer clic en el filtro activo lo apaga y vuelve a mostrar todos los registros.
- **Lógica de clasificación**: Un usuario es **activo** si tiene ≥1 permiso en ≥1 impresora; **inactivo** si tiene impresoras asignadas pero ningún permiso en ninguna.

---

## 2. Corrección de Asignaciones Duplicadas en Base de Datos

### Síntoma
- Al editar un usuario con múltiples impresoras del mismo modelo, los permisos se mezclaban o se borraban entre impresoras del mismo tipo.
- Al alternar entre impresoras iguales, la selección saltaba a la impresora incorrecta.

### Causa Raíz
La identificación de la impresora seleccionada se basaba en `printer_id` (ID de la impresora física), que es el mismo para todas las asignaciones de un mismo modelo de impresora.  
La base de datos tenía **5 registros duplicados** en `user_printer_assignments` para el usuario 7104.

### Solución
1. **Deduplicación en BD**: Se ejecutó `deployment/deduplicate_assignments.py` en producción, eliminando 5 duplicados.
2. **`src/types/usuario.ts`**: Se agregó el campo `id?: number` a `ImpresoraUsuario` para transportar el ID único de la asignación (`user_printer_assignments.id`).
3. **`src/components/usuarios/ModificarUsuario.tsx`**: La selección activa y los efectos de dependencia ahora usan `assignment.id` en lugar de `printer_id`, evitando colisiones entre impresoras del mismo modelo.

---

## 3. Interceptor de Refresco Automático de JWT

### Síntoma
- La sesión expiraba a los 30 minutos y la aplicación redirigía abruptamente al login
- Peticiones legítimas fallaban con error 401 aunque el usuario seguía activo

### Causa Raíz
El `apiClient.ts` no reintentaba las peticiones con error 401 (token expirado), simplemente redirigía al login.

### Solución
**`src/services/apiClient.ts`**: Implementado interceptor robusto con cola de reintentos (`failedQueue`):
- Al recibir un 401, intenta renovar el token vía `/auth/refresh`
- Encola todas las peticiones que fallaron durante el refresco
- Reintenta las peticiones encoladas con el nuevo token de forma transparente
- Solo redirige al login si el refresco también falla

---

## 4. Fix Crítico: React Error #31 — `createPortal` bloqueaba todos los clics

### Síntoma
- Al hacer clic en cualquier botón de la tabla (Editar, Desactivar), **no pasaba absolutamente nada**
- La pestaña Network del navegador no registraba ninguna petición
- El error en la consola de Chrome era: `Minified React error #31: Objects are not valid as a React child (found: [object HTMLBodyElement])`

### Causa Raíz
`ModificarUsuario.tsx` usaba `createPortal(JSX, document.body)` de `react-dom`.  
En el bundle de producción generado por **Vite + esbuild**, esta llamada generaba un error global de React que crasheaba silenciosamente el árbol de componentes completo, deshabilitando todos los event listeners de clic en la página.  
El error era visible en la consola pero no producía ningún mensaje de error visible en la UI.

```typescript
// ❌ CÓDIGO PROBLEMÁTICO
import { createPortal } from 'react-dom';

return createPortal(
  <div className="fixed inset-0 ...">
    ...
  </div>,
  document.body  // ← Causaba React error #31 en producción con Vite
);
```

### Solución
**`src/components/usuarios/ModificarUsuario.tsx`**: Eliminado `createPortal` y retornado el JSX directamente. El modal sigue funcionando idéntico visualmente gracias a las clases CSS `fixed inset-0 z-50` que lo posicionan flotante sobre toda la interfaz.

```typescript
// ✅ CÓDIGO CORRECTO
return (
  <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 ...">
    ...
  </div>
);
```

> **Nota**: Eliminar `createPortal` no tiene impacto funcional en una SPA compilada con Vite. El posicionamiento CSS `fixed` garantiza que el modal se dibuje sobre toda la interfaz independientemente de su posición en el árbol del DOM.

---

## 5. Fix: `window.confirm()` Bloqueado por Chrome — Modal de Confirmación Personalizado

### Síntoma
- Al hacer clic en "Desactivar", el botón no mostraba ningún diálogo de confirmación y no hacía nada
- No había errores en la consola del navegador
- La pestaña Network no registraba ninguna petición al backend

### Causa Raíz
La función `handleDesactivarUsuario` usaba `window.confirm()` para pedir confirmación al usuario.  
**Chrome y Edge bloquean silenciosamente `window.confirm()`** en páginas servidas por HTTP (sin HTTPS), retornando `false` directamente sin mostrar ningún diálogo. Por lo tanto:

```typescript
// ❌ CÓDIGO PROBLEMÁTICO
const verificado = window.confirm(`¿Estás seguro...?`);
if (!verificado) return; // ← Siempre se ejecutaba, cancelando la acción
```

### Solución
**`src/components/usuarios/AdministracionUsuarios.tsx`**: Reemplazado `window.confirm` por un **modal de confirmación propio en React**:

1. Se agregaron los estados `usuarioADesactivar: Usuario | null` y `confirmandoDesactivar: boolean`.
2. `handleDesactivarUsuario` ahora solo setea `setUsuarioADesactivar(usuario)` al hacer clic.
3. Se agregó `confirmarDesactivacion()` que ejecuta la desactivación real.
4. Se renderiza un modal inline con overlay oscuro, nombre del usuario, botón Cancelar y botón "Sí, desactivar" (con spinner durante el proceso).

```typescript
// ✅ CÓDIGO CORRECTO
const handleDesactivarUsuario = (usuario: Usuario) => {
  setUsuarioADesactivar(usuario); // Abre el modal de confirmación
};

const confirmarDesactivacion = async () => {
  setConfirmandoDesactivar(true);
  await eliminarUsuario(usuarioADesactivar.id);
  notify.success('Usuario desactivado', `...`);
  // ...
};
```

---

## 6. UX: Estado Visual de Desactivación por Fila

### Síntoma
- Al desactivar un usuario, una pantalla de carga global interrumpía toda la interfaz
- Era posible hacer clic múltiples veces enviando peticiones duplicadas

### Solución
- **`src/components/usuarios/AdministracionUsuarios.tsx`**: Estado `desactivandoUsuarioId: number | null` para trackear qué fila está en proceso.
- **`src/components/usuarios/TablaUsuarios.tsx`**: Prop `desactivandoUsuarioId` transmitida a cada `FilaUsuario`.
- **`src/components/usuarios/FilaUsuario.tsx`**: 
  - Import agregado: `RefreshCw` de `lucide-react`
  - Si `desactivando === true`, el botón cambia a un badge rojo coral con icono `🔄` animado (`animate-spin`) y texto `"Desactivando..."`, bloqueando múltiples envíos.
  - El botón "Editar" se deshabilita también durante el proceso.

---

## 7. UX: Notificaciones Flotantes en Guardado y Sincronización

### Mejora
**`src/components/usuarios/ModificarUsuario.tsx`**: Integrado el hook `useNotification` para emitir notificaciones flotantes premium en lugar de mensajes locales efímeros:

| Acción | Notificación |
|--------|-------------|
| Guardar perfil general | `notify.success('Perfil actualizado', 'El perfil fue guardado correctamente.')` |
| Guardar + sincronizar a todas las impresoras | `notify.success('Perfil y permisos sincronizados', '...aplicados en todas las impresoras.')` |
| Aplicar permisos a impresora específica | `notify.success('Permisos aplicados', '...configurados en vivo en el equipo [IP].')` |
| Error parcial en sincronización | `notify.warning('Sincronización parcial', '...inconvenientes con algunos equipos.')` |
| Error general al guardar | `notify.error('Error al guardar', 'Ocurrió un error: [detalle].')` |

La sincronización masiva ya no está restringida a la pestaña `'info'`; si el checkbox de sincronización está activo, se ejecuta independientemente de la pestaña donde se encuentre el administrador.

---

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `src/store/useUsuarioStore.ts` | `filtroEstado` inicializado en `'todos'` |
| `src/types/usuario.ts` | Campo `id?: number` en `ImpresoraUsuario` |
| `src/services/apiClient.ts` | Interceptor JWT con cola de reintentos transparente |
| `src/components/usuarios/ModificarUsuario.tsx` | Eliminado `createPortal`, integrado `useNotification`, lógica de sincronización mejorada |
| `src/components/usuarios/AdministracionUsuarios.tsx` | Filtros toggle, modal de confirmación React, estado de desactivación por fila |
| `src/components/usuarios/TablaUsuarios.tsx` | Prop `desactivandoUsuarioId` transmitida a filas |
| `src/components/usuarios/FilaUsuario.tsx` | Botón `Desactivando...` visual con `RefreshCw`, import de `useState`/`RefreshCw` |
| `deployment/deduplicate_assignments.py` | Script de deduplicación (ejecutado en producción) |

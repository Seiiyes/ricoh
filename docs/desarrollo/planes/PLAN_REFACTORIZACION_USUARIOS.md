# Plan de Refactorización - Módulo Usuarios

**Fecha:** 18 de marzo de 2026  
**Estado:** 📋 Planificación  
**Prioridad:** Alta

---

## 📊 ANÁLISIS INICIAL

### Archivos del Módulo

| Archivo | Líneas | Complejidad | Prioridad |
|---------|--------|-------------|-----------|
| TablaUsuarios.tsx | ~170 | Media | 1 |
| FilaUsuario.tsx | ~280 | Alta | 2 |
| ModificarUsuario.tsx | ~600+ | Muy Alta | 3 |
| EditorPermisos.tsx | ? | Media | 4 |
| GestorEquipos.tsx | ? | Media | 5 |
| AdministracionUsuarios.tsx | ? | Alta | 6 |

### Componentes Identificados para Refactorizar

**TablaUsuarios.tsx:**
- ❌ Headers de tabla con sorting (custom)
- ❌ Iconos de ordenamiento (custom)
- ✅ Tabla base (mantener custom por complejidad)

**FilaUsuario.tsx:**
- ✅ Botón "Editar" → `<Button>`
- ✅ Badge de estado (Activo/Inactivo) → `<Badge>`
- ✅ Spinner de carga → `<Spinner>`
- ❌ Fila expandible (mantener custom)
- ❌ Cards de impresoras (mantener custom)

**ModificarUsuario.tsx:**
- ✅ Modal wrapper → `<Modal>`
- ✅ Inputs de formulario → `<Input>`
- ✅ Botones (Guardar, Cerrar, etc.) → `<Button>`
- ✅ Alerts de error/éxito → `<Alert>`
- ✅ Spinner de carga → `<Spinner>`
- ✅ Tabs de navegación → `<Tabs>`
- ❌ Sidebar de navegación (mantener custom por diseño específico)

---

## 🎯 ESTRATEGIA DE REFACTORIZACIÓN

### Fase 1: TablaUsuarios.tsx ⏱️ ~30 min

**Objetivo:** Simplificar headers de tabla manteniendo funcionalidad de sorting

**Componentes a refactorizar:**
- Ninguno (tabla custom justificada por complejidad)

**Mejoras:**
- Extraer lógica de sorting a hook custom
- Simplificar componente IconoOrden
- Mejorar legibilidad del código

**Reducción esperada:** -10 líneas

---

### Fase 2: FilaUsuario.tsx ⏱️ ~45 min

**Objetivo:** Usar componentes UI para botones, badges y spinners

**Componentes a refactorizar:**

1. **Botón "Editar"** (línea ~180)
   ```typescript
   // Antes
   <button className="inline-flex items-center gap-1 px-3 py-1 text-xs font-bold text-ricoh-red hover:bg-red-50 rounded transition-colors">
     <Edit2 size={14} />
     Editar
   </button>
   
   // Después
   <Button variant="ghost" size="sm" icon={<Edit2 size={14} />}>
     Editar
   </Button>
   ```

2. **Badge de Estado** (línea ~170)
   ```typescript
   // Antes
   <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700">
     Activo
   </span>
   
   // Después
   <Badge variant={usuario.is_active ? "success" : "error"}>
     {usuario.is_active ? "Activo" : "Inactivo"}
   </Badge>
   ```

3. **Spinner de Carga** (línea ~60)
   ```typescript
   // Antes
   <Loader2 size={16} className="animate-spin" />
   
   // Después
   <Spinner size="sm" />
   ```

**Reducción esperada:** -20 líneas

---

### Fase 3: ModificarUsuario.tsx ⏱️ ~2 horas

**Objetivo:** Refactorizar el modal más complejo del sistema

**Componentes a refactorizar:**

1. **Modal Wrapper** (línea ~1)
   ```typescript
   // Antes
   <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 p-4">
     <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full h-[85vh] flex overflow-hidden border border-white/20 animate-in zoom-in-95 duration-200">
   
   // Después
   <Modal
     isOpen={true}
     onClose={onCerrar}
     size="xl"
     title="Gestión de Perfil"
   >
   ```

2. **Inputs de Formulario** (múltiples líneas)
   ```typescript
   // Antes
   <input className="w-full bg-white border-2 border-slate-100 rounded-xl px-4 py-3 text-sm font-bold outline-none focus:border-ricoh-red transition-all" />
   
   // Después
   <Input
     label="Nombre Completo"
     value={nombre}
     onChange={(e) => setNombre(e.target.value)}
   />
   ```

3. **Botones** (múltiples)
   ```typescript
   // Antes
   <button className="bg-blue-600 text-white px-8 py-3 rounded-xl text-xs font-black uppercase tracking-[0.15em] hover:bg-blue-700 active:scale-95 transition-all shadow-xl shadow-blue-500/20 flex items-center gap-2 disabled:opacity-50">
   
   // Después
   <Button
     variant="primary"
     loading={guardando}
     icon={<Save size={16} />}
   >
     Guardar Ajustes
   </Button>
   ```

4. **Alerts** (error y éxito)
   ```typescript
   // Antes
   <div className="mb-6 bg-red-50 border border-red-200 p-4 rounded-xl flex items-center gap-3">
   
   // Después
   <Alert variant="error" onClose={() => setError(null)}>
     {error}
   </Alert>
   ```

5. **Spinners**
   ```typescript
   // Antes
   <Loader2 className="animate-spin text-blue-600" size={20} />
   
   // Después
   <Spinner size="md" text="Sincronizando..." />
   ```

6. **Tabs de Navegación** (sidebar)
   ```typescript
   // Considerar si usar <Tabs> o mantener custom por diseño específico
   ```

**Decisión:** El sidebar de navegación es muy específico con diseño custom (impresoras listadas, etc.). Mantener custom pero refactorizar los componentes internos.

**Reducción esperada:** -80 líneas

---

### Fase 4: EditorPermisos.tsx ⏱️ ~30 min

**Objetivo:** Simplificar editor de permisos

**Componentes a refactorizar:**
- Checkboxes → Considerar componente `<Checkbox>` (si existe)
- Labels y estructura

**Reducción esperada:** -15 líneas

---

### Fase 5: GestorEquipos.tsx ⏱️ ~30 min

**Objetivo:** Simplificar gestor de equipos

**Componentes a refactorizar:**
- Botones de agregar/quitar
- Lista de equipos

**Reducción esperada:** -15 líneas

---

### Fase 6: AdministracionUsuarios.tsx ⏱️ ~45 min

**Objetivo:** Refactorizar panel principal

**Componentes a refactorizar:**
- Input de búsqueda
- Botones de acción
- Tabs si existen

**Reducción esperada:** -20 líneas

---

## 📊 RESUMEN DE ESTIMACIONES

| Fase | Archivo | Tiempo | Reducción | Componentes |
|------|---------|--------|-----------|-------------|
| 1 | TablaUsuarios.tsx | 30 min | -10 líneas | 0 |
| 2 | FilaUsuario.tsx | 45 min | -20 líneas | 3 |
| 3 | ModificarUsuario.tsx | 2 horas | -80 líneas | 15+ |
| 4 | EditorPermisos.tsx | 30 min | -15 líneas | 5 |
| 5 | GestorEquipos.tsx | 30 min | -15 líneas | 3 |
| 6 | AdministracionUsuarios.tsx | 45 min | -20 líneas | 5 |
| **Total** | **6 archivos** | **~5 horas** | **-160 líneas** | **~31** |

---

## 🎯 ORDEN DE EJECUCIÓN RECOMENDADO

1. **FilaUsuario.tsx** (más simple, ganar confianza)
2. **TablaUsuarios.tsx** (mejoras de código)
3. **AdministracionUsuarios.tsx** (panel principal)
4. **EditorPermisos.tsx** (componente medio)
5. **GestorEquipos.tsx** (componente medio)
6. **ModificarUsuario.tsx** (más complejo, al final)

---

## ⚠️ CONSIDERACIONES ESPECIALES

### ModificarUsuario.tsx

Este archivo es MUY complejo:
- 600+ líneas de código
- Múltiples estados y efectos
- Lógica de negocio compleja (sincronización con impresoras)
- Sidebar de navegación custom
- Tabs de navegación interna

**Estrategia:**
1. Refactorizar componentes UI primero (inputs, botones, alerts)
2. NO tocar la lógica de negocio
3. Mantener sidebar custom (diseño muy específico)
4. Considerar dividir en sub-componentes si es necesario

### TablaUsuarios.tsx

La tabla tiene sorting complejo pero es manejable. Mantener custom pero mejorar código.

### FilaUsuario.tsx

Tiene filas expandibles con carga lazy de equipos. Mantener lógica pero usar componentes UI para elementos visuales.

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Crear este plan
2. ⏳ Empezar con FilaUsuario.tsx
3. ⏳ Continuar con orden recomendado
4. ⏳ Documentar cambios en cada fase
5. ⏳ Verificar con getDiagnostics después de cada archivo
6. ⏳ Crear documento de resumen al finalizar

---

**Creado:** 18 de marzo de 2026  
**Estimado de finalización:** 18 de marzo de 2026 (mismo día)  
**Estado:** 📋 LISTO PARA EMPEZAR

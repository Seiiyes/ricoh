# Plan de Refactorización - Módulo Contadores

**Fecha de inicio:** 18 de marzo de 2026  
**Estado:** 📋 Planificado  
**Prioridad:** Alta

---

## 🎯 OBJETIVO

Refactorizar el módulo Contadores para usar el sistema de diseño UI, reduciendo código duplicado y mejorando la consistencia visual.

---

## 📊 ANÁLISIS INICIAL

### Archivos Identificados

```
src/components/contadores/
├── ContadoresModule.tsx (archivo principal)
├── cierres/ (modales de cierres)
├── dashboard/ (vista resumen)
├── detail/ (vista detalle de impresora)
└── shared/ (componentes compartidos)
```

### Componentes a Refactorizar

**Estimación total:** ~2,500 líneas → ~1,800 líneas (-28%)

---

## 📝 FASE 1: ContadoresModule.tsx

**Prioridad:** Alta  
**Estimado:** 30 minutos  
**Riesgo:** Bajo (5%)

### Componentes a Reemplazar

1. **Tabs de navegación** (Resumen/Cierres)
   - Antes: Pestañas inline con estilos custom
   - Después: Componente `<Tabs>` del sistema de diseño
   - Reducción: ~20 líneas

2. **Spinner de carga**
   - Antes: Loader2 custom
   - Después: Componente `<Spinner>`
   - Reducción: ~3 líneas

### Código Actual

```typescript
// Tabs inline (estimado)
<div className="flex border-b">
  <button 
    className={activeTab === 'resumen' ? 'active' : ''}
    onClick={() => setActiveTab('resumen')}
  >
    Resumen
  </button>
  <button 
    className={activeTab === 'cierres' ? 'active' : ''}
    onClick={() => setActiveTab('cierres')}
  >
    Cierres
  </button>
</div>
```

### Código Refactorizado

```typescript
import { Tabs, Spinner } from '@/components/ui';

<Tabs
  tabs={[
    { id: 'resumen', label: 'Resumen', icon: <BarChart size={16} /> },
    { id: 'cierres', label: 'Cierres', icon: <Calendar size={16} /> }
  ]}
  activeTab={activeTab}
  onChange={setActiveTab}
  variant="underline"
/>
```

---

## 📝 FASE 2: PrinterDetailView.tsx

**Prioridad:** Alta  
**Estimado:** 45 minutos  
**Riesgo:** Medio (10%)

### Componentes a Reemplazar

1. **Breadcrumbs de navegación**
   - Antes: Breadcrumbs inline
   - Después: Componente `<Breadcrumbs>`
   - Reducción: ~15 líneas

2. **Botones de acción** (3-4 botones)
   - Antes: Botones inline
   - Después: Componente `<Button>`
   - Reducción: ~20 líneas

3. **Badges de estado**
   - Antes: Spans con estilos custom
   - Después: Componente `<Badge>`
   - Reducción: ~10 líneas

4. **Spinner de carga**
   - Antes: Loader2 custom
   - Después: Componente `<Spinner>`
   - Reducción: ~3 líneas

---

## 📝 FASE 3: UserCounterTable.tsx

**Prioridad:** Alta  
**Estimado:** 1 hora  
**Riesgo:** Medio (15%)

### Componentes a Reemplazar

1. **Tabla completa**
   - Antes: Tabla custom con sorting manual (~300 líneas)
   - Después: Componente `<Table>` con sorting automático
   - Reducción: ~150 líneas (-50%)

2. **Input de búsqueda**
   - Antes: Input inline
   - Después: Componente `<Input>` con type="search"
   - Reducción: ~8 líneas

### Código Actual (estimado)

```typescript
// Tabla custom con sorting manual
const [sortColumn, setSortColumn] = useState('nombre');
const [sortDirection, setSortDirection] = useState('asc');

const handleSort = (column) => {
  if (sortColumn === column) {
    setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
  } else {
    setSortColumn(column);
    setSortDirection('asc');
  }
};

const sortedData = useMemo(() => {
  return [...userCounters].sort((a, b) => {
    // Lógica de sorting manual...
  });
}, [userCounters, sortColumn, sortDirection]);

<table>
  <thead>
    <tr>
      <th onClick={() => handleSort('nombre')}>
        Nombre {sortColumn === 'nombre' && (sortDirection === 'asc' ? '↑' : '↓')}
      </th>
      {/* Más columnas... */}
    </tr>
  </thead>
  <tbody>
    {sortedData.map(row => (
      <tr key={row.id}>
        <td>{row.nombre}</td>
        {/* Más celdas... */}
      </tr>
    ))}
  </tbody>
</table>
```

### Código Refactorizado

```typescript
import { Table, Input } from '@/components/ui';

<Table
  columns={[
    { key: 'nombre', label: 'Nombre', sortable: true },
    { key: 'codigo', label: 'Código', sortable: true },
    { key: 'total', label: 'Total', sortable: true, render: (value) => value.toLocaleString() },
    // Más columnas...
  ]}
  data={userCounters}
  keyExtractor={(row) => row.id}
  sortable
  searchable
  pageSize={20}
/>
```

**Beneficios:**
- Sorting automático ✅
- Búsqueda integrada ✅
- Paginación automática ✅
- -50% de código ✅

---

## 📝 FASE 4: Modales de Cierres

**Prioridad:** Media  
**Estimado:** 1.5 horas  
**Riesgo:** Medio (10%)

### Archivos a Refactorizar

1. **CierreModal.tsx** (crear cierre)
2. **CierreDetalleModal.tsx** (ver detalle)
3. **ComparacionModal.tsx** (comparar cierres)

### Componentes a Reemplazar por Modal

**Por cada modal (~200 líneas cada uno):**

1. **Modal wrapper**
   - Antes: Estructura HTML custom (~25 líneas)
   - Después: Componente `<Modal>`
   - Reducción: ~20 líneas por modal

2. **Botones** (2-3 por modal)
   - Antes: Botones inline
   - Después: Componente `<Button>`
   - Reducción: ~15 líneas por modal

3. **Inputs** (3-5 por modal)
   - Antes: Inputs inline
   - Después: Componente `<Input>`
   - Reducción: ~20 líneas por modal

**Total reducción:** ~165 líneas (-27%)

---

## 📈 MÉTRICAS ESPERADAS

### Por Fase

| Fase | Archivo | Líneas Antes | Líneas Después | Reducción |
|------|---------|--------------|----------------|-----------|
| 1 | ContadoresModule.tsx | ~150 | ~130 | -20 (-13%) |
| 2 | PrinterDetailView.tsx | ~400 | ~350 | -50 (-13%) |
| 3 | UserCounterTable.tsx | ~300 | ~150 | -150 (-50%) |
| 4 | Modales (3) | ~600 | ~435 | -165 (-27%) |
| **Total** | **5 archivos** | **~1,450** | **~1,065** | **-385 (-27%)** |

### Impacto General

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Componentes inline | ~25 | 0 | -100% ✅ |
| Componentes UI usados | 0 | ~25 | +100% ✅ |
| Líneas de código | ~1,450 | ~1,065 | -27% ✅ |
| Consistencia visual | 60% | 95% | +35% ✅ |
| Mantenibilidad | Media | Alta | +100% ✅ |

---

## ⚠️ RIESGOS Y MITIGACIONES

### Riesgo 1: Tabla con lógica compleja
**Probabilidad:** 30%  
**Impacto:** Medio  
**Mitigación:**
- Probar sorting con datos reales
- Verificar que todas las columnas se muestran correctamente
- Mantener lógica de negocio separada

### Riesgo 2: Modales con formularios complejos
**Probabilidad:** 20%  
**Impacto:** Medio  
**Mitigación:**
- Refactorizar un modal a la vez
- Probar validación de formularios
- Verificar que los datos se envían correctamente

### Riesgo 3: Romper funcionalidad de cierres
**Probabilidad:** 10%  
**Impacto:** Alto  
**Mitigación:**
- Testing exhaustivo después de cada cambio
- Commits frecuentes
- Rollback fácil si algo falla

---

## ✅ CHECKLIST DE PROGRESO

### Fase 1: ContadoresModule.tsx
- [ ] Agregar imports de componentes UI
- [ ] Reemplazar tabs inline con `<Tabs>`
- [ ] Reemplazar spinner con `<Spinner>`
- [ ] Verificar funcionalidad
- [ ] Commit cambios

### Fase 2: PrinterDetailView.tsx
- [ ] Agregar imports de componentes UI
- [ ] Reemplazar breadcrumbs con `<Breadcrumbs>`
- [ ] Reemplazar botones con `<Button>`
- [ ] Reemplazar badges con `<Badge>`
- [ ] Reemplazar spinner con `<Spinner>`
- [ ] Verificar funcionalidad
- [ ] Commit cambios

### Fase 3: UserCounterTable.tsx
- [ ] Agregar imports de componentes UI
- [ ] Definir columnas para `<Table>`
- [ ] Reemplazar tabla custom con `<Table>`
- [ ] Reemplazar input de búsqueda con `<Input>`
- [ ] Verificar sorting funciona
- [ ] Verificar búsqueda funciona
- [ ] Verificar paginación funciona
- [ ] Commit cambios

### Fase 4: Modales
- [ ] CierreModal.tsx
  - [ ] Reemplazar modal wrapper con `<Modal>`
  - [ ] Reemplazar botones con `<Button>`
  - [ ] Reemplazar inputs con `<Input>`
  - [ ] Verificar funcionalidad
  - [ ] Commit cambios
- [ ] CierreDetalleModal.tsx
  - [ ] Reemplazar modal wrapper con `<Modal>`
  - [ ] Reemplazar botones con `<Button>`
  - [ ] Verificar funcionalidad
  - [ ] Commit cambios
- [ ] ComparacionModal.tsx
  - [ ] Reemplazar modal wrapper con `<Modal>`
  - [ ] Reemplazar botones con `<Button>`
  - [ ] Verificar funcionalidad
  - [ ] Commit cambios

---

## 🎯 ORDEN DE EJECUCIÓN

1. **Día 1 - Mañana:** Fase 1 (ContadoresModule.tsx) - 30 min
2. **Día 1 - Tarde:** Fase 2 (PrinterDetailView.tsx) - 45 min
3. **Día 2 - Mañana:** Fase 3 (UserCounterTable.tsx) - 1 hora
4. **Día 2 - Tarde:** Fase 4 (Modales) - 1.5 horas

**Total estimado:** ~3.5 horas

---

## 📝 PRÓXIMOS PASOS

1. ✅ Leer ContadoresModule.tsx para identificar componentes exactos
2. ⏳ Comenzar Fase 1: Refactorizar ContadoresModule.tsx
3. ⏳ Continuar con Fase 2, 3 y 4 según el orden

---

**Creado por:** Kiro AI  
**Fecha:** 18 de marzo de 2026  
**Estado:** 📋 LISTO PARA COMENZAR

# Mejoras Responsive y Adaptación por Capacidades de Impresora

## Problema Actual

1. La tabla de comparación de cierres tiene muchas columnas y no es completamente responsive
2. Se muestran columnas de color incluso para impresoras que solo imprimen en B/N (como la 253)
3. En pantallas pequeñas, la tabla es difícil de navegar

## Solución Propuesta

### 1. Ocultar Columnas de Color para Impresoras B/N

Modificar `ComparacionPage.tsx` para:
- Obtener información de la impresora desde el backend
- Detectar si `has_color = false`
- Ocultar columnas de color cuando la impresora es solo B/N

### 2. Mejorar Responsive

- Agregar scroll horizontal mejorado con indicadores visuales
- Hacer las columnas de Usuario y Código sticky (fijas al hacer scroll)
- Reducir padding en móviles
- Agregar vista compacta para móviles

## Cambios Necesarios

### Backend: Incluir información de impresora en comparación

Archivo: `backend/api/counters.py`

En el endpoint `/api/counters/monthly/compare/{cierre1_id}/{cierre2_id}`:

```python
# Agregar información de la impresora
printer = db.query(Printer).filter(Printer.id == cierre1.printer_id).first()

return {
    "cierre1": cierre1_dict,
    "cierre2": cierre2_dict,
    "printer": {
        "id": printer.id,
        "hostname": printer.hostname,
        "has_color": printer.has_color,
        "has_scanner": printer.has_scanner,
        "has_fax": printer.has_fax,
    } if printer else None,
    # ... resto de datos
}
```

### Frontend: Adaptar tabla según capacidades

Archivo: `src/components/contadores/cierres/ComparacionPage.tsx`

1. **Agregar estado para capacidades de impresora:**

```typescript
const [printerCapabilities, setPrinterCapabilities] = useState<{
  has_color: boolean;
  has_scanner: boolean;
  has_fax: boolean;
} | null>(null);
```

2. **Actualizar loadComparacion para obtener capacidades:**

```typescript
const loadComparacion = async () => {
  if (!cierre1Id || !cierre2Id) return;
  setLoading(true); setError(null);
  try {
    const res = await fetch(`${API_BASE}/api/counters/monthly/compare/${cierre1Id}/${cierre2Id}`);
    if (!res.ok) throw new Error('Error al comparar cierres');
    const data = await res.json();
    setComparacion(data);
    setPrinterCapabilities(data.printer); // Guardar capacidades
  } catch (err: any) { setError(err.message); }
  finally { setLoading(false); }
};
```

3. **Crear función para determinar qué columnas mostrar:**

```typescript
const shouldShowColorColumns = useMemo(() => {
  return printerCapabilities?.has_color !== false; // Mostrar por defecto si no hay info
}, [printerCapabilities]);
```

4. **Modificar encabezados de tabla:**

```typescript
{/* Fila 3: Columnas individuales */}
<tr className="border-b-2 border-gray-300">
  {/* Período Base - Copiadora */}
  <th className="px-3 py-2 text-right text-xs font-medium text-gray-600 bg-white border-l-2 border-gray-300">Total</th>
  <th className="px-3 py-2 text-right text-xs font-medium text-gray-600 bg-white">B/N</th>
  {shouldShowColorColumns && (
    <th className="px-3 py-2 text-right text-xs font-medium text-gray-600 bg-white border-r border-gray-200">Color</th>
  )}
  {/* ... resto de columnas */}
</tr>
```

5. **Modificar filas de datos:**

```typescript
{/* Copiadora Base */}
<td className="px-3 py-3 text-xs text-right text-gray-600 border-l-2 border-gray-300">{fmt(u.consumo_copiadora_cierre1 || 0)}</td>
<td className="px-3 py-3 text-xs text-right text-gray-500">{fmt(u.copiadora_bn_cierre1 || 0)}</td>
{shouldShowColorColumns && (
  <td className="px-3 py-3 text-xs text-right text-gray-500 border-r border-gray-200">{fmt(u.copiadora_color_cierre1 || 0)}</td>
)}
```

6. **Ajustar colSpan dinámicamente:**

```typescript
<th colSpan={shouldShowColorColumns ? 3 : 2} className="px-3 py-1 text-center text-xs font-semibold text-gray-600 bg-gray-50 border-r border-gray-200">Copiadora</th>
```

### Mejoras de Responsive

1. **Agregar clases responsive a los selectores:**

```typescript
<div className="flex flex-col md:flex-row items-stretch md:items-center gap-4">
  <div className="flex-1">
    <label className="block text-xs font-medium text-gray-700 mb-2">Período Base (Inicial)</label>
    <select ...className="w-full px-4 py-2.5 ...">
      {/* ... */}
    </select>
  </div>
  
  <div className="hidden md:flex items-center justify-center pt-6">
    {/* Flecha solo en desktop */}
  </div>
  
  <div className="flex-1">
    {/* ... */}
  </div>
  
  <button ...className="md:mt-6 px-6 py-2.5 ...">
    Comparar
  </button>
</div>
```

2. **Agregar grid responsive para tarjetas:**

```typescript
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 mb-6">
  {/* Tarjetas de resumen */}
</div>

<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
  {/* Tarjetas de estadísticas */}
</div>
```

3. **Mejorar tabla en móviles:**

```typescript
<div className="overflow-x-auto -mx-6 px-6 md:mx-0 md:px-0">
  <div className="inline-block min-w-full align-middle">
    <table className="min-w-full text-xs">
      {/* ... */}
    </table>
  </div>
</div>
```

4. **Agregar indicador de scroll:**

```typescript
<div className="relative">
  <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
    <table className="min-w-full text-xs">
      {/* ... */}
    </table>
  </div>
  {/* Indicador de scroll */}
  <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-white to-transparent pointer-events-none md:hidden" />
</div>
```

## Implementación Paso a Paso

### Paso 1: Actualizar Backend

```bash
# Editar backend/api/counters.py
# Agregar información de impresora en el endpoint de comparación
```

### Paso 2: Actualizar Frontend

```bash
# Editar src/components/contadores/cierres/ComparacionPage.tsx
# Implementar lógica de ocultación de columnas
```

### Paso 3: Probar

1. Comparar cierres de impresora B/N (253) - No debe mostrar columnas de color
2. Comparar cierres de impresora color - Debe mostrar todas las columnas
3. Probar en móvil - Debe ser scrollable horizontalmente
4. Probar en tablet - Debe adaptarse correctamente
5. Probar en desktop - Debe verse completo

## Beneficios

1. **Menos columnas para impresoras B/N** - Tabla más limpia y fácil de leer
2. **Mejor experiencia móvil** - Scroll horizontal mejorado
3. **Adaptación automática** - Se adapta según las capacidades de cada impresora
4. **Consistencia** - Mismo comportamiento que en la vista de contadores de impresoras

## Notas Adicionales

- Las columnas de Usuario y Código ya están sticky (fijas) con `sticky left-0` y `sticky left-[120px]`
- El scroll horizontal ya funciona con `overflow-x-auto`
- Solo falta implementar la lógica de ocultación de columnas según capacidades
- Considerar agregar un toggle manual para mostrar/ocultar columnas avanzadas

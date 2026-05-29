# Resumen de Mejoras - Cierres Responsive y Adaptación por Capacidades

## ✅ Cambios Completados en Backend

### 1. Servicio de Comparación (`backend/services/close_service.py`)
- ✅ Agregado obtención de información de impresora
- ✅ Incluye `has_color`, `has_scanner`, `has_fax` en la respuesta
- ✅ Retorna objeto `printer` con capacidades

### 2. Schema de Respuesta (`backend/api/counter_schemas.py`)
- ✅ Agregado campo `printer: Optional[Dict[str, Any]]` a `ComparacionCierresResponse`
- ✅ Agregados imports necesarios (`Dict`, `Any`)

## 📝 Cambios Pendientes en Frontend

### Archivo: `src/components/contadores/cierres/ComparacionPage.tsx`

#### 1. Agregar Estado para Capacidades

```typescript
// Línea ~30, después de los otros estados
const [printerCapabilities, setPrinterCapabilities] = useState<{
  has_color: boolean;
  has_scanner: boolean;
  has_fax: boolean;
} | null>(null);
```

#### 2. Actualizar loadComparacion

```typescript
// Línea ~45, en loadComparacion
const loadComparacion = async () => {
  if (!cierre1Id || !cierre2Id) return;
  setLoading(true); setError(null);
  try {
    const res = await fetch(`${API_BASE}/api/counters/monthly/compare/${cierre1Id}/${cierre2Id}`);
    if (!res.ok) throw new Error('Error al comparar cierres');
    const data = await res.json();
    setComparacion(data);
    setPrinterCapabilities(data.printer); // AGREGAR ESTA LÍNEA
  } catch (err: any) { setError(err.message); }
  finally { setLoading(false); }
};
```

#### 3. Crear useMemo para Determinar Columnas Visibles

```typescript
// Línea ~60, después de fmtDate
const shouldShowColorColumns = useMemo(() => {
  // Mostrar por defecto si no hay info (backward compatibility)
  return printerCapabilities?.has_color !== false;
}, [printerCapabilities]);

const shouldShowScannerColumns = useMemo(() => {
  return printerCapabilities?.has_scanner !== false;
}, [printerCapabilities]);

const shouldShowFaxColumns = useMemo(() => {
  return printerCapabilities?.has_fax !== false;
}, [printerCapabilities]);
```

#### 4. Ajustar colSpan Dinámicamente en Encabezados

```typescript
// Línea ~200, en la fila 2 de encabezados
<th colSpan={shouldShowColorColumns ? 3 : 2} className="px-3 py-1 text-center text-xs font-semibold text-gray-600 bg-gray-50 border-r border-gray-200">Copiadora</th>
<th colSpan={shouldShowColorColumns ? 3 : 2} className="px-3 py-1 text-center text-xs font-semibold text-gray-600 bg-gray-50 border-r border-gray-200">Impresora</th>
{shouldShowScannerColumns && (
  <th colSpan={shouldShowColorColumns ? 3 : 2} className="px-3 py-1 text-center text-xs font-semibold text-gray-600 bg-gray-50 border-r-2 border-gray-300">Escáner</th>
)}
```

#### 5. Ocultar Columnas de Color Condicionalmente

```typescript
// Línea ~220, en la fila 3 de encabezados (Período Base - Copiadora)
<th className="px-3 py-2 text-right text-xs font-medium text-gray-600 bg-white border-l-2 border-gray-300">Total</th>
<th className="px-3 py-2 text-right text-xs font-medium text-gray-600 bg-white">B/N</th>
{shouldShowColorColumns && (
  <th className="px-3 py-2 text-right text-xs font-medium text-gray-600 bg-white border-r border-gray-200">Color</th>
)}
```

Repetir para:
- Período Base - Impresora
- Período Base - Escáner
- Período Comparado - Copiadora
- Período Comparado - Impresora
- Período Comparado - Escáner
- Diferencias - Copiadora
- Diferencias - Impresora
- Diferencias - Escáner

#### 6. Ocultar Celdas de Color en Filas de Datos

```typescript
// Línea ~280, en el map de pageUsers
{/* Copiadora Base */}
<td className="px-3 py-3 text-xs text-right text-gray-600 border-l-2 border-gray-300">{fmt(u.consumo_copiadora_cierre1 || 0)}</td>
<td className="px-3 py-3 text-xs text-right text-gray-500">{fmt(u.copiadora_bn_cierre1 || 0)}</td>
{shouldShowColorColumns && (
  <td className="px-3 py-3 text-xs text-right text-gray-500 border-r border-gray-200">{fmt(u.copiadora_color_cierre1 || 0)}</td>
)}
```

Repetir para todas las secciones de datos.

#### 7. Ocultar Tarjetas de Resumen Condicionalmente

```typescript
// Línea ~180, en las tarjetas de resumen
{[
  { label: 'Total páginas', val: comparacion.diferencia_total, icon: '📄' },
  { label: 'Copiadora', val: comparacion.diferencia_copiadora, icon: '📋' },
  { label: 'Impresora', val: comparacion.diferencia_impresora, icon: '🖨️' },
  shouldShowScannerColumns && { label: 'Escáner', val: comparacion.diferencia_escaner, icon: '📷' },
  shouldShowFaxColumns && { label: 'Fax', val: comparacion.diferencia_fax, icon: '📠' },
].filter(Boolean).map(({ label, val, icon }) => (
  // ... resto del código
))}
```

## 🎨 Mejoras de Responsive Adicionales

### 1. Selectores de Período

```typescript
// Hacer responsive el layout de selectores
<div className="flex flex-col md:flex-row items-stretch md:items-center gap-4">
  <div className="flex-1">
    {/* Período Base */}
  </div>
  
  <div className="hidden md:flex items-center justify-center pt-6">
    {/* Flecha solo en desktop */}
  </div>
  
  <div className="flex-1">
    {/* Período Comparado */}
  </div>
  
  <button className="md:mt-6 ...">
    Comparar
  </button>
</div>
```

### 2. Grid de Tarjetas

```typescript
// Ya está implementado correctamente
<div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
  {/* Tarjetas de resumen */}
</div>

<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  {/* Tarjetas de estadísticas */}
</div>
```

### 3. Tabla con Scroll Mejorado

```typescript
// Agregar indicador de scroll en móviles
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

## 🧪 Pruebas Necesarias

### 1. Impresora Solo B/N (253)
- [ ] Comparar cierres de impresora 253
- [ ] Verificar que NO se muestran columnas de color
- [ ] Verificar que las tarjetas de resumen se ajustan
- [ ] Verificar que el colSpan es correcto

### 2. Impresora con Color
- [ ] Comparar cierres de impresora con color
- [ ] Verificar que SÍ se muestran columnas de color
- [ ] Verificar que todas las columnas están presentes

### 3. Responsive
- [ ] Probar en móvil (< 768px)
- [ ] Probar en tablet (768px - 1024px)
- [ ] Probar en desktop (> 1024px)
- [ ] Verificar scroll horizontal funciona
- [ ] Verificar columnas sticky funcionan

### 4. Sin Escáner/Fax
- [ ] Comparar cierres de impresora sin escáner
- [ ] Verificar que columnas de escáner se ocultan
- [ ] Comparar cierres de impresora sin fax
- [ ] Verificar que columnas de fax se ocultan

## 📋 Checklist de Implementación

- [x] Backend: Agregar información de impresora al servicio
- [x] Backend: Actualizar schema de respuesta
- [ ] Frontend: Agregar estado para capacidades
- [ ] Frontend: Actualizar loadComparacion
- [ ] Frontend: Crear useMemo para columnas visibles
- [ ] Frontend: Ajustar colSpan dinámicamente
- [ ] Frontend: Ocultar columnas de color condicionalmente
- [ ] Frontend: Ocultar celdas de color en datos
- [ ] Frontend: Ajustar tarjetas de resumen
- [ ] Frontend: Mejorar responsive de selectores
- [ ] Frontend: Agregar indicador de scroll
- [ ] Pruebas: Impresora B/N
- [ ] Pruebas: Impresora color
- [ ] Pruebas: Responsive móvil
- [ ] Pruebas: Responsive tablet
- [ ] Pruebas: Responsive desktop

## 🚀 Próximos Pasos

1. Reiniciar el backend para aplicar cambios:
   ```bash
   docker-compose restart backend
   ```

2. Implementar cambios en el frontend según la guía arriba

3. Probar con diferentes impresoras:
   - Impresora 253 (solo B/N)
   - Impresoras con color
   - Impresoras sin escáner/fax

4. Verificar responsive en diferentes tamaños de pantalla

## 💡 Notas Adicionales

- Las columnas de Usuario y Código ya están sticky (fijas)
- El scroll horizontal ya funciona
- Solo falta implementar la lógica de ocultación de columnas
- Considerar agregar un toggle manual para mostrar/ocultar columnas avanzadas en el futuro
- La implementación es backward compatible (muestra todo por defecto si no hay info de capacidades)

# Instrucciones para Corrección del Frontend - Cierres

## ✅ ESTADO ACTUAL
- Datos en BD: CORRECTOS
- Backend devuelve capacidades de impresora en `comparacion.printer`
- Ya agregué detección de capacidades en ComparacionPage.tsx

## 🎯 CAMBIOS NECESARIOS EN ComparacionPage.tsx

### 1. Ocultar Columnas de Color (si has_color = false)

Buscar todas las columnas que dicen "Color" y envolverlas en condicional:

```tsx
{printerCapabilities.has_color && (
  <th className="...">Color</th>
)}
```

Aplicar en:
- Encabezados de tabla (th)
- Celdas de datos (td)

### 2. Ocultar Columnas de Escáner (si has_scanner = false)

Buscar todas las secciones de "Escáner" y envolverlas:

```tsx
{printerCapabilities.has_scanner && (
  <>
    <th colSpan={3} className="...">Escáner</th>
  </>
)}
```

### 3. Ocultar Columnas de Fax (si has_fax = false)

Actualmente no se muestra Fax en la tabla, pero si se agrega:

```tsx
{printerCapabilities.has_fax && (
  <th className="...">Fax</th>
)}
```

### 4. Mejorar Responsive

#### A. Sticky Columns (Usuario y Código)
Ya están implementadas con `sticky left-0` y `sticky left-[120px]`

#### B. Scroll Horizontal
Envolver la tabla en:
```tsx
<div className="overflow-x-auto">
  <table className="min-w-full">
    ...
  </table>
</div>
```

#### C. Vista Móvil (< 768px)
Agregar vista de tarjetas para móvil:

```tsx
{/* Vista Desktop */}
<div className="hidden md:block overflow-x-auto">
  <table>...</table>
</div>

{/* Vista Móvil */}
<div className="md:hidden space-y-4">
  {pageUsers.map(u => (
    <div key={u.codigo_usuario} className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold">{u.nombre_usuario}</h3>
      <p className="text-sm text-gray-500">[{u.codigo_usuario}]</p>
      <div className="mt-3 space-y-2">
        <div className="flex justify-between">
          <span>Total:</span>
          <span className="font-semibold">{fmt(u.consumo_cierre2)}</span>
        </div>
        <div className="flex justify-between">
          <span>Diferencia:</span>
          <span className={diffColor(u.diferencia)}>{fmtDiff(u.diferencia)}</span>
        </div>
        {/* Más campos... */}
      </div>
    </div>
  ))}
</div>
```

### 5. Ajustar colSpan Dinámicamente

Cuando se ocultan columnas, ajustar el colSpan:

```tsx
<th colSpan={printerCapabilities.has_color ? 3 : 2} className="...">
  Copiadora
</th>
```

## 📝 EJEMPLO COMPLETO DE SECCIÓN

```tsx
{/* Copiadora Base */}
<td className="px-3 py-3 text-xs text-right text-gray-600 border-l-2 border-gray-300">
  {fmt(u.consumo_copiadora_cierre1 || 0)}
</td>
<td className="px-3 py-3 text-xs text-right text-gray-500">
  {fmt(u.copiadora_bn_cierre1 || 0)}
</td>
{printerCapabilities.has_color && (
  <td className="px-3 py-3 text-xs text-right text-gray-500 border-r border-gray-200">
    {fmt(u.copiadora_color_cierre1 || 0)}
  </td>
)}
```

## 🚀 ORDEN DE IMPLEMENTACIÓN

1. ✅ Agregar detección de capacidades (HECHO)
2. ⏳ Ocultar columnas de Color condicionalmente
3. ⏳ Ocultar columnas de Escáner condicionalmente
4. ⏳ Ajustar colSpan dinámicamente
5. ⏳ Agregar vista móvil con tarjetas
6. ⏳ Probar con las 5 impresoras

## 🧪 PRUEBAS

Probar con cada impresora:
- E174M210096: Solo B/N, tiene escáner → Ocultar columnas Color
- E174MA11130: Tiene color y escáner → Mostrar todo
- E176M460020: Solo B/N, NO escáner → Ocultar Color y Escáner
- G986XA16285: Solo B/N, tiene escáner → Ocultar Color
- W533L900719: Solo B/N, tiene escáner → Ocultar Color

## 📌 NOTAS IMPORTANTES

1. El backend YA devuelve las capacidades correctamente
2. Los datos en BD están correctos
3. Solo falta adaptar la visualización
4. Mantener la funcionalidad de ordenamiento y paginación
5. No modificar la lógica de cálculo de diferencias

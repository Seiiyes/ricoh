# Cambios en Comparación de Cierres

## Problemas Corregidos

### 1. Ordenamiento de Usuarios
**Problema**: Al ordenar por "Total" en orden ascendente, no aparecían los usuarios con consumo positivo.

**Causa**: El código estaba usando `consumo_cierre1` y `consumo_cierre2` (que no existen) en lugar de `total_paginas_cierre1` y `total_paginas_cierre2`.

**Solución**: Corregido en `src/components/contadores/cierres/ComparacionPage.tsx`:
```typescript
case 'total1': return mul * ((a.total_paginas_cierre1 || 0) - (b.total_paginas_cierre1 || 0));
case 'total2': return mul * ((a.total_paginas_cierre2 || 0) - (b.total_paginas_cierre2 || 0));
```

### 2. Información de la Impresora en Banner
**Problema**: No se mostraba la IP, ubicación y serial de la impresora.

**Causa**: El backend no estaba enviando estos campos en la respuesta de comparación.

**Solución**: Agregados los campos en `backend/services/close_service.py`:
```python
"printer": {
    "id": printer.id,
    "hostname": printer.hostname,
    "ip_address": printer.ip_address,
    "location": printer.location,
    "serial_number": printer.serial_number,
    "has_color": printer.has_color,
    "has_scanner": printer.has_scanner,
    "has_fax": printer.has_fax,
}
```

### 3. Tabla de Comparación Completa
**Cambio**: La tabla ahora muestra TODA la información de contadores desglosada:

**Estructura actual (23 columnas)**:
- Usuario (1)
- Código (1)
- **Período Base** (7): Total + Copiadora (B/N, Color) + Impresora (B/N, Color) + Escáner (B/N, Color)
- **Período Comparado** (7): Total + Copiadora (B/N, Color) + Impresora (B/N, Color) + Escáner (B/N, Color)
- **Diferencias** (7): Total + Copiadora (B/N, Color) + Impresora (B/N, Color) + Escáner (B/N, Color)

**Columnas eliminadas**: Fax (no se usa)

## Pendiente

### Adaptación según Capacidades de la Impresora
**Objetivo**: Si la impresora es solo B/N, ocultar las columnas de Color.

**Estado**: Preparado pero no implementado completamente.
- Ya se pasa el parámetro `hasColor` a la tabla
- Falta modificar la estructura de encabezados y celdas para adaptarse

**Implementación sugerida**:
- Si `hasColor = false`: Mostrar solo 1 columna por función (Total B/N)
- Si `hasColor = true`: Mostrar 2 columnas por función (B/N y Color)
- Esto reduciría de 23 a 11 columnas para impresoras solo B/N

## Archivos Modificados

1. `backend/services/close_service.py` - Agregados campos de impresora
2. `src/components/contadores/cierres/ComparacionPage.tsx` - Corregido ordenamiento
3. `src/components/contadores/cierres/TablaComparacionSimplificada.tsx` - Tabla completa con desglose
4. `backend/services/export_ricoh.py` - Exportación Excel adaptativa

## Notas

- El ordenamiento ahora funciona correctamente para todas las columnas
- La información de la impresora se muestra completa en el banner
- La tabla muestra el desglose completo de contadores por función y tipo
- La exportación Excel ya se adapta a las capacidades de la impresora

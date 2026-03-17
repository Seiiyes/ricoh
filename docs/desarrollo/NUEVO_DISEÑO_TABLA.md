# Nuevo Diseño de Tabla de Comparación

## Problema Actual
- Demasiadas columnas (32 columnas)
- Texto muy pequeño
- Difícil de leer
- Estructura confusa con 3 niveles de headers

## Solución Propuesta

### Estructura Simplificada
En lugar de mostrar TODOS los detalles en columnas separadas, agrupar la información:

**Columnas principales (10 total):**
1. Usuario (sticky)
2. Código (sticky)
3. Total Base
4. Desglose Base (una celda con 3 líneas: Copia, Impre, Scan)
5. Total Comparado
6. Desglose Comparado (una celda con 3 líneas)
7. Diferencia Total (destacada)
8. Dif. Copiadora
9. Dif. Impresora
10. Dif. Escáner

### Mejoras Visuales
1. **Headers de 2 niveles** en lugar de 3
2. **Colores diferenciados** por sección:
   - Azul para Período Base
   - Morado para Período Comparado
   - Verde para Diferencias
3. **Texto más grande**: text-sm en lugar de text-xs
4. **Más padding**: px-4 py-3 en lugar de px-3 py-2
5. **Iconos** para identificar funciones rápidamente
6. **Desglose vertical** en lugar de horizontal

### Ventajas
- Menos scroll horizontal
- Más legible
- Más espacio para cada dato
- Colores ayudan a identificar secciones
- Iconos mejoran la comprensión visual

## Implementación

Reemplazar toda la tabla actual con la nueva estructura simplificada.

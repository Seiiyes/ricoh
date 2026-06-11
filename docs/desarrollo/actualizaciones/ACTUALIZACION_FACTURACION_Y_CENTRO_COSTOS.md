# Actualización de Sistema de Facturación y Centro de Costos

**Fecha**: Junio de 2026

## 1. Resumen de Implementación
Se ha implementado el módulo de facturación consolidada y el manejo avanzado de Centros de Costos, permitiendo un desglose multinivel (Empresa > Centro de Costos > Usuario > Impresora) con funcionalidades de exportación y UI jerárquica desplegable tipo Excel.

## 2. Novedades y Mejoras en UI/UX
- **Desglose Consolidado Plegable**: Se implementó una tabla jerárquica interactiva que agrupa el consumo por capas organizacionales. El usuario puede expandir/contraer ramas (sin íconos intrusivos, utilizando indicadores sutiles) logrando un diseño muy similar a tablas dinámicas de Excel.
- **Gestión de Centros de Costos**: En los selectores (dropdowns) de usuarios y configuración de dispositivos, se añadió el campo "Centro de Costos". Permite seleccionar centros existentes o crear nuevos dinámicamente si no existen (creación en tiempo de ejecución).
- **Simetría y Diseño Premium**: Mantenimiento de la estética visual con la paleta de colores institucional, optimizando los espacios y la legibilidad de la jerarquía.

## 3. Impacto en Otros Módulos
- **Modelo de Base de Datos**: La tabla `usuarios` y `contadores_usuarios` se ha integrado fuertemente con la tabla `centros_costos`. La jerarquía permite ahora asociar de manera estricta el uso de la impresora a una persona física y su respectivo centro, impactando de forma directa el cálculo en el módulo de facturación.
- **API Endpoints**: Se crearon endpoints en `/api/facturacion/` y `/api/centros-costos/` para servir los datos jerárquicos a la vista de analítica, requiriendo validaciones de sesión y permisos (rol admin/superadmin).
- **Módulo de Exportación**: Adaptación de los reportes PDF, Excel y CSV para reflejar este agrupamiento, facilitando la entrega directa de facturas a los clientes con un desglose granular.

## 4. Normalización de Base de Datos
Se analizó la estructura de la tabla `centros_costos`. Los centros de costos ahora admiten sugerencias transversales pero mantienen una relación con la `empresa_id` principal para evitar fugas de información. Sin embargo, para la creación de un nuevo centro, el sistema automáticamente valida su existencia bajo la misma empresa antes de insertar registros duplicados, normalizando el input.

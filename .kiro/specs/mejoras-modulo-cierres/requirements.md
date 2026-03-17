# Requirements Document

## Introduction

Este documento especifica los requisitos para mejorar el módulo de cierres de contadores, basándose en un análisis exhaustivo del sistema actual. El objetivo es eliminar restricciones artificiales, clarificar la información mostrada, y proporcionar un desglose completo de usuarios para análisis de consumo.

### Contexto del Sistema Actual

**Arquitectura:**
- Backend 100% funcional con validaciones robustas
- Base de datos con snapshots inmutables (tablas: `cierres_mensuales`, `cierres_mensuales_usuarios`)
- API REST completa con 11 validaciones previas a creación de cierre
- Rendimiento excelente: consultas en <10ms
- Escalabilidad garantizada: solo 3,192 registros/año por impresora

**Cómo Funciona el Sistema de Cierres:**

1. **Generación de Cierre (CloseService.create_close):**
   - Captura snapshot de contadores totales de impresora en `fecha_fin`
   - Captura snapshot de contadores por usuario (si tiene contador por usuario o contador ecológico)
   - Calcula consumo del período: `consumo = total_actual - total_anterior`
   - Guarda datos inmutables en `cierres_mensuales_usuarios`
   - Valida integridad: suma de consumos de usuarios ≈ diferencia total de impresora
   - Genera hash SHA-256 para detectar modificaciones

2. **Campos Clave:**
   - `total_paginas`: Contador acumulado desde instalación (siempre crece)
   - `consumo_total`: Páginas impresas en el período específico (calculado)
   - `diferencia_total`: Consumo del período a nivel impresora

3. **Comparación de Cierres:**
   - Obtiene usuarios de ambos cierres desde `cierres_mensuales_usuarios`
   - Calcula diferencia: `consumo_cierre2 - consumo_cierre1`
   - Muestra cuánto cambió el consumo entre períodos

### Problemas Identificados

**Limitaciones actuales:**
1. ⚠️ **Límite artificial:** Comparación limitada a 100 usuarios (hay impresoras con 266 usuarios)
2. ⚠️ **Información confusa:** Etiquetas no distinguen entre "contador acumulado" y "consumo del período"
3. ⚠️ **Desglose incompleto:** No muestra `total_paginas` (contador acumulado) en comparaciones
4. ⚠️ **Falta de contexto:** No muestra tipo de cierre ni rango de fechas en comparaciones

**Impacto:**
- Solo se analiza 37.6% de usuarios (100 de 266)
- Usuario confundido sobre qué representan los números
- Análisis incompleto de consumo
- Suma de consumos no coincide con total de impresora

Estas mejoras permitirán un análisis completo y preciso del consumo, con información clara y sin restricciones artificiales.

## Glossary

- **Sistema_Cierres**: Módulo del sistema que gestiona los cierres de contadores y sus comparaciones
- **Cierre**: Snapshot inmutable de datos de consumo de contadores en un momento específico, almacenado en tabla `cierres_mensuales`
- **Usuario_Cierre**: Usuario que tiene datos registrados en un cierre específico, almacenado en tabla `cierres_mensuales_usuarios`
- **Comparacion**: Análisis de diferencias entre dos cierres usando endpoint `/api/counters/closes/{id1}/compare/{id2}`
- **Total_Paginas**: Contador acumulado desde la instalación del contador (valor absoluto que siempre crece)
- **Consumo_Total**: Consumo calculado para un período específico (diferencia entre lecturas: `total_actual - total_anterior`)
- **Diferencia_Total**: Consumo del período a nivel impresora (campo en `cierres_mensuales`)
- **Tipo_Periodo**: Clasificación del cierre (diario, semanal, mensual, personalizado)
- **Backend_API**: Servicio FastAPI que expone los endpoints de cierres (archivo: `backend/api/counters.py`)
- **Frontend_UI**: Interfaz React que consume la API y presenta los datos (componente: `ComparacionModal.tsx`)
- **Endpoint_Comparacion**: Ruta `/api/counters/closes/{id1}/compare/{id2}` en el backend
- **ComparacionModal**: Componente React que muestra la comparación de cierres
- **CloseService**: Servicio de backend que maneja la lógica de creación de cierres (archivo: `backend/services/close_service.py`)
- **Snapshot**: Captura inmutable de datos en un momento específico, almacenada en `cierres_mensuales_usuarios`
- **Hash_Verificacion**: SHA-256 calculado sobre datos del cierre para detectar modificaciones
- **Top_Usuarios**: Parámetro del endpoint de comparación que limita cantidad de usuarios retornados (actualmente máximo 100)

## Requirements

### Requirement 1: Mostrar Todos los Usuarios en Comparaciones

**User Story:** Como administrador del sistema, quiero ver todos los usuarios que tienen datos en un cierre sin restricciones de cantidad, para poder analizar completamente el consumo de toda la organización y garantizar que la suma de consumos coincida con el total de la impresora.

**Contexto:** Actualmente el endpoint `/api/counters/closes/{id1}/compare/{id2}` tiene un parámetro `top_usuarios` con máximo 100. La impresora 4 tiene 266 usuarios activos, lo que significa que solo se muestra el 37.6% de los usuarios en la comparación.

#### Acceptance Criteria

1. WHEN se solicita una comparación de cierres, THE Backend_API SHALL retornar datos de todos los Usuario_Cierre sin límite de cantidad
2. THE Backend_API SHALL eliminar el parámetro `top_usuarios` del Endpoint_Comparacion en `backend/api/counters.py` línea ~543
3. THE Backend_API SHALL eliminar la validación `le=100` que limita el máximo de usuarios
4. WHEN un Cierre contiene 266 Usuario_Cierre, THE Sistema_Cierres SHALL retornar los 266 usuarios en la comparación
5. THE Frontend_UI SHALL renderizar todos los Usuario_Cierre recibidos del backend sin paginación artificial
6. WHEN se suman los consumos de todos los usuarios, THE suma SHALL coincidir aproximadamente con la diferencia_total de la impresora (tolerancia: 10%)
7. THE Backend_API SHALL mantener el ordenamiento por diferencia de consumo (mayor a menor) para todos los usuarios

### Requirement 2: Clarificar Etiquetas de Campos en la UI

**User Story:** Como usuario del sistema, quiero que las etiquetas de los campos sean claras y descriptivas, para entender qué representa cada valor sin ambigüedad y distinguir entre contadores acumulados y consumos del período.

**Contexto:** Actualmente las columnas no indican claramente si muestran `total_paginas` (contador acumulado desde instalación) o `consumo_total` (páginas impresas en el período). Esto causa confusión: ¿1,000 es el total acumulado o el consumo del período?

#### Acceptance Criteria

1. WHEN se muestra Total_Paginas en Frontend_UI, THE ComparacionModal SHALL etiquetar el campo como "Contador Acumulado" o "Total desde Instalación"
2. WHEN se muestra Consumo_Total en Frontend_UI, THE ComparacionModal SHALL etiquetar el campo como "Consumo del Período" o "Páginas Impresas"
3. WHEN se muestra una diferencia entre cierres, THE ComparacionModal SHALL etiquetar el campo como "Variación de Consumo" o "Diferencia"
4. THE Frontend_UI SHALL incluir tooltips o ayuda contextual que explique:
   - "Contador Acumulado: Total de páginas desde que se instaló el contador (siempre crece)"
   - "Consumo del Período: Páginas impresas en este período específico (calculado)"
5. THE ComparacionModal SHALL usar terminología consistente en todas las vistas de comparación
6. THE Frontend_UI SHALL usar iconos distintivos para cada tipo de dato:
   - 📊 para contadores acumulados
   - 📄 para consumos del período
   - 📈 para diferencias/variaciones

### Requirement 3: Permitir Comparaciones Entre Cualquier Tipo de Cierre

**User Story:** Como analista de datos, quiero comparar cualquier cierre con cualquier otro independientemente de su tipo de período, para tener flexibilidad total en el análisis de consumo y poder comparar cierres diarios con mensuales si es necesario.

**Contexto:** El backend ya permite comparar cualquier cierre con cualquier otro (solo valida que sean de la misma impresora). Esta funcionalidad está implementada en `backend/api/counters.py` línea ~543. El frontend debe aprovechar esta flexibilidad.

#### Acceptance Criteria

1. WHEN se solicita una comparación entre dos Cierre, THE Backend_API SHALL procesar la comparación sin validar Tipo_Periodo (ya implementado)
2. THE Backend_API SHALL mantener la validación existente que requiere que ambos cierres sean de la misma impresora
3. WHEN se compara un cierre diario con un cierre mensual, THE Sistema_Cierres SHALL calcular y mostrar las diferencias correctamente
4. THE Frontend_UI SHALL permitir seleccionar cualquier combinación de cierres para comparación sin restricciones de tipo
5. WHEN los cierres comparados tienen diferentes Tipo_Periodo, THE ComparacionModal SHALL mostrar claramente el tipo de cada cierre en la cabecera
6. THE ComparacionModal SHALL mostrar el rango de fechas de cada cierre (fecha_inicio a fecha_fin)
7. THE ComparacionModal SHALL mostrar los días entre cierres para dar contexto a la comparación

### Requirement 4: Mostrar Desglose Completo de Usuarios en Comparación

**User Story:** Como usuario del sistema, quiero ver el desglose completo de cada usuario mostrando sus contadores totales capturados en cada cierre y el consumo calculado entre cierres, para entender exactamente cuántas páginas está gastando cada usuario de cierre en cierre y poder verificar la consistencia de los datos.

**Contexto:** Actualmente la comparación solo muestra `consumo_total` de cada período. Falta mostrar `total_paginas` (contador acumulado) que permite verificar que los cálculos son correctos. Por ejemplo: Si Juan tiene 1,000 páginas acumuladas en Cierre 1 y 1,050 en Cierre 2, el consumo debe ser 50 páginas.

#### Acceptance Criteria

1. WHEN se muestra un Usuario_Cierre en la comparación, THE ComparacionModal SHALL mostrar las siguientes columnas:
   - Nombre y código del usuario
   - **Total acumulado en Cierre 1** (campo `total_paginas` del snapshot del cierre 1)
   - **Total acumulado en Cierre 2** (campo `total_paginas` del snapshot del cierre 2)
   - **Consumo calculado** (Total Cierre 2 - Total Cierre 1 = páginas gastadas entre los dos cierres)
   - Porcentaje de cambio en el consumo

2. THE Backend_API SHALL retornar para cada usuario en la comparación:
   - `total_paginas` del Usuario_Cierre en Cierre 1 (contador capturado en el snapshot)
   - `total_paginas` del Usuario_Cierre en Cierre 2 (contador capturado en el snapshot)
   - `diferencia` calculada (total_paginas_cierre2 - total_paginas_cierre1)

3. THE ComparacionModal SHALL etiquetar claramente cada columna:
   - "Contador en [Fecha Cierre 1]" o "Total Acumulado Cierre 1"
   - "Contador en [Fecha Cierre 2]" o "Total Acumulado Cierre 2"
   - "Páginas Consumidas" o "Consumo entre Cierres"

4. WHEN un Usuario_Cierre aparece solo en uno de los cierres, THE ComparacionModal SHALL:
   - Mostrar el total_paginas del cierre donde aparece
   - Mostrar 0 o "N/A" en el cierre donde no aparece
   - Calcular el consumo como la diferencia disponible
   - Marcar visualmente que es un usuario nuevo o eliminado

5. THE Frontend_UI SHALL ordenar los resultados por consumo absoluto (mayor a menor) por defecto, mostrando primero los usuarios que más páginas gastaron entre los dos cierres

6. THE ComparacionModal SHALL usar indicadores visuales (colores, iconos) para resaltar:
   - 🟢 Verde para consumo positivo alto (usuario imprimió muchas páginas)
   - 🟡 Amarillo para consumo positivo bajo
   - ⚪ Gris para consumo cero (usuario no imprimió)
   - 🔵 Azul para casos especiales (usuario nuevo o eliminado)

7. THE ComparacionModal SHALL mostrar al final de la tabla:
   - Suma total de páginas consumidas por todos los usuarios
   - Diferencia total de la impresora (del campo `diferencia_total` del cierre)
   - Porcentaje de coincidencia entre ambos valores
   - Advertencia si la diferencia es mayor al 10%

8. THE ComparacionModal SHALL permitir alternar entre vista simple (solo consumos) y vista detallada (con totales acumulados)

### Requirement 5: Simplificar la Presentación de Datos de Comparación

**User Story:** Como usuario del sistema, quiero que la información de comparación sea clara y directa, para entender rápidamente los resultados sin confusión.

#### Acceptance Criteria

1. THE ComparacionModal SHALL mostrar la fecha y tipo de cada Cierre en la cabecera de la comparación
2. THE Frontend_UI SHALL agrupar la información en secciones claramente identificadas:
   - Resumen de diferencias totales (impresora)
   - Desglose completo por usuario
   - Estadísticas agregadas
3. WHEN un Usuario_Cierre aparece en un cierre pero no en el otro, THE ComparacionModal SHALL indicar claramente esta situación mostrando valores en 0 o "N/A"
4. THE ComparacionModal SHALL incluir tooltips explicativos en los encabezados de columnas
5. THE Frontend_UI SHALL permitir búsqueda y filtrado de usuarios en la tabla de comparación

### Requirement 5: Simplificar la Presentación de Datos de Comparación

**User Story:** Como usuario del sistema, quiero que la información de comparación sea clara y directa, para entender rápidamente los resultados sin confusión.

#### Acceptance Criteria

1. THE ComparacionModal SHALL mostrar la fecha y tipo de cada Cierre en la cabecera de la comparación
2. THE Frontend_UI SHALL agrupar la información en secciones claramente identificadas:
   - Resumen de diferencias totales (impresora)
   - Desglose completo por usuario
   - Estadísticas agregadas
3. WHEN un Usuario_Cierre aparece en un cierre pero no en el otro, THE ComparacionModal SHALL indicar claramente esta situación mostrando valores en 0 o "N/A"
4. THE ComparacionModal SHALL incluir tooltips explicativos en los encabezados de columnas
5. THE Frontend_UI SHALL permitir búsqueda y filtrado de usuarios en la tabla de comparación

### Requirement 6: Mantener Compatibilidad con Sistema Existente

**User Story:** Como desarrollador del sistema, quiero que las mejoras no rompan funcionalidad existente, para asegurar una transición suave sin regresiones.

#### Acceptance Criteria

1. THE Backend_API SHALL mantener la estructura de respuesta JSON existente del Endpoint_Comparacion
2. WHEN se realizan cambios en el backend, THE Sistema_Cierres SHALL pasar todas las pruebas existentes en `backend/test_sistema_unificado.py`
3. THE Frontend_UI SHALL mantener compatibilidad con otros componentes de cierres (CierreDetalleModal, CierreModal, ListaCierres)
4. THE Backend_API SHALL continuar usando Consumo_Total (no Total_Paginas) para cálculos de diferencias
5. WHEN se despliegan los cambios, THE Sistema_Cierres SHALL funcionar con datos de cierres existentes sin requerir migraciones

### Requirement 6: Mantener Compatibilidad con Sistema Existente

**User Story:** Como desarrollador del sistema, quiero que las mejoras no rompan funcionalidad existente, para asegurar una transición suave sin regresiones.

#### Acceptance Criteria

1. THE Backend_API SHALL mantener la estructura de respuesta JSON existente del Endpoint_Comparacion
2. WHEN se realizan cambios en el backend, THE Sistema_Cierres SHALL pasar todas las pruebas existentes en `backend/test_sistema_unificado.py`
3. THE Frontend_UI SHALL mantener compatibilidad con otros componentes de cierres (CierreDetalleModal, CierreModal, ListaCierres)
4. THE Backend_API SHALL continuar usando Consumo_Total (no Total_Paginas) para cálculos de diferencias
5. WHEN se despliegan los cambios, THE Sistema_Cierres SHALL funcionar con datos de cierres existentes sin requerir migraciones

### Requirement 7: Optimizar Rendimiento con Grandes Volúmenes

**User Story:** Como administrador del sistema, quiero que las comparaciones sean eficientes incluso con miles de usuarios, para mantener tiempos de respuesta aceptables.

#### Acceptance Criteria

1. WHEN una comparación incluye más de 1000 Usuario_Cierre, THE Backend_API SHALL responder en menos de 5 segundos
2. THE Backend_API SHALL usar índices de base de datos apropiados para consultas de comparación
3. WHEN el Frontend_UI recibe más de 500 Usuario_Cierre, THE ComparacionModal SHALL implementar virtualización o paginación en el cliente
4. THE Backend_API SHALL usar consultas SQL optimizadas con JOINs eficientes
5. WHEN se detecta una consulta lenta, THE Sistema_Cierres SHALL registrar métricas de rendimiento en los logs

# Requirements Document

## Introduction

Este documento define los requisitos para implementar un sistema de detección automática de capacidades por impresora en el módulo de contadores. El sistema resolverá el problema actual donde el frontend muestra todas las columnas de contadores sin importar las capacidades reales de cada impresora, generando confusión al mostrar columnas de "Color" con valores en 0 para impresoras blanco y negro.

El sistema detectará automáticamente las capacidades de cada impresora (formato de contadores, soporte de color, etc.), las almacenará en la base de datos y adaptará la interfaz para mostrar solo las columnas relevantes según las capacidades detectadas.

## Glossary

- **Parser**: Módulo backend que analiza el HTML de contadores de las impresoras Ricoh
- **Printer**: Modelo de base de datos que representa una impresora física
- **Counter_Format**: Estructura de datos de contadores que puede ser "estandar" (18 columnas), "simplificado" (13 columnas) o "ecologico"
- **Capabilities**: Conjunto de características técnicas de una impresora (soporte de color, formato de contadores, campos disponibles)
- **API**: Interfaz de programación de aplicaciones que expone datos del backend al frontend
- **Frontend**: Aplicación React que muestra la interfaz de usuario
- **Column_Visibility**: Configuración que determina qué columnas mostrar en las tablas del frontend

## Requirements

### Requirement 1: Detección Automática de Capacidades

**User Story:** Como administrador del sistema, quiero que el sistema detecte automáticamente las capacidades de cada impresora al leer sus contadores, para que no tenga que configurar manualmente cada modelo.

#### Acceptance Criteria

1. WHEN THE Parser procesa contadores de una impresora, THE Parser SHALL detectar el formato de contadores basándose en el número de columnas HTML
2. WHEN THE Parser detecta 13 columnas en el HTML, THE Parser SHALL identificar el formato como "simplificado"
3. WHEN THE Parser detecta 18 o más columnas con class='listData', THE Parser SHALL identificar el formato como "estandar"
4. WHEN THE Parser detecta formato ecológico, THE Parser SHALL identificar el formato como "ecologico"
5. WHEN THE Parser detecta valores mayores a 0 en columnas de color, THE Parser SHALL marcar la impresora como compatible con color
6. WHEN THE Parser detecta valores mayores a 0 en columnas de hojas_2_caras o paginas_combinadas, THE Parser SHALL marcar estos campos como disponibles
7. THE Parser SHALL retornar un objeto Capabilities con todos los campos detectados

### Requirement 2: Almacenamiento de Capacidades

**User Story:** Como desarrollador, quiero que las capacidades detectadas se almacenen en la base de datos, para que persistan entre lecturas de contadores y puedan consultarse posteriormente.

#### Acceptance Criteria

1. WHEN THE Parser detecta capacidades de una impresora, THE System SHALL actualizar el campo formato_contadores en el modelo Printer
2. WHEN THE Parser detecta soporte de color, THE System SHALL actualizar el campo has_color en el modelo Printer
3. THE System SHALL crear un nuevo campo capabilities_json en el modelo Printer para almacenar capacidades detalladas
4. THE capabilities_json field SHALL almacenar un objeto JSON con los campos disponibles (has_hojas_2_caras, has_paginas_combinadas, has_mono_color, has_dos_colores)
5. WHEN se actualiza una impresora existente, THE System SHALL preservar capacidades previamente detectadas y solo agregar nuevas
6. THE System SHALL registrar la fecha de última detección de capacidades en el campo updated_at

### Requirement 3: Exposición de Capacidades en la API

**User Story:** Como desarrollador frontend, quiero que la API incluya las capacidades de cada impresora en sus respuestas, para poder adaptar la interfaz según las características de cada equipo.

#### Acceptance Criteria

1. WHEN THE API retorna información de una impresora, THE API SHALL incluir el campo formato_contadores
2. WHEN THE API retorna información de una impresora, THE API SHALL incluir el campo has_color
3. WHEN THE API retorna información de una impresora, THE API SHALL incluir el objeto capabilities con todos los campos disponibles
4. WHEN THE API retorna contadores de usuario, THE API SHALL incluir las capacidades de la impresora asociada
5. WHEN THE API retorna cierres mensuales, THE API SHALL incluir las capacidades de la impresora asociada
6. THE API SHALL mantener compatibilidad con clientes existentes incluyendo todos los campos de contadores

### Requirement 4: Adaptación del Frontend según Capacidades

**User Story:** Como usuario final, quiero ver solo las columnas relevantes para cada impresora en las tablas de contadores, para que la interfaz sea más clara y no muestre información innecesaria.

#### Acceptance Criteria

1. WHEN THE Frontend recibe capacidades de una impresora, THE Frontend SHALL ocultar columnas de color si has_color es false
2. WHEN THE Frontend recibe capacidades de una impresora, THE Frontend SHALL ocultar columnas de hojas_2_caras si capabilities.has_hojas_2_caras es false
3. WHEN THE Frontend recibe capacidades de una impresora, THE Frontend SHALL ocultar columnas de paginas_combinadas si capabilities.has_paginas_combinadas es false
4. WHEN THE Frontend recibe capacidades de una impresora, THE Frontend SHALL ocultar columnas de mono_color y dos_colores si capabilities.has_mono_color y capabilities.has_dos_colores son false
5. THE Frontend SHALL aplicar el filtrado de columnas en UserCounterTable
6. THE Frontend SHALL aplicar el filtrado de columnas en CierreDetalleModal
7. THE Frontend SHALL aplicar el filtrado de columnas en ComparacionModal
8. WHEN todas las columnas de un grupo están ocultas, THE Frontend SHALL ocultar el encabezado del grupo completo

### Requirement 5: Migración de Datos Existentes

**User Story:** Como administrador del sistema, quiero que las impresoras existentes en la base de datos se actualicen con sus capacidades correctas, para que el sistema funcione correctamente desde el primer momento.

#### Acceptance Criteria

1. THE System SHALL proporcionar un script de migración para actualizar impresoras existentes
2. WHEN el script de migración se ejecuta, THE Script SHALL actualizar formato_contadores según la configuración conocida de cada IP
3. THE Script SHALL configurar 192.168.91.250 con formato "estandar" y has_color false
4. THE Script SHALL configurar 192.168.91.251 con formato "estandar" y has_color true
5. THE Script SHALL configurar 192.168.91.252 con formato "simplificado" y has_color false
6. THE Script SHALL configurar 192.168.91.253 con formato "ecologico" y has_color false
7. THE Script SHALL configurar 192.168.110.250 con formato "estandar" y has_color false
8. THE Script SHALL registrar en logs cada impresora actualizada

### Requirement 6: Validación y Consistencia de Datos

**User Story:** Como desarrollador, quiero que el sistema valide la consistencia entre las capacidades detectadas y los datos de contadores, para detectar posibles errores de configuración o cambios en el hardware.

#### Acceptance Criteria

1. WHEN THE Parser detecta valores de color mayores a 0 pero has_color es false, THE System SHALL registrar una advertencia en logs
2. WHEN THE Parser detecta un formato diferente al almacenado, THE System SHALL actualizar el formato y registrar el cambio en logs
3. WHEN THE API retorna contadores, THE API SHALL validar que los campos no nulos correspondan con las capacidades declaradas
4. IF THE System detecta inconsistencias en 3 lecturas consecutivas, THEN THE System SHALL enviar una notificación al administrador
5. THE System SHALL mantener un contador de inconsistencias detectadas por impresora

### Requirement 7: Configuración Manual de Capacidades

**User Story:** Como administrador del sistema, quiero poder configurar manualmente las capacidades de una impresora, para casos donde la detección automática no funcione correctamente o para impresoras nuevas.

#### Acceptance Criteria

1. THE API SHALL proporcionar un endpoint PUT /api/printers/{id}/capabilities para actualizar capacidades
2. WHEN un administrador actualiza capacidades manualmente, THE System SHALL validar que el formato sea uno de los valores permitidos
3. WHEN un administrador actualiza capacidades manualmente, THE System SHALL registrar el cambio en logs con el usuario que lo realizó
4. THE System SHALL permitir sobrescribir capacidades detectadas automáticamente
5. WHEN se actualiza manualmente, THE System SHALL marcar la impresora con un flag manual_override true
6. WHILE manual_override es true, THE System SHALL no actualizar automáticamente las capacidades

### Requirement 8: Documentación de Formatos de Contadores

**User Story:** Como desarrollador, quiero tener documentación clara de cada formato de contadores soportado, para entender las diferencias y poder mantener el código correctamente.

#### Acceptance Criteria

1. THE System SHALL incluir documentación en código que describa el formato "estandar"
2. THE System SHALL incluir documentación en código que describa el formato "simplificado"
3. THE System SHALL incluir documentación en código que describa el formato "ecologico"
4. THE Documentation SHALL especificar qué columnas están disponibles en cada formato
5. THE Documentation SHALL incluir ejemplos de HTML para cada formato
6. THE Documentation SHALL explicar cómo el Parser detecta cada formato

### Requirement 9: Retrocompatibilidad

**User Story:** Como desarrollador, quiero que el sistema mantenga compatibilidad con código existente, para que la implementación no rompa funcionalidades actuales.

#### Acceptance Criteria

1. WHEN THE API retorna contadores sin capacidades detectadas, THE API SHALL incluir valores por defecto seguros
2. THE API SHALL continuar retornando todos los campos de contadores incluso si están en 0
3. WHEN THE Frontend no recibe información de capacidades, THE Frontend SHALL mostrar todas las columnas como comportamiento por defecto
4. THE System SHALL mantener la estructura actual de la base de datos agregando solo nuevos campos opcionales
5. THE Parser SHALL continuar funcionando con impresoras que no tengan capacidades configuradas

### Requirement 10: Testing de Capacidades

**User Story:** Como desarrollador, quiero tener tests automatizados para la detección de capacidades, para asegurar que el sistema funciona correctamente con todos los formatos de impresoras.

#### Acceptance Criteria

1. THE System SHALL incluir tests unitarios para la detección de formato "estandar"
2. THE System SHALL incluir tests unitarios para la detección de formato "simplificado"
3. THE System SHALL incluir tests unitarios para la detección de formato "ecologico"
4. THE System SHALL incluir tests de integración que validen el flujo completo desde Parser hasta API
5. THE System SHALL incluir tests que validen la actualización correcta de la base de datos
6. FOR ALL formatos conocidos, parsear HTML de ejemplo y luego serializar las capacidades SHALL producir el mismo objeto de capacidades (round-trip property)

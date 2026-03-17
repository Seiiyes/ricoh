# Plan de Implementación: Sistema de Capacidades de Impresora

## Overview

Este plan implementa el sistema de detección automática de capacidades por impresora en 4 fases incrementales. Cada fase es desplegable independientemente y agrega valor al sistema sin romper funcionalidad existente.

El sistema detectará automáticamente las capacidades de cada impresora (formato de contadores, soporte de color, campos especiales), las almacenará en la base de datos y adaptará la interfaz para mostrar solo las columnas relevantes.

## Fase 1: Backend - Detección de Capacidades

- [x] 1. Crear estructura de datos de capacidades
  - [x] 1.1 Implementar modelo Pydantic Capabilities en backend/models/capabilities.py
    - Incluir campos: formato_contadores, has_color, has_hojas_2_caras, has_paginas_combinadas, has_mono_color, has_dos_colores, detected_at, manual_override
    - Implementar métodos to_json(), from_json() y merge()
    - _Requirements: 1.7, 2.3, 2.4_
  
  - [ ]* 1.2 Escribir property test para serialización JSON round-trip
    - **Property 6: JSON Serialization Round-Trip**
    - **Valida: Requirements 2.4, 10.6**
  
  - [ ]* 1.3 Escribir property test para merge de capacidades
    - **Property 7: Capabilities Merge Preservation**
    - **Valida: Requirements 2.5**
  
  - [ ]* 1.4 Escribir unit tests para casos específicos de Capabilities
    - Test de creación con valores por defecto
    - Test de merge con diferentes combinaciones
    - _Requirements: 2.3, 2.4, 2.5_

- [x] 2. Implementar detector de formato de contadores
  - [x] 2.1 Crear clase FormatDetector en backend/services/capabilities_detector.py
    - Implementar método detect_format(html_content: str) -> str
    - Detectar formato "simplificado" (13 columnas)
    - Detectar formato "estandar" (18+ columnas con class='listData')
    - Detectar formato "ecologico" (por URL o estructura)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ]* 2.2 Escribir unit tests para detección de cada formato
    - Test con HTML de formato simplificado (252)
    - Test con HTML de formato estándar (250, 251)
    - Test con HTML de formato ecológico (253)
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ]* 2.3 Escribir property test para consistencia de detección de formato
    - **Property 1: Format Detection Consistency**
    - **Valida: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 3. Implementar detector de soporte de color
  - [x] 3.1 Implementar método detect_color_support(counters_data: dict) -> bool
    - Analizar valores en campos copiadora_color, impresora_color, etc.
    - Retornar True si algún valor > 0
    - _Requirements: 1.5_
  
  - [ ]* 3.2 Escribir property test para detección de color
    - **Property 2: Color Support Detection**
    - **Valida: Requirements 1.5**
  
  - [ ]* 3.3 Escribir unit tests para casos edge de detección de color
    - Test con todos los valores en 0
    - Test con valores negativos (edge case)
    - Test con valores muy grandes
    - _Requirements: 1.5_

- [x] 4. Implementar detector de campos especiales
  - [x] 4.1 Implementar método detect_special_fields(counters_data: dict) -> dict
    - Detectar has_hojas_2_caras
    - Detectar has_paginas_combinadas
    - Detectar has_mono_color
    - Detectar has_dos_colores
    - _Requirements: 1.6_
  
  - [ ]* 4.2 Escribir property test para detección de campos especiales
    - **Property 3: Special Fields Detection**
    - **Valida: Requirements 1.6**
  
  - [ ]* 4.3 Escribir unit tests para campos especiales
    - Test con diferentes combinaciones de campos
    - _Requirements: 1.6_

- [x] 5. Integrar detector completo de capacidades
  - [x] 5.1 Implementar método detect_capabilities(html_content, counters_data) -> Capabilities
    - Integrar detección de formato, color y campos especiales
    - Establecer timestamp detected_at
    - Retornar objeto Capabilities completo
    - _Requirements: 1.7_
  
  - [ ]* 5.2 Escribir property test para completitud de estructura
    - **Property 4: Capabilities Structure Completeness**
    - **Valida: Requirements 1.7**
  
  - [ ]* 5.3 Escribir unit tests de integración del detector
    - Test con HTML real de cada impresora conocida
    - _Requirements: 1.7, 10.4_

- [x] 6. Checkpoint - Validar detección de capacidades
  - Ejecutar todos los tests del detector
  - Verificar que los tests de property pasen con 100+ iteraciones
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas

## Fase 2: Base de Datos y Persistencia

- [x] 7. Crear migración de base de datos
  - [x] 7.1 Crear migración Alembic para agregar campo capabilities_json
    - Agregar columna capabilities_json JSONB a tabla printers
    - Crear índice GIN para búsquedas en JSON
    - Incluir upgrade() y downgrade()
    - _Requirements: 2.3_
  
  - [x] 7.2 Ejecutar migración en base de datos de desarrollo
    - Aplicar migración con alembic upgrade head
    - Verificar que la columna se creó correctamente
    - _Requirements: 2.3_

- [x] 8. Extender modelo Printer con capacidades
  - [x] 8.1 Agregar property capabilities al modelo Printer
    - Implementar deserialización desde capabilities_json
    - Implementar método update_capabilities(new_caps, manual)
    - Incluir lógica de merge y respeto de manual_override
    - _Requirements: 2.1, 2.2, 2.5, 7.5, 7.6_
  
  - [ ]* 8.2 Escribir property test para persistencia en DB
    - **Property 5: Database Persistence**
    - **Valida: Requirements 2.1, 2.2**
  
  - [ ]* 8.3 Escribir property test para actualización de timestamp
    - **Property 8: Timestamp Recording**
    - **Valida: Requirements 2.6**
  
  - [ ]* 8.4 Escribir unit tests para update_capabilities
    - Test de actualización automática
    - Test de actualización manual con override
    - Test de respeto de manual_override
    - _Requirements: 2.5, 7.5, 7.6_

- [-] 9. Integrar detección en CounterService
  - [x] 9.1 Modificar método read_user_counters para detectar capacidades
    - Llamar a capabilities_detector.detect_capabilities()
    - Actualizar printer con capacidades detectadas
    - Commit a base de datos
    - _Requirements: 1.7, 2.1, 2.2, 2.6_
  
  - [ ] 9.2 Implementar validación de consistencia
    - Crear método _validate_consistency()
    - Detectar valores de color > 0 con has_color=False
    - Detectar cambios de formato
    - Registrar advertencias en logs
    - _Requirements: 6.1, 6.2_
  
  - [ ] 9.3 Implementar contador de inconsistencias
    - Agregar campo inconsistency_count a modelo Printer (o usar tabla separada)
    - Incrementar contador al detectar inconsistencias
    - _Requirements: 6.5_
  
  - [ ]* 9.4 Escribir property test para validación de contadores
    - **Property 19: Counter Validation**
    - **Valida: Requirements 6.3**
  
  - [ ]* 9.5 Escribir unit tests de integración completa
    - Test del flujo completo: HTML → detección → DB → validación
    - _Requirements: 10.4, 10.5_

- [x] 10. Crear script de migración de datos existentes
  - [x] 10.1 Implementar script migrate_printer_capabilities.py
    - Definir diccionario KNOWN_PRINTERS con configuración de IPs conocidas
    - Implementar función migrate_printer_capabilities()
    - Incluir logging de cada impresora actualizada
    - Incluir manejo de errores y rollback
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [ ]* 10.2 Escribir property test para actualizaciones del script
    - **Property 15: Migration Script Updates**
    - **Valida: Requirements 5.2**
  
  - [ ]* 10.3 Escribir property test para logging de migración
    - **Property 16: Migration Logging**
    - **Valida: Requirements 5.8**
  
  - [x] 10.4 Ejecutar script de migración en desarrollo
    - Ejecutar script y verificar logs
    - Validar que las 5 impresoras conocidas se actualizaron
    - _Requirements: 5.1_

- [x] 11. Checkpoint - Validar persistencia y migración
  - Verificar que capabilities_json se guarda correctamente
  - Confirmar que el script de migración actualizó todas las impresoras
  - Ejecutar tests de integración
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas

## Fase 3: API - Exposición de Capacidades

- [x] 12. Extender schemas de API con capacidades
  - [x] 12.1 Crear schema CapabilitiesResponse en backend/schemas/printer.py
    - Incluir todos los campos de capacidades
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 12.2 Extender PrinterResponse para incluir capabilities
    - Agregar campo capabilities: Optional[CapabilitiesResponse]
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 12.3 Crear schema CapabilitiesUpdate para actualizaciones manuales
    - Incluir validación de formato_contadores
    - _Requirements: 7.1, 7.2_

- [x] 13. Implementar endpoints de capacidades
  - [x] 13.1 Crear endpoint GET /api/printers/{printer_id}/capabilities
    - Retornar capacidades de una impresora
    - Retornar valores por defecto seguros si no hay capacidades
    - _Requirements: 3.1, 3.2, 3.3, 9.1_
  
  - [x] 13.2 Crear endpoint PUT /api/printers/{printer_id}/capabilities
    - Permitir actualización manual de capacidades
    - Validar formato_contadores contra valores permitidos
    - Establecer manual_override=True
    - Registrar cambio en logs con usuario
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 13.3 Escribir property test para validación de actualización manual
    - **Property 21: Manual Update Validation**
    - **Valida: Requirements 7.2**
  
  - [ ]* 13.4 Escribir property test para logging de actualización manual
    - **Property 22: Manual Update Logging**
    - **Valida: Requirements 7.3**
  
  - [ ]* 13.5 Escribir property test para flag de override manual
    - **Property 23: Manual Override Flag**
    - **Valida: Requirements 7.5**
  
  - [ ]* 13.6 Escribir property test para protección de override
    - **Property 24: Manual Override Protection**
    - **Valida: Requirements 7.6**

- [x] 14. Modificar endpoints existentes para incluir capacidades
  - [x] 14.1 Modificar GET /api/counters/latest/{printer_id}
    - Incluir capabilities en respuesta de printer
    - Mantener todos los campos de contadores (retrocompatibilidad)
    - _Requirements: 3.4, 9.2_
  
  - [x] 14.2 Modificar GET /api/counters/user-counters/{printer_id}
    - Incluir capabilities en respuesta de printer
    - _Requirements: 3.4_
  
  - [x] 14.3 Modificar GET /api/closes/{cierre_id}
    - Incluir capabilities de la impresora asociada
    - _Requirements: 3.5_
  
  - [ ]* 14.4 Escribir property test para inclusión de capacidades en API
    - **Property 9: API Response Includes Capabilities**
    - **Valida: Requirements 3.1, 3.2, 3.3**
  
  - [ ]* 14.5 Escribir property test para inclusión en respuestas de contadores
    - **Property 10: Counter Responses Include Printer Capabilities**
    - **Valida: Requirements 3.4, 3.5**
  
  - [ ]* 14.6 Escribir property test para campos completos de contadores
    - **Property 26: Complete Counter Fields**
    - **Valida: Requirements 9.2**

- [x] 15. Implementar valores por defecto para retrocompatibilidad
  - [x] 15.1 Agregar lógica de fallback en endpoints
    - Si capabilities es None, retornar valores por defecto seguros (mostrar todo)
    - _Requirements: 9.1, 9.3_
  
  - [ ]* 15.2 Escribir property test para fallback de capacidades
    - **Property 25: Default Capabilities Fallback**
    - **Valida: Requirements 9.1**
  
  - [ ]* 15.3 Escribir unit tests de retrocompatibilidad
    - Test con impresora sin capabilities_json
    - Test con cliente que no espera campo capabilities
    - _Requirements: 9.1, 9.2, 9.3_

- [x] 16. Checkpoint - Validar API y retrocompatibilidad
  - Probar endpoints con Postman/curl
  - Verificar que respuestas incluyen capabilities
  - Confirmar que clientes antiguos siguen funcionando
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas

## Fase 4: Frontend - Adaptación de UI

- [x] 17. Crear tipos TypeScript para capacidades
  - [x] 17.1 Definir interfaces en src/types/printer.ts
    - Crear interface PrinterCapabilities
    - Crear interface ColumnVisibilityConfig
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 17.2 Extender tipo Printer para incluir capabilities
    - Agregar campo capabilities?: PrinterCapabilities
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 18. Implementar lógica de visibilidad de columnas
  - [x] 18.1 Crear hook useColumnVisibility en src/hooks/useColumnVisibility.ts
    - Implementar función calculateColumnVisibility()
    - Retornar configuración de visibilidad basada en capabilities
    - Incluir fallback a mostrar todo si no hay capabilities
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 9.3_
  
  - [ ]* 18.2 Escribir property test para visibilidad de columnas de color
    - **Property 11: Frontend Column Visibility**
    - **Valida: Requirements 4.1**
  
  - [ ]* 18.3 Escribir property test para visibilidad de campos especiales
    - **Property 12: Frontend Special Fields Visibility**
    - **Valida: Requirements 4.2, 4.3**
  
  - [ ]* 18.4 Escribir property test para visibilidad de mono/dos colores
    - **Property 13: Frontend Mono/Dos Colores Visibility**
    - **Valida: Requirements 4.4**
  
  - [ ]* 18.5 Escribir property test para comportamiento por defecto
    - **Property 27: Frontend Default Behavior**
    - **Valida: Requirements 9.3**

- [x] 19. Implementar filtrado de columnas en tablas
  - [-] 19.1 Crear utilidades de filtrado en src/utils/columnFiltering.ts
    - Implementar función filterColumns()
    - Implementar función shouldShowColumn()
    - Implementar función shouldShowGroupHeader()
    - _Requirements: 4.5, 4.6, 4.7, 4.8_
  
  - [ ]* 19.2 Escribir property test para ocultación de encabezados de grupo
    - **Property 14: Group Header Visibility**
    - **Valida: Requirements 4.8**
  
  - [ ]* 19.3 Escribir unit tests para filtrado de columnas
    - Test con diferentes configuraciones de visibilidad
    - Test de ocultación de grupos completos
    - _Requirements: 4.5, 4.6, 4.7, 4.8_

- [x] 20. Adaptar UserCounterTable con visibilidad dinámica
  - [x] 20.1 Modificar componente UserCounterTable
    - Integrar hook useColumnVisibility
    - Aplicar filtrado de columnas visibles
    - Ocultar encabezados de grupos cuando corresponda
    - _Requirements: 4.5_
  
  - [x] 20.2 Definir configuración de columnas con grupos
    - Asignar grupo 'color' a columnas de color
    - Asignar grupo 'hojas_2_caras' a columnas correspondientes
    - Asignar grupo 'paginas_combinadas' a columnas correspondientes
    - Asignar grupo 'mono_color' y 'dos_colores' a columnas correspondientes
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 21. Adaptar CierreDetalleModal con visibilidad dinámica
  - [x] 21.1 Modificar componente CierreDetalleModal
    - Integrar hook useColumnVisibility
    - Aplicar filtrado de columnas visibles
    - _Requirements: 4.6_
  
  - [x] 21.2 Adaptar resumen de totales según formato de impresora
    - Detectar formato_contadores de las capabilities de la impresora
    - Para formato "ecologico": Mostrar SOLO Total Páginas (sin desglose de Copiadora, Impresora, Escáner, Fax)
    - Para formato "estandar": Mostrar Total, Copiadora, Impresora, Escáner, Fax
    - Para formato "simplificado": Mostrar todos los totales
    - _Requirements: 1.4, 4.6_
  
  - [x] 21.3 Adaptar tabla de detalle según formato de impresora
    - Detectar formato_contadores de las capabilities de la impresora
    - Para formato "ecologico": Mostrar SOLO Usuario, Código, Total, Consumo
    - Para formato "estandar": Mostrar Usuario, Código, Total, Consumo, B/N, Color, Copiadora, Impresora, Escáner
    - Para formato "simplificado": Mostrar sin columnas de color
    - _Requirements: 1.4, 4.6_
  
  - [x] 21.4 Verificar que el parser de contador ecológico captura correctamente
    - Revisar backend/services/counter_service.py para formato ecológico
    - Asegurar que solo captura total_paginas y métricas ecológicas
    - Validar que los datos se guardan correctamente en CierreMensualUsuario
    - _Requirements: 1.4_
  
  - [x] 21.5 Adaptar CounterBreakdown (resumen principal) según formato de impresora
    - Modificar componente CounterBreakdown para recibir capabilities
    - Para formato "ecologico": Mostrar SOLO Total Páginas centrado
    - Para formato "estandar/simplificado": Mostrar desglose completo
    - Actualizar PrinterDetailView para pasar capabilities
    - _Requirements: 1.4, 4.6_
  
  - [x] 21.6 Adaptar UserCounterTable (tabla principal) según formato de impresora
    - Modificar lógica shouldShowColumn para formato ecológico
    - Para formato "ecologico": Mostrar SOLO Código, Nombre, Total
    - Para formato "estandar/simplificado": Mostrar todas las columnas según capabilities
    - _Requirements: 1.4, 4.5_

- [ ] 22. Adaptar ComparacionModal con visibilidad dinámica
  - [ ] 22.1 Modificar componente ComparacionModal
    - Integrar hook useColumnVisibility
    - Aplicar filtrado de columnas visibles
    - _Requirements: 4.7_

- [ ] 23. Implementar manejo de errores y estados de carga
  - [ ] 23.1 Agregar estados de carga en componentes
    - Mostrar skeleton mientras se cargan capabilities
    - Manejar errores de API gracefully
    - _Requirements: 9.3_
  
  - [ ]* 23.2 Escribir unit tests para estados de carga y error
    - Test con capabilities undefined (cargando)
    - Test con capabilities null (error)
    - Test con capabilities válidas
    - _Requirements: 9.3_

- [ ] 24. Testing end-to-end del frontend
  - [ ]* 24.1 Escribir tests E2E con Playwright/Cypress
    - Test de tabla con impresora B/N (columnas de color ocultas)
    - Test de tabla con impresora color (todas las columnas visibles)
    - Test de tabla con formato simplificado
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ] 25. Checkpoint final - Validar sistema completo
  - Probar flujo completo: lectura de contadores → detección → API → UI
  - Verificar con cada impresora conocida (250, 251, 252, 253, 110.250)
  - Confirmar que columnas se ocultan/muestran correctamente
  - Validar retrocompatibilidad con impresoras sin capabilities
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas

## Documentación y Finalización

- [ ] 26. Documentar código y APIs
  - [ ] 26.1 Agregar docstrings a todas las clases y métodos del backend
    - Documentar CapabilitiesDetector con ejemplos
    - Documentar formatos de contadores soportados
    - Incluir ejemplos de HTML para cada formato
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [ ] 26.2 Actualizar documentación de API (OpenAPI/Swagger)
    - Documentar nuevos endpoints de capabilities
    - Incluir ejemplos de respuestas
    - Documentar códigos de error
    - _Requirements: 7.1_
  
  - [ ] 26.3 Agregar comentarios JSDoc en código TypeScript
    - Documentar interfaces y tipos
    - Documentar hooks y utilidades
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 27. Crear documentación de usuario
  - [ ] 27.1 Escribir guía de interpretación de capacidades
    - Explicar qué significa cada campo de capabilities
    - Documentar formatos de contadores
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [ ] 27.2 Escribir guía de actualización manual de capacidades
    - Explicar cuándo usar actualización manual
    - Documentar endpoint PUT /api/printers/{id}/capabilities
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ] 27.3 Crear guía de troubleshooting
    - Documentar cómo investigar inconsistencias
    - Explicar logs y advertencias
    - _Requirements: 6.1, 6.2, 6.4_
  
  - [ ] 27.4 Crear FAQ sobre columnas ocultas
    - Explicar por qué algunas columnas no se muestran
    - Cómo verificar capacidades de una impresora
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 28. Configurar monitoreo y alertas
  - [ ] 28.1 Configurar métricas de monitoreo
    - Contador de inconsistencias por día
    - Distribución de formatos detectados
    - Tiempo de detección de capacidades
    - _Requirements: 6.4, 6.5_
  
  - [ ] 28.2 Implementar sistema de notificaciones
    - Crear clase InconsistencyNotifier
    - Configurar envío de alertas después de 3 inconsistencias
    - Integrar con sistema de logging
    - _Requirements: 6.4_

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada fase es desplegable independientemente sin romper funcionalidad existente
- Los checkpoints permiten validación incremental y detección temprana de problemas
- Los property tests validan propiedades universales con datos generados (100+ iteraciones)
- Los unit tests validan casos específicos y edge cases conocidos
- La implementación sigue el plan de despliegue en 4 fases del documento de diseño

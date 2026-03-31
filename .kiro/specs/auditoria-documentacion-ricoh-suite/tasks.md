# Implementation Plan: Auditoría y Mejora de Documentación

## Overview

Este plan implementa un sistema de auditoría automatizada para Ricoh Suite que verifica código contra documentación, identifica vulnerabilidades de seguridad, analiza cobertura de tests, y genera documentación estructurada. El sistema sigue una arquitectura de pipeline en tres fases: Collection, Analysis, y Reporting.

## Tasks

- [ ] 1. Configurar estructura del proyecto y modelos de datos
  - Crear directorio `audit_system/` en la raíz del proyecto
  - Implementar todos los dataclasses y enums en `audit_system/models.py`
  - Configurar pytest y hypothesis para testing
  - Crear estructura de directorios para tests (unit/, property/, integration/, fixtures/)
  - _Requirements: Todos (estructura base)_

- [ ]* 1.1 Escribir property test para Property 1: Configuration Parsing Round Trip
  - **Property 1: Configuration Parsing Round Trip**
  - **Validates: Requirements 1.1, 1.2, 12.1, 12.2**

- [ ] 2. Implementar FileSystemScanner
  - [ ] 2.1 Implementar scan_source_code() para archivos Python y TypeScript
    - Escanear recursivamente directorios backend/ y src/
    - Filtrar por extensiones .py, .ts, .tsx
    - Crear objetos SourceFile con contenido y metadatos
    - _Requirements: 2.1, 2.2, 3.1, 3.2_
  
  - [ ] 2.2 Implementar scan_documentation() para archivos Markdown
    - Escanear directorio docs/
    - Crear objetos DocumentFile con contenido
    - _Requirements: 9.1_
  
  - [ ] 2.3 Implementar scan_configuration() para archivos de configuración
    - Leer y parsear package.json
    - Leer y parsear requirements.txt
    - Leer .env.example si existe
    - Leer .gitignore
    - _Requirements: 1.1, 1.2, 3.6, 11.1_
  
  - [ ] 2.4 Implementar scan_tests() para archivos de test
    - Escanear backend/tests/ y src/ para archivos de test
    - Identificar patrones: test_*.py, *.test.ts, *.spec.ts
    - _Requirements: 4.1, 4.6_

- [ ]* 2.5 Escribir property test para Property 2: File Counting Accuracy
  - **Property 2: File Counting Accuracy**
  - **Validates: Requirements 2.1, 2.2, 2.3, 4.1, 4.3**

- [ ]* 2.6 Escribir property test para Property 11: Test File Pattern Matching
  - **Property 11: Test File Pattern Matching**
  - **Validates: Requirements 4.6**

- [ ] 3. Implementar MetricsCollector
  - [ ] 3.1 Implementar extract_versions() para extraer versiones
    - Extraer version de package.json
    - Extraer versiones de paquetes Python de requirements.txt
    - Parsear formato "package==version" y "package>=version"
    - _Requirements: 1.1, 1.2_
  
  - [ ] 3.2 Implementar count_endpoints() para contar rutas FastAPI
    - Buscar patrones @router.get, @router.post, etc.
    - Buscar patrones @app.get, @app.post, etc.
    - Contar ocurrencias en archivos de backend/api/
    - _Requirements: 2.1_
  
  - [ ] 3.3 Implementar count_components() para contar componentes React
    - Buscar patrones de export function, export const
    - Identificar componentes por convención de nombres (PascalCase)
    - Contar archivos en src/components/
    - _Requirements: 2.2_
  
  - [ ] 3.4 Implementar count_tests() y count_lines_of_code()
    - Contar archivos de test
    - Contar líneas excluyendo docs/ y node_modules/
    - _Requirements: 2.3, 2.4_
  
  - [ ] 3.5 Implementar get_last_commit_date() usando subprocess
    - Ejecutar comando git log -1 --format=%cd
    - Parsear fecha de último commit
    - Manejar error si no es repositorio git
    - _Requirements: 1.3_
  
  - [ ] 3.6 Implementar list_dependencies() para listar dependencias
    - Extraer dependencias de package.json (dependencies y devDependencies)
    - Extraer dependencias de requirements.txt
    - Clasificar versiones como 'pinned' o 'range'
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [ ]* 3.7 Escribir property test para Property 3: Exclusion Rules in Line Counting
  - **Property 3: Exclusion Rules in Line Counting**
  - **Validates: Requirements 2.4**

- [ ]* 3.8 Escribir property test para Property 35: Dependency Version Classification
  - **Property 35: Dependency Version Classification**
  - **Validates: Requirements 12.3**

- [ ]* 3.9 Escribir property test para Property 36: Dependency List Completeness
  - **Property 36: Dependency List Completeness**
  - **Validates: Requirements 12.4**

- [ ] 4. Checkpoint - Verificar funcionalidad básica de escaneo
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implementar SecurityScanner
  - [ ] 5.1 Implementar scan_for_credentials() con patrones regex
    - Definir CREDENTIAL_PATTERNS para password, secret, api_key, token, auth
    - Buscar patrones en archivos Python y TypeScript
    - Capturar contexto (3 líneas antes y después)
    - Clasificar todos los hallazgos como CRITICAL
    - _Requirements: 3.1, 3.2, 3.3, 3.8_
  
  - [ ] 5.2 Implementar scan_for_hardcoded_ips() para IPs hardcodeadas
    - Usar patrón IP_PATTERN para detectar direcciones IP
    - Registrar file path y line number
    - _Requirements: 3.4_
  
  - [ ] 5.3 Implementar verify_gitignore() para validar .gitignore
    - Verificar que .env esté listado en .gitignore
    - Verificar patrones .env* o *.env
    - _Requirements: 3.6_
  
  - [ ] 5.4 Implementar check_git_history_for_secrets()
    - Ejecutar git log --all --full-history -- "*.env"
    - Verificar si hay commits con archivos .env
    - _Requirements: 3.7, 11.5_
  
  - [ ] 5.5 Implementar validate_env_configuration()
    - Extraer variables de entorno usadas en código (os.environ, process.env)
    - Comparar contra variables en .env.example
    - Identificar variables faltantes
    - Verificar que valores en .env.example sean placeholders
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.6_

- [ ]* 5.6 Escribir property test para Property 4: Pattern Detection Completeness
  - **Property 4: Pattern Detection Completeness**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [ ]* 5.7 Escribir property test para Property 5: Gitignore Validation
  - **Property 5: Gitignore Validation**
  - **Validates: Requirements 3.6**

- [ ]* 5.8 Escribir property test para Property 7: Severity Classification Consistency
  - **Property 7: Severity Classification Consistency**
  - **Validates: Requirements 3.8**

- [ ]* 5.9 Escribir property test para Property 20: Environment Variable Naming Convention
  - **Property 20: Environment Variable Naming Convention**
  - **Validates: Requirements 7.2**

- [ ]* 5.10 Escribir property test para Property 21: Environment Variable Completeness Check
  - **Property 21: Environment Variable Completeness Check**
  - **Validates: Requirements 7.3, 11.2, 11.3, 11.4**

- [ ]* 5.11 Escribir property test para Property 34: Placeholder Value Validation
  - **Property 34: Placeholder Value Validation**
  - **Validates: Requirements 11.6**

- [ ] 6. Implementar TestCoverageAnalyzer
  - [ ] 6.1 Implementar map_tests_to_modules()
    - Analizar imports en archivos de test
    - Mapear test files a source modules
    - Crear TestCoverageMap
    - _Requirements: 4.2_
  
  - [ ] 6.2 Implementar identify_untested_modules()
    - Comparar source modules contra modules con tests
    - Identificar módulos sin cobertura
    - _Requirements: 4.4_
  
  - [ ] 6.3 Implementar calculate_coverage_percentage()
    - Calcular (modules_with_tests / total_modules) * 100
    - _Requirements: 4.8_
  
  - [ ] 6.4 Implementar check_test_configuration()
    - Buscar pytest.ini, setup.cfg, .coveragerc
    - _Requirements: 4.5_

- [ ]* 6.5 Escribir property test para Property 8: Test-to-Module Mapping Accuracy
  - **Property 8: Test-to-Module Mapping Accuracy**
  - **Validates: Requirements 4.2**

- [ ]* 6.6 Escribir property test para Property 9: Untested Module Identification
  - **Property 9: Untested Module Identification**
  - **Validates: Requirements 4.4**

- [ ]* 6.7 Escribir property test para Property 12: Coverage Percentage Calculation
  - **Property 12: Coverage Percentage Calculation**
  - **Validates: Requirements 4.8**

- [ ]* 6.8 Escribir property test para Property 10: Test Configuration Detection
  - **Property 10: Test Configuration Detection**
  - **Validates: Requirements 4.5**

- [ ] 7. Implementar IntegrityValidator
  - [ ] 7.1 Implementar validate_documentation_references()
    - Extraer file paths de documentos markdown
    - Verificar existencia de cada archivo referenciado
    - Registrar IntegrityFinding para referencias rotas
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ] 7.2 Implementar validate_python_imports()
    - Extraer imports usando regex o AST
    - Verificar que módulos importados existan
    - _Requirements: 9.4_
  
  - [ ] 7.3 Implementar validate_typescript_imports()
    - Extraer imports de archivos TypeScript
    - Verificar que módulos importados existan
    - _Requirements: 9.5_
  
  - [ ] 7.4 Implementar verify_bug_fixes()
    - Escanear docs/fixes/ para documentos de bugs
    - Extraer file paths afectados de cada bug
    - Verificar si fix está presente en código
    - Registrar BugStatusFinding para inconsistencias
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 7.5 Escribir property test para Property 27: File Reference Extraction
  - **Property 27: File Reference Extraction**
  - **Validates: Requirements 9.1**

- [ ]* 7.6 Escribir property test para Property 28: File Existence Validation
  - **Property 28: File Existence Validation**
  - **Validates: Requirements 9.2**

- [ ]* 7.7 Escribir property test para Property 13: Bug Fix Document Listing
  - **Property 13: Bug Fix Document Listing**
  - **Validates: Requirements 5.1**

- [ ]* 7.8 Escribir property test para Property 14: Affected File Extraction
  - **Property 14: Affected File Extraction**
  - **Validates: Requirements 5.2**

- [ ] 8. Implementar StatusDocumentParser y Comparator
  - [ ] 8.1 Implementar StatusDocumentParser
    - Implementar parse_status_document() para leer documento de estado
    - Implementar extract_version_table() para extraer versiones de tablas markdown
    - Implementar extract_metrics_table() para extraer métricas de código
    - Implementar extract_file_references() para extraer referencias
    - _Requirements: 1.4, 2.5_
  
  - [ ] 8.2 Implementar Comparator
    - Implementar compare_versions() para comparar versiones
    - Implementar compare_metrics() para comparar métricas de código
    - Implementar calculate_difference_percentage()
    - Registrar Inconsistency cuando diferencia > 10%
    - _Requirements: 1.4, 1.5, 2.5, 2.6_

- [ ]* 8.3 Escribir property test para Property 38: Metrics Comparison Consistency
  - **Property 38: Metrics Comparison Consistency**
  - **Validates: Requirements 1.4, 2.5, 2.6**

- [ ]* 8.4 Escribir property test para Property 39: Version Comparison Recording
  - **Property 39: Version Comparison Recording**
  - **Validates: Requirements 1.6**

- [ ] 9. Checkpoint - Verificar análisis y comparación
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implementar DocumentationGenerator
  - [ ] 10.1 Implementar generate_findings_report()
    - Crear AUDITORIA_HALLAZGOS.md con todas las secciones requeridas
    - Incluir secciones: version inconsistencies, security findings, test coverage, bug status, metric discrepancies
    - Incluir executive summary con totales por categoría
    - Formatear cada finding con todos los campos requeridos
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  
  - [ ] 10.2 Implementar generate_security_proposals()
    - Generar propuestas para cada SecurityFinding
    - Proponer nombres de variables de entorno en UPPER_SNAKE_CASE
    - Incluir snippets de código before/after
    - Priorizar findings críticos primero
    - _Requirements: 7.1, 7.2, 7.6, 7.7_
  
  - [ ] 10.3 Implementar generate_executive_documentation()
    - Generar ESTADO_EJECUTIVO.md con lenguaje no técnico
    - Generar TESTS_Y_CALIDAD.md con métricas de calidad
    - Generar SEGURIDAD.md con arquitectura de seguridad
    - Generar PENDIENTES.md con tareas pendientes
    - Generar CHANGELOG.md con historial de versiones
    - Incluir cross-references entre documentos
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [ ] 10.4 Implementar generate_validation_checklist()
    - Crear checklist con todas las fases de auditoría
    - Incluir: completed status, findings count, critical issues count
    - Calcular completion percentage
    - Incluir timestamps para cada fase
    - _Requirements: 10.1, 10.2, 10.3, 10.5, 10.6_
  
  - [ ] 10.5 Implementar generate_env_example_template()
    - Generar template con todas las variables faltantes
    - Usar valores placeholder para variables sensibles
    - _Requirements: 7.4, 11.4_

- [ ]* 10.6 Escribir property test para Property 16: Report Section Completeness
  - **Property 16: Report Section Completeness**
  - **Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6**

- [ ]* 10.7 Escribir property test para Property 17: Finding Structure Completeness
  - **Property 17: Finding Structure Completeness**
  - **Validates: Requirements 6.7**

- [ ]* 10.8 Escribir property test para Property 18: Executive Summary Aggregation
  - **Property 18: Executive Summary Aggregation**
  - **Validates: Requirements 6.8**

- [ ]* 10.9 Escribir property test para Property 19: Security Proposal Generation
  - **Property 19: Security Proposal Generation**
  - **Validates: Requirements 7.1, 7.6**

- [ ]* 10.10 Escribir property test para Property 22: Template Generation Completeness
  - **Property 22: Template Generation Completeness**
  - **Validates: Requirements 7.4**

- [ ]* 10.11 Escribir property test para Property 25: Technical Documentation Code References
  - **Property 25: Technical Documentation Code References**
  - **Validates: Requirements 8.7**

- [ ]* 10.12 Escribir property test para Property 26: Cross-Reference Presence
  - **Property 26: Cross-Reference Presence**
  - **Validates: Requirements 8.8**

- [ ]* 10.13 Escribir property test para Property 30: Checklist Item Structure
  - **Property 30: Checklist Item Structure**
  - **Validates: Requirements 10.3**

- [ ]* 10.14 Escribir property test para Property 31: Completion Percentage Calculation
  - **Property 31: Completion Percentage Calculation**
  - **Validates: Requirements 10.5**

- [ ] 11. Implementar AuditOrchestrator
  - [ ] 11.1 Implementar __init__() e inicialización de componentes
    - Inicializar todos los componentes del pipeline
    - Configurar paths y opciones
    - _Requirements: Todos (orquestación)_
  
  - [ ] 11.2 Implementar run_audit() para ejecutar pipeline completo
    - Ejecutar FileSystemScanner para recopilar archivos
    - Ejecutar MetricsCollector para extraer métricas reales
    - Ejecutar StatusDocumentParser para extraer métricas declaradas
    - Ejecutar SecurityScanner para identificar vulnerabilidades
    - Ejecutar TestCoverageAnalyzer para analizar cobertura
    - Ejecutar IntegrityValidator para validar referencias
    - Ejecutar Comparator para comparar métricas
    - Agregar todos los resultados en AuditFindings
    - Manejar errores gracefully y continuar auditoría
    - _Requirements: Todos_
  
  - [ ] 11.3 Implementar generate_reports() para generar documentación
    - Llamar a DocumentationGenerator para cada tipo de reporte
    - Escribir archivos en docs/
    - Garantizar que no se modifiquen archivos de código fuente
    - _Requirements: 6.1, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 10.1_

- [ ]* 11.4 Escribir property test para Property 23: Read-Only Guarantee
  - **Property 23: Read-Only Guarantee**
  - **Validates: Requirements 7.5**

- [ ] 12. Implementar CLI y punto de entrada
  - [ ] 12.1 Crear audit_system/main.py con CLI usando argparse
    - Definir argumentos: --root, --status-doc, --output-dir, --skip-git, --verbose
    - Configurar logging
    - _Requirements: Todos (ejecución)_
  
  - [ ] 12.2 Implementar función main() que ejecuta el pipeline
    - Instanciar AuditOrchestrator
    - Ejecutar run_audit()
    - Ejecutar generate_reports()
    - Manejar excepciones y logging
    - Imprimir resumen de hallazgos en consola
    - _Requirements: Todos_

- [ ] 13. Checkpoint - Verificar pipeline completo
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Escribir tests de integración
  - [ ]* 14.1 Escribir test de pipeline completo end-to-end
    - Crear fixtures con proyecto de ejemplo
    - Ejecutar auditoría completa
    - Verificar que se generen todos los reportes
    - Verificar que hallazgos sean correctos
    - _Requirements: Todos_

- [ ] 15. Crear documentación de uso
  - [ ] 15.1 Crear README.md para audit_system
    - Documentar instalación y dependencias
    - Documentar uso del CLI
    - Incluir ejemplos de ejecución
    - Documentar estructura de reportes generados
    - _Requirements: Todos (documentación)_

- [ ] 16. Checkpoint final - Validación completa
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- El sistema opera en modo read-only por defecto y no modifica código fuente
- Property tests usan Hypothesis con mínimo 100 iteraciones
- Unit tests complementan property tests para casos específicos y edge cases
- Checkpoints aseguran validación incremental del sistema
- El sistema genera 9 archivos de documentación al completarse

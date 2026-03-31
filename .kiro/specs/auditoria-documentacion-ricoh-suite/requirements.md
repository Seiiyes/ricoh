# Requirements Document

## Introduction

Este documento especifica los requisitos para el sistema de Auditoría y Mejora de Documentación del proyecto Ricoh Suite. El sistema auditará el código fuente contra la documentación existente, verificará métricas reales, identificará problemas de seguridad, y producirá documentación confiable y estructurada lista para producción.

El objetivo principal es garantizar que la documentación refleje fielmente el estado real del código, identificar vulnerabilidades de seguridad, y reestructurar la documentación en un formato ejecutivo y mantenible.

## Glossary

- **Audit_System**: El sistema de auditoría que verifica código contra documentación
- **Status_Document**: El documento `docs/ESTADO_PROYECTO_2026_03_30.md` que declara el estado del proyecto
- **Source_Code**: El código fuente del proyecto en `/backend` y `/src`
- **Security_Scanner**: Componente que busca credenciales y datos sensibles hardcodeados
- **Metrics_Collector**: Componente que recopila métricas reales del código
- **Documentation_Generator**: Componente que genera documentación estructurada
- **Hardcoded_Credential**: Cualquier contraseña, token, API key, o secreto escrito directamente en código
- **Test_Coverage**: Porcentaje de código cubierto por tests automatizados
- **Real_Metric**: Métrica obtenida directamente del filesystem o código fuente
- **Declared_Metric**: Métrica declarada en el Status_Document
- **Critical_Finding**: Hallazgo de seguridad que requiere acción inmediata
- **Inconsistency**: Diferencia entre Real_Metric y Declared_Metric
- **Bug_Fix**: Corrección documentada en `/docs/fixes/`
- **Executive_Documentation**: Documentación de alto nivel para stakeholders
- **Technical_Documentation**: Documentación detallada para desarrolladores

## Requirements

### Requirement 1: Verificación de Versiones y Fechas

**User Story:** Como auditor del sistema, quiero verificar que las versiones y fechas declaradas en la documentación coincidan con las reales del código, para garantizar que la documentación está actualizada.

#### Acceptance Criteria

1. WHEN the Audit_System reads `package.json`, THE Metrics_Collector SHALL extract the frontend version number
2. WHEN the Audit_System reads `backend/requirements.txt`, THE Metrics_Collector SHALL extract all Python package versions
3. WHEN the Audit_System queries git history, THE Metrics_Collector SHALL extract the last commit date
4. THE Audit_System SHALL compare extracted versions against versions declared in Status_Document
5. IF any version mismatch is detected, THEN THE Audit_System SHALL record an Inconsistency with file path and line number
6. THE Audit_System SHALL record all version comparisons in the audit report

### Requirement 2: Verificación de Métricas de Código

**User Story:** Como auditor del sistema, quiero verificar que las métricas de código declaradas (endpoints, componentes, líneas de código) coincidan con las reales, para garantizar precisión en la documentación.

#### Acceptance Criteria

1. WHEN the Audit_System scans `/backend/api/`, THE Metrics_Collector SHALL count all Python files containing FastAPI route definitions
2. WHEN the Audit_System scans `/src/components/`, THE Metrics_Collector SHALL count all React component files
3. WHEN the Audit_System scans `/backend/tests/` and `/src/`, THE Metrics_Collector SHALL count all test files
4. WHEN the Audit_System counts lines of code, THE Metrics_Collector SHALL exclude documentation files and node_modules directory
5. THE Audit_System SHALL compare each Real_Metric against the corresponding Declared_Metric in Status_Document
6. IF any metric differs by more than 10 percent, THEN THE Audit_System SHALL record an Inconsistency
7. THE Audit_System SHALL generate a metrics comparison table with columns: metric name, declared value, real value, difference percentage

### Requirement 3: Escaneo de Seguridad de Credenciales

**User Story:** Como auditor de seguridad, quiero identificar todas las credenciales hardcodeadas en el código fuente, para eliminar vulnerabilidades críticas antes de producción.

#### Acceptance Criteria

1. WHEN the Security_Scanner scans all Python files, THE Security_Scanner SHALL search for patterns: "password", "secret", "key", "token", "api_key", "auth"
2. WHEN the Security_Scanner scans all TypeScript files, THE Security_Scanner SHALL search for the same credential patterns
3. WHEN the Security_Scanner finds a potential credential, THE Security_Scanner SHALL record the file path, line number, and matched text
4. THE Security_Scanner SHALL search for hardcoded IP addresses matching pattern `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`
5. THE Security_Scanner SHALL search for hardcoded usernames in network configuration contexts
6. THE Security_Scanner SHALL verify that `.env` files are listed in `.gitignore`
7. WHEN the Security_Scanner queries git history, THE Security_Scanner SHALL verify that no `.env` files have been committed
8. IF any Hardcoded_Credential is found, THEN THE Audit_System SHALL classify it as a Critical_Finding
9. THE Audit_System SHALL generate a security findings report with severity levels: critical, high, medium, low

### Requirement 4: Análisis de Cobertura de Tests

**User Story:** Como auditor de calidad, quiero conocer la cobertura real de tests por módulo, para identificar áreas sin cobertura y priorizar esfuerzos de testing.

#### Acceptance Criteria

1. WHEN the Audit_System scans `/backend/tests/`, THE Metrics_Collector SHALL list all test files
2. FOR EACH test file, THE Audit_System SHALL identify which source modules are being tested
3. WHEN the Audit_System scans `/backend/services/` and `/backend/api/`, THE Metrics_Collector SHALL list all modules
4. THE Audit_System SHALL identify modules without corresponding test files
5. WHEN the Audit_System searches for test configuration files, THE Metrics_Collector SHALL check for `pytest.ini`, `setup.cfg`, or `.coveragerc`
6. WHEN the Audit_System scans `/src/`, THE Metrics_Collector SHALL search for files matching patterns `*.test.ts`, `*.test.tsx`, `*.spec.ts`, `*.spec.tsx`
7. THE Audit_System SHALL generate a coverage table with columns: module name, has tests, test file path, coverage status
8. THE Audit_System SHALL calculate the percentage of modules with tests

### Requirement 5: Verificación de Estado de Bugs

**User Story:** Como auditor de calidad, quiero verificar que los bugs marcados como resueltos realmente estén corregidos en el código, para garantizar la integridad del registro de bugs.

#### Acceptance Criteria

1. WHEN the Audit_System scans `/docs/fixes/`, THE Audit_System SHALL list all Bug_Fix documents
2. FOR EACH Bug_Fix marked as resolved, THE Audit_System SHALL extract the affected file paths
3. WHEN the Audit_System reads the affected files, THE Audit_System SHALL verify that the documented fix is present in Source_Code
4. IF a Bug_Fix is marked as resolved but the fix is not present, THEN THE Audit_System SHALL record an Inconsistency
5. FOR EACH Bug_Fix marked as pending, THE Audit_System SHALL verify if the bug still exists in Source_Code
6. THE Audit_System SHALL generate a bug status report with columns: bug ID, status declared, status verified, file path

### Requirement 6: Generación de Reporte de Hallazgos

**User Story:** Como auditor del sistema, quiero un reporte consolidado de todos los hallazgos de la auditoría, para comunicar resultados a stakeholders y priorizar acciones correctivas.

#### Acceptance Criteria

1. THE Documentation_Generator SHALL create a file `AUDITORIA_HALLAZGOS.md` in `/docs/`
2. THE Documentation_Generator SHALL include a section for version inconsistencies with file references
3. THE Documentation_Generator SHALL include a section for security findings with severity classification
4. THE Documentation_Generator SHALL include a section for modules without test coverage
5. THE Documentation_Generator SHALL include a section for bug status inconsistencies
6. THE Documentation_Generator SHALL include a section for metric discrepancies with percentage differences
7. FOR EACH finding, THE Documentation_Generator SHALL include: category, severity, file path, line number, description, recommended action
8. THE Documentation_Generator SHALL include an executive summary with total findings by category

### Requirement 7: Propuesta de Correcciones de Seguridad

**User Story:** Como auditor de seguridad, quiero propuestas específicas para corregir cada vulnerabilidad encontrada, para facilitar la remediación sin modificar código directamente.

#### Acceptance Criteria

1. FOR EACH Hardcoded_Credential found, THE Audit_System SHALL generate a secure replacement proposal
2. THE Audit_System SHALL propose environment variable names following naming conventions
3. WHEN the Audit_System checks for `.env.example`, THE Audit_System SHALL verify it contains all required environment variables
4. IF `.env.example` is missing variables, THEN THE Audit_System SHALL generate a complete `.env.example` template
5. THE Audit_System SHALL NOT modify Source_Code without explicit user confirmation
6. THE Audit_System SHALL include code snippets showing before and after for each proposed change
7. THE Audit_System SHALL prioritize Critical_Finding items in the proposal list

### Requirement 8: Reestructuración de Documentación Ejecutiva

**User Story:** Como stakeholder del proyecto, quiero documentación ejecutiva clara y estructurada, para entender rápidamente el estado del sistema sin detalles técnicos innecesarios.

#### Acceptance Criteria

1. THE Documentation_Generator SHALL create `docs/ESTADO_EJECUTIVO.md` with project overview, key metrics, and status summary
2. THE Documentation_Generator SHALL create `docs/TESTS_Y_CALIDAD.md` with test coverage, quality metrics, and testing guidelines
3. THE Documentation_Generator SHALL create `docs/SEGURIDAD.md` with security architecture, implemented protections, and security checklist
4. THE Documentation_Generator SHALL create `docs/PENDIENTES.md` with pending tasks, known issues, and prioritized roadmap
5. THE Documentation_Generator SHALL create `docs/CHANGELOG.md` with version history and notable changes
6. WHEN generating Executive_Documentation, THE Documentation_Generator SHALL use non-technical language
7. WHEN generating Technical_Documentation, THE Documentation_Generator SHALL include code references and technical details
8. THE Documentation_Generator SHALL include cross-references between related documents

### Requirement 9: Validación de Integridad de Archivos

**User Story:** Como auditor del sistema, quiero verificar que todos los archivos referenciados en la documentación existan realmente, para evitar referencias rotas y documentación obsoleta.

#### Acceptance Criteria

1. WHEN the Audit_System reads Status_Document, THE Audit_System SHALL extract all file path references
2. FOR EACH file path reference, THE Audit_System SHALL verify the file exists in the filesystem
3. IF a referenced file does not exist, THEN THE Audit_System SHALL record an Inconsistency with the document location
4. THE Audit_System SHALL verify that all imports in Python files reference existing modules
5. THE Audit_System SHALL verify that all imports in TypeScript files reference existing modules
6. THE Audit_System SHALL generate a file integrity report with columns: referenced file, exists, referenced in document, line number

### Requirement 10: Checklist de Validación Final

**User Story:** Como auditor del sistema, quiero un checklist completo de validación, para confirmar que todos los aspectos de la auditoría han sido completados correctamente.

#### Acceptance Criteria

1. THE Audit_System SHALL create a validation checklist with all audit phases
2. THE Audit_System SHALL include checklist items for: version verification, metrics verification, security scan, test coverage analysis, bug status verification, file integrity check
3. FOR EACH checklist item, THE Audit_System SHALL indicate: completed status, findings count, critical issues count
4. THE Audit_System SHALL include a final approval section requiring manual review
5. THE Audit_System SHALL calculate an overall audit completion percentage
6. THE Audit_System SHALL include timestamps for each completed audit phase

### Requirement 11: Análisis de Configuración de Entorno

**User Story:** Como auditor de seguridad, quiero verificar que la configuración de variables de entorno sea completa y segura, para garantizar que el sistema puede desplegarse sin exponer secretos.

#### Acceptance Criteria

1. WHEN the Security_Scanner reads `.env.example`, THE Security_Scanner SHALL extract all declared environment variables
2. WHEN the Security_Scanner scans Source_Code, THE Security_Scanner SHALL identify all environment variable references
3. THE Security_Scanner SHALL compare declared variables in `.env.example` against variables used in Source_Code
4. IF a variable is used in Source_Code but not declared in `.env.example`, THEN THE Audit_System SHALL record an Inconsistency
5. THE Security_Scanner SHALL verify that `.env` files are not committed to git repository
6. THE Security_Scanner SHALL verify that sensitive variables have placeholder values in `.env.example`
7. THE Audit_System SHALL generate an environment configuration report with missing variables and recommendations

### Requirement 12: Análisis de Dependencias y Vulnerabilidades

**User Story:** Como auditor de seguridad, quiero conocer el estado de las dependencias del proyecto y sus vulnerabilidades conocidas, para evaluar riesgos de seguridad.

#### Acceptance Criteria

1. WHEN the Audit_System reads `package.json`, THE Metrics_Collector SHALL extract all frontend dependencies with versions
2. WHEN the Audit_System reads `backend/requirements.txt`, THE Metrics_Collector SHALL extract all Python dependencies with versions
3. THE Audit_System SHALL identify dependencies with version ranges versus pinned versions
4. THE Audit_System SHALL list all dependencies in a structured format
5. THE Audit_System SHALL note any dependencies mentioned in Status_Document as having known vulnerabilities
6. THE Audit_System SHALL generate a dependencies report with columns: package name, current version, type (frontend/backend), notes


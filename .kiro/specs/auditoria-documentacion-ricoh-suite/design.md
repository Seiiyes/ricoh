# Design Document: Auditoría y Mejora de Documentación

## Overview

Este documento especifica el diseño técnico del sistema de auditoría y mejora de documentación para Ricoh Suite. El sistema auditará el código fuente contra la documentación existente, verificará métricas reales, identificará problemas de seguridad, y producirá documentación confiable y estructurada.

### Objetivos del Sistema

1. **Verificación de Integridad**: Comparar métricas declaradas en documentación contra métricas reales del código
2. **Seguridad**: Identificar credenciales hardcodeadas, configuraciones inseguras, y vulnerabilidades
3. **Calidad**: Analizar cobertura de tests y estado de bugs documentados
4. **Documentación**: Generar documentación ejecutiva y técnica estructurada y confiable

### Alcance

El sistema auditará:
- Versiones de dependencias (package.json, requirements.txt)
- Métricas de código (endpoints, componentes, líneas de código, tests)
- Credenciales hardcodeadas en código fuente
- Configuración de variables de entorno
- Cobertura de tests por módulo
- Estado de bugs documentados
- Integridad de referencias en documentación
- Dependencias y sus versiones

El sistema generará:
- Reporte consolidado de hallazgos (`AUDITORIA_HALLAZGOS.md`)
- Propuestas de correcciones de seguridad
- Documentación ejecutiva reestructurada
- Checklist de validación final

### Restricciones

- El sistema NO modificará código fuente sin confirmación explícita del usuario
- El sistema operará en modo read-only por defecto
- El sistema NO ejecutará análisis de vulnerabilidades en línea (solo análisis estático local)
- El sistema generará propuestas, no aplicará cambios automáticamente

---

## Architecture

### Arquitectura General

El sistema sigue una arquitectura de pipeline con tres fases principales:

```
┌─────────────────────────────────────────────────────────────────┐
│                        AUDIT PIPELINE                            │
└─────────────────────────────────────────────────────────────────┘

Phase 1: COLLECTION
┌──────────────────────────────────────────────────────────────┐
│  File System Scanner                                         │
│  ├─ Source Code Scanner (Python, TypeScript)                │
│  ├─ Documentation Scanner (Markdown)                        │
│  ├─ Configuration Scanner (.env, package.json, etc.)        │
│  └─ Git History Scanner                                     │
└──────────────────────────────────────────────────────────────┘
                          ↓
                   Raw Data Collected
                          ↓
Phase 2: ANALYSIS
┌──────────────────────────────────────────────────────────────┐
│  Metrics Collector                                           │
│  ├─ Version Extractor                                       │
│  ├─ Code Metrics Counter                                    │
│  ├─ Test Coverage Analyzer                                  │
│  └─ Dependency Analyzer                                     │
│                                                              │
│  Security Scanner                                            │
│  ├─ Credential Pattern Matcher                              │
│  ├─ Environment Variable Validator                          │
│  ├─ Git History Checker                                     │
│  └─ Configuration Security Analyzer                         │
│                                                              │
│  Integrity Validator                                         │
│  ├─ File Reference Checker                                  │
│  ├─ Import Validator                                        │
│  └─ Bug Status Verifier                                     │
│                                                              │
│  Comparator                                                  │
│  ├─ Version Comparator                                      │
│  ├─ Metrics Comparator                                      │
│  └─ Consistency Checker                                     │
└──────────────────────────────────────────────────────────────┘
                          ↓
                   Analysis Results
                          ↓
Phase 3: REPORTING
┌──────────────────────────────────────────────────────────────┐
│  Documentation Generator                                     │
│  ├─ Findings Report Generator                               │
│  ├─ Security Proposal Generator                             │
│  ├─ Executive Documentation Generator                       │
│  └─ Validation Checklist Generator                          │
└──────────────────────────────────────────────────────────────┘
                          ↓
                   Generated Documentation
```

### Principios de Diseño

1. **Separation of Concerns**: Cada componente tiene una responsabilidad única y bien definida
2. **Immutability**: El sistema no modifica archivos existentes sin confirmación explícita
3. **Traceability**: Cada hallazgo incluye file path, line number, y contexto
4. **Extensibility**: Fácil agregar nuevos tipos de análisis o patrones de seguridad
5. **Testability**: Componentes independientes y testables con property-based testing

### Tecnología

- **Lenguaje**: Python 3.11+ (consistente con el backend existente)
- **File System**: Módulo `pathlib` para manejo de rutas
- **Pattern Matching**: Expresiones regulares con módulo `re`
- **Git Integration**: Módulo `subprocess` para comandos git
- **Parsing**: 
  - JSON: módulo `json`
  - YAML: `pyyaml` (si es necesario)
  - Markdown: parsing manual con regex
  - Python AST: módulo `ast` para análisis de código Python
  - TypeScript: parsing con regex (no AST completo)
- **Testing**: 
  - Unit tests: `pytest`
  - Property-based tests: `hypothesis`

---

## Components and Interfaces

### 1. File System Scanner

**Responsabilidad**: Escanear el filesystem y recopilar archivos relevantes para auditoría.

**Interface**:

```python
class FileSystemScanner:
    """Scans filesystem and collects relevant files for audit"""
    
    def scan_source_code(self, root_path: Path) -> List[SourceFile]:
        """Scan all Python and TypeScript source files"""
        pass
    
    def scan_documentation(self, docs_path: Path) -> List[DocumentFile]:
        """Scan all markdown documentation files"""
        pass
    
    def scan_configuration(self, root_path: Path) -> ConfigFiles:
        """Scan configuration files (package.json, requirements.txt, .env, etc.)"""
        pass
    
    def scan_tests(self, root_path: Path) -> List[TestFile]:
        """Scan all test files"""
        pass
```

**Data Structures**:

```python
@dataclass
class SourceFile:
    path: Path
    language: str  # 'python' or 'typescript'
    content: str
    line_count: int

@dataclass
class DocumentFile:
    path: Path
    content: str
    references: List[str]  # File paths referenced in document

@dataclass
class ConfigFiles:
    package_json: Optional[Dict]
    requirements_txt: Optional[List[str]]
    env_example: Optional[Dict[str, str]]
    gitignore: Optional[List[str]]
```

### 2. Metrics Collector

**Responsabilidad**: Extraer métricas reales del código fuente y configuración.

**Interface**:

```python
class MetricsCollector:
    """Collects real metrics from source code and configuration"""
    
    def extract_versions(self, config: ConfigFiles) -> VersionMetrics:
        """Extract version numbers from package.json and requirements.txt"""
        pass
    
    def count_endpoints(self, source_files: List[SourceFile]) -> int:
        """Count FastAPI route definitions in backend/api/"""
        pass
    
    def count_components(self, source_files: List[SourceFile]) -> int:
        """Count React component files in src/components/"""
        pass
    
    def count_tests(self, test_files: List[TestFile]) -> int:
        """Count test files"""
        pass
    
    def count_lines_of_code(self, source_files: List[SourceFile]) -> int:
        """Count total lines of code excluding docs and node_modules"""
        pass
    
    def get_last_commit_date(self) -> datetime:
        """Query git history for last commit date"""
        pass
    
    def list_dependencies(self, config: ConfigFiles) -> DependencyList:
        """List all frontend and backend dependencies with versions"""
        pass
```

**Data Structures**:

```python
@dataclass
class VersionMetrics:
    frontend_version: str
    python_packages: Dict[str, str]  # package_name -> version
    last_commit_date: datetime

@dataclass
class CodeMetrics:
    endpoints_count: int
    components_count: int
    test_files_count: int
    lines_of_code: int

@dataclass
class DependencyList:
    frontend: List[Dependency]
    backend: List[Dependency]

@dataclass
class Dependency:
    name: str
    version: str
    version_type: str  # 'pinned' or 'range'
```

### 3. Security Scanner

**Responsabilidad**: Identificar vulnerabilidades de seguridad en código y configuración.

**Interface**:

```python
class SecurityScanner:
    """Scans for security vulnerabilities and hardcoded credentials"""
    
    CREDENTIAL_PATTERNS = [
        r'password\s*=\s*["\']([^"\']+)["\']',
        r'secret\s*=\s*["\']([^"\']+)["\']',
        r'api_key\s*=\s*["\']([^"\']+)["\']',
        r'token\s*=\s*["\']([^"\']+)["\']',
        r'auth\s*=\s*["\']([^"\']+)["\']',
    ]
    
    IP_PATTERN = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    
    def scan_for_credentials(self, source_files: List[SourceFile]) -> List[SecurityFinding]:
        """Search for hardcoded credentials in source code"""
        pass
    
    def scan_for_hardcoded_ips(self, source_files: List[SourceFile]) -> List[SecurityFinding]:
        """Search for hardcoded IP addresses"""
        pass
    
    def validate_env_configuration(self, config: ConfigFiles, source_files: List[SourceFile]) -> List[SecurityFinding]:
        """Validate .env.example completeness and security"""
        pass
    
    def check_git_history_for_secrets(self) -> List[SecurityFinding]:
        """Check if .env files have been committed to git"""
        pass
    
    def verify_gitignore(self, config: ConfigFiles) -> List[SecurityFinding]:
        """Verify .env files are in .gitignore"""
        pass
```

**Data Structures**:

```python
@dataclass
class SecurityFinding:
    category: str  # 'credential', 'ip_address', 'env_config', 'git_history'
    severity: str  # 'critical', 'high', 'medium', 'low'
    file_path: Path
    line_number: int
    matched_text: str
    context: str  # Surrounding lines for context
    description: str
    recommended_action: str
    proposed_fix: Optional[str] = None
```

### 4. Test Coverage Analyzer

**Responsabilidad**: Analizar cobertura de tests por módulo.

**Interface**:

```python
class TestCoverageAnalyzer:
    """Analyzes test coverage by module"""
    
    def map_tests_to_modules(self, test_files: List[TestFile], source_files: List[SourceFile]) -> TestCoverageMap:
        """Map test files to source modules they test"""
        pass
    
    def identify_untested_modules(self, coverage_map: TestCoverageMap, source_files: List[SourceFile]) -> List[UntestedModule]:
        """Identify modules without corresponding test files"""
        pass
    
    def calculate_coverage_percentage(self, coverage_map: TestCoverageMap, source_files: List[SourceFile]) -> float:
        """Calculate percentage of modules with tests"""
        pass
    
    def check_test_configuration(self, root_path: Path) -> TestConfiguration:
        """Check for pytest.ini, setup.cfg, or .coveragerc"""
        pass
```

**Data Structures**:

```python
@dataclass
class TestCoverageMap:
    mappings: Dict[Path, List[Path]]  # source_file -> test_files

@dataclass
class UntestedModule:
    module_path: Path
    module_name: str
    coverage_status: str  # 'no_tests', 'partial', 'full'

@dataclass
class TestConfiguration:
    has_pytest_ini: bool
    has_setup_cfg: bool
    has_coveragerc: bool
    config_paths: List[Path]
```

### 5. Integrity Validator

**Responsabilidad**: Validar integridad de referencias en documentación y código.

**Interface**:

```python
class IntegrityValidator:
    """Validates integrity of file references and imports"""
    
    def validate_documentation_references(self, doc_files: List[DocumentFile]) -> List[IntegrityFinding]:
        """Verify all file paths referenced in documentation exist"""
        pass
    
    def validate_python_imports(self, source_files: List[SourceFile]) -> List[IntegrityFinding]:
        """Verify all Python imports reference existing modules"""
        pass
    
    def validate_typescript_imports(self, source_files: List[SourceFile]) -> List[IntegrityFinding]:
        """Verify all TypeScript imports reference existing modules"""
        pass
    
    def verify_bug_fixes(self, bug_docs: List[DocumentFile], source_files: List[SourceFile]) -> List[BugStatusFinding]:
        """Verify documented bug fixes are present in code"""
        pass
```

**Data Structures**:

```python
@dataclass
class IntegrityFinding:
    finding_type: str  # 'missing_file', 'broken_import', 'broken_reference'
    file_path: Path
    line_number: int
    referenced_path: str
    exists: bool
    description: str

@dataclass
class BugStatusFinding:
    bug_id: str
    status_declared: str  # 'resolved', 'pending'
    status_verified: str  # 'resolved', 'pending', 'inconsistent'
    file_path: Path
    description: str
```

### 6. Comparator

**Responsabilidad**: Comparar métricas declaradas contra métricas reales.

**Interface**:

```python
class Comparator:
    """Compares declared metrics against real metrics"""
    
    def compare_versions(self, declared: VersionMetrics, real: VersionMetrics) -> List[Inconsistency]:
        """Compare declared versions against real versions"""
        pass
    
    def compare_metrics(self, declared: CodeMetrics, real: CodeMetrics) -> List[Inconsistency]:
        """Compare declared code metrics against real metrics"""
        pass
    
    def calculate_difference_percentage(self, declared: float, real: float) -> float:
        """Calculate percentage difference between declared and real values"""
        pass
```

**Data Structures**:

```python
@dataclass
class Inconsistency:
    metric_name: str
    declared_value: Any
    real_value: Any
    difference_percentage: Optional[float]
    file_path: Path
    line_number: int
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
```

### 7. Documentation Generator

**Responsabilidad**: Generar documentación estructurada basada en resultados de auditoría.

**Interface**:

```python
class DocumentationGenerator:
    """Generates structured documentation from audit results"""
    
    def generate_findings_report(self, findings: AuditFindings) -> str:
        """Generate AUDITORIA_HALLAZGOS.md with all findings"""
        pass
    
    def generate_security_proposals(self, security_findings: List[SecurityFinding]) -> str:
        """Generate security remediation proposals"""
        pass
    
    def generate_executive_documentation(self, findings: AuditFindings, metrics: CodeMetrics) -> ExecutiveDocs:
        """Generate executive-level documentation"""
        pass
    
    def generate_validation_checklist(self, findings: AuditFindings) -> str:
        """Generate validation checklist"""
        pass
    
    def generate_env_example_template(self, env_vars: Set[str]) -> str:
        """Generate complete .env.example template"""
        pass
```

**Data Structures**:

```python
@dataclass
class AuditFindings:
    version_inconsistencies: List[Inconsistency]
    metric_inconsistencies: List[Inconsistency]
    security_findings: List[SecurityFinding]
    integrity_findings: List[IntegrityFinding]
    bug_status_findings: List[BugStatusFinding]
    untested_modules: List[UntestedModule]
    test_coverage_percentage: float
    dependencies: DependencyList
    timestamp: datetime

@dataclass
class ExecutiveDocs:
    estado_ejecutivo: str  # Content for ESTADO_EJECUTIVO.md
    tests_y_calidad: str   # Content for TESTS_Y_CALIDAD.md
    seguridad: str         # Content for SEGURIDAD.md
    pendientes: str        # Content for PENDIENTES.md
    changelog: str         # Content for CHANGELOG.md
```

### 8. Audit Orchestrator

**Responsabilidad**: Orquestar el pipeline completo de auditoría.

**Interface**:

```python
class AuditOrchestrator:
    """Orchestrates the complete audit pipeline"""
    
    def __init__(self, root_path: Path, status_doc_path: Path):
        self.scanner = FileSystemScanner()
        self.metrics_collector = MetricsCollector()
        self.security_scanner = SecurityScanner()
        self.coverage_analyzer = TestCoverageAnalyzer()
        self.integrity_validator = IntegrityValidator()
        self.comparator = Comparator()
        self.doc_generator = DocumentationGenerator()
    
    def run_audit(self) -> AuditFindings:
        """Execute complete audit pipeline"""
        pass
    
    def generate_reports(self, findings: AuditFindings) -> None:
        """Generate all documentation outputs"""
        pass
```

### Component Interaction Flow

```
AuditOrchestrator.run_audit()
    ↓
1. FileSystemScanner collects all files
    ↓
2. MetricsCollector extracts real metrics
    ↓
3. SecurityScanner identifies vulnerabilities
    ↓
4. TestCoverageAnalyzer analyzes test coverage
    ↓
5. IntegrityValidator checks references
    ↓
6. Comparator compares declared vs real
    ↓
7. AuditFindings aggregated
    ↓
AuditOrchestrator.generate_reports()
    ↓
8. DocumentationGenerator creates all outputs
```

---

## Data Models

### Core Data Models

```python
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Set
from enum import Enum

# Enums

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class FindingCategory(Enum):
    VERSION = "version"
    METRIC = "metric"
    SECURITY = "security"
    INTEGRITY = "integrity"
    BUG_STATUS = "bug_status"
    TEST_COVERAGE = "test_coverage"

class Language(Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"

# File Models

@dataclass
class SourceFile:
    path: Path
    language: Language
    content: str
    line_count: int
    
    def get_lines(self) -> List[str]:
        """Return file content as list of lines"""
        return self.content.splitlines()

@dataclass
class TestFile:
    path: Path
    language: Language
    content: str
    tested_modules: List[str]  # Module names this test file tests

@dataclass
class DocumentFile:
    path: Path
    content: str
    file_references: List[str]  # File paths mentioned in document
    
    def extract_references(self) -> List[str]:
        """Extract file path references from markdown"""
        pass

# Configuration Models

@dataclass
class ConfigFiles:
    package_json: Optional[Dict]
    requirements_txt: Optional[List[str]]
    env_example: Optional[Dict[str, str]]
    gitignore: Optional[List[str]]
    root_path: Path

# Metrics Models

@dataclass
class VersionMetrics:
    frontend_version: str
    python_packages: Dict[str, str]
    last_commit_date: datetime

@dataclass
class CodeMetrics:
    endpoints_count: int
    components_count: int
    test_files_count: int
    lines_of_code: int

@dataclass
class Dependency:
    name: str
    version: str
    version_type: str  # 'pinned' or 'range'
    package_manager: str  # 'npm' or 'pip'

@dataclass
class DependencyList:
    frontend: List[Dependency]
    backend: List[Dependency]

# Finding Models

@dataclass
class Inconsistency:
    metric_name: str
    declared_value: Any
    real_value: Any
    difference_percentage: Optional[float]
    file_path: Path
    line_number: int
    description: str
    severity: Severity

@dataclass
class SecurityFinding:
    category: str  # 'credential', 'ip_address', 'env_config', 'git_history'
    severity: Severity
    file_path: Path
    line_number: int
    matched_text: str
    context: str  # 3 lines before and after
    description: str
    recommended_action: str
    proposed_fix: Optional[str] = None
    env_var_name: Optional[str] = None  # Proposed env var name

@dataclass
class IntegrityFinding:
    finding_type: str  # 'missing_file', 'broken_import', 'broken_reference'
    file_path: Path
    line_number: int
    referenced_path: str
    exists: bool
    description: str

@dataclass
class BugStatusFinding:
    bug_id: str
    bug_doc_path: Path
    status_declared: str  # 'resolved', 'pending'
    status_verified: str  # 'resolved', 'pending', 'inconsistent'
    affected_files: List[Path]
    description: str

@dataclass
class UntestedModule:
    module_path: Path
    module_name: str
    coverage_status: str  # 'no_tests', 'partial', 'full'

# Aggregate Models

@dataclass
class TestCoverageMap:
    mappings: Dict[Path, List[Path]]  # source_file -> test_files
    untested_modules: List[UntestedModule]
    coverage_percentage: float

@dataclass
class TestConfiguration:
    has_pytest_ini: bool
    has_setup_cfg: bool
    has_coveragerc: bool
    config_paths: List[Path]

@dataclass
class AuditFindings:
    version_inconsistencies: List[Inconsistency]
    metric_inconsistencies: List[Inconsistency]
    security_findings: List[SecurityFinding]
    integrity_findings: List[IntegrityFinding]
    bug_status_findings: List[BugStatusFinding]
    test_coverage_map: TestCoverageMap
    dependencies: DependencyList
    timestamp: datetime
    
    def get_critical_findings(self) -> List[SecurityFinding]:
        """Return only critical severity findings"""
        return [f for f in self.security_findings if f.severity == Severity.CRITICAL]
    
    def get_findings_by_category(self, category: FindingCategory) -> List[Any]:
        """Return findings filtered by category"""
        pass
    
    def total_findings_count(self) -> int:
        """Return total count of all findings"""
        return (
            len(self.version_inconsistencies) +
            len(self.metric_inconsistencies) +
            len(self.security_findings) +
            len(self.integrity_findings) +
            len(self.bug_status_findings) +
            len(self.test_coverage_map.untested_modules)
        )

# Output Models

@dataclass
class ExecutiveDocs:
    estado_ejecutivo: str
    tests_y_calidad: str
    seguridad: str
    pendientes: str
    changelog: str

@dataclass
class ValidationChecklist:
    items: List[ChecklistItem]
    completion_percentage: float
    timestamp: datetime

@dataclass
class ChecklistItem:
    phase: str
    description: str
    completed: bool
    findings_count: int
    critical_issues_count: int
```

### Status Document Parser

Para extraer métricas declaradas del documento de estado:

```python
class StatusDocumentParser:
    """Parses the status document to extract declared metrics"""
    
    def parse_status_document(self, doc_path: Path) -> DeclaredMetrics:
        """Parse status document and extract declared metrics"""
        pass
    
    def extract_version_table(self, content: str) -> VersionMetrics:
        """Extract version information from markdown tables"""
        pass
    
    def extract_metrics_table(self, content: str) -> CodeMetrics:
        """Extract code metrics from markdown tables"""
        pass
    
    def extract_file_references(self, content: str) -> List[str]:
        """Extract all file path references"""
        pass

@dataclass
class DeclaredMetrics:
    versions: VersionMetrics
    code_metrics: CodeMetrics
    file_references: List[str]
```

---

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration Parsing Round Trip

*For any* valid package.json or requirements.txt file, parsing the file to extract versions/dependencies and then reconstructing the data structure should preserve all package names and version information.

**Validates: Requirements 1.1, 1.2, 12.1, 12.2**

### Property 2: File Counting Accuracy

*For any* directory structure, counting files matching a specific pattern (e.g., FastAPI routes, React components, test files) should return a count equal to the actual number of files matching that pattern in the directory tree.

**Validates: Requirements 2.1, 2.2, 2.3, 4.1, 4.3**

### Property 3: Exclusion Rules in Line Counting

*For any* file tree containing documentation files and node_modules directories, counting lines of code with exclusion rules should return a count that does not include any lines from excluded paths.

**Validates: Requirements 2.4**

### Property 4: Pattern Detection Completeness

*For any* source file containing credential patterns (password, secret, key, token, api_key, auth) or IP addresses, the security scanner should detect and record all occurrences with correct file path and line number.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 5: Gitignore Validation

*For any* .gitignore file content, checking if .env files are listed should return true if and only if the content contains a pattern matching .env files.

**Validates: Requirements 3.6**

### Property 6: Git History Verification

*For any* git log output, checking for committed .env files should return true if and only if the log contains entries for files matching .env patterns.

**Validates: Requirements 3.7, 11.5**

### Property 7: Severity Classification Consistency

*For any* security finding classified as a hardcoded credential, the severity level should be set to CRITICAL.

**Validates: Requirements 3.8**

### Property 8: Test-to-Module Mapping Accuracy

*For any* test file, extracting the source modules it tests (via import analysis) should return a list that includes all modules imported from the source directories.

**Validates: Requirements 4.2**

### Property 9: Untested Module Identification

*For any* set of source modules and test files, the untested modules should be exactly the set difference between all source modules and modules that have corresponding tests.

**Validates: Requirements 4.4**

### Property 10: Test Configuration Detection

*For any* directory structure, checking for test configuration files should return true for pytest.ini, setup.cfg, or .coveragerc if and only if those files exist in the directory.

**Validates: Requirements 4.5**

### Property 11: Test File Pattern Matching

*For any* directory structure, scanning for test files with patterns (*.test.ts, *.test.tsx, *.spec.ts, *.spec.tsx) should return all and only files whose names match those patterns.

**Validates: Requirements 4.6**

### Property 12: Coverage Percentage Calculation

*For any* set of modules and test coverage map, the coverage percentage should equal (modules_with_tests / total_modules) * 100.

**Validates: Requirements 4.8**

### Property 13: Bug Fix Document Listing

*For any* directory containing bug fix documents, scanning the directory should return all markdown files in that directory.

**Validates: Requirements 5.1**

### Property 14: Affected File Extraction

*For any* bug fix document containing file path references, extracting affected files should return all file paths mentioned in the document.

**Validates: Requirements 5.2**

### Property 15: Conditional Inconsistency Recording

*For any* bug fix marked as resolved where the fix is determined to be absent, an inconsistency should be recorded with the bug ID and affected file paths.

**Validates: Requirements 5.4**

### Property 16: Report Section Completeness

*For any* audit findings, the generated report should contain all required sections: version inconsistencies, security findings, test coverage, bug status, and metric discrepancies.

**Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6**

### Property 17: Finding Structure Completeness

*For any* finding in the generated report, it should include all required fields: category, severity, file path, line number, description, and recommended action.

**Validates: Requirements 6.7**

### Property 18: Executive Summary Aggregation

*For any* set of audit findings, the executive summary should contain total counts for each finding category that match the actual counts in the detailed findings.

**Validates: Requirements 6.8**

### Property 19: Security Proposal Generation

*For any* hardcoded credential finding, a security proposal should be generated that includes an environment variable name, before/after code snippets, and recommended action.

**Validates: Requirements 7.1, 7.6**

### Property 20: Environment Variable Naming Convention

*For any* proposed environment variable name, it should follow UPPER_SNAKE_CASE convention (all uppercase letters with underscores separating words).

**Validates: Requirements 7.2**

### Property 21: Environment Variable Completeness Check

*For any* set of environment variables used in source code and variables declared in .env.example, the missing variables should be exactly the set difference between used variables and declared variables.

**Validates: Requirements 7.3, 11.2, 11.3, 11.4**

### Property 22: Template Generation Completeness

*For any* set of missing environment variables, the generated .env.example template should contain entries for all missing variables with placeholder values.

**Validates: Requirements 7.4**

### Property 23: Read-Only Guarantee

*For any* audit execution, no source code files should be modified (file modification timestamps should remain unchanged).

**Validates: Requirements 7.5**

### Property 24: Proposal Prioritization

*For any* list of security proposals containing findings with different severity levels, critical findings should appear before high, high before medium, and medium before low in the ordered list.

**Validates: Requirements 7.7**

### Property 25: Technical Documentation Code References

*For any* generated technical documentation, it should contain at least one code reference (file path or code block).

**Validates: Requirements 8.7**

### Property 26: Cross-Reference Presence

*For any* set of generated executive documentation files, each document should contain at least one reference to another related document.

**Validates: Requirements 8.8**

### Property 27: File Reference Extraction

*For any* markdown document, extracting file path references should return all strings that match file path patterns (e.g., paths with extensions, paths with slashes).

**Validates: Requirements 9.1**

### Property 28: File Existence Validation

*For any* file path, verifying its existence should return true if and only if the file exists in the filesystem at that path.

**Validates: Requirements 9.2**

### Property 29: Import Validation Accuracy

*For any* Python or TypeScript file, validating imports should identify as broken any import that references a non-existent module path.

**Validates: Requirements 9.4, 9.5**

### Property 30: Checklist Item Structure

*For any* checklist item, it should contain all required fields: phase name, completed status, findings count, and critical issues count.

**Validates: Requirements 10.3**

### Property 31: Completion Percentage Calculation

*For any* validation checklist, the completion percentage should equal (completed_items / total_items) * 100.

**Validates: Requirements 10.5**

### Property 32: Phase Timestamp Presence

*For any* completed audit phase in the checklist, it should have an associated timestamp indicating when it was completed.

**Validates: Requirements 10.6**

### Property 33: Environment Variable Extraction

*For any* .env.example file content, parsing it should extract all variable names (keys before the = sign).

**Validates: Requirements 11.1**

### Property 34: Placeholder Value Validation

*For any* sensitive environment variable in .env.example (containing keywords like PASSWORD, SECRET, KEY, TOKEN), its value should be a placeholder (e.g., "your_password_here", "CHANGE_ME") and not a real credential.

**Validates: Requirements 11.6**

### Property 35: Dependency Version Classification

*For any* dependency version string, classifying it should return "pinned" if it's an exact version (e.g., "1.2.3") and "range" if it contains operators (e.g., "^1.2.3", ">=1.0.0").

**Validates: Requirements 12.3**

### Property 36: Dependency List Completeness

*For any* package.json and requirements.txt, the extracted dependency list should contain all packages listed in both files.

**Validates: Requirements 12.4**

### Property 37: Vulnerability Note Cross-Reference

*For any* dependency mentioned in the Status_Document as having a known vulnerability, the dependencies report should include a note about that vulnerability.

**Validates: Requirements 12.5**

### Property 38: Metrics Comparison Consistency

*For any* pair of declared and real metrics, if the difference percentage is greater than 10%, an inconsistency should be recorded.

**Validates: Requirements 1.4, 2.5, 2.6**

### Property 39: Version Comparison Recording

*For any* version comparison performed, it should be recorded in the audit report with both declared and real values.

**Validates: Requirements 1.6**

---

## Error Handling

### Error Categories

1. **File System Errors**
   - File not found
   - Permission denied
   - Invalid path
   - Strategy: Log error, skip file, continue audit, report in findings

2. **Parsing Errors**
   - Invalid JSON
   - Malformed requirements.txt
   - Invalid markdown structure
   - Strategy: Log error, use partial data if possible, report parsing failure in findings

3. **Git Errors**
   - Not a git repository
   - Git command failed
   - Strategy: Log warning, skip git-based checks, note in report

4. **Pattern Matching Errors**
   - Regex compilation failure
   - Strategy: Log error, skip that pattern, continue with other patterns

5. **Comparison Errors**
   - Missing declared metrics in status document
   - Type mismatch in comparison
   - Strategy: Record as inconsistency, continue audit

### Error Handling Principles

1. **Fail Gracefully**: Never crash the entire audit due to a single file error
2. **Continue on Error**: Skip problematic files and continue with remaining files
3. **Report All Errors**: Include all errors encountered in the audit report
4. **Provide Context**: Include file path, line number, and error message for all errors
5. **Partial Results**: Return partial results even if some checks fail

### Error Reporting

All errors should be included in a dedicated section of the audit report:

```markdown
## Errors Encountered During Audit

| Error Type | File Path | Description | Impact |
|------------|-----------|-------------|--------|
| Parse Error | config.json | Invalid JSON syntax | Skipped configuration check |
| File Not Found | docs/missing.md | Referenced file does not exist | Recorded as integrity finding |
```

---

## Testing Strategy

### Dual Testing Approach

This system requires both unit tests and property-based tests for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs

Both approaches are complementary and necessary. Unit tests catch concrete bugs and verify specific behaviors, while property tests verify general correctness across a wide range of inputs.

### Unit Testing

**Framework**: pytest

**Focus Areas**:
- Specific examples of credential detection (e.g., test with known hardcoded password)
- Edge cases (empty files, files with no imports, malformed JSON)
- Error conditions (file not found, permission denied, invalid regex)
- Integration between components (e.g., scanner → collector → comparator)

**Example Unit Tests**:
- Test parsing a specific package.json with known structure
- Test detecting a specific hardcoded password pattern
- Test handling an empty requirements.txt file
- Test generating a report with zero findings
- Test error handling when git is not available

**Coverage Target**: Aim for 80%+ line coverage on core logic

### Property-Based Testing

**Framework**: Hypothesis (Python)

**Configuration**: Minimum 100 iterations per property test

**Tagging**: Each property test must include a comment referencing the design property:
```python
# Feature: auditoria-documentacion-ricoh-suite, Property 1: Configuration Parsing Round Trip
@given(st.dictionaries(st.text(), st.text()))
def test_package_json_parsing_round_trip(package_data):
    ...
```

**Focus Areas**:
- Configuration parsing (Properties 1, 33, 36)
- File counting (Property 2)
- Pattern detection (Property 4)
- Comparison logic (Property 38)
- Calculation accuracy (Properties 12, 31)
- Classification logic (Properties 7, 35)
- Set operations (Properties 9, 21)

**Generator Strategies**:

1. **File Content Generators**:
   - Generate valid package.json structures
   - Generate valid requirements.txt lines
   - Generate source code with various patterns
   - Generate markdown with file references

2. **Path Generators**:
   - Generate valid file paths
   - Generate directory structures

3. **Metrics Generators**:
   - Generate version numbers
   - Generate metric values (counts, percentages)

4. **Finding Generators**:
   - Generate security findings with various severities
   - Generate inconsistencies with various difference percentages

**Example Property Tests**:

```python
# Property 1: Configuration Parsing Round Trip
@given(st.dictionaries(
    keys=st.text(min_size=1, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    values=st.text(min_size=1)
))
def test_package_json_parsing_preserves_data(dependencies):
    """For any valid dependencies dict, parsing should preserve all data"""
    package_json = {"dependencies": dependencies}
    parsed = MetricsCollector().extract_versions(package_json)
    # Verify all dependencies are preserved
    assert len(parsed.frontend_dependencies) == len(dependencies)

# Property 2: File Counting Accuracy
@given(st.lists(st.text(min_size=1), min_size=0, max_size=100))
def test_file_counting_matches_actual_count(file_names):
    """For any list of file names, counting should match actual count"""
    # Create temporary directory structure
    # Count files
    # Verify count matches len(file_names)
    pass

# Property 38: Metrics Comparison Consistency
@given(
    st.floats(min_value=0, max_value=10000),
    st.floats(min_value=0, max_value=10000)
)
def test_inconsistency_recorded_when_difference_exceeds_threshold(declared, real):
    """For any metric pair, inconsistency recorded iff difference > 10%"""
    comparator = Comparator()
    inconsistencies = comparator.compare_metrics(declared, real)
    
    diff_pct = abs(declared - real) / declared * 100 if declared > 0 else 0
    
    if diff_pct > 10:
        assert len(inconsistencies) > 0
    else:
        assert len(inconsistencies) == 0
```

### Test Organization

```
tests/
├── unit/
│   ├── test_file_system_scanner.py
│   ├── test_metrics_collector.py
│   ├── test_security_scanner.py
│   ├── test_coverage_analyzer.py
│   ├── test_integrity_validator.py
│   ├── test_comparator.py
│   ├── test_documentation_generator.py
│   └── test_audit_orchestrator.py
├── property/
│   ├── test_properties_parsing.py
│   ├── test_properties_counting.py
│   ├── test_properties_security.py
│   ├── test_properties_comparison.py
│   └── test_properties_generation.py
├── integration/
│   └── test_full_audit_pipeline.py
└── fixtures/
    ├── sample_package_json.py
    ├── sample_requirements_txt.py
    ├── sample_source_files.py
    └── sample_status_document.py
```

### Testing Execution

Run tests with:
```bash
# Run all tests
pytest tests/

# Run only unit tests
pytest tests/unit/

# Run only property tests
pytest tests/property/

# Run with coverage
pytest --cov=audit_system --cov-report=html tests/
```

### Continuous Testing

- Run tests before committing changes
- Run full test suite in CI/CD pipeline
- Monitor property test failures for edge cases
- Update generators when new patterns are discovered

---

## Implementation Notes

### Phase 1: Core Infrastructure

1. Implement data models (dataclasses)
2. Implement FileSystemScanner with basic file reading
3. Implement basic pattern matching in SecurityScanner
4. Write unit tests for core components

### Phase 2: Metrics and Analysis

1. Implement MetricsCollector with all extraction methods
2. Implement TestCoverageAnalyzer
3. Implement Comparator
4. Write property tests for metrics and comparison logic

### Phase 3: Validation and Integrity

1. Implement IntegrityValidator
2. Implement StatusDocumentParser
3. Write property tests for validation logic

### Phase 4: Reporting

1. Implement DocumentationGenerator
2. Implement report templates
3. Write tests for report generation

### Phase 5: Orchestration

1. Implement AuditOrchestrator
2. Implement CLI interface
3. Write integration tests
4. End-to-end testing

### Execution Model

The audit system will be executed as a standalone Python script:

```bash
python -m audit_system.main --root . --status-doc docs/ESTADO_PROYECTO_2026_03_30.md
```

**CLI Options**:
- `--root`: Root directory of project (default: current directory)
- `--status-doc`: Path to status document to audit against
- `--output-dir`: Directory for generated reports (default: docs/)
- `--skip-git`: Skip git history checks
- `--verbose`: Enable verbose logging

### Output Files

After execution, the system will generate:

1. `docs/AUDITORIA_HALLAZGOS.md` - Consolidated findings report
2. `docs/PROPUESTAS_SEGURIDAD.md` - Security remediation proposals
3. `docs/ESTADO_EJECUTIVO.md` - Executive summary
4. `docs/TESTS_Y_CALIDAD.md` - Test coverage and quality metrics
5. `docs/SEGURIDAD.md` - Security architecture and checklist
6. `docs/PENDIENTES.md` - Pending tasks and issues
7. `docs/CHANGELOG.md` - Version history
8. `docs/CHECKLIST_VALIDACION.md` - Validation checklist
9. `.env.example.proposed` - Proposed complete .env.example (if needed)

### Performance Considerations

- Use parallel processing for scanning large numbers of files
- Cache parsed file contents to avoid re-reading
- Use generators for large file lists to reduce memory usage
- Limit git history queries to recent commits (e.g., last 1000 commits)

### Extensibility Points

1. **New Pattern Types**: Add new regex patterns to SecurityScanner.CREDENTIAL_PATTERNS
2. **New Metrics**: Add new extraction methods to MetricsCollector
3. **New Report Sections**: Add new generation methods to DocumentationGenerator
4. **New Validators**: Add new validation methods to IntegrityValidator

---

## Appendix: Pattern Definitions

### Credential Patterns

```python
CREDENTIAL_PATTERNS = {
    'password': r'password\s*[=:]\s*["\']([^"\']+)["\']',
    'secret': r'secret\s*[=:]\s*["\']([^"\']+)["\']',
    'api_key': r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']',
    'token': r'token\s*[=:]\s*["\']([^"\']+)["\']',
    'auth': r'auth\s*[=:]\s*["\']([^"\']+)["\']',
}
```

### File Path Patterns

```python
FILE_PATH_PATTERNS = {
    'absolute': r'/[a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+',
    'relative': r'[a-zA-Z0-9_.-]+/[a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+',
    'markdown_link': r'\[.*?\]\(([^)]+)\)',
    'code_block': r'`([^`]+\.[a-zA-Z0-9]+)`',
}
```

### Import Patterns

```python
IMPORT_PATTERNS = {
    'python_import': r'^\s*import\s+([a-zA-Z0-9_\.]+)',
    'python_from': r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import',
    'typescript_import': r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
    'typescript_require': r'require\(["\']([^"\']+)["\']\)',
}
```

### Test File Patterns

```python
TEST_FILE_PATTERNS = {
    'pytest': r'test_.*\.py$',
    'vitest': r'.*\.(test|spec)\.(ts|tsx|js|jsx)$',
}
```

### FastAPI Route Patterns

```python
FASTAPI_ROUTE_PATTERNS = [
    r'@router\.(get|post|put|delete|patch)',
    r'@app\.(get|post|put|delete|patch)',
]
```

### React Component Patterns

```python
REACT_COMPONENT_PATTERNS = [
    r'export\s+(default\s+)?function\s+[A-Z][a-zA-Z0-9]*',
    r'export\s+const\s+[A-Z][a-zA-Z0-9]*\s*[=:]\s*\(',
    r'const\s+[A-Z][a-zA-Z0-9]*\s*[=:]\s*\(\s*\)\s*=>\s*{',
]
```

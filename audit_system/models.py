"""
Modelos de datos para el sistema de auditoría.

Define las estructuras de datos utilizadas para representar la estructura del proyecto,
hallazgos, métricas y resultados del análisis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Any


class Severity(Enum):
    """Niveles de severidad de hallazgos."""
    CRITICO = "Crítico"
    ALTO = "Alto"
    MEDIO = "Medio"
    BAJO = "Bajo"
    
    def get_emoji(self) -> str:
        """Retorna emoji para representación visual."""
        return {
            Severity.CRITICO: "🔴",
            Severity.ALTO: "🟠",
            Severity.MEDIO: "🟡",
            Severity.BAJO: "🟢"
        }[self]
    
    def get_weight(self) -> int:
        """Retorna peso numérico para cálculos."""
        return {
            Severity.CRITICO: 4,
            Severity.ALTO: 3,
            Severity.MEDIO: 2,
            Severity.BAJO: 1
        }[self]


@dataclass
class Vulnerability:
    """Vulnerabilidad de seguridad."""
    cve_id: str
    cvss_score: float
    description: str
    fixed_in_version: Optional[str] = None


@dataclass
class Dependency:
    """Dependencia de software."""
    name: str
    current_version: str
    latest_version: str
    is_outdated: bool
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    ecosystem: str = "python"  # 'python' | 'npm'
    
    def has_critical_vulnerability(self) -> bool:
        """Verifica si tiene vulnerabilidad crítica (CVSS ≥9.0)."""
        return any(v.cvss_score >= 9.0 for v in self.vulnerabilities)


@dataclass
class SourceFile:
    """Archivo de código fuente."""
    path: str
    language: str  # 'python' | 'typescript'
    lines_of_code: int
    is_large: bool  # True si >300 líneas
    content: str
    ast_tree: Optional[Any] = None  # AST parseado
    
    def get_functions(self) -> List[Any]:
        """Extrae todas las funciones del archivo."""
        # Implementación en componentes específicos
        pass
    
    def get_classes(self) -> List[Any]:
        """Extrae todas las clases del archivo."""
        # Implementación en componentes específicos
        pass


@dataclass
class PythonFile(SourceFile):
    """Archivo Python específico."""
    has_type_hints: bool = False
    has_docstrings: bool = False
    imports: List[str] = field(default_factory=list)


@dataclass
class TypeScriptFile(SourceFile):
    """Archivo TypeScript específico."""
    is_component: bool = False  # True si es componente React
    has_tests: bool = False
    exports: List[str] = field(default_factory=list)


@dataclass
class CodeMetrics:
    """Métricas del código."""
    # Backend
    backend_total_lines: int = 0
    backend_total_files: int = 0
    backend_large_files: int = 0
    backend_long_functions: int = 0
    backend_dependencies_count: int = 0
    
    # Frontend
    frontend_total_lines: int = 0
    frontend_total_files: int = 0
    frontend_large_components: int = 0
    frontend_dependencies_count: int = 0
    
    # General
    total_outdated_dependencies: int = 0
    total_vulnerabilities: int = 0
    
    def to_table(self) -> str:
        """Convierte métricas a tabla markdown."""
        return f"""
| Métrica | Backend | Frontend |
|---------|---------|----------|
| Total líneas | {self.backend_total_lines} | {self.frontend_total_lines} |
| Total archivos | {self.backend_total_files} | {self.frontend_total_files} |
| Archivos grandes | {self.backend_large_files} | {self.frontend_large_components} |
| Funciones largas | {self.backend_long_functions} | - |
| Dependencias | {self.backend_dependencies_count} | {self.frontend_dependencies_count} |

**Dependencias:**
- Desactualizadas: {self.total_outdated_dependencies}
- Con vulnerabilidades: {self.total_vulnerabilities}
"""


@dataclass
class ProjectStructure:
    """Estructura del proyecto Ricoh Suite."""
    root_path: str
    backend_files: List[PythonFile] = field(default_factory=list)
    frontend_files: List[TypeScriptFile] = field(default_factory=list)
    backend_dependencies: List[Dependency] = field(default_factory=list)
    frontend_dependencies: List[Dependency] = field(default_factory=list)
    metrics: Optional[CodeMetrics] = None
    
    def get_all_files(self) -> List[SourceFile]:
        """Retorna todos los archivos de código."""
        return self.backend_files + self.frontend_files


@dataclass
class Finding:
    """Hallazgo de auditoría."""
    id: str
    category: str  # 'performance' | 'quality' | 'security' | 'architecture'
    subcategory: str  # 'n_plus_one' | 'long_function' | 'hardcoded_secret' | etc.
    severity: Severity
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    impact_score: float = 0.0
    effort_score: float = 0.0
    priority_ratio: float = 0.0  # impact_score / effort_score
    
    def to_markdown(self) -> str:
        """Convierte el hallazgo a formato markdown."""
        emoji = self.severity.get_emoji()
        md = f"### {emoji} {self.title}\n\n"
        md += f"**Severidad:** {self.severity.value}\n"
        md += f"**Categoría:** {self.category} / {self.subcategory}\n"
        md += f"**Ubicación:** `{self.file_path}`"
        
        if self.line_number:
            md += f" (línea {self.line_number})"
        md += "\n\n"
        
        md += f"**Descripción:** {self.description}\n\n"
        
        if self.code_snippet:
            md += f"**Código:**\n```\n{self.code_snippet}\n```\n\n"
        
        if self.recommendation:
            md += f"**Recomendación:** {self.recommendation}\n\n"
        
        md += f"**Impacto:** {self.impact_score:.1f} | **Esfuerzo:** {self.effort_score:.1f} | **Prioridad:** {self.priority_ratio:.2f}\n"
        
        return md


@dataclass
class PriorityMatrix:
    """Matriz de priorización."""
    high_impact_low_effort: List[Finding] = field(default_factory=list)  # Quick wins
    high_impact_high_effort: List[Finding] = field(default_factory=list)  # Major projects
    low_impact_low_effort: List[Finding] = field(default_factory=list)   # Fill-ins
    low_impact_high_effort: List[Finding] = field(default_factory=list)  # Avoid
    
    def to_markdown(self) -> str:
        """Genera representación markdown de la matriz."""
        md = "## Matriz de Priorización (Impacto vs Esfuerzo)\n\n"
        
        md += "### 🎯 Quick Wins (Alto Impacto, Bajo Esfuerzo)\n"
        md += f"Total: {len(self.high_impact_low_effort)} hallazgos\n\n"
        
        md += "### 🚀 Major Projects (Alto Impacto, Alto Esfuerzo)\n"
        md += f"Total: {len(self.high_impact_high_effort)} hallazgos\n\n"
        
        md += "### ✅ Fill-ins (Bajo Impacto, Bajo Esfuerzo)\n"
        md += f"Total: {len(self.low_impact_low_effort)} hallazgos\n\n"
        
        md += "### ⚠️ Avoid (Bajo Impacto, Alto Esfuerzo)\n"
        md += f"Total: {len(self.low_impact_high_effort)} hallazgos\n\n"
        
        return md


@dataclass
class RefactorPlan:
    """Plan de refactor temporal."""
    week_1: List[Finding] = field(default_factory=list)  # Crítico
    week_2: List[Finding] = field(default_factory=list)  # Alto + Medio
    week_3: List[Finding] = field(default_factory=list)  # Medio + Bajo
    week_4: List[Finding] = field(default_factory=list)  # Bajo
    
    def calculate_weekly_effort(self, week: int) -> float:
        """Calcula horas de esfuerzo estimadas para una semana."""
        week_findings = getattr(self, f"week_{week}", [])
        return sum(f.effort_score for f in week_findings)
    
    def balance_workload(self) -> None:
        """Balancea carga entre Backend y Frontend por semana."""
        # Implementación en componentes específicos
        pass
    
    def to_markdown(self) -> str:
        """Genera plan en formato markdown."""
        md = "## Plan de Refactor (4 Semanas)\n\n"
        
        for week in range(1, 5):
            week_findings = getattr(self, f"week_{week}")
            effort = self.calculate_weekly_effort(week)
            
            md += f"### Semana {week}\n"
            md += f"**Esfuerzo estimado:** {effort:.1f} horas\n"
            md += f"**Hallazgos:** {len(week_findings)}\n\n"
        
        return md


@dataclass
class AnalysisResult:
    """Resultado completo de la auditoría."""
    structure: ProjectStructure
    findings: List[Finding] = field(default_factory=list)
    top_10: List[Finding] = field(default_factory=list)
    priority_matrix: Optional[PriorityMatrix] = None
    dependencies: List[Dependency] = field(default_factory=list)
    metrics: Optional[CodeMetrics] = None
    refactor_plan: Optional[RefactorPlan] = None
    generated_at: datetime = field(default_factory=datetime.now)
    
    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        """Filtra hallazgos por severidad."""
        return [f for f in self.findings if f.severity == severity]
    
    def get_findings_by_category(self, category: str) -> List[Finding]:
        """Filtra hallazgos por categoría."""
        return [f for f in self.findings if f.category == category]

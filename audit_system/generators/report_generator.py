"""
Generador de reportes markdown para auditoría de código.

Genera un reporte completo en formato markdown con todas las secciones requeridas:
resumen ejecutivo, Top 10, hallazgos por severidad, métricas, matriz de priorización,
y plan de refactor de 4 semanas.
"""

from typing import List, Dict
from datetime import datetime
from audit_system.models import (
    Finding, 
    Severity, 
    AnalysisResult, 
    PriorityMatrix, 
    RefactorPlan,
    CodeMetrics
)
from audit_system.config import get_config


class ReportGenerator:
    """Genera reportes markdown estructurados de auditoría."""
    
    def __init__(self):
        """Inicializa el generador con configuración."""
        self.config = get_config()
    
    def generate_report(self, analysis_result: AnalysisResult) -> str:
        """
        Genera el reporte completo en formato markdown.
        
        Args:
            analysis_result: Resultado completo de la auditoría
            
        Returns:
            Reporte en formato markdown
        """
        sections = []
        
        # Encabezado y metadata
        sections.append(self._generate_header(analysis_result))
        
        # Tabla de contenidos
        sections.append(self.generate_table_of_contents())
        
        # Resumen ejecutivo
        sections.append(self.generate_executive_summary(analysis_result.findings))
        
        # Top 10
        sections.append(self.generate_top_10(analysis_result.top_10))
        
        # Métricas
        if analysis_result.metrics:
            sections.append(self.generate_metrics_section(analysis_result.metrics))
        
        # Matriz de priorización
        if analysis_result.priority_matrix:
            sections.append(self.generate_priority_matrix(analysis_result.priority_matrix))
        
        # Hallazgos por severidad
        sections.append(self.generate_findings_by_severity(analysis_result.findings))
        
        # Plan de refactor
        if analysis_result.refactor_plan:
            sections.append(self.generate_refactor_plan(analysis_result.refactor_plan))
        
        return "\n\n".join(sections)
    
    def _generate_header(self, analysis_result: AnalysisResult) -> str:
        """
        Genera encabezado del reporte con metadata.
        
        Args:
            analysis_result: Resultado de la auditoría
            
        Returns:
            Encabezado en markdown
        """
        header = "# Reporte de Optimización - Ricoh Suite\n\n"
        header += f"**Fecha de generación:** {analysis_result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"**Proyecto:** {analysis_result.structure.root_path}\n"
        header += f"**Total de hallazgos:** {len(analysis_result.findings)}\n"
        
        return header
    
    def generate_table_of_contents(self) -> str:
        """
        Genera tabla de contenidos con enlaces a secciones.
        
        Returns:
            Tabla de contenidos en markdown
        """
        toc = "## Tabla de Contenidos\n\n"
        toc += "1. [Resumen Ejecutivo](#resumen-ejecutivo)\n"
        toc += "2. [Top 10 Mejoras Prioritarias](#top-10-mejoras-prioritarias)\n"
        toc += "3. [Métricas del Código](#métricas-del-código)\n"
        toc += "4. [Matriz de Priorización](#matriz-de-priorización)\n"
        toc += "5. [Hallazgos por Severidad](#hallazgos-por-severidad)\n"
        toc += "   - [🔴 Crítico](#-crítico)\n"
        toc += "   - [🟠 Alto](#-alto)\n"
        toc += "   - [🟡 Medio](#-medio)\n"
        toc += "   - [🟢 Bajo](#-bajo)\n"
        toc += "6. [Plan de Refactor (4 Semanas)](#plan-de-refactor-4-semanas)\n"
        
        return toc
    
    def generate_executive_summary(self, findings: List[Finding]) -> str:
        """
        Genera resumen ejecutivo con tabla de severidades.
        
        Args:
            findings: Lista de hallazgos
            
        Returns:
            Resumen ejecutivo en markdown
        """
        summary = "## Resumen Ejecutivo\n\n"
        
        # Contar por severidad
        severity_counts = {
            Severity.CRITICO: 0,
            Severity.ALTO: 0,
            Severity.MEDIO: 0,
            Severity.BAJO: 0
        }
        
        for finding in findings:
            severity_counts[finding.severity] += 1
        
        # Tabla de severidades
        summary += "### Distribución por Severidad\n\n"
        summary += "| Severidad | Cantidad | Emoji |\n"
        summary += "|-----------|----------|-------|\n"
        
        for severity in [Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]:
            emoji = severity.get_emoji()
            count = severity_counts[severity]
            summary += f"| {severity.value} | {count} | {emoji} |\n"
        
        summary += f"\n**Total de hallazgos:** {len(findings)}\n"
        
        # Resumen por categoría
        category_counts: Dict[str, int] = {}
        for finding in findings:
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
        
        summary += "\n### Distribución por Categoría\n\n"
        summary += "| Categoría | Cantidad |\n"
        summary += "|-----------|----------|\n"
        
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {category.title()} | {count} |\n"
        
        return summary
    
    def generate_top_10(self, top_findings: List[Finding]) -> str:
        """
        Genera sección Top 10 con mejoras de mayor impacto.
        
        Args:
            top_findings: Lista de los 10 hallazgos prioritarios
            
        Returns:
            Sección Top 10 en markdown
        """
        section = "## Top 10 Mejoras Prioritarias\n\n"
        section += "Las siguientes mejoras ofrecen el mejor ratio impacto/esfuerzo:\n\n"
        
        for i, finding in enumerate(top_findings[:10], 1):
            emoji = finding.severity.get_emoji()
            section += f"### {i}. {emoji} {finding.title}\n\n"
            section += f"**Severidad:** {finding.severity.value}  \n"
            section += f"**Categoría:** {finding.category} / {finding.subcategory}  \n"
            section += f"**Ubicación:** [`{finding.file_path}`]({finding.file_path})"
            
            if finding.line_number:
                section += f"#L{finding.line_number}"
            section += "  \n"
            
            section += f"**Ratio Prioridad:** {finding.priority_ratio:.2f}  \n"
            section += f"**Impacto:** {finding.impact_score:.1f} | **Esfuerzo:** {finding.effort_score:.1f}\n\n"
            
            section += f"**Descripción:** {finding.description}\n\n"
            
            if finding.code_snippet:
                section += "**Código:**\n"
                section += f"```python\n{finding.code_snippet}\n```\n\n"
            
            if finding.recommendation:
                section += f"**Recomendación:** {finding.recommendation}\n\n"
            
            section += "---\n\n"
        
        return section
    
    def generate_findings_by_severity(self, findings: List[Finding]) -> str:
        """
        Genera hallazgos organizados por severidad.
        
        Args:
            findings: Lista de hallazgos
            
        Returns:
            Sección de hallazgos por severidad en markdown
        """
        section = "## Hallazgos por Severidad\n\n"
        
        for severity in [Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]:
            emoji = severity.get_emoji()
            severity_findings = [f for f in findings if f.severity == severity]
            
            section += f"### {emoji} {severity.value}\n\n"
            section += f"**Total:** {len(severity_findings)} hallazgos\n\n"
            
            if not severity_findings:
                section += "*No se encontraron hallazgos de esta severidad.*\n\n"
                continue
            
            # Agrupar por categoría
            by_category: Dict[str, List[Finding]] = {}
            for finding in severity_findings:
                if finding.category not in by_category:
                    by_category[finding.category] = []
                by_category[finding.category].append(finding)
            
            for category, category_findings in sorted(by_category.items()):
                section += f"#### {category.title()}\n\n"
                
                for finding in category_findings:
                    section += f"**{finding.title}**  \n"
                    section += f"*Ubicación:* [`{finding.file_path}`]({finding.file_path})"
                    
                    if finding.line_number:
                        section += f"#L{finding.line_number}"
                    section += "  \n"
                    
                    section += f"*Descripción:* {finding.description}  \n"
                    
                    if finding.recommendation:
                        section += f"*Recomendación:* {finding.recommendation}  \n"
                    
                    section += "\n"
                
                section += "\n"
        
        return section
    
    def generate_metrics_section(self, metrics: CodeMetrics) -> str:
        """
        Genera sección de métricas cuantitativas.
        
        Args:
            metrics: Métricas del código
            
        Returns:
            Sección de métricas en markdown
        """
        section = "## Métricas del Código\n\n"
        section += "### Métricas Generales\n\n"
        
        section += "| Métrica | Backend | Frontend |\n"
        section += "|---------|---------|----------|\n"
        section += f"| Total líneas | {metrics.backend_total_lines:,} | {metrics.frontend_total_lines:,} |\n"
        section += f"| Total archivos | {metrics.backend_total_files} | {metrics.frontend_total_files} |\n"
        section += f"| Archivos grandes (>300 líneas) | {metrics.backend_large_files} | {metrics.frontend_large_components} |\n"
        section += f"| Funciones largas (>50 líneas) | {metrics.backend_long_functions} | - |\n"
        section += f"| Dependencias | {metrics.backend_dependencies_count} | {metrics.frontend_dependencies_count} |\n"
        
        section += "\n### Métricas de Dependencias\n\n"
        section += "| Métrica | Cantidad |\n"
        section += "|---------|----------|\n"
        section += f"| Dependencias desactualizadas | {metrics.total_outdated_dependencies} |\n"
        section += f"| Dependencias con vulnerabilidades | {metrics.total_vulnerabilities} |\n"
        
        return section
    
    def generate_priority_matrix(self, matrix: PriorityMatrix) -> str:
        """
        Genera matriz impacto/esfuerzo.
        
        Args:
            matrix: Matriz de priorización
            
        Returns:
            Sección de matriz en markdown
        """
        section = "## Matriz de Priorización\n\n"
        section += "Clasificación de hallazgos según impacto y esfuerzo:\n\n"
        
        section += "```\n"
        section += "                    IMPACTO\n"
        section += "                      ↑\n"
        section += "         Alto    |         |\n"
        section += "                 |  Major  |  Quick  \n"
        section += "                 | Projects|  Wins   \n"
        section += "                 |    🚀   |   🎯    \n"
        section += "    ─────────────┼─────────┼─────────→ ESFUERZO\n"
        section += "                 |  Avoid  | Fill-ins\n"
        section += "                 |    ⚠️    |   ✅    \n"
        section += "         Bajo    |         |\n"
        section += "                      ↓\n"
        section += "```\n\n"
        
        section += f"### 🎯 Quick Wins (Alto Impacto, Bajo Esfuerzo)\n\n"
        section += f"**Total:** {len(matrix.high_impact_low_effort)} hallazgos\n\n"
        section += "Estas mejoras ofrecen el mayor retorno de inversión:\n\n"
        
        for finding in matrix.high_impact_low_effort[:5]:
            emoji = finding.severity.get_emoji()
            section += f"- {emoji} **{finding.title}** - `{finding.file_path}`\n"
        
        if len(matrix.high_impact_low_effort) > 5:
            section += f"\n*...y {len(matrix.high_impact_low_effort) - 5} más*\n"
        
        section += f"\n### 🚀 Major Projects (Alto Impacto, Alto Esfuerzo)\n\n"
        section += f"**Total:** {len(matrix.high_impact_high_effort)} hallazgos\n\n"
        section += "Proyectos importantes que requieren planificación:\n\n"
        
        for finding in matrix.high_impact_high_effort[:5]:
            emoji = finding.severity.get_emoji()
            section += f"- {emoji} **{finding.title}** - `{finding.file_path}`\n"
        
        if len(matrix.high_impact_high_effort) > 5:
            section += f"\n*...y {len(matrix.high_impact_high_effort) - 5} más*\n"
        
        section += f"\n### ✅ Fill-ins (Bajo Impacto, Bajo Esfuerzo)\n\n"
        section += f"**Total:** {len(matrix.low_impact_low_effort)} hallazgos\n\n"
        section += "Mejoras rápidas para tiempo libre:\n\n"
        
        for finding in matrix.low_impact_low_effort[:3]:
            emoji = finding.severity.get_emoji()
            section += f"- {emoji} **{finding.title}** - `{finding.file_path}`\n"
        
        if len(matrix.low_impact_low_effort) > 3:
            section += f"\n*...y {len(matrix.low_impact_low_effort) - 3} más*\n"
        
        section += f"\n### ⚠️ Avoid (Bajo Impacto, Alto Esfuerzo)\n\n"
        section += f"**Total:** {len(matrix.low_impact_high_effort)} hallazgos\n\n"
        section += "Considerar cuidadosamente antes de abordar.\n"
        
        return section
    
    def generate_refactor_plan(self, plan: RefactorPlan) -> str:
        """
        Genera plan de refactor de 4 semanas.
        
        Args:
            plan: Plan de refactor
            
        Returns:
            Sección de plan en markdown
        """
        section = "## Plan de Refactor (4 Semanas)\n\n"
        section += "Distribución sugerida de hallazgos por semana:\n\n"
        
        for week in range(1, 5):
            week_findings = getattr(plan, f"week_{week}")
            effort = plan.calculate_weekly_effort(week)
            
            section += f"### Semana {week}\n\n"
            section += f"**Esfuerzo estimado:** {effort:.1f} horas  \n"
            section += f"**Total hallazgos:** {len(week_findings)}\n\n"
            
            if not week_findings:
                section += "*No hay hallazgos asignados a esta semana.*\n\n"
                continue
            
            # Contar por severidad
            severity_counts = {
                Severity.CRITICO: 0,
                Severity.ALTO: 0,
                Severity.MEDIO: 0,
                Severity.BAJO: 0
            }
            
            for finding in week_findings:
                severity_counts[finding.severity] += 1
            
            section += "**Distribución por severidad:**\n\n"
            for severity in [Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]:
                count = severity_counts[severity]
                if count > 0:
                    emoji = severity.get_emoji()
                    section += f"- {emoji} {severity.value}: {count}\n"
            
            section += "\n**Hallazgos principales:**\n\n"
            
            # Mostrar los primeros 5 hallazgos
            for finding in week_findings[:5]:
                emoji = finding.severity.get_emoji()
                section += f"- {emoji} **{finding.title}** - `{finding.file_path}`"
                
                if finding.line_number:
                    section += f"#L{finding.line_number}"
                section += f" (Esfuerzo: {finding.effort_score:.1f}h)\n"
            
            if len(week_findings) > 5:
                section += f"\n*...y {len(week_findings) - 5} hallazgos más*\n"
            
            section += "\n"
        
        return section

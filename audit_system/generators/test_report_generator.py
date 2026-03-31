"""
Tests para ReportGenerator.

Valida la generación correcta de reportes markdown con todas las secciones,
formato apropiado, emojis, tablas, y enlaces.
"""

import pytest
from datetime import datetime
from audit_system.generators.report_generator import ReportGenerator
from audit_system.models import (
    Finding, 
    Severity, 
    AnalysisResult, 
    PriorityMatrix, 
    RefactorPlan,
    CodeMetrics,
    ProjectStructure
)


@pytest.fixture
def sample_findings():
    """Crea hallazgos de ejemplo para testing."""
    findings = [
        Finding(
            id="F001",
            category="security",
            subcategory="hardcoded_secret",
            severity=Severity.CRITICO,
            title="Credencial hardcodeada en auth.py",
            description="Se encontró una contraseña hardcodeada",
            file_path="backend/api/auth.py",
            line_number=42,
            code_snippet='password = "admin123"',
            recommendation="Usar variables de entorno",
            impact_score=50.0,
            effort_score=2.0,
            priority_ratio=25.0
        ),
        Finding(
            id="F002",
            category="performance",
            subcategory="n_plus_one",
            severity=Severity.ALTO,
            title="Query N+1 en users endpoint",
            description="Patrón N+1 detectado en iteración",
            file_path="backend/api/users.py",
            line_number=78,
            recommendation="Usar eager loading",
            impact_score=40.0,
            effort_score=5.0,
            priority_ratio=8.0
        ),
        Finding(
            id="F003",
            category="quality",
            subcategory="type_any",
            severity=Severity.MEDIO,
            title="Uso de 'any' en componente",
            description="Tipo 'any' elimina verificación de tipos",
            file_path="src/components/UserList.tsx",
            line_number=15,
            recommendation="Definir interface apropiada",
            impact_score=20.0,
            effort_score=3.0,
            priority_ratio=6.67
        ),
        Finding(
            id="F004",
            category="quality",
            subcategory="console_log",
            severity=Severity.BAJO,
            title="Console.log en producción",
            description="Console.log sin remover",
            file_path="src/utils/helpers.ts",
            line_number=23,
            recommendation="Remover console.log",
            impact_score=5.0,
            effort_score=1.0,
            priority_ratio=5.0
        )
    ]
    return findings


@pytest.fixture
def sample_metrics():
    """Crea métricas de ejemplo."""
    return CodeMetrics(
        backend_total_lines=15000,
        backend_total_files=45,
        backend_large_files=8,
        backend_long_functions=12,
        backend_dependencies_count=35,
        frontend_total_lines=12000,
        frontend_total_files=38,
        frontend_large_components=5,
        frontend_dependencies_count=42,
        total_outdated_dependencies=7,
        total_vulnerabilities=3
    )


@pytest.fixture
def sample_priority_matrix(sample_findings):
    """Crea matriz de priorización de ejemplo."""
    matrix = PriorityMatrix()
    matrix.high_impact_low_effort = [sample_findings[0]]
    matrix.high_impact_high_effort = [sample_findings[1]]
    matrix.low_impact_low_effort = [sample_findings[3]]
    matrix.low_impact_high_effort = [sample_findings[2]]
    return matrix


@pytest.fixture
def sample_refactor_plan(sample_findings):
    """Crea plan de refactor de ejemplo."""
    plan = RefactorPlan()
    plan.week_1 = [sample_findings[0]]
    plan.week_2 = [sample_findings[1]]
    plan.week_3 = [sample_findings[2]]
    plan.week_4 = [sample_findings[3]]
    return plan


@pytest.fixture
def sample_analysis_result(sample_findings, sample_metrics, sample_priority_matrix, sample_refactor_plan):
    """Crea resultado de análisis completo."""
    structure = ProjectStructure(root_path="/test/project")
    
    return AnalysisResult(
        structure=structure,
        findings=sample_findings,
        top_10=sample_findings[:2],
        priority_matrix=sample_priority_matrix,
        metrics=sample_metrics,
        refactor_plan=sample_refactor_plan,
        generated_at=datetime(2024, 1, 15, 10, 30, 0)
    )


class TestReportGenerator:
    """Tests para ReportGenerator."""
    
    def test_generate_report_contains_all_sections(self, sample_analysis_result):
        """Verifica que el reporte contenga todas las secciones requeridas."""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_result)
        
        assert "# Reporte de Optimización" in report
        assert "## Tabla de Contenidos" in report
        assert "## Resumen Ejecutivo" in report
        assert "## Top 10 Mejoras Prioritarias" in report
        assert "## Métricas del Código" in report
        assert "## Matriz de Priorización" in report
        assert "## Hallazgos por Severidad" in report
        assert "## Plan de Refactor (4 Semanas)" in report
    
    def test_generate_executive_summary_has_severity_table(self, sample_findings):
        """Verifica que el resumen ejecutivo incluya tabla de severidades."""
        generator = ReportGenerator()
        summary = generator.generate_executive_summary(sample_findings)
        
        assert "## Resumen Ejecutivo" in summary
        assert "### Distribución por Severidad" in summary
        assert "| Severidad | Cantidad | Emoji |" in summary
        assert "| Crítico | 1 | 🔴 |" in summary
        assert "| Alto | 1 | 🟠 |" in summary
        assert "| Medio | 1 | 🟡 |" in summary
        assert "| Bajo | 1 | 🟢 |" in summary
    
    def test_generate_executive_summary_has_category_distribution(self, sample_findings):
        """Verifica que el resumen incluya distribución por categoría."""
        generator = ReportGenerator()
        summary = generator.generate_executive_summary(sample_findings)
        
        assert "### Distribución por Categoría" in summary
        assert "| Categoría | Cantidad |" in summary
        assert "Quality" in summary
        assert "Security" in summary
        assert "Performance" in summary
    
    def test_generate_top_10_shows_priority_findings(self, sample_findings):
        """Verifica que Top 10 muestre hallazgos prioritarios con detalles."""
        generator = ReportGenerator()
        top_10 = generator.generate_top_10(sample_findings[:2])
        
        assert "## Top 10 Mejoras Prioritarias" in top_10
        assert "Credencial hardcodeada en auth.py" in top_10
        assert "Query N+1 en users endpoint" in top_10
        assert "backend/api/auth.py" in top_10
        assert "Ratio Prioridad:" in top_10
        assert "Impacto:" in top_10
        assert "Esfuerzo:" in top_10
    
    def test_generate_top_10_includes_code_snippets(self, sample_findings):
        """Verifica que Top 10 incluya snippets de código."""
        generator = ReportGenerator()
        top_10 = generator.generate_top_10(sample_findings[:1])
        
        assert "**Código:**" in top_10
        assert "```python" in top_10
        assert 'password = "admin123"' in top_10
    
    def test_generate_top_10_includes_recommendations(self, sample_findings):
        """Verifica que Top 10 incluya recomendaciones."""
        generator = ReportGenerator()
        top_10 = generator.generate_top_10(sample_findings[:1])
        
        assert "**Recomendación:**" in top_10
        assert "Usar variables de entorno" in top_10
    
    def test_generate_top_10_uses_severity_emojis(self, sample_findings):
        """Verifica que Top 10 use emojis para severidades."""
        generator = ReportGenerator()
        top_10 = generator.generate_top_10(sample_findings[:2])
        
        assert "🔴" in top_10  # Crítico
        assert "🟠" in top_10  # Alto
    
    def test_generate_top_10_includes_line_numbers(self, sample_findings):
        """Verifica que Top 10 incluya números de línea en enlaces."""
        generator = ReportGenerator()
        top_10 = generator.generate_top_10(sample_findings[:1])
        
        assert "#L42" in top_10
    
    def test_generate_findings_by_severity_organizes_correctly(self, sample_findings):
        """Verifica que hallazgos se organicen por severidad."""
        generator = ReportGenerator()
        section = generator.generate_findings_by_severity(sample_findings)
        
        assert "## Hallazgos por Severidad" in section
        assert "### 🔴 Crítico" in section
        assert "### 🟠 Alto" in section
        assert "### 🟡 Medio" in section
        assert "### 🟢 Bajo" in section
    
    def test_generate_findings_by_severity_groups_by_category(self, sample_findings):
        """Verifica que hallazgos se agrupen por categoría dentro de severidad."""
        generator = ReportGenerator()
        section = generator.generate_findings_by_severity(sample_findings)
        
        assert "#### Security" in section
        assert "#### Performance" in section
        assert "#### Quality" in section
    
    def test_generate_findings_by_severity_includes_file_links(self, sample_findings):
        """Verifica que hallazgos incluyan enlaces a archivos."""
        generator = ReportGenerator()
        section = generator.generate_findings_by_severity(sample_findings)
        
        assert "[`backend/api/auth.py`](backend/api/auth.py)" in section
        assert "[`backend/api/users.py`](backend/api/users.py)" in section
    
    def test_generate_metrics_section_has_tables(self, sample_metrics):
        """Verifica que métricas se presenten en tablas."""
        generator = ReportGenerator()
        section = generator.generate_metrics_section(sample_metrics)
        
        assert "## Métricas del Código" in section
        assert "| Métrica | Backend | Frontend |" in section
        assert "| Total líneas | 15,000 | 12,000 |" in section
        assert "| Total archivos | 45 | 38 |" in section
    
    def test_generate_metrics_section_includes_dependencies(self, sample_metrics):
        """Verifica que métricas incluyan información de dependencias."""
        generator = ReportGenerator()
        section = generator.generate_metrics_section(sample_metrics)
        
        assert "### Métricas de Dependencias" in section
        assert "| Dependencias desactualizadas | 7 |" in section
        assert "| Dependencias con vulnerabilidades | 3 |" in section
    
    def test_generate_priority_matrix_has_all_quadrants(self, sample_priority_matrix):
        """Verifica que matriz incluya todos los cuadrantes."""
        generator = ReportGenerator()
        section = generator.generate_priority_matrix(sample_priority_matrix)
        
        assert "## Matriz de Priorización" in section
        assert "🎯 Quick Wins" in section
        assert "🚀 Major Projects" in section
        assert "✅ Fill-ins" in section
        assert "⚠️ Avoid" in section
    
    def test_generate_priority_matrix_shows_visual_diagram(self, sample_priority_matrix):
        """Verifica que matriz incluya diagrama visual."""
        generator = ReportGenerator()
        section = generator.generate_priority_matrix(sample_priority_matrix)
        
        assert "IMPACTO" in section
        assert "ESFUERZO" in section
        assert "```" in section  # Code block para diagrama
    
    def test_generate_refactor_plan_has_4_weeks(self, sample_refactor_plan):
        """Verifica que plan incluya 4 semanas."""
        generator = ReportGenerator()
        section = generator.generate_refactor_plan(sample_refactor_plan)
        
        assert "## Plan de Refactor (4 Semanas)" in section
        assert "### Semana 1" in section
        assert "### Semana 2" in section
        assert "### Semana 3" in section
        assert "### Semana 4" in section
    
    def test_generate_refactor_plan_shows_effort_estimates(self, sample_refactor_plan):
        """Verifica que plan muestre estimaciones de esfuerzo."""
        generator = ReportGenerator()
        section = generator.generate_refactor_plan(sample_refactor_plan)
        
        assert "**Esfuerzo estimado:**" in section
        assert "horas" in section
    
    def test_generate_refactor_plan_shows_severity_distribution(self, sample_refactor_plan):
        """Verifica que plan muestre distribución por severidad."""
        generator = ReportGenerator()
        section = generator.generate_refactor_plan(sample_refactor_plan)
        
        assert "**Distribución por severidad:**" in section
        assert "🔴 Crítico:" in section
        assert "🟠 Alto:" in section
    
    def test_generate_table_of_contents_has_all_links(self):
        """Verifica que tabla de contenidos tenga todos los enlaces."""
        generator = ReportGenerator()
        toc = generator.generate_table_of_contents()
        
        assert "## Tabla de Contenidos" in toc
        assert "[Resumen Ejecutivo](#resumen-ejecutivo)" in toc
        assert "[Top 10 Mejoras Prioritarias](#top-10-mejoras-prioritarias)" in toc
        assert "[Métricas del Código](#métricas-del-código)" in toc
        assert "[Matriz de Priorización](#matriz-de-priorización)" in toc
        assert "[Hallazgos por Severidad](#hallazgos-por-severidad)" in toc
        assert "[Plan de Refactor (4 Semanas)](#plan-de-refactor-4-semanas)" in toc
    
    def test_generate_table_of_contents_has_severity_sublinks(self):
        """Verifica que tabla de contenidos tenga subenlaces de severidad."""
        generator = ReportGenerator()
        toc = generator.generate_table_of_contents()
        
        assert "[🔴 Crítico](#-crítico)" in toc
        assert "[🟠 Alto](#-alto)" in toc
        assert "[🟡 Medio](#-medio)" in toc
        assert "[🟢 Bajo](#-bajo)" in toc
    
    def test_report_includes_generation_date(self, sample_analysis_result):
        """Verifica que reporte incluya fecha de generación."""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_result)
        
        assert "**Fecha de generación:**" in report
        assert "2024-01-15 10:30:00" in report
    
    def test_report_includes_project_path(self, sample_analysis_result):
        """Verifica que reporte incluya ruta del proyecto."""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_result)
        
        assert "**Proyecto:**" in report
        assert "/test/project" in report
    
    def test_report_includes_total_findings_count(self, sample_analysis_result):
        """Verifica que reporte incluya conteo total de hallazgos."""
        generator = ReportGenerator()
        report = generator.generate_report(sample_analysis_result)
        
        assert "**Total de hallazgos:**" in report
        assert "4" in report
    
    def test_empty_findings_handled_gracefully(self):
        """Verifica que reporte maneje lista vacía de hallazgos."""
        generator = ReportGenerator()
        summary = generator.generate_executive_summary([])
        
        assert "## Resumen Ejecutivo" in summary
        assert "**Total de hallazgos:** 0" in summary
    
    def test_findings_without_line_numbers_handled(self):
        """Verifica que hallazgos sin número de línea se manejen correctamente."""
        finding = Finding(
            id="F001",
            category="quality",
            subcategory="test",
            severity=Severity.BAJO,
            title="Test finding",
            description="Test",
            file_path="test.py",
            line_number=None
        )
        
        generator = ReportGenerator()
        top_10 = generator.generate_top_10([finding])
        
        assert "test.py" in top_10
        assert "#L" not in top_10  # No debe incluir número de línea
    
    def test_findings_without_code_snippet_handled(self):
        """Verifica que hallazgos sin snippet se manejen correctamente."""
        finding = Finding(
            id="F001",
            category="quality",
            subcategory="test",
            severity=Severity.BAJO,
            title="Test finding",
            description="Test",
            file_path="test.py",
            code_snippet=None
        )
        
        generator = ReportGenerator()
        top_10 = generator.generate_top_10([finding])
        
        assert "Test finding" in top_10
        assert "**Código:**" not in top_10

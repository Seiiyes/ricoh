"""
Tests para RefactorPlanner.

Valida la distribución de hallazgos en planes de 4 semanas,
cálculo de esfuerzo semanal, y balanceo de carga Backend/Frontend.
"""

import pytest
from audit_system.planners.refactor_planner import RefactorPlanner
from audit_system.models import Finding, RefactorPlan, Severity
from audit_system.config import get_config


@pytest.fixture
def planner():
    """Fixture que retorna una instancia de RefactorPlanner."""
    return RefactorPlanner()


@pytest.fixture
def sample_findings():
    """Fixture que retorna hallazgos de ejemplo con diferentes severidades."""
    findings = []
    
    # 2 Críticos (Backend)
    findings.append(Finding(
        id="C1",
        category="security",
        subcategory="hardcoded_secret",
        severity=Severity.CRITICO,
        title="Secret hardcodeado",
        description="Password en código",
        file_path="backend/api/auth.py",
        effort_score=5.0
    ))
    findings.append(Finding(
        id="C2",
        category="quality",
        subcategory="long_function",
        severity=Severity.CRITICO,
        title="Función muy larga",
        description="Función de 150 líneas",
        file_path="backend/db/repository.py",
        effort_score=8.0
    ))
    
    # 4 Altos (2 Backend, 2 Frontend)
    findings.append(Finding(
        id="H1",
        category="performance",
        subcategory="n_plus_one",
        severity=Severity.ALTO,
        title="Query N+1",
        description="Loop con queries",
        file_path="backend/api/users.py",
        effort_score=6.0
    ))
    findings.append(Finding(
        id="H2",
        category="security",
        subcategory="no_input_validation",
        severity=Severity.ALTO,
        title="Sin validación",
        description="Endpoint sin schema",
        file_path="backend/api/printers.py",
        effort_score=4.0
    ))
    findings.append(Finding(
        id="H3",
        category="performance",
        subcategory="unnecessary_rerender",
        severity=Severity.ALTO,
        title="Re-render innecesario",
        description="Componente sin memo",
        file_path="src/components/PrinterList.tsx",
        effort_score=3.0
    ))
    findings.append(Finding(
        id="H4",
        category="quality",
        subcategory="large_component",
        severity=Severity.ALTO,
        title="Componente grande",
        description="250 líneas",
        file_path="src/pages/Dashboard.tsx",
        effort_score=7.0
    ))
    
    # 4 Medios (2 Backend, 2 Frontend)
    findings.append(Finding(
        id="M1",
        category="quality",
        subcategory="missing_type_hints",
        severity=Severity.MEDIO,
        title="Sin type hints",
        description="Función sin tipos",
        file_path="backend/services/printer_service.py",
        effort_score=2.0
    ))
    findings.append(Finding(
        id="M2",
        category="quality",
        subcategory="deep_nesting",
        severity=Severity.MEDIO,
        title="Indentación profunda",
        description="4 niveles de nesting",
        file_path="backend/jobs/sync_job.py",
        effort_score=3.0
    ))
    findings.append(Finding(
        id="M3",
        category="quality",
        subcategory="type_any",
        severity=Severity.MEDIO,
        title="Uso de any",
        description="Type any en props",
        file_path="src/components/Button.tsx",
        effort_score=1.0
    ))
    findings.append(Finding(
        id="M4",
        category="quality",
        subcategory="console_log",
        severity=Severity.MEDIO,
        title="Console.log",
        description="Debug en producción",
        file_path="src/utils/helpers.ts",
        effort_score=1.0
    ))
    
    # 4 Bajos (2 Backend, 2 Frontend)
    findings.append(Finding(
        id="L1",
        category="quality",
        subcategory="todo_comment",
        severity=Severity.BAJO,
        title="TODO pendiente",
        description="Comentario TODO",
        file_path="backend/api/export.py",
        effort_score=1.0
    ))
    findings.append(Finding(
        id="L2",
        category="quality",
        subcategory="missing_docstring",
        severity=Severity.BAJO,
        title="Sin docstring",
        description="Función sin docs",
        file_path="backend/utils/validators.py",
        effort_score=0.5
    ))
    findings.append(Finding(
        id="L3",
        category="quality",
        subcategory="todo_comment",
        severity=Severity.BAJO,
        title="FIXME pendiente",
        description="Comentario FIXME",
        file_path="src/hooks/usePrinter.ts",
        effort_score=1.0
    ))
    findings.append(Finding(
        id="L4",
        category="quality",
        subcategory="missing_comments",
        severity=Severity.BAJO,
        title="Sin comentarios",
        description="Lógica compleja sin docs",
        file_path="src/services/api.ts",
        effort_score=0.5
    ))
    
    return findings


def test_create_4_week_plan_distributes_by_severity(planner, sample_findings):
    """Verifica que los hallazgos se distribuyan según severidad."""
    plan = planner.create_4_week_plan(sample_findings)
    
    # Semana 1 debe contener todos los críticos
    critical_in_week1 = [f for f in plan.week_1 if f.severity == Severity.CRITICO]
    assert len(critical_in_week1) == 2
    
    # Semanas 1-2 deben contener hallazgos altos
    high_in_week1 = [f for f in plan.week_1 if f.severity == Severity.ALTO]
    high_in_week2 = [f for f in plan.week_2 if f.severity == Severity.ALTO]
    assert len(high_in_week1) + len(high_in_week2) == 4
    
    # Semanas 2-3 deben contener hallazgos medios
    medium_in_week2 = [f for f in plan.week_2 if f.severity == Severity.MEDIO]
    medium_in_week3 = [f for f in plan.week_3 if f.severity == Severity.MEDIO]
    assert len(medium_in_week2) + len(medium_in_week3) == 4
    
    # Semanas 3-4 deben contener hallazgos bajos
    low_in_week3 = [f for f in plan.week_3 if f.severity == Severity.BAJO]
    low_in_week4 = [f for f in plan.week_4 if f.severity == Severity.BAJO]
    assert len(low_in_week3) + len(low_in_week4) == 4


def test_calculate_weekly_effort(planner):
    """Verifica el cálculo de esfuerzo semanal."""
    plan = RefactorPlan()
    
    # Agregar hallazgos con esfuerzos conocidos a semana 1
    plan.week_1.append(Finding(
        id="F1",
        category="test",
        subcategory="test",
        severity=Severity.ALTO,
        title="Test",
        description="Test",
        file_path="test.py",
        effort_score=5.0
    ))
    plan.week_1.append(Finding(
        id="F2",
        category="test",
        subcategory="test",
        severity=Severity.MEDIO,
        title="Test",
        description="Test",
        file_path="test.py",
        effort_score=3.0
    ))
    
    effort = planner.calculate_weekly_effort(plan, 1)
    assert effort == 8.0


def test_calculate_weekly_effort_invalid_week(planner):
    """Verifica que se lance error con número de semana inválido."""
    plan = RefactorPlan()
    
    with pytest.raises(ValueError, match="Week must be between 1 and 4"):
        planner.calculate_weekly_effort(plan, 0)
    
    with pytest.raises(ValueError, match="Week must be between 1 and 4"):
        planner.calculate_weekly_effort(plan, 5)


def test_balance_workload_distributes_backend_frontend(planner):
    """Verifica que se balancee la carga entre Backend y Frontend."""
    plan = RefactorPlan()
    
    # Crear desbalance: 5 Backend, 1 Frontend en semana 1
    for i in range(5):
        plan.week_1.append(Finding(
            id=f"B{i}",
            category="test",
            subcategory="test",
            severity=Severity.ALTO,
            title="Backend",
            description="Backend",
            file_path=f"backend/api/test{i}.py",
            effort_score=5.0
        ))
    
    plan.week_1.append(Finding(
        id="F1",
        category="test",
        subcategory="test",
        severity=Severity.ALTO,
        title="Frontend",
        description="Frontend",
        file_path="src/components/Test.tsx",
        effort_score=5.0
    ))
    
    # Balancear
    planner.balance_workload(plan)
    
    # Verificar que se movieron algunos hallazgos de Backend a semana 2
    backend_week1 = [f for f in plan.week_1 if "backend/" in f.file_path]
    backend_week2 = [f for f in plan.week_2 if "backend/" in f.file_path]
    
    # Debe haber menos de 5 Backend en semana 1 después del balance
    assert len(backend_week1) < 5
    # Y algunos deben haberse movido a semana 2
    assert len(backend_week2) > 0


def test_redistribute_by_effort_when_exceeds_40_hours(planner, sample_findings):
    """Verifica redistribución cuando esfuerzo semanal excede 40 horas."""
    # Crear hallazgos con alto esfuerzo
    high_effort_findings = []
    for i in range(10):
        high_effort_findings.append(Finding(
            id=f"HE{i}",
            category="test",
            subcategory="test",
            severity=Severity.CRITICO,
            title=f"High effort {i}",
            description="Test",
            file_path=f"backend/test{i}.py",
            effort_score=8.0  # 10 * 8 = 80 horas
        ))
    
    plan = planner.create_4_week_plan(high_effort_findings)
    
    # Verificar que ninguna semana exceda 40 horas
    for week in range(1, 5):
        effort = planner.calculate_weekly_effort(plan, week)
        assert effort <= get_config().MAX_WEEKLY_EFFORT_HOURS


def test_get_weekly_summary(planner, sample_findings):
    """Verifica generación de resumen semanal."""
    plan = planner.create_4_week_plan(sample_findings)
    summary = planner.get_weekly_summary(plan)
    
    # Verificar que hay resumen para cada semana
    assert len(summary) == 4
    
    # Verificar estructura del resumen
    for week in range(1, 5):
        assert week in summary
        week_summary = summary[week]
        
        assert "total_findings" in week_summary
        assert "total_effort" in week_summary
        assert "backend_findings" in week_summary
        assert "frontend_findings" in week_summary
        assert "backend_effort" in week_summary
        assert "frontend_effort" in week_summary
        assert "severity_counts" in week_summary
        
        # Verificar que los conteos sean consistentes
        assert week_summary["total_findings"] == (
            week_summary["backend_findings"] + week_summary["frontend_findings"]
        )


def test_is_backend_file(planner):
    """Verifica identificación correcta de archivos Backend."""
    assert planner._is_backend_file("backend/api/auth.py") is True
    assert planner._is_backend_file("backend/db/models.py") is True
    assert planner._is_backend_file("src/components/Button.tsx") is False
    assert planner._is_backend_file("src/pages/Dashboard.tsx") is False


def test_empty_findings_list(planner):
    """Verifica manejo de lista vacía de hallazgos."""
    plan = planner.create_4_week_plan([])
    
    assert len(plan.week_1) == 0
    assert len(plan.week_2) == 0
    assert len(plan.week_3) == 0
    assert len(plan.week_4) == 0
    
    assert planner.calculate_weekly_effort(plan, 1) == 0.0


def test_single_finding(planner):
    """Verifica manejo de un solo hallazgo."""
    finding = Finding(
        id="F1",
        category="test",
        subcategory="test",
        severity=Severity.CRITICO,
        title="Test",
        description="Test",
        file_path="test.py",
        effort_score=5.0
    )
    
    plan = planner.create_4_week_plan([finding])
    
    # Debe estar en semana 1 (crítico)
    assert len(plan.week_1) == 1
    assert plan.week_1[0].id == "F1"


def test_all_same_severity(planner):
    """Verifica distribución cuando todos los hallazgos tienen la misma severidad."""
    findings = []
    for i in range(10):
        findings.append(Finding(
            id=f"M{i}",
            category="test",
            subcategory="test",
            severity=Severity.MEDIO,
            title=f"Medium {i}",
            description="Test",
            file_path=f"test{i}.py",
            effort_score=2.0
        ))
    
    plan = planner.create_4_week_plan(findings)
    
    # Hallazgos medios deben distribuirse principalmente en semanas 2-3
    # (pero pueden redistribuirse a semana 4 por balanceo de esfuerzo)
    assert len(plan.week_1) == 0  # No críticos ni altos
    assert len(plan.week_2) > 0  # Debe haber algunos medios
    assert len(plan.week_3) > 0  # Debe haber algunos medios
    
    # Total debe ser 10
    total = len(plan.week_1) + len(plan.week_2) + len(plan.week_3) + len(plan.week_4)
    assert total == 10

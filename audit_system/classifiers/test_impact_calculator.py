"""Tests para ImpactCalculator."""
import pytest
from hypothesis import given, strategies as st
from audit_system.classifiers.impact_calculator import ImpactCalculator
from audit_system.models import Finding, Severity, PriorityMatrix


class TestImpactCalculator:
    @pytest.fixture
    def calculator(self):
        return ImpactCalculator()
    
    # Unit Tests
    
    def test_calculate_impact_score_basic(self, calculator):
        """Verifica cálculo básico de impact score."""
        finding = Finding(
            id="TEST-001", category="performance", subcategory="n_plus_one",
            severity=Severity.CRITICO, title="Test", description="Test",
            file_path="test.py"
        )
        finding.metadata = {"affected_files": 5, "frequency": 3}
        
        # (4 * 10) + (5 * 2) + (3 * 5) = 40 + 10 + 15 = 65
        score = calculator.calculate_impact_score(finding)
        assert score == 65.0
    
    def test_calculate_impact_score_without_metadata(self, calculator):
        """Verifica cálculo de impact score sin metadata."""
        finding = Finding(
            id="TEST-002", category="quality", subcategory="long_function",
            severity=Severity.MEDIO, title="Test", description="Test",
            file_path="test.py"
        )
        
        # (2 * 10) + (1 * 2) + (1 * 5) = 20 + 2 + 5 = 27
        score = calculator.calculate_impact_score(finding)
        assert score == 27.0
    
    def test_calculate_effort_score_simple(self, calculator):
        """Verifica cálculo de effort score con complejidad simple."""
        finding = Finding(
            id="TEST-003", category="quality", subcategory="todo_comment",
            severity=Severity.BAJO, title="Test", description="Test",
            file_path="test.py"
        )
        finding.metadata = {
            "complexity": "simple",
            "files_to_modify": 1,
            "dependencies": 0
        }
        
        # 1 + (1 * 2) + (0 * 3) = 1 + 2 + 0 = 3
        score = calculator.calculate_effort_score(finding)
        assert score == 3.0
    
    def test_calculate_effort_score_complex(self, calculator):
        """Verifica cálculo de effort score con complejidad alta."""
        finding = Finding(
            id="TEST-004", category="architecture", subcategory="layer_violation",
            severity=Severity.ALTO, title="Test", description="Test",
            file_path="test.py"
        )
        finding.metadata = {
            "complexity": "complejo",
            "files_to_modify": 8,
            "dependencies": 4
        }
        
        # 5 + (8 * 2) + (4 * 3) = 5 + 16 + 12 = 33
        score = calculator.calculate_effort_score(finding)
        assert score == 33.0
    
    def test_calculate_priority_matrix_empty_list(self, calculator):
        """Verifica que matriz vacía se maneje correctamente."""
        matrix = calculator.calculate_priority_matrix([])
        
        assert isinstance(matrix, PriorityMatrix)
        assert len(matrix.high_impact_low_effort) == 0
        assert len(matrix.high_impact_high_effort) == 0
        assert len(matrix.low_impact_low_effort) == 0
        assert len(matrix.low_impact_high_effort) == 0
    
    def test_calculate_priority_matrix_classification(self, calculator):
        """Verifica clasificación correcta en cuadrantes."""
        findings = [
            # Alto impacto, bajo esfuerzo (Quick win)
            Finding(
                id="F1", category="security", subcategory="hardcoded_secret",
                severity=Severity.CRITICO, title="Secret", description="Test",
                file_path="test1.py"
            ),
            # Alto impacto, alto esfuerzo (Major project)
            Finding(
                id="F2", category="architecture", subcategory="layer_violation",
                severity=Severity.CRITICO, title="Architecture", description="Test",
                file_path="test2.py"
            ),
            # Bajo impacto, bajo esfuerzo (Fill-in)
            Finding(
                id="F3", category="quality", subcategory="todo_comment",
                severity=Severity.BAJO, title="TODO", description="Test",
                file_path="test3.py"
            ),
            # Bajo impacto, alto esfuerzo (Avoid)
            Finding(
                id="F4", category="quality", subcategory="refactor",
                severity=Severity.BAJO, title="Refactor", description="Test",
                file_path="test4.py"
            )
        ]
        
        # Configurar metadata para control de clasificación
        findings[0].metadata = {"affected_files": 1, "frequency": 1, "complexity": "simple", "files_to_modify": 1, "dependencies": 0}
        findings[1].metadata = {"affected_files": 10, "frequency": 5, "complexity": "complejo", "files_to_modify": 15, "dependencies": 8}
        findings[2].metadata = {"affected_files": 1, "frequency": 1, "complexity": "simple", "files_to_modify": 1, "dependencies": 0}
        findings[3].metadata = {"affected_files": 1, "frequency": 1, "complexity": "complejo", "files_to_modify": 10, "dependencies": 5}
        
        matrix = calculator.calculate_priority_matrix(findings)
        
        # Verificar que todos los findings fueron clasificados
        total_classified = (
            len(matrix.high_impact_low_effort) +
            len(matrix.high_impact_high_effort) +
            len(matrix.low_impact_low_effort) +
            len(matrix.low_impact_high_effort)
        )
        assert total_classified == 4
    
    def test_select_top_10_with_less_than_10(self, calculator):
        """Verifica selección cuando hay menos de 10 hallazgos."""
        findings = [
            Finding(
                id=f"F{i}", category="quality", subcategory="test",
                severity=Severity.MEDIO, title=f"Test {i}", description="Test",
                file_path=f"test{i}.py"
            )
            for i in range(5)
        ]
        
        # Configurar metadata
        for i, finding in enumerate(findings):
            finding.metadata = {
                "affected_files": i + 1,
                "frequency": 1,
                "complexity": "simple",
                "files_to_modify": 1,
                "dependencies": 0
            }
        
        top_10 = calculator.select_top_10(findings)
        
        assert len(top_10) == 5
    
    def test_select_top_10_orders_by_priority_ratio(self, calculator):
        """Verifica que top 10 esté ordenado por priority_ratio descendente."""
        findings = []
        for i in range(15):
            finding = Finding(
                id=f"F{i}", category="quality", subcategory="test",
                severity=Severity.MEDIO, title=f"Test {i}", description="Test",
                file_path=f"test{i}.py"
            )
            # Variar impacto y esfuerzo para crear diferentes ratios
            finding.metadata = {
                "affected_files": i + 1,
                "frequency": i % 3 + 1,
                "complexity": "simple" if i % 2 == 0 else "moderado",
                "files_to_modify": i % 5 + 1,
                "dependencies": i % 3
            }
            findings.append(finding)
        
        top_10 = calculator.select_top_10(findings)
        
        assert len(top_10) == 10
        
        # Verificar orden descendente por priority_ratio
        for i in range(len(top_10) - 1):
            assert top_10[i].priority_ratio >= top_10[i + 1].priority_ratio
    
    def test_calculate_impact_score_with_high_frequency(self, calculator):
        """Verifica que frecuencia alta aumente el impact score."""
        finding = Finding(
            id="TEST-005", category="quality", subcategory="code_duplication",
            severity=Severity.MEDIO, title="Test", description="Test",
            file_path="test.py"
        )
        finding.metadata = {"affected_files": 3, "frequency": 10}
        
        # (2 * 10) + (3 * 2) + (10 * 5) = 20 + 6 + 50 = 76
        score = calculator.calculate_impact_score(finding)
        assert score == 76.0
    
    def test_calculate_effort_score_with_many_dependencies(self, calculator):
        """Verifica que dependencias aumenten el effort score."""
        finding = Finding(
            id="TEST-006", category="architecture", subcategory="coupling",
            severity=Severity.ALTO, title="Test", description="Test",
            file_path="test.py"
        )
        finding.metadata = {
            "complexity": "moderado",
            "files_to_modify": 5,
            "dependencies": 10
        }
        
        # 3 + (5 * 2) + (10 * 3) = 3 + 10 + 30 = 43
        score = calculator.calculate_effort_score(finding)
        assert score == 43.0
    
    def test_priority_ratio_calculation(self, calculator):
        """Verifica cálculo correcto del priority_ratio."""
        finding = Finding(
            id="TEST-007", category="performance", subcategory="blocking_operation",
            severity=Severity.ALTO, title="Test", description="Test",
            file_path="test.py"
        )
        finding.metadata = {
            "affected_files": 2,
            "frequency": 2,
            "complexity": "simple",
            "files_to_modify": 1,
            "dependencies": 0
        }
        
        impact = calculator.calculate_impact_score(finding)
        effort = calculator.calculate_effort_score(finding)
        
        # Calcular priority_ratio manualmente
        expected_ratio = impact / effort
        
        # Usar select_top_10 para calcular el ratio
        top = calculator.select_top_10([finding])
        
        assert abs(top[0].priority_ratio - expected_ratio) < 0.01
    
    def test_effort_score_zero_handling(self, calculator):
        """Verifica manejo de effort_score cero."""
        finding = Finding(
            id="TEST-008", category="quality", subcategory="test",
            severity=Severity.MEDIO, title="Test", description="Test",
            file_path="test.py"
        )
        finding.metadata = {
            "affected_files": 5,
            "frequency": 3,
            "complexity": "simple",
            "files_to_modify": 0,
            "dependencies": 0
        }
        
        # effort_score = 1 + 0 + 0 = 1 (no debería ser cero con complexity simple)
        effort = calculator.calculate_effort_score(finding)
        assert effort > 0
        
        # Verificar que priority_ratio se calcule correctamente
        top = calculator.select_top_10([finding])
        assert top[0].priority_ratio > 0


# Property-Based Tests

@given(
    severity=st.sampled_from([Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]),
    affected_files=st.integers(min_value=1, max_value=100),
    frequency=st.integers(min_value=1, max_value=50)
)
def test_property_impact_score_formula(severity, affected_files, frequency):
    """
    **Validates: Requirements 15.1**
    
    Property: For any finding, impact score must be calculated using the formula:
    (severity_weight * 10) + (affected_files * 2) + (frequency * 5)
    """
    calculator = ImpactCalculator()
    finding = Finding(
        id="PBT-001", category="test", subcategory="test",
        severity=severity, title="Test", description="Test",
        file_path="test.py"
    )
    finding.metadata = {
        "affected_files": affected_files,
        "frequency": frequency
    }
    
    score = calculator.calculate_impact_score(finding)
    
    # Calcular score esperado
    severity_weight = severity.get_weight()
    expected_score = (severity_weight * 10) + (affected_files * 2) + (frequency * 5)
    
    assert score == expected_score


@given(
    complexity=st.sampled_from(["simple", "moderado", "complejo"]),
    files_to_modify=st.integers(min_value=1, max_value=50),
    dependencies=st.integers(min_value=0, max_value=30)
)
def test_property_effort_score_formula(complexity, files_to_modify, dependencies):
    """
    **Validates: Requirements 15.2**
    
    Property: For any finding, effort score must be calculated using the formula:
    complexity_factor + (files_to_modify * 2) + (dependencies * 3)
    """
    calculator = ImpactCalculator()
    finding = Finding(
        id="PBT-002", category="test", subcategory="test",
        severity=Severity.MEDIO, title="Test", description="Test",
        file_path="test.py"
    )
    finding.metadata = {
        "complexity": complexity,
        "files_to_modify": files_to_modify,
        "dependencies": dependencies
    }
    
    score = calculator.calculate_effort_score(finding)
    
    # Calcular score esperado
    complexity_factors = {"simple": 1, "moderado": 3, "complejo": 5}
    complexity_factor = complexity_factors[complexity]
    expected_score = complexity_factor + (files_to_modify * 2) + (dependencies * 3)
    
    assert score == expected_score


@given(
    findings_data=st.lists(
        st.tuples(
            st.sampled_from([Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]),
            st.integers(min_value=1, max_value=20),
            st.integers(min_value=1, max_value=10),
            st.sampled_from(["simple", "moderado", "complejo"]),
            st.integers(min_value=1, max_value=10),
            st.integers(min_value=0, max_value=5)
        ),
        min_size=1,
        max_size=50
    )
)
def test_property_priority_matrix_classifies_all_findings(findings_data):
    """
    **Validates: Requirements 15.3**
    
    Property: For any list of findings, the priority matrix must classify
    all findings into one of the four quadrants without losing any.
    """
    calculator = ImpactCalculator()
    
    # Crear findings desde datos generados
    findings = []
    for i, (severity, affected_files, frequency, complexity, files_to_modify, deps) in enumerate(findings_data):
        finding = Finding(
            id=f"PBT-{i}", category="test", subcategory="test",
            severity=severity, title=f"Test {i}", description="Test",
            file_path=f"test{i}.py"
        )
        finding.metadata = {
            "affected_files": affected_files,
            "frequency": frequency,
            "complexity": complexity,
            "files_to_modify": files_to_modify,
            "dependencies": deps
        }
        findings.append(finding)
    
    matrix = calculator.calculate_priority_matrix(findings)
    
    # Verificar que todos los findings fueron clasificados
    total_classified = (
        len(matrix.high_impact_low_effort) +
        len(matrix.high_impact_high_effort) +
        len(matrix.low_impact_low_effort) +
        len(matrix.low_impact_high_effort)
    )
    
    assert total_classified == len(findings)


@given(
    findings_data=st.lists(
        st.tuples(
            st.sampled_from([Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]),
            st.integers(min_value=1, max_value=20),
            st.integers(min_value=1, max_value=10),
            st.sampled_from(["simple", "moderado", "complejo"]),
            st.integers(min_value=1, max_value=10),
            st.integers(min_value=0, max_value=5)
        ),
        min_size=10,
        max_size=100
    )
)
def test_property_top_10_selects_highest_priority_ratio(findings_data):
    """
    **Validates: Requirements 15.4**
    
    Property: For any list of findings with at least 10 items,
    the top 10 selected must have the highest priority ratios.
    """
    calculator = ImpactCalculator()
    
    # Crear findings desde datos generados
    findings = []
    for i, (severity, affected_files, frequency, complexity, files_to_modify, deps) in enumerate(findings_data):
        finding = Finding(
            id=f"PBT-{i}", category="test", subcategory="test",
            severity=severity, title=f"Test {i}", description="Test",
            file_path=f"test{i}.py"
        )
        finding.metadata = {
            "affected_files": affected_files,
            "frequency": frequency,
            "complexity": complexity,
            "files_to_modify": files_to_modify,
            "dependencies": deps
        }
        findings.append(finding)
    
    top_10 = calculator.select_top_10(findings)
    
    # Verificar que se seleccionaron máximo 10
    assert len(top_10) <= 10
    
    # Si hay al menos 10 findings, debe retornar exactamente 10
    if len(findings) >= 10:
        assert len(top_10) == 10
    else:
        assert len(top_10) == len(findings)
    
    # Verificar que están ordenados por priority_ratio descendente
    for i in range(len(top_10) - 1):
        assert top_10[i].priority_ratio >= top_10[i + 1].priority_ratio
    
    # Verificar que los 10 seleccionados tienen los ratios más altos
    if len(findings) >= 10:
        all_ratios = sorted([f.priority_ratio for f in findings], reverse=True)
        top_10_ratios = [f.priority_ratio for f in top_10]
        
        # Los 10 ratios más altos deben estar en top_10
        for ratio in all_ratios[:10]:
            assert ratio in top_10_ratios


@given(
    affected_files=st.integers(min_value=1, max_value=20),
    frequency=st.integers(min_value=1, max_value=10)
)
def test_property_impact_score_increases_with_severity(affected_files, frequency):
    """
    **Validates: Requirements 15.1**
    
    Property: For any two findings with the same metadata but different severity,
    the finding with higher severity must have a higher impact score.
    """
    calculator = ImpactCalculator()
    
    finding_low = Finding(
        id="LOW", category="test", subcategory="test",
        severity=Severity.BAJO, title="Test", description="Test",
        file_path="test.py"
    )
    finding_low.metadata = {"affected_files": affected_files, "frequency": frequency}
    
    finding_high = Finding(
        id="HIGH", category="test", subcategory="test",
        severity=Severity.CRITICO, title="Test", description="Test",
        file_path="test.py"
    )
    finding_high.metadata = {"affected_files": affected_files, "frequency": frequency}
    
    score_low = calculator.calculate_impact_score(finding_low)
    score_high = calculator.calculate_impact_score(finding_high)
    
    assert score_high > score_low


@given(
    findings_data=st.lists(
        st.tuples(
            st.sampled_from([Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]),
            st.integers(min_value=1, max_value=20),
            st.integers(min_value=1, max_value=10),
            st.sampled_from(["simple", "moderado", "complejo"]),
            st.integers(min_value=1, max_value=10),
            st.integers(min_value=0, max_value=5)
        ),
        min_size=1,
        max_size=30
    )
)
def test_property_priority_ratio_is_impact_over_effort(findings_data):
    """
    **Validates: Requirements 15.1, 15.2**
    
    Property: For any finding, priority_ratio must equal impact_score / effort_score.
    """
    calculator = ImpactCalculator()
    
    for i, (severity, affected_files, frequency, complexity, files_to_modify, deps) in enumerate(findings_data):
        finding = Finding(
            id=f"PBT-{i}", category="test", subcategory="test",
            severity=severity, title=f"Test {i}", description="Test",
            file_path=f"test{i}.py"
        )
        finding.metadata = {
            "affected_files": affected_files,
            "frequency": frequency,
            "complexity": complexity,
            "files_to_modify": files_to_modify,
            "dependencies": deps
        }
        
        impact = calculator.calculate_impact_score(finding)
        effort = calculator.calculate_effort_score(finding)
        
        # Calcular priority_ratio a través de select_top_10
        top = calculator.select_top_10([finding])
        
        expected_ratio = impact / effort if effort > 0 else impact
        
        assert abs(top[0].priority_ratio - expected_ratio) < 0.01


@given(
    findings_data=st.lists(
        st.tuples(
            st.sampled_from([Severity.CRITICO, Severity.ALTO, Severity.MEDIO, Severity.BAJO]),
            st.integers(min_value=1, max_value=20),
            st.integers(min_value=1, max_value=10),
            st.sampled_from(["simple", "moderado", "complejo"]),
            st.integers(min_value=1, max_value=10),
            st.integers(min_value=0, max_value=5)
        ),
        min_size=4,
        max_size=20
    )
)
def test_property_matrix_quadrants_use_median_split(findings_data):
    """
    **Validates: Requirements 15.3**
    
    Property: For any list of findings, the priority matrix must split
    findings into quadrants using median values for impact and effort.
    """
    calculator = ImpactCalculator()
    
    # Crear findings
    findings = []
    for i, (severity, affected_files, frequency, complexity, files_to_modify, deps) in enumerate(findings_data):
        finding = Finding(
            id=f"PBT-{i}", category="test", subcategory="test",
            severity=severity, title=f"Test {i}", description="Test",
            file_path=f"test{i}.py"
        )
        finding.metadata = {
            "affected_files": affected_files,
            "frequency": frequency,
            "complexity": complexity,
            "files_to_modify": files_to_modify,
            "dependencies": deps
        }
        findings.append(finding)
    
    matrix = calculator.calculate_priority_matrix(findings)
    
    # Calcular mediana manualmente
    impact_scores = [f.impact_score for f in findings]
    effort_scores = [f.effort_score for f in findings]
    
    sorted_impact = sorted(impact_scores)
    sorted_effort = sorted(effort_scores)
    
    n_impact = len(sorted_impact)
    n_effort = len(sorted_effort)
    
    if n_impact % 2 == 0:
        impact_median = (sorted_impact[n_impact // 2 - 1] + sorted_impact[n_impact // 2]) / 2
    else:
        impact_median = sorted_impact[n_impact // 2]
    
    if n_effort % 2 == 0:
        effort_median = (sorted_effort[n_effort // 2 - 1] + sorted_effort[n_effort // 2]) / 2
    else:
        effort_median = sorted_effort[n_effort // 2]
    
    # Verificar que los findings en cada cuadrante cumplen las condiciones
    for finding in matrix.high_impact_low_effort:
        assert finding.impact_score >= impact_median
        assert finding.effort_score < effort_median
    
    for finding in matrix.high_impact_high_effort:
        assert finding.impact_score >= impact_median
        assert finding.effort_score >= effort_median
    
    for finding in matrix.low_impact_low_effort:
        assert finding.impact_score < impact_median
        assert finding.effort_score < effort_median
    
    for finding in matrix.low_impact_high_effort:
        assert finding.impact_score < impact_median
        assert finding.effort_score >= effort_median

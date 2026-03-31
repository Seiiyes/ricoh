"""Tests para SeverityClassifier."""
import pytest
from hypothesis import given, strategies as st
from audit_system.classifiers.severity_classifier import SeverityClassifier
from audit_system.models import Finding, Severity

class TestSeverityClassifier:
    @pytest.fixture
    def classifier(self):
        return SeverityClassifier()
    
    def test_classify_hardcoded_secret_as_critical(self, classifier):
        finding = Finding(
            id="SEC-001", category="security", subcategory="hardcoded_secret",
            severity=Severity.BAJO, title="Secret", description="Test",
            file_path="backend/api/auth.py"
        )
        assert classifier.classify(finding) == Severity.CRITICO
    
    def test_classify_function_over_100_lines_as_critical(self, classifier):
        finding = Finding(
            id="QUAL-001", category="quality", subcategory="long_function",
            severity=Severity.BAJO, title="Función larga", description="Test",
            file_path="backend/api/users.py"
        )
        finding.metadata = {"lines": 150}
        assert classifier.classify(finding) == Severity.CRITICO
    
    def test_classify_cvss_9_as_critical(self, classifier):
        finding = Finding(
            id="SEC-002", category="security", subcategory="vulnerability",
            severity=Severity.BAJO, title="Vuln", description="Test",
            file_path="requirements.txt"
        )
        finding.metadata = {"cvss_score": 9.5}
        assert classifier.classify(finding) == Severity.CRITICO
    
    def test_classify_n_plus_one_over_100_as_high(self, classifier):
        finding = Finding(
            id="PERF-001", category="performance", subcategory="n_plus_one",
            severity=Severity.BAJO, title="N+1", description="Test",
            file_path="backend/db/repository.py"
        )
        finding.metadata = {"records": 150}
        assert classifier.classify(finding) == Severity.ALTO
    
    def test_classify_no_db_exception_as_high(self, classifier):
        finding = Finding(
            id="ERR-001", category="error_handling", subcategory="no_db_exception_handling",
            severity=Severity.BAJO, title="No DB exception", description="Test",
            file_path="backend/api/printers.py"
        )
        assert classifier.classify(finding) == Severity.ALTO
    
    def test_classify_type_any_as_medium(self, classifier):
        finding = Finding(
            id="QUAL-003", category="quality", subcategory="type_any",
            severity=Severity.BAJO, title="Type any", description="Test",
            file_path="src/components/UserList.tsx"
        )
        assert classifier.classify(finding) == Severity.MEDIO
    
    def test_classify_missing_type_hints_as_medium(self, classifier):
        finding = Finding(
            id="QUAL-004", category="quality", subcategory="missing_type_hints",
            severity=Severity.BAJO, title="No type hints", description="Test",
            file_path="backend/services/printer_service.py"
        )
        assert classifier.classify(finding) == Severity.MEDIO
    
    def test_classify_todo_comment_as_low(self, classifier):
        finding = Finding(
            id="QUAL-007", category="quality", subcategory="todo_comment",
            severity=Severity.BAJO, title="TODO", description="Test",
            file_path="backend/api/counters.py"
        )
        assert classifier.classify(finding) == Severity.BAJO
    
    def test_classify_console_log_as_low(self, classifier):
        finding = Finding(
            id="QUAL-009", category="quality", subcategory="console_log",
            severity=Severity.BAJO, title="console.log", description="Test",
            file_path="src/services/api.ts"
        )
        assert classifier.classify(finding) == Severity.BAJO

@given(cvss_score=st.floats(min_value=9.0, max_value=10.0, allow_nan=False, allow_infinity=False))
def test_property_cvss_9_or_higher_always_critical(cvss_score):
    """**Validates: Requirements 4.8, 14.7**"""
    classifier = SeverityClassifier()
    finding = Finding(
        id="SEC-PBT", category="security", subcategory="vulnerability",
        severity=Severity.BAJO, title="Vuln", description="Test",
        file_path="requirements.txt"
    )
    finding.metadata = {"cvss_score": cvss_score}
    assert classifier.classify(finding) == Severity.CRITICO

@given(lines=st.integers(min_value=101, max_value=1000))
def test_property_function_over_100_lines_always_critical(lines):
    """**Validates: Requirements 3.8**"""
    classifier = SeverityClassifier()
    finding = Finding(
        id="QUAL-PBT", category="quality", subcategory="long_function",
        severity=Severity.BAJO, title="Función larga", description="Test",
        file_path="backend/api/test.py"
    )
    finding.metadata = {"lines": lines}
    assert classifier.classify(finding) == Severity.CRITICO

@given(records=st.integers(min_value=101, max_value=10000))
def test_property_n_plus_one_over_100_records_always_high(records):
    """**Validates: Requirements 2.7**"""
    classifier = SeverityClassifier()
    finding = Finding(
        id="PERF-PBT", category="performance", subcategory="n_plus_one",
        severity=Severity.BAJO, title="N+1", description="Test",
        file_path="backend/db/repository.py"
    )
    finding.metadata = {"records": records}
    assert classifier.classify(finding) == Severity.ALTO
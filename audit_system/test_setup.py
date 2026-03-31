"""
Script de verificación de la configuración del sistema de auditoría.
Valida que todos los componentes estén correctamente configurados.
"""

from audit_system.models import (
    Severity, Finding, ProjectStructure, CodeMetrics,
    Dependency, Vulnerability, PriorityMatrix, RefactorPlan, AnalysisResult
)
from audit_system.config import get_config
from audit_system.logger import setup_logger


def test_models():
    """Verifica que todos los modelos funcionen correctamente."""
    print("Testing models...")
    
    # Test Severity
    assert Severity.CRITICO.get_emoji() == "🔴"
    assert Severity.CRITICO.get_weight() == 4
    
    # Test Finding
    finding = Finding(
        id="F001",
        category="quality",
        subcategory="long_function",
        severity=Severity.CRITICO,
        title="Test Finding",
        description="Test description",
        file_path="test.py"
    )
    assert finding.severity == Severity.CRITICO
    
    # Test CodeMetrics
    metrics = CodeMetrics(backend_total_lines=1000)
    assert metrics.backend_total_lines == 1000
    
    # Test ProjectStructure
    structure = ProjectStructure(root_path="/test", metrics=metrics)
    assert structure.root_path == "/test"
    
    print("✓ All models working correctly")


def test_config():
    """Verifica que la configuración tenga los valores correctos."""
    print("\nTesting configuration...")
    
    config = get_config()
    
    # Verificar umbrales según requirements
    assert config.LARGE_FILE_THRESHOLD == 300
    assert config.LONG_FUNCTION_THRESHOLD == 50
    assert config.DEEP_NESTING_THRESHOLD == 3
    assert config.CODE_DUPLICATION_THRESHOLD == 0.8
    assert config.CRITICAL_FUNCTION_THRESHOLD == 100
    
    print("✓ Configuration values correct")


def test_logger():
    """Verifica que el logger funcione correctamente."""
    print("\nTesting logger...")
    
    logger = setup_logger("test_audit")
    logger.info("Test log message")
    
    print("✓ Logger working correctly")


def main():
    """Ejecuta todas las verificaciones."""
    print("=" * 60)
    print("VERIFICACIÓN DEL SISTEMA DE AUDITORÍA")
    print("=" * 60)
    
    test_models()
    test_config()
    test_logger()
    
    print("\n" + "=" * 60)
    print("✓ TODAS LAS VERIFICACIONES COMPLETADAS EXITOSAMENTE")
    print("=" * 60)
    print("\nEstructura del proyecto configurada:")
    print("  - audit_system/models.py: Modelos de datos")
    print("  - audit_system/config.py: Configuración y umbrales")
    print("  - audit_system/logger.py: Sistema de logging")
    print("  - audit_system/logs/: Directorio de logs")


if __name__ == "__main__":
    main()

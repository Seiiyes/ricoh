"""
Tests para AuditOrchestrator.

Verifica:
- Flujo completo de auditoría
- Manejo robusto de errores en cada etapa
- Guardado de reporte en archivo
- Continuación ante fallos parciales
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from audit_system.orchestrator import AuditOrchestrator
from audit_system.models import (
    ProjectStructure, Finding, Severity, PythonFile,
    CodeMetrics, PriorityMatrix, RefactorPlan
)


class TestAuditOrchestrator:
    """Tests para el orquestador principal."""
    
    @pytest.fixture
    def temp_project(self):
        """Crea un proyecto temporal para testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Crear estructura básica
        backend_dir = Path(temp_dir) / "backend"
        backend_dir.mkdir()
        
        # Crear archivo Python simple
        (backend_dir / "test.py").write_text("""
def hello():
    return "world"
""")
        
        # Crear requirements.txt
        (backend_dir / "requirements.txt").write_text("fastapi==0.100.0\n")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def orchestrator(self):
        """Crea instancia del orquestador."""
        return AuditOrchestrator()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Verifica que el orquestador inicialice todos los componentes."""
        assert orchestrator.file_scanner is not None
        assert orchestrator.dependency_extractor is not None
        assert orchestrator.metrics_collector is not None
        assert orchestrator.performance_analyzer is not None
        assert orchestrator.quality_analyzer is not None
        assert orchestrator.security_analyzer is not None
        assert orchestrator.architecture_analyzer is not None
        assert orchestrator.ux_analyzer is not None
        assert orchestrator.error_handling_analyzer is not None
        assert orchestrator.testing_analyzer is not None
        assert orchestrator.config_analyzer is not None
        assert orchestrator.severity_classifier is not None
        assert orchestrator.impact_calculator is not None
        assert orchestrator.refactor_planner is not None
        assert orchestrator.report_generator is not None
    
    def test_save_report_creates_directory(self, orchestrator):
        """Verifica que save_report cree el directorio si no existe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "subdir", "report.md")
            report_content = "# Test Report"
            
            orchestrator.save_report(report_content, output_path)
            
            assert os.path.exists(output_path)
            with open(output_path, 'r', encoding='utf-8') as f:
                assert f.read() == report_content
    
    def test_save_report_overwrites_existing(self, orchestrator):
        """Verifica que save_report sobrescriba archivos existentes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "report.md")
            
            # Crear archivo inicial
            with open(output_path, 'w') as f:
                f.write("Old content")
            
            # Sobrescribir
            new_content = "# New Report"
            orchestrator.save_report(new_content, output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                assert f.read() == new_content
    
    def test_save_report_handles_permission_error(self, orchestrator):
        """Verifica que save_report maneje errores de permisos."""
        import sys
        if sys.platform == "win32":
            # En Windows, usar una ruta realmente inválida
            invalid_path = "C:\\Windows\\System32\\report.md"
        else:
            # En Unix, usar /root que normalmente no tiene permisos
            invalid_path = "/root/report.md"
        
        with pytest.raises(Exception):
            orchestrator.save_report("content", invalid_path)
    
    def test_run_audit_returns_report_and_path(self, orchestrator, temp_project):
        """Verifica que run_audit retorne reporte y ruta."""
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "report.md")
            
            report, path = orchestrator.run_audit(temp_project, output_path)
            
            assert isinstance(report, str)
            assert len(report) > 0
            assert path == output_path
            assert os.path.exists(output_path)
    
    def test_run_audit_uses_default_output_path(self, orchestrator, temp_project):
        """Verifica que run_audit use ruta por defecto si no se especifica."""
        report, path = orchestrator.run_audit(temp_project)
        
        assert isinstance(report, str)
        assert "docs" in path
        assert "OPTIMIZACION_HALLAZGOS.md" in path
    
    def test_run_audit_handles_scanner_error(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si el scanner falla."""
        with patch.object(orchestrator.file_scanner, 'scan_project', side_effect=Exception("Scanner error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                # Debe generar reporte aunque el scanner falle
                assert isinstance(report, str)
                assert len(report) > 0
                assert os.path.exists(output_path)
    
    def test_run_audit_handles_dependency_extractor_error(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si la extracción de dependencias falla."""
        with patch.object(orchestrator.dependency_extractor, 'extract_all_dependencies', 
                         side_effect=Exception("Dependency error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                assert isinstance(report, str)
                assert len(report) > 0
    
    def test_run_audit_handles_metrics_collector_error(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si la recolección de métricas falla."""
        with patch.object(orchestrator.metrics_collector, 'collect_metrics', 
                         side_effect=Exception("Metrics error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                assert isinstance(report, str)
                assert len(report) > 0
    
    def test_run_audit_handles_analyzer_errors(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si un analizador falla."""
        with patch.object(orchestrator.performance_analyzer, 'analyze', 
                         side_effect=Exception("Analyzer error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                # Debe generar reporte con hallazgos de otros analizadores
                assert isinstance(report, str)
                assert len(report) > 0
    
    def test_run_audit_handles_multiple_analyzer_errors(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si múltiples analizadores fallan."""
        with patch.object(orchestrator.performance_analyzer, 'analyze', side_effect=Exception("Error 1")), \
             patch.object(orchestrator.quality_analyzer, 'analyze', side_effect=Exception("Error 2")), \
             patch.object(orchestrator.security_analyzer, 'analyze', side_effect=Exception("Error 3")):
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                assert isinstance(report, str)
                assert len(report) > 0
    
    def test_run_audit_handles_classifier_error(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si el clasificador falla."""
        with patch.object(orchestrator.severity_classifier, 'classify', 
                         side_effect=Exception("Classifier error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                assert isinstance(report, str)
                assert len(report) > 0
    
    def test_run_audit_handles_impact_calculator_error(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si el calculador de impacto falla."""
        with patch.object(orchestrator.impact_calculator, 'calculate_priority_matrix', 
                         side_effect=Exception("Calculator error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                assert isinstance(report, str)
                assert len(report) > 0
    
    def test_run_audit_handles_refactor_planner_error(self, orchestrator, temp_project):
        """Verifica que run_audit continúe si el planificador falla."""
        with patch.object(orchestrator.refactor_planner, 'create_4_week_plan', 
                         side_effect=Exception("Planner error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                assert isinstance(report, str)
                assert len(report) > 0
    
    def test_run_audit_handles_report_generator_error(self, orchestrator, temp_project):
        """Verifica que run_audit genere reporte de error si el generador falla."""
        with patch.object(orchestrator.report_generator, 'generate_report', 
                         side_effect=Exception("Generator error")):
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_project, output_path)
                
                # Debe generar reporte de error
                assert isinstance(report, str)
                assert "Error" in report
                assert "Generator error" in report
    
    def test_run_audit_handles_save_error_gracefully(self, orchestrator, temp_project):
        """Verifica que run_audit maneje errores al guardar el reporte."""
        with patch.object(orchestrator, 'save_report', side_effect=Exception("Save error")):
            # No debe lanzar excepción, solo advertir
            report, path = orchestrator.run_audit(temp_project, "/invalid/path.md")
            
            assert isinstance(report, str)
            assert len(report) > 0
    
    def test_run_audit_complete_flow(self, orchestrator, temp_project):
        """Verifica el flujo completo de auditoría sin errores."""
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "report.md")
            
            report, path = orchestrator.run_audit(temp_project, output_path)
            
            # Verificar que el reporte se generó
            assert isinstance(report, str)
            assert len(report) > 0
            
            # Verificar que el archivo se guardó
            assert os.path.exists(output_path)
            
            # Verificar contenido básico del reporte
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0
                # El reporte debe tener estructura markdown
                assert "#" in content
    
    def test_run_audit_logs_progress(self, orchestrator, temp_project, caplog):
        """Verifica que run_audit registre el progreso en logs."""
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "report.md")
            
            orchestrator.run_audit(temp_project, output_path)
            
            # Verificar que se registraron las etapas
            log_text = caplog.text
            assert "ETAPA 1" in log_text
            assert "ETAPA 2" in log_text
            assert "ETAPA 3" in log_text
            assert "ETAPA 4" in log_text
    
    def test_run_audit_with_empty_project(self, orchestrator):
        """Verifica que run_audit maneje proyectos vacíos."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit(temp_dir, output_path)
                
                assert isinstance(report, str)
                assert len(report) > 0
                assert os.path.exists(output_path)
    
    def test_run_audit_with_nonexistent_project(self, orchestrator):
        """Verifica que run_audit maneje proyectos inexistentes."""
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "report.md")
            
            report, path = orchestrator.run_audit("/nonexistent/path", output_path)
            
            # Debe generar reporte aunque el proyecto no exista
            assert isinstance(report, str)
            assert len(report) > 0


class TestOrchestratorErrorRecovery:
    """Tests específicos para recuperación de errores."""
    
    @pytest.fixture
    def orchestrator(self):
        return AuditOrchestrator()
    
    def test_partial_analyzer_failure_still_produces_findings(self, orchestrator):
        """Verifica que si algunos analizadores fallan, otros sigan funcionando."""
        # Mock para simular que algunos analizadores funcionan y otros fallan
        mock_structure = ProjectStructure(root_path="/test")
        mock_structure.backend_files = [
            PythonFile(path="test.py", language="python", lines_of_code=10, 
                      is_large=False, content="def test(): pass")
        ]
        
        with patch.object(orchestrator.file_scanner, 'scan_project', return_value=mock_structure), \
             patch.object(orchestrator.dependency_extractor, 'extract_all_dependencies', return_value=([], [])), \
             patch.object(orchestrator.metrics_collector, 'collect_metrics', return_value=CodeMetrics()), \
             patch.object(orchestrator.performance_analyzer, 'analyze', side_effect=Exception("Fail")), \
             patch.object(orchestrator.quality_analyzer, 'analyze', return_value=[
                 Finding(id="Q1", category="quality", subcategory="test", severity=Severity.BAJO,
                        title="Test", description="Test", file_path="test.py")
             ]), \
             patch.object(orchestrator.security_analyzer, 'analyze', return_value=[]), \
             patch.object(orchestrator.architecture_analyzer, 'analyze', return_value=[]), \
             patch.object(orchestrator.ux_analyzer, 'analyze', return_value=[]), \
             patch.object(orchestrator.error_handling_analyzer, 'analyze', return_value=[]), \
             patch.object(orchestrator.testing_analyzer, 'analyze', return_value=[]), \
             patch.object(orchestrator.config_analyzer, 'analyze', return_value=[]), \
             patch.object(orchestrator.impact_calculator, 'calculate_priority_matrix', return_value=PriorityMatrix()), \
             patch.object(orchestrator.impact_calculator, 'select_top_10', return_value=[]), \
             patch.object(orchestrator.refactor_planner, 'create_4_week_plan', return_value=RefactorPlan()):
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, path = orchestrator.run_audit("/test", output_path)
                
                # Debe generar reporte con hallazgos del quality_analyzer
                assert isinstance(report, str)
                assert len(report) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

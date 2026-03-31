"""
Tests de integración end-to-end para el sistema de auditoría.

Verifica:
- Flujo completo desde proyecto de prueba hasta reporte generado
- Detección de patrones conocidos en código de prueba
- Generación correcta de todas las secciones del reporte
- Integración entre todos los componentes del sistema
"""

import os
import tempfile
import shutil
from pathlib import Path

import pytest

from audit_system.orchestrator import AuditOrchestrator


class TestIntegrationEndToEnd:
    """Tests de integración end-to-end del sistema completo."""
    
    @pytest.fixture
    def test_project(self):
        """Crea un proyecto de prueba con patrones conocidos."""
        temp_dir = tempfile.mkdtemp()
        
        # Crear estructura Backend
        backend_dir = Path(temp_dir) / "backend"
        backend_dir.mkdir()
        
        # Archivo con función larga (patrón conocido)
        (backend_dir / "long_function.py").write_text("""
def very_long_function():
    # Esta función tiene más de 50 líneas
    line_1 = 1
    line_2 = 2
    line_3 = 3
    line_4 = 4
    line_5 = 5
    line_6 = 6
    line_7 = 7
    line_8 = 8
    line_9 = 9
    line_10 = 10
    line_11 = 11
    line_12 = 12
    line_13 = 13
    line_14 = 14
    line_15 = 15
    line_16 = 16
    line_17 = 17
    line_18 = 18
    line_19 = 19
    line_20 = 20
    line_21 = 21
    line_22 = 22
    line_23 = 23
    line_24 = 24
    line_25 = 25
    line_26 = 26
    line_27 = 27
    line_28 = 28
    line_29 = 29
    line_30 = 30
    line_31 = 31
    line_32 = 32
    line_33 = 33
    line_34 = 34
    line_35 = 35
    line_36 = 36
    line_37 = 37
    line_38 = 38
    line_39 = 39
    line_40 = 40
    line_41 = 41
    line_42 = 42
    line_43 = 43
    line_44 = 44
    line_45 = 45
    line_46 = 46
    line_47 = 47
    line_48 = 48
    line_49 = 49
    line_50 = 50
    line_51 = 51
    return line_51
""")
        
        # Archivo con secret hardcodeado (patrón conocido)
        (backend_dir / "secrets.py").write_text("""
# Configuración de API
api_key = "sk-1234567890abcdef"
password = "admin123"

def connect_to_api():
    return api_key
""")
        
        # Archivo con indentación profunda (patrón conocido)
        (backend_dir / "deep_nesting.py").write_text("""
def process_data(data):
    if data:
        for item in data:
            if item.valid:
                if item.active:
                    if item.priority > 5:
                        return item
    return None
""")
        
        # Archivo con type any (TypeScript)
        frontend_dir = Path(temp_dir) / "frontend" / "src"
        frontend_dir.mkdir(parents=True)
        
        (frontend_dir / "component.tsx").write_text("""
import React from 'react';

interface Props {
    data: any;  // Type any detectado
    callback: any;
}

export const MyComponent: React.FC<Props> = ({ data, callback }) => {
    return <div>{data}</div>;
};
""")
        
        # Archivo requirements.txt
        (backend_dir / "requirements.txt").write_text("""
fastapi==0.100.0
pydantic==2.0.0
sqlalchemy==2.0.0
""")
        
        # Archivo package.json
        (frontend_dir.parent / "package.json").write_text("""
{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
""")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_end_to_end_audit_generates_report(self, test_project):
        """Verifica que la auditoría end-to-end genere un reporte completo."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            
            # Ejecutar auditoría completa
            report, path = orchestrator.run_audit(test_project, output_path)
            
            # Verificar que se generó el reporte
            assert isinstance(report, str)
            assert len(report) > 0
            assert os.path.exists(output_path)
            
            # Verificar que el archivo contiene el reporte
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert content == report
    
    def test_end_to_end_detects_known_patterns(self, test_project):
        """Verifica que el sistema detecte patrones conocidos en el proyecto de prueba."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            
            report, _ = orchestrator.run_audit(test_project, output_path)
            
            # Verificar detección de función larga
            assert "long_function" in report or "función larga" in report.lower() or "líneas" in report
            
            # Verificar detección de secrets
            assert "secret" in report.lower() or "api_key" in report or "password" in report
            
            # Verificar detección de indentación profunda
            assert "indentación" in report.lower() or "nesting" in report.lower() or "anidación" in report.lower()
            
            # Verificar detección de type any
            assert "any" in report.lower() or "tipo" in report.lower()
    
    def test_end_to_end_report_has_required_sections(self, test_project):
        """Verifica que el reporte contenga todas las secciones requeridas."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            
            report, _ = orchestrator.run_audit(test_project, output_path)
            
            # Verificar secciones principales
            assert "# Reporte de Auditoría" in report or "# Análisis" in report
            
            # Verificar resumen ejecutivo
            assert "Resumen" in report or "Summary" in report
            
            # Verificar que tenga estructura markdown
            assert report.count("#") >= 3  # Al menos 3 headers
            
            # Verificar que tenga contenido sustancial
            assert len(report) > 500  # Reporte debe tener contenido significativo
    
    def test_end_to_end_report_includes_metrics(self, test_project):
        """Verifica que el reporte incluya métricas del código."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            
            report, _ = orchestrator.run_audit(test_project, output_path)
            
            # Verificar que incluya métricas
            assert "líneas" in report.lower() or "lines" in report.lower()
            assert "archivos" in report.lower() or "files" in report.lower()
    
    def test_end_to_end_report_includes_severity_classification(self, test_project):
        """Verifica que el reporte incluya clasificación de severidades."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            
            report, _ = orchestrator.run_audit(test_project, output_path)
            
            # Verificar que incluya emojis de severidad
            has_severity_indicators = (
                "🔴" in report or "🟠" in report or "🟡" in report or "🟢" in report or
                "CRITICO" in report or "ALTO" in report or "MEDIO" in report or "BAJO" in report or
                "Crítico" in report or "Alto" in report or "Medio" in report or "Bajo" in report
            )
            assert has_severity_indicators
    
    def test_end_to_end_report_includes_file_locations(self, test_project):
        """Verifica que el reporte incluya ubicaciones exactas de archivos."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            
            report, _ = orchestrator.run_audit(test_project, output_path)
            
            # Verificar que incluya referencias a archivos
            assert ".py" in report or ".tsx" in report or ".ts" in report
    
    def test_end_to_end_no_source_modification(self, test_project):
        """Verifica que la auditoría no modifique archivos fuente."""
        # Guardar checksums de archivos antes de la auditoría
        import hashlib
        
        def get_file_hash(filepath):
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        
        # Recolectar hashes de todos los archivos
        file_hashes = {}
        for root, dirs, files in os.walk(test_project):
            # Excluir directorios de output
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            for file in files:
                if file.endswith(('.py', '.ts', '.tsx', '.txt', '.json')):
                    filepath = os.path.join(root, file)
                    file_hashes[filepath] = get_file_hash(filepath)
        
        # Ejecutar auditoría
        orchestrator = AuditOrchestrator()
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            orchestrator.run_audit(test_project, output_path)
        
        # Verificar que ningún archivo fuente cambió
        for filepath, original_hash in file_hashes.items():
            current_hash = get_file_hash(filepath)
            assert current_hash == original_hash, f"Archivo modificado: {filepath}"
    
    def test_end_to_end_with_multiple_file_types(self, test_project):
        """Verifica que el sistema maneje múltiples tipos de archivos."""
        # Agregar más archivos de diferentes tipos
        backend_dir = Path(test_project) / "backend"
        
        # Archivo con query N+1
        (backend_dir / "repository.py").write_text("""
def get_users_with_posts(db):
    users = db.query(User).all()
    for user in users:
        posts = db.query(Post).filter(Post.user_id == user.id).all()
        user.posts = posts
    return users
""")
        
        # Archivo con console.log
        frontend_dir = Path(test_project) / "frontend" / "src"
        (frontend_dir / "debug.tsx").write_text("""
export const DebugComponent = () => {
    console.log("Debug info");
    console.error("Error info");
    return <div>Debug</div>;
};
""")
        
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "test_report.md")
            
            report, _ = orchestrator.run_audit(test_project, output_path)
            
            # Verificar que detectó múltiples tipos de patrones
            assert len(report) > 1000  # Reporte sustancial
            
            # Verificar que menciona diferentes archivos
            assert "repository.py" in report or "debug.tsx" in report or ".py" in report


class TestIntegrationReportStructure:
    """Tests de integración para verificar estructura del reporte."""
    
    @pytest.fixture
    def simple_project(self):
        """Crea un proyecto simple para testing."""
        temp_dir = tempfile.mkdtemp()
        
        backend_dir = Path(temp_dir) / "backend"
        backend_dir.mkdir()
        
        (backend_dir / "simple.py").write_text("""
def simple_function():
    return "hello"
""")
        
        (backend_dir / "requirements.txt").write_text("fastapi==0.100.0\n")
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_report_is_valid_markdown(self, simple_project):
        """Verifica que el reporte sea markdown válido."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "report.md")
            
            report, _ = orchestrator.run_audit(simple_project, output_path)
            
            # Verificar estructura markdown básica
            assert report.startswith("#")  # Debe empezar con header
            assert "\n" in report  # Debe tener múltiples líneas
            
            # Verificar que no tenga errores de formato obvios
            assert report.count("```") % 2 == 0  # Bloques de código balanceados
    
    def test_report_includes_timestamp(self, simple_project):
        """Verifica que el reporte incluya fecha de generación."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "report.md")
            
            report, _ = orchestrator.run_audit(simple_project, output_path)
            
            # Verificar que incluya fecha
            import datetime
            current_year = str(datetime.datetime.now().year)
            assert current_year in report
    
    def test_report_saved_to_correct_location(self, simple_project):
        """Verifica que el reporte se guarde en la ubicación correcta."""
        orchestrator = AuditOrchestrator()
        
        with tempfile.TemporaryDirectory() as output_dir:
            custom_path = os.path.join(output_dir, "custom", "my_report.md")
            
            report, path = orchestrator.run_audit(simple_project, custom_path)
            
            # Verificar que se creó en la ubicación especificada
            assert os.path.exists(custom_path)
            assert path == custom_path
            
            # Verificar que el contenido es correcto
            with open(custom_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
                assert saved_content == report


class TestIntegrationPatternDetection:
    """Tests de integración para verificar detección de patrones específicos."""
    
    def test_detects_hardcoded_secrets(self):
        """Verifica detección de secrets hardcodeados."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            backend_dir = Path(temp_dir) / "backend"
            backend_dir.mkdir()
            
            (backend_dir / "config.py").write_text("""
DATABASE_URL = "postgresql://user:password123@localhost/db"
API_KEY = "sk-secret-key-12345"
""")
            
            orchestrator = AuditOrchestrator()
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                report, _ = orchestrator.run_audit(temp_dir, output_path)
                
                # Debe detectar secrets
                assert "password" in report.lower() or "secret" in report.lower() or "api" in report.lower()
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detects_long_functions(self):
        """Verifica detección de funciones largas."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            backend_dir = Path(temp_dir) / "backend"
            backend_dir.mkdir()
            
            # Crear función con exactamente 60 líneas
            lines = ["def long_func():"]
            lines.extend([f"    line_{i} = {i}" for i in range(58)])
            lines.append("    return line_57")
            
            (backend_dir / "long.py").write_text("\n".join(lines))
            
            orchestrator = AuditOrchestrator()
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                report, _ = orchestrator.run_audit(temp_dir, output_path)
                
                # Debe detectar función larga
                assert "long_func" in report or "función" in report.lower() or "líneas" in report.lower()
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detects_deep_nesting(self):
        """Verifica detección de indentación profunda."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            backend_dir = Path(temp_dir) / "backend"
            backend_dir.mkdir()
            
            (backend_dir / "nested.py").write_text("""
def process(data):
    if data:
        for item in data:
            if item.valid:
                if item.active:
                    return item
""")
            
            orchestrator = AuditOrchestrator()
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                report, _ = orchestrator.run_audit(temp_dir, output_path)
                
                # Debe detectar indentación profunda
                assert "indentación" in report.lower() or "nesting" in report.lower() or "anidación" in report.lower()
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detects_type_any(self):
        """Verifica detección de type any en TypeScript."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            frontend_dir = Path(temp_dir) / "frontend" / "src"
            frontend_dir.mkdir(parents=True)
            
            (frontend_dir / "types.tsx").write_text("""
interface User {
    id: number;
    data: any;
    metadata: any;
}
""")
            
            orchestrator = AuditOrchestrator()
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                report, _ = orchestrator.run_audit(temp_dir, output_path)
                
                # Debe detectar type any
                assert "any" in report.lower() or "tipo" in report.lower()
        
        finally:
            shutil.rmtree(temp_dir)


class TestIntegrationErrorHandling:
    """Tests de integración para manejo de errores."""
    
    def test_handles_invalid_python_syntax(self):
        """Verifica que el sistema maneje archivos con sintaxis inválida."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            backend_dir = Path(temp_dir) / "backend"
            backend_dir.mkdir()
            
            # Archivo con sintaxis inválida
            (backend_dir / "invalid.py").write_text("""
def broken_function(
    # Sintaxis incompleta
""")
            
            # Archivo válido
            (backend_dir / "valid.py").write_text("""
def valid_function():
    return True
""")
            
            orchestrator = AuditOrchestrator()
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                # No debe lanzar excepción
                report, _ = orchestrator.run_audit(temp_dir, output_path)
                
                # Debe generar reporte (posiblemente con advertencias)
                assert isinstance(report, str)
                assert len(report) > 0
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_handles_empty_project(self):
        """Verifica que el sistema maneje proyectos vacíos."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            orchestrator = AuditOrchestrator()
            
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = os.path.join(output_dir, "report.md")
                
                report, _ = orchestrator.run_audit(temp_dir, output_path)
                
                # Debe generar reporte aunque esté vacío
                assert isinstance(report, str)
                assert len(report) > 0
                assert os.path.exists(output_path)
        
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

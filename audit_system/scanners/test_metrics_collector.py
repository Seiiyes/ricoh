"""
Tests para MetricsCollector.

Incluye unit tests y property-based tests para verificar la correctitud
de la recolección de métricas del código.
"""

import tempfile
import os

import pytest
from hypothesis import given, settings, strategies as st

from audit_system.scanners.metrics_collector import MetricsCollector
from audit_system.models import (
    ProjectStructure, PythonFile, TypeScriptFile, 
    Dependency, Vulnerability, CodeMetrics
)
from audit_system.config import get_config


class TestMetricsCollector:
    """Tests unitarios para MetricsCollector."""
    
    def test_count_total_lines_empty_list(self):
        """Verifica conteo de líneas con lista vacía."""
        collector = MetricsCollector()
        
        total = collector.count_total_lines([])
        assert total == 0
    
    def test_count_total_lines_single_file(self):
        """Verifica conteo de líneas con un solo archivo."""
        collector = MetricsCollector()
        
        files = [
            PythonFile(
                path="test.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="# test"
            )
        ]
        
        total = collector.count_total_lines(files)
        assert total == 100
    
    def test_count_total_lines_multiple_files(self):
        """Verifica conteo de líneas con múltiples archivos."""
        collector = MetricsCollector()
        
        files = [
            PythonFile(path="a.py", language="python", lines_of_code=50, 
                      is_large=False, content=""),
            PythonFile(path="b.py", language="python", lines_of_code=150, 
                      is_large=False, content=""),
            PythonFile(path="c.py", language="python", lines_of_code=200, 
                      is_large=False, content="")
        ]
        
        total = collector.count_total_lines(files)
        assert total == 400
    
    def test_count_large_files(self):
        """Verifica conteo de archivos grandes."""
        collector = MetricsCollector()
        
        files = [
            PythonFile(path="small.py", language="python", lines_of_code=100, 
                      is_large=False, content=""),
            PythonFile(path="large1.py", language="python", lines_of_code=350, 
                      is_large=True, content=""),
            PythonFile(path="large2.py", language="python", lines_of_code=500, 
                      is_large=True, content="")
        ]
        
        count = collector.count_large_files(files)
        assert count == 2
    
    def test_count_long_functions_no_functions(self):
        """Verifica conteo con archivo sin funciones."""
        collector = MetricsCollector()
        
        files = [
            PythonFile(
                path="test.py",
                language="python",
                lines_of_code=10,
                is_large=False,
                content="# Just a comment\nx = 1\ny = 2\n"
            )
        ]
        
        count = collector.count_long_functions(files)
        assert count == 0
    
    def test_count_long_functions_short_function(self):
        """Verifica que funciones cortas no se cuenten."""
        collector = MetricsCollector()
        
        code = """
def short_function():
    x = 1
    y = 2
    return x + y
"""
        
        files = [
            PythonFile(
                path="test.py",
                language="python",
                lines_of_code=5,
                is_large=False,
                content=code
            )
        ]
        
        count = collector.count_long_functions(files)
        assert count == 0
    
    def test_count_long_functions_long_function(self):
        """Verifica detección de función larga (>50 líneas)."""
        collector = MetricsCollector()
        
        # Generar función con más de 50 líneas
        lines = ["def long_function():"]
        for i in range(55):
            lines.append(f"    line_{i} = {i}")
        lines.append("    return True")
        code = "\n".join(lines)
        
        files = [
            PythonFile(
                path="test.py",
                language="python",
                lines_of_code=len(lines),
                is_large=False,
                content=code
            )
        ]
        
        count = collector.count_long_functions(files)
        assert count == 1
    
    def test_count_long_functions_multiple_functions(self):
        """Verifica conteo con múltiples funciones."""
        collector = MetricsCollector()
        
        # Función corta
        short_func = "def short():\n    return 1\n\n"
        
        # Función larga
        long_lines = ["def long_function():"]
        for i in range(55):
            long_lines.append(f"    line_{i} = {i}")
        long_lines.append("    return True")
        long_func = "\n".join(long_lines) + "\n\n"
        
        # Otra función larga
        long_lines2 = ["def another_long():"]
        for i in range(60):
            long_lines2.append(f"    x_{i} = {i}")
        long_lines2.append("    return x_0")
        long_func2 = "\n".join(long_lines2)
        
        code = short_func + long_func + long_func2
        
        files = [
            PythonFile(
                path="test.py",
                language="python",
                lines_of_code=code.count('\n'),
                is_large=False,
                content=code
            )
        ]
        
        count = collector.count_long_functions(files)
        assert count == 2
    
    def test_count_long_functions_async_function(self):
        """Verifica detección de funciones async largas."""
        collector = MetricsCollector()
        
        lines = ["async def async_long_function():"]
        for i in range(55):
            lines.append(f"    await something_{i}()")
        lines.append("    return True")
        code = "\n".join(lines)
        
        files = [
            PythonFile(
                path="test.py",
                language="python",
                lines_of_code=len(lines),
                is_large=False,
                content=code
            )
        ]
        
        count = collector.count_long_functions(files)
        assert count == 1
    
    def test_count_long_functions_syntax_error(self):
        """Verifica manejo de errores de sintaxis."""
        collector = MetricsCollector()
        
        # Código con error de sintaxis
        code = "def broken_function(\n    # Missing closing parenthesis"
        
        files = [
            PythonFile(
                path="broken.py",
                language="python",
                lines_of_code=2,
                is_large=False,
                content=code
            )
        ]
        
        # No debe lanzar excepción, debe retornar 0
        count = collector.count_long_functions(files)
        assert count == 0
    
    def test_count_large_components_no_components(self):
        """Verifica conteo con archivos que no son componentes."""
        collector = MetricsCollector()
        
        files = [
            TypeScriptFile(
                path="utils.ts",
                language="typescript",
                lines_of_code=100,
                is_large=False,
                content="export const add = (a, b) => a + b;",
                is_component=False
            )
        ]
        
        count = collector.count_large_components(files)
        assert count == 0
    
    def test_count_large_components_small_component(self):
        """Verifica que componentes pequeños no se cuenten."""
        collector = MetricsCollector()
        
        files = [
            TypeScriptFile(
                path="Button.tsx",
                language="typescript",
                lines_of_code=50,
                is_large=False,
                content="export const Button = () => <button>Click</button>;",
                is_component=True
            )
        ]
        
        count = collector.count_large_components(files)
        assert count == 0
    
    def test_count_large_components_large_component(self):
        """Verifica detección de componente grande (>200 líneas)."""
        collector = MetricsCollector()
        
        files = [
            TypeScriptFile(
                path="LargeComponent.tsx",
                language="typescript",
                lines_of_code=250,
                is_large=True,
                content="// Large component",
                is_component=True
            )
        ]
        
        count = collector.count_large_components(files)
        assert count == 1
    
    def test_count_large_components_boundary(self):
        """Verifica comportamiento en el límite de 200 líneas."""
        collector = MetricsCollector()
        
        files = [
            TypeScriptFile(
                path="Exactly200.tsx",
                language="typescript",
                lines_of_code=200,
                is_large=False,
                content="",
                is_component=True
            ),
            TypeScriptFile(
                path="Over200.tsx",
                language="typescript",
                lines_of_code=201,
                is_large=True,
                content="",
                is_component=True
            )
        ]
        
        count = collector.count_large_components(files)
        assert count == 1  # Solo el de 201 líneas
    
    def test_count_outdated_dependencies(self):
        """Verifica conteo de dependencias desactualizadas."""
        collector = MetricsCollector()
        
        dependencies = [
            Dependency(
                name="package1",
                current_version="1.0.0",
                latest_version="2.0.0",
                is_outdated=True,
                ecosystem="python"
            ),
            Dependency(
                name="package2",
                current_version="3.0.0",
                latest_version="3.0.0",
                is_outdated=False,
                ecosystem="python"
            ),
            Dependency(
                name="package3",
                current_version="1.5.0",
                latest_version="2.1.0",
                is_outdated=True,
                ecosystem="npm"
            )
        ]
        
        count = collector.count_outdated_dependencies(dependencies)
        assert count == 2
    
    def test_count_vulnerabilities_no_vulnerabilities(self):
        """Verifica conteo sin vulnerabilidades."""
        collector = MetricsCollector()
        
        dependencies = [
            Dependency(
                name="safe_package",
                current_version="1.0.0",
                latest_version="1.0.0",
                is_outdated=False,
                vulnerabilities=[],
                ecosystem="python"
            )
        ]
        
        count = collector.count_vulnerabilities(dependencies)
        assert count == 0
    
    def test_count_vulnerabilities_with_vulnerabilities(self):
        """Verifica conteo de vulnerabilidades."""
        collector = MetricsCollector()
        
        dependencies = [
            Dependency(
                name="vuln_package1",
                current_version="1.0.0",
                latest_version="2.0.0",
                is_outdated=True,
                vulnerabilities=[
                    Vulnerability(cve_id="CVE-2023-1234", cvss_score=7.5, 
                                description="Test vuln 1"),
                    Vulnerability(cve_id="CVE-2023-5678", cvss_score=9.0, 
                                description="Test vuln 2")
                ],
                ecosystem="python"
            ),
            Dependency(
                name="vuln_package2",
                current_version="2.0.0",
                latest_version="3.0.0",
                is_outdated=True,
                vulnerabilities=[
                    Vulnerability(cve_id="CVE-2023-9999", cvss_score=6.0, 
                                description="Test vuln 3")
                ],
                ecosystem="npm"
            )
        ]
        
        count = collector.count_vulnerabilities(dependencies)
        assert count == 3
    
    def test_collect_metrics_complete(self):
        """Verifica recolección completa de métricas."""
        collector = MetricsCollector()
        
        # Crear estructura de proyecto de prueba
        backend_files = [
            PythonFile(path="api.py", language="python", lines_of_code=400, 
                      is_large=True, content="def long():\n" + "    x=1\n" * 60),
            PythonFile(path="models.py", language="python", lines_of_code=200, 
                      is_large=False, content="class Model: pass")
        ]
        
        frontend_files = [
            TypeScriptFile(path="App.tsx", language="typescript", lines_of_code=250, 
                          is_large=True, content="", is_component=True),
            TypeScriptFile(path="utils.ts", language="typescript", lines_of_code=100, 
                          is_large=False, content="", is_component=False)
        ]
        
        backend_deps = [
            Dependency(name="dep1", current_version="1.0", latest_version="2.0", 
                      is_outdated=True, vulnerabilities=[], ecosystem="python")
        ]
        
        frontend_deps = [
            Dependency(name="dep2", current_version="3.0", latest_version="3.0", 
                      is_outdated=False, vulnerabilities=[
                          Vulnerability(cve_id="CVE-123", cvss_score=8.0, description="Test")
                      ], ecosystem="npm")
        ]
        
        structure = ProjectStructure(
            root_path="/test",
            backend_files=backend_files,
            frontend_files=frontend_files,
            backend_dependencies=backend_deps,
            frontend_dependencies=frontend_deps
        )
        
        # Recolectar métricas
        metrics = collector.collect_metrics(structure)
        
        # Verificar métricas de backend
        assert metrics.backend_total_lines == 600
        assert metrics.backend_total_files == 2
        assert metrics.backend_large_files == 1
        assert metrics.backend_long_functions == 1
        assert metrics.backend_dependencies_count == 1
        
        # Verificar métricas de frontend
        assert metrics.frontend_total_lines == 350
        assert metrics.frontend_total_files == 2
        assert metrics.frontend_large_components == 1
        assert metrics.frontend_dependencies_count == 1
        
        # Verificar métricas generales
        assert metrics.total_outdated_dependencies == 1
        assert metrics.total_vulnerabilities == 1


class TestMetricsCollectorProperties:
    """Property-based tests para MetricsCollector."""
    
    @given(
        file_lines=st.lists(st.integers(min_value=1, max_value=1000), min_size=0, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_count_total_lines(self, file_lines):
        """
        Property: For any list of files with N lines each, total lines
        must equal the sum of all individual file lines.
        
        **Validates: Requirements 12.1, 12.2**
        """
        collector = MetricsCollector()
        
        # Crear archivos con las líneas especificadas
        files = [
            PythonFile(
                path=f"file_{i}.py",
                language="python",
                lines_of_code=lines,
                is_large=lines > 300,
                content=""
            )
            for i, lines in enumerate(file_lines)
        ]
        
        total = collector.count_total_lines(files)
        expected = sum(file_lines)
        
        assert total == expected
    
    @given(
        large_count=st.integers(min_value=0, max_value=10),
        small_count=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=100)
    def test_property_count_large_files(self, large_count, small_count):
        """
        Property: For any N large files and M small files, count_large_files
        must return exactly N.
        
        **Validates: Requirements 12.4**
        """
        collector = MetricsCollector()
        
        # Crear archivos grandes
        large_files = [
            PythonFile(
                path=f"large_{i}.py",
                language="python",
                lines_of_code=350,
                is_large=True,
                content=""
            )
            for i in range(large_count)
        ]
        
        # Crear archivos pequeños
        small_files = [
            PythonFile(
                path=f"small_{i}.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content=""
            )
            for i in range(small_count)
        ]
        
        all_files = large_files + small_files
        count = collector.count_large_files(all_files)
        
        assert count == large_count
    
    @given(
        num_short_functions=st.integers(min_value=0, max_value=5),
        num_long_functions=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=50)
    def test_property_count_long_functions(self, num_short_functions, num_long_functions):
        """
        Property: For any file with N short functions and M long functions,
        count_long_functions must return exactly M.
        
        **Validates: Requirements 12.5**
        """
        collector = MetricsCollector()
        config = get_config()
        
        # Generar funciones cortas
        short_functions = []
        for i in range(num_short_functions):
            lines = [f"def short_func_{i}():"]
            for j in range(10):  # 10 líneas < 50
                lines.append(f"    x_{j} = {j}")
            lines.append("    return True")
            short_functions.append("\n".join(lines))
        
        # Generar funciones largas
        long_functions = []
        for i in range(num_long_functions):
            lines = [f"def long_func_{i}():"]
            for j in range(55):  # 55 líneas > 50
                lines.append(f"    y_{j} = {j}")
            lines.append("    return True")
            long_functions.append("\n".join(lines))
        
        # Combinar todo el código
        code = "\n\n".join(short_functions + long_functions)
        
        files = [
            PythonFile(
                path="test.py",
                language="python",
                lines_of_code=code.count('\n'),
                is_large=False,
                content=code
            )
        ]
        
        count = collector.count_long_functions(files)
        assert count == num_long_functions
    
    @given(
        num_small_components=st.integers(min_value=0, max_value=10),
        num_large_components=st.integers(min_value=0, max_value=10),
        num_non_components=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=50)
    def test_property_count_large_components(self, num_small_components, 
                                            num_large_components, num_non_components):
        """
        Property: For any N small components, M large components, and K non-components,
        count_large_components must return exactly M.
        
        **Validates: Requirements 12.6**
        """
        collector = MetricsCollector()
        config = get_config()
        
        files = []
        
        # Componentes pequeños
        for i in range(num_small_components):
            files.append(TypeScriptFile(
                path=f"SmallComp_{i}.tsx",
                language="typescript",
                lines_of_code=100,
                is_large=False,
                content="",
                is_component=True
            ))
        
        # Componentes grandes
        for i in range(num_large_components):
            files.append(TypeScriptFile(
                path=f"LargeComp_{i}.tsx",
                language="typescript",
                lines_of_code=250,
                is_large=True,
                content="",
                is_component=True
            ))
        
        # No componentes
        for i in range(num_non_components):
            files.append(TypeScriptFile(
                path=f"utils_{i}.ts",
                language="typescript",
                lines_of_code=300,
                is_large=True,
                content="",
                is_component=False
            ))
        
        count = collector.count_large_components(files)
        assert count == num_large_components
    
    @given(
        num_outdated=st.integers(min_value=0, max_value=20),
        num_updated=st.integers(min_value=0, max_value=20)
    )
    @settings(max_examples=100)
    def test_property_count_outdated_dependencies(self, num_outdated, num_updated):
        """
        Property: For any N outdated dependencies and M updated dependencies,
        count_outdated_dependencies must return exactly N.
        
        **Validates: Requirements 12.8**
        """
        collector = MetricsCollector()
        
        dependencies = []
        
        # Dependencias desactualizadas
        for i in range(num_outdated):
            dependencies.append(Dependency(
                name=f"outdated_{i}",
                current_version="1.0.0",
                latest_version="2.0.0",
                is_outdated=True,
                ecosystem="python"
            ))
        
        # Dependencias actualizadas
        for i in range(num_updated):
            dependencies.append(Dependency(
                name=f"updated_{i}",
                current_version="2.0.0",
                latest_version="2.0.0",
                is_outdated=False,
                ecosystem="python"
            ))
        
        count = collector.count_outdated_dependencies(dependencies)
        assert count == num_outdated

"""
Tests para FileScanner.

Incluye unit tests y property-based tests para verificar la correctitud
del escaneo de archivos y clasificación de tamaño.
"""

import os
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from audit_system.scanners.file_scanner import FileScanner
from audit_system.config import get_config


class TestFileScanner:
    """Tests unitarios para FileScanner."""
    
    def test_classify_file_size_boundary(self):
        """Verifica clasificación en el límite exacto de 300 líneas."""
        scanner = FileScanner()
        
        # Exactamente 300 líneas - no debe ser "grande"
        assert scanner.classify_file_size(300) is False
        
        # 301 líneas - debe ser "grande"
        assert scanner.classify_file_size(301) is True
        
        # Menos de 300 líneas
        assert scanner.classify_file_size(299) is False
        assert scanner.classify_file_size(1) is False
    
    def test_classify_file_size_edge_cases(self):
        """Verifica casos extremos de clasificación."""
        scanner = FileScanner()
        
        # Archivo vacío
        assert scanner.classify_file_size(0) is False
        
        # Archivo muy grande
        assert scanner.classify_file_size(10000) is True
    
    def test_find_python_files_empty_directory(self):
        """Verifica que el scanner maneje directorios vacíos correctamente."""
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = scanner.find_python_files(temp_dir)
            assert files == []
    
    def test_find_python_files_nonexistent_directory(self):
        """Verifica manejo de directorios inexistentes."""
        scanner = FileScanner()
        
        files = scanner.find_python_files("/path/that/does/not/exist")
        assert files == []
    
    def test_find_python_files_with_files(self):
        """Verifica identificación de archivos Python."""
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivos de prueba
            py_file = os.path.join(temp_dir, "test.py")
            with open(py_file, 'w') as f:
                f.write("# Test file\nprint('hello')\n")
            
            # Crear archivo no-Python
            txt_file = os.path.join(temp_dir, "test.txt")
            with open(txt_file, 'w') as f:
                f.write("Not a Python file")
            
            files = scanner.find_python_files(temp_dir)
            
            # Debe encontrar solo el archivo .py
            assert len(files) == 1
            assert files[0].language == 'python'
            assert files[0].lines_of_code == 2
            assert files[0].is_large is False
    
    def test_find_python_files_excludes_pycache(self):
        """Verifica que se excluyan directorios __pycache__."""
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo Python en directorio principal
            py_file = os.path.join(temp_dir, "main.py")
            with open(py_file, 'w') as f:
                f.write("print('main')\n")
            
            # Crear directorio __pycache__ con archivo
            pycache_dir = os.path.join(temp_dir, "__pycache__")
            os.makedirs(pycache_dir)
            cache_file = os.path.join(pycache_dir, "cached.py")
            with open(cache_file, 'w') as f:
                f.write("# Should be excluded\n")
            
            files = scanner.find_python_files(temp_dir)
            
            # Debe encontrar solo main.py, no el archivo en __pycache__
            assert len(files) == 1
            assert "main.py" in files[0].path
    
    def test_find_typescript_files_with_tsx(self):
        """Verifica identificación de archivos TypeScript y TSX."""
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo .ts
            ts_file = os.path.join(temp_dir, "utils.ts")
            with open(ts_file, 'w') as f:
                f.write("export const add = (a: number, b: number) => a + b;\n")
            
            # Crear archivo .tsx (componente React)
            tsx_file = os.path.join(temp_dir, "Component.tsx")
            with open(tsx_file, 'w') as f:
                f.write("export const Component = () => {\n  return <div>Hello</div>;\n};\n")
            
            files = scanner.find_typescript_files(temp_dir)
            
            # Debe encontrar ambos archivos
            assert len(files) == 2
            
            # Verificar que el .tsx se identifique como componente
            tsx_files = [f for f in files if f.path.endswith('.tsx')]
            assert len(tsx_files) == 1
            assert tsx_files[0].is_component is True
    
    def test_find_python_files_large_file(self):
        """Verifica clasificación de archivos grandes."""
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo con más de 300 líneas
            large_file = os.path.join(temp_dir, "large.py")
            with open(large_file, 'w') as f:
                for i in range(350):
                    f.write(f"line_{i} = {i}\n")
            
            files = scanner.find_python_files(temp_dir)
            
            assert len(files) == 1
            assert files[0].is_large is True
            assert files[0].lines_of_code == 350
    
    def test_scan_project_structure(self):
        """Verifica escaneo completo de estructura del proyecto."""
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear estructura backend
            backend_dir = os.path.join(temp_dir, "backend")
            os.makedirs(backend_dir)
            py_file = os.path.join(backend_dir, "main.py")
            with open(py_file, 'w') as f:
                f.write("print('backend')\n")
            
            # Crear estructura frontend
            frontend_dir = os.path.join(temp_dir, "src")
            os.makedirs(frontend_dir)
            ts_file = os.path.join(frontend_dir, "index.ts")
            with open(ts_file, 'w') as f:
                f.write("console.log('frontend');\n")
            
            # Escanear proyecto
            structure = scanner.scan_project(temp_dir)
            
            assert structure.root_path == temp_dir
            assert len(structure.backend_files) == 1
            assert len(structure.frontend_files) == 1


class TestFileScannerProperties:
    """Property-based tests para FileScanner."""
    
    @given(lines=st.integers(min_value=0, max_value=1000))
    @settings(max_examples=100)
    def test_property_classify_file_size(self, lines):
        """
        Property: For any number of lines, classification must be consistent
        with the threshold (>300 lines = large).
        
        **Validates: Requirements 1.3**
        """
        scanner = FileScanner()
        config = get_config()
        
        is_large = scanner.classify_file_size(lines)
        
        # Verificar que la clasificación sea correcta según el umbral
        if lines > config.LARGE_FILE_THRESHOLD:
            assert is_large is True
        else:
            assert is_large is False
    
    @given(
        num_py_files=st.integers(min_value=0, max_value=10),
        num_txt_files=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=50)
    def test_property_find_python_files_completeness(self, num_py_files, num_txt_files):
        """
        Property: For any directory with N Python files and M non-Python files,
        FileScanner must identify exactly N Python files.
        
        **Validates: Requirements 1.1**
        """
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivos Python
            for i in range(num_py_files):
                py_file = os.path.join(temp_dir, f"file_{i}.py")
                with open(py_file, 'w') as f:
                    f.write(f"# Python file {i}\n")
            
            # Crear archivos no-Python
            for i in range(num_txt_files):
                txt_file = os.path.join(temp_dir, f"file_{i}.txt")
                with open(txt_file, 'w') as f:
                    f.write(f"Text file {i}\n")
            
            # Escanear
            files = scanner.find_python_files(temp_dir)
            
            # Verificar que se encontraron exactamente los archivos Python
            assert len(files) == num_py_files
            
            # Verificar que todos son archivos Python
            for file in files:
                assert file.language == 'python'
                assert file.path.endswith('.py')
    
    @given(
        num_ts_files=st.integers(min_value=0, max_value=10),
        num_tsx_files=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=50)
    def test_property_find_typescript_files_completeness(self, num_ts_files, num_tsx_files):
        """
        Property: For any directory with N .ts files and M .tsx files,
        FileScanner must identify exactly N+M TypeScript files.
        
        **Validates: Requirements 1.2**
        """
        scanner = FileScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivos .ts
            for i in range(num_ts_files):
                ts_file = os.path.join(temp_dir, f"utils_{i}.ts")
                with open(ts_file, 'w') as f:
                    f.write(f"export const func{i} = () => {i};\n")
            
            # Crear archivos .tsx
            for i in range(num_tsx_files):
                tsx_file = os.path.join(temp_dir, f"Component_{i}.tsx")
                with open(tsx_file, 'w') as f:
                    f.write(f"export const Comp{i} = () => <div>{i}</div>;\n")
            
            # Escanear
            files = scanner.find_typescript_files(temp_dir)
            
            # Verificar que se encontraron todos los archivos TypeScript
            assert len(files) == num_ts_files + num_tsx_files
            
            # Verificar que todos son archivos TypeScript
            for file in files:
                assert file.language == 'typescript'
                assert file.path.endswith('.ts') or file.path.endswith('.tsx')

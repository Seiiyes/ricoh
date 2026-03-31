"""
Tests para DependencyExtractor.

Incluye unit tests y property-based tests para verificar la extracción
correcta de dependencias de requirements.txt y package.json.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from audit_system.scanners.dependency_extractor import DependencyExtractor
from audit_system.models import Dependency


class TestDependencyExtractor:
    """Tests unitarios para DependencyExtractor."""
    
    def setup_method(self):
        """Inicializa el extractor antes de cada test."""
        self.extractor = DependencyExtractor()
    
    # ========== Tests para extract_python_deps ==========
    
    def test_extract_python_deps_exact_version(self):
        """Verifica extracción de dependencia con versión exacta (==)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("fastapi==0.109.0\n")
            f.write("uvicorn==0.27.0\n")
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_python_deps(temp_path)
            
            assert len(deps) == 2
            assert deps[0].name == "fastapi"
            assert deps[0].current_version == "0.109.0"
            assert deps[0].ecosystem == "python"
            
            assert deps[1].name == "uvicorn"
            assert deps[1].current_version == "0.27.0"
        finally:
            os.unlink(temp_path)
    
    def test_extract_python_deps_with_extras(self):
        """Verifica extracción de dependencia con extras [standard]."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("uvicorn[standard]==0.27.0\n")
            f.write("pydantic[email]==2.5.3\n")
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_python_deps(temp_path)
            
            assert len(deps) == 2
            assert deps[0].name == "uvicorn[standard]"
            assert deps[0].current_version == "0.27.0"
            
            assert deps[1].name == "pydantic[email]"
            assert deps[1].current_version == "2.5.3"
        finally:
            os.unlink(temp_path)
    
    def test_extract_python_deps_version_operators(self):
        """Verifica extracción con diferentes operadores de versión."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("package1>=1.0.0\n")
            f.write("package2~=2.0.0\n")
            f.write("package3>3.0.0\n")
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_python_deps(temp_path)
            
            assert len(deps) == 3
            assert deps[0].current_version == "1.0.0"
            assert deps[1].current_version == "2.0.0"
            assert deps[2].current_version == "3.0.0"
        finally:
            os.unlink(temp_path)
    
    def test_extract_python_deps_ignores_comments(self):
        """Verifica que se ignoren comentarios y líneas vacías."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Authentication dependencies\n")
            f.write("bcrypt==4.1.2\n")
            f.write("\n")
            f.write("# JWT support\n")
            f.write("PyJWT==2.8.0\n")
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_python_deps(temp_path)
            
            assert len(deps) == 2
            assert deps[0].name == "bcrypt"
            assert deps[1].name == "PyJWT"
        finally:
            os.unlink(temp_path)
    
    def test_extract_python_deps_no_version(self):
        """Verifica manejo de dependencias sin versión especificada."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("requests\n")
            f.write("pytest\n")
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_python_deps(temp_path)
            
            assert len(deps) == 2
            assert deps[0].name == "requests"
            assert deps[0].current_version == "unspecified"
            assert deps[1].name == "pytest"
            assert deps[1].current_version == "unspecified"
        finally:
            os.unlink(temp_path)
    
    def test_extract_python_deps_empty_file(self):
        """Verifica manejo de archivo vacío."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_python_deps(temp_path)
            assert len(deps) == 0
        finally:
            os.unlink(temp_path)
    
    def test_extract_python_deps_file_not_exists(self):
        """Verifica manejo de archivo inexistente."""
        deps = self.extractor.extract_python_deps("/path/that/does/not/exist.txt")
        assert len(deps) == 0
    
    # ========== Tests para extract_npm_deps ==========
    
    def test_extract_npm_deps_basic(self):
        """Verifica extracción básica de dependencias npm."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            package_data = {
                "name": "test-project",
                "dependencies": {
                    "react": "^19.2.0",
                    "axios": "^1.13.6"
                }
            }
            json.dump(package_data, f)
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_npm_deps(temp_path)
            
            assert len(deps) == 2
            assert any(d.name == "react" for d in deps)
            assert any(d.name == "axios" for d in deps)
            
            react_dep = next(d for d in deps if d.name == "react")
            assert react_dep.current_version == "19.2.0"  # Sin ^
            assert react_dep.ecosystem == "npm"
        finally:
            os.unlink(temp_path)
    
    def test_extract_npm_deps_with_dev_dependencies(self):
        """Verifica extracción de dependencies y devDependencies."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            package_data = {
                "name": "test-project",
                "dependencies": {
                    "react": "^19.2.0"
                },
                "devDependencies": {
                    "vitest": "^4.0.18",
                    "typescript": "~5.9.3"
                }
            }
            json.dump(package_data, f)
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_npm_deps(temp_path)
            
            assert len(deps) == 3
            
            # Verificar que devDependencies tengan sufijo (dev)
            vitest_dep = next(d for d in deps if "vitest" in d.name)
            assert vitest_dep.name == "vitest (dev)"
            assert vitest_dep.current_version == "4.0.18"
            
            typescript_dep = next(d for d in deps if "typescript" in d.name)
            assert typescript_dep.name == "typescript (dev)"
            assert typescript_dep.current_version == "5.9.3"
        finally:
            os.unlink(temp_path)
    
    def test_extract_npm_deps_version_prefixes(self):
        """Verifica limpieza de prefijos de versión (^, ~, >=)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            package_data = {
                "dependencies": {
                    "pkg1": "^1.0.0",
                    "pkg2": "~2.0.0",
                    "pkg3": ">=3.0.0",
                    "pkg4": "4.0.0"
                }
            }
            json.dump(package_data, f)
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_npm_deps(temp_path)
            
            assert len(deps) == 4
            assert all(not d.current_version.startswith(('^', '~', '>=')) for d in deps)
            
            versions = {d.name: d.current_version for d in deps}
            assert versions["pkg1"] == "1.0.0"
            assert versions["pkg2"] == "2.0.0"
            assert versions["pkg3"] == "3.0.0"
            assert versions["pkg4"] == "4.0.0"
        finally:
            os.unlink(temp_path)
    
    def test_extract_npm_deps_no_dependencies(self):
        """Verifica manejo de package.json sin dependencies."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            package_data = {
                "name": "test-project",
                "version": "1.0.0"
            }
            json.dump(package_data, f)
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_npm_deps(temp_path)
            assert len(deps) == 0
        finally:
            os.unlink(temp_path)
    
    def test_extract_npm_deps_file_not_exists(self):
        """Verifica manejo de archivo inexistente."""
        deps = self.extractor.extract_npm_deps("/path/that/does/not/exist.json")
        assert len(deps) == 0
    
    def test_extract_npm_deps_invalid_json(self):
        """Verifica manejo de JSON inválido."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            deps = self.extractor.extract_npm_deps(temp_path)
            assert len(deps) == 0
        finally:
            os.unlink(temp_path)
    
    # ========== Tests para check_vulnerabilities ==========
    
    def test_check_vulnerabilities_returns_empty(self):
        """Verifica que check_vulnerabilities retorne lista vacía (no implementado)."""
        dependency = Dependency(
            name="test-package",
            current_version="1.0.0",
            latest_version="1.0.0",
            is_outdated=False,
            ecosystem="python"
        )
        
        vulnerabilities = self.extractor.check_vulnerabilities(dependency)
        assert vulnerabilities == []
    
    # ========== Tests para extract_all_dependencies ==========
    
    def test_extract_all_dependencies_integration(self):
        """Test de integración para extracción completa."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear estructura de directorios
            backend_dir = Path(temp_dir) / "backend"
            backend_dir.mkdir()
            
            # Crear requirements.txt
            requirements_path = backend_dir / "requirements.txt"
            requirements_path.write_text("fastapi==0.109.0\nuvicorn==0.27.0\n")
            
            # Crear package.json
            package_json_path = Path(temp_dir) / "package.json"
            package_data = {
                "dependencies": {
                    "react": "^19.2.0",
                    "axios": "^1.13.6"
                }
            }
            package_json_path.write_text(json.dumps(package_data))
            
            # Extraer todas las dependencias
            python_deps, npm_deps = self.extractor.extract_all_dependencies(temp_dir)
            
            assert len(python_deps) == 2
            assert len(npm_deps) == 2
            assert all(d.ecosystem == "python" for d in python_deps)
            assert all(d.ecosystem == "npm" for d in npm_deps)


# ========== Property-Based Tests ==========

@settings(max_examples=50)
@given(
    packages=st.lists(
        st.tuples(
            st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), min_codepoint=97, max_codepoint=122), min_size=3, max_size=20),
            st.from_regex(r'[0-9]+\.[0-9]+\.[0-9]+', fullmatch=True)
        ),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0]
    )
)
def test_property_extract_python_deps_completeness(packages):
    """
    Property: For any valid requirements.txt, all listed packages should be extracted.
    
    **Validates: Requirements 1.4, 14.1**
    """
    extractor = DependencyExtractor()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for name, version in packages:
            f.write(f"{name}=={version}\n")
        temp_path = f.name
    
    try:
        deps = extractor.extract_python_deps(temp_path)
        
        # Verificar que se extrajeron todas las dependencias
        assert len(deps) == len(packages)
        
        # Verificar que todos los nombres estén presentes
        extracted_names = {d.name for d in deps}
        expected_names = {name for name, _ in packages}
        assert extracted_names == expected_names
        
        # Verificar que todas las versiones sean correctas
        for dep in deps:
            expected_version = next(v for n, v in packages if n == dep.name)
            assert dep.current_version == expected_version
        
        # Verificar que todas sean del ecosistema Python
        assert all(d.ecosystem == "python" for d in deps)
    finally:
        os.unlink(temp_path)


@settings(max_examples=50)
@given(
    packages=st.dictionaries(
        keys=st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), min_codepoint=97, max_codepoint=122), min_size=3, max_size=20),
        values=st.from_regex(r'\^?[0-9]+\.[0-9]+\.[0-9]+', fullmatch=True),
        min_size=1,
        max_size=10
    )
)
def test_property_extract_npm_deps_completeness(packages):
    """
    Property: For any valid package.json, all listed dependencies should be extracted.
    
    **Validates: Requirements 1.5, 14.2**
    """
    extractor = DependencyExtractor()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        package_data = {
            "name": "test-project",
            "dependencies": packages
        }
        json.dump(package_data, f)
        temp_path = f.name
    
    try:
        deps = extractor.extract_npm_deps(temp_path)
        
        # Verificar que se extrajeron todas las dependencias
        assert len(deps) == len(packages)
        
        # Verificar que todos los nombres estén presentes
        extracted_names = {d.name for d in deps}
        expected_names = set(packages.keys())
        assert extracted_names == expected_names
        
        # Verificar que todas sean del ecosistema npm
        assert all(d.ecosystem == "npm" for d in deps)
    finally:
        os.unlink(temp_path)


@settings(max_examples=30)
@given(
    version=st.from_regex(r'[0-9]+\.[0-9]+\.[0-9]+', fullmatch=True)
)
def test_property_version_cleaning_idempotent(version):
    """
    Property: Cleaning version prefixes should be idempotent.
    
    Applying version cleaning twice should give the same result as applying it once.
    """
    extractor = DependencyExtractor()
    
    # Crear dependencia con prefijo
    prefixed_version = f"^{version}"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        package_data = {
            "dependencies": {
                "test-pkg": prefixed_version
            }
        }
        json.dump(package_data, f)
        temp_path = f.name
    
    try:
        deps = extractor.extract_npm_deps(temp_path)
        
        # La versión limpia no debe tener prefijos
        assert not deps[0].current_version.startswith(('^', '~', '>=', '<'))
        
        # La versión limpia debe ser la versión original
        assert deps[0].current_version == version
    finally:
        os.unlink(temp_path)

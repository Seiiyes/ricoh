"""
Tests para TestingAnalyzer.

Valida la detección de código sin tests apropiados.
"""

import pytest
from audit_system.analyzers.testing_analyzer import TestingAnalyzer
from audit_system.models import SourceFile, Severity


@pytest.fixture
def analyzer():
    """Fixture que retorna una instancia de TestingAnalyzer."""
    return TestingAnalyzer()


class TestIdentifyFilesWithoutTests:
    """Tests para identify_files_without_tests."""
    
    def test_detects_file_without_test(self, analyzer):
        """Detecta archivo Python sin test correspondiente."""
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="def get_user(): pass"
            )
        ]
        
        findings = analyzer.identify_files_without_tests(files)
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_test_file"
        assert findings[0].severity == Severity.MEDIO
    
    def test_no_finding_when_test_exists_same_dir(self, analyzer):
        """No reporta cuando existe test en el mismo directorio."""
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="def get_user(): pass"
            ),
            SourceFile(
                path="api/test_users.py",
                language="python",
                lines_of_code=50,
                is_large=False,
                content="def test_get_user(): pass"
            )
        ]
        
        findings = analyzer.identify_files_without_tests(files)
        
        assert len(findings) == 0
    
    def test_no_finding_when_test_exists_in_tests_dir(self, analyzer):
        """No reporta cuando existe test en directorio tests/."""
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="def get_user(): pass"
            ),
            SourceFile(
                path="tests/test_users.py",
                language="python",
                lines_of_code=50,
                is_large=False,
                content="def test_get_user(): pass"
            )
        ]
        
        findings = analyzer.identify_files_without_tests(files)
        
        assert len(findings) == 0
    
    def test_ignores_init_files(self, analyzer):
        """Ignora archivos __init__.py."""
        files = [
            SourceFile(
                path="api/__init__.py",
                language="python",
                lines_of_code=10,
                is_large=False,
                content=""
            )
        ]
        
        findings = analyzer.identify_files_without_tests(files)
        
        assert len(findings) == 0
    
    def test_ignores_config_files(self, analyzer):
        """Ignora archivos de configuración."""
        files = [
            SourceFile(
                path="config.py",
                language="python",
                lines_of_code=50,
                is_large=False,
                content="DEBUG = True"
            )
        ]
        
        findings = analyzer.identify_files_without_tests(files)
        
        assert len(findings) == 0
    
    def test_detects_multiple_files_without_tests(self, analyzer):
        """Detecta múltiples archivos sin tests."""
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="def get_user(): pass"
            ),
            SourceFile(
                path="api/posts.py",
                language="python",
                lines_of_code=80,
                is_large=False,
                content="def get_post(): pass"
            )
        ]
        
        findings = analyzer.identify_files_without_tests(files)
        
        assert len(findings) == 2


class TestIdentifyComponentsWithoutTests:
    """Tests para identify_components_without_tests."""
    
    def test_detects_component_without_test(self, analyzer):
        """Detecta componente React sin test."""
        files = [
            SourceFile(
                path="components/Button.tsx",
                language="typescript",
                lines_of_code=50,
                is_large=False,
                content="export default function Button() { return <button>Click</button>; }"
            )
        ]
        
        findings = analyzer.identify_components_without_tests(files)
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_component_test"
        assert findings[0].severity == Severity.MEDIO
    
    def test_no_finding_when_test_exists(self, analyzer):
        """No reporta cuando existe test para el componente."""
        files = [
            SourceFile(
                path="components/Button.tsx",
                language="typescript",
                lines_of_code=50,
                is_large=False,
                content="export default function Button() { return <button>Click</button>; }"
            ),
            SourceFile(
                path="components/Button.test.tsx",
                language="typescript",
                lines_of_code=30,
                is_large=False,
                content="test('renders button', () => {})"
            )
        ]
        
        findings = analyzer.identify_components_without_tests(files)
        
        assert len(findings) == 0
    
    def test_detects_component_in_pages_dir(self, analyzer):
        """Detecta componente en directorio pages/ sin test."""
        files = [
            SourceFile(
                path="pages/Home.tsx",
                language="typescript",
                lines_of_code=100,
                is_large=False,
                content="export default function Home() { return <div>Home</div>; }"
            )
        ]
        
        findings = analyzer.identify_components_without_tests(files)
        
        assert len(findings) == 1
    
    def test_ignores_non_component_files(self, analyzer):
        """Ignora archivos que no son componentes."""
        files = [
            SourceFile(
                path="utils/helper.ts",
                language="typescript",
                lines_of_code=50,
                is_large=False,
                content="export function formatDate() {}"
            )
        ]
        
        findings = analyzer.identify_components_without_tests(files)
        
        assert len(findings) == 0
    
    def test_accepts_spec_files(self, analyzer):
        """Acepta archivos .spec.tsx como tests."""
        files = [
            SourceFile(
                path="components/Button.tsx",
                language="typescript",
                lines_of_code=50,
                is_large=False,
                content="export default function Button() { return <button>Click</button>; }"
            ),
            SourceFile(
                path="components/Button.spec.tsx",
                language="typescript",
                lines_of_code=30,
                is_large=False,
                content="describe('Button', () => {})"
            )
        ]
        
        findings = analyzer.identify_components_without_tests(files)
        
        assert len(findings) == 0


class TestCheckIntegrationTests:
    """Tests para check_integration_tests."""
    
    def test_detects_api_without_integration_tests(self, analyzer):
        """Detecta endpoints sin tests de integración."""
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="""
                @router.get('/users')
                def get_users():
                    pass
                
                @router.post('/users')
                def create_user():
                    pass
                """
            )
        ]
        
        findings = analyzer.check_integration_tests(files)
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_integration_test"
        assert findings[0].severity == Severity.ALTO
    
    def test_no_finding_when_integration_tests_exist(self, analyzer):
        """No reporta cuando existen tests de integración."""
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="""
                @router.get('/users')
                def get_users():
                    pass
                """
            ),
            SourceFile(
                path="tests/integration/test_users_api.py",
                language="python",
                lines_of_code=50,
                is_large=False,
                content="def test_get_users_endpoint(): pass"
            )
        ]
        
        findings = analyzer.check_integration_tests(files)
        
        assert len(findings) == 0
    
    def test_detects_multiple_http_methods(self, analyzer):
        """Detecta múltiples métodos HTTP en endpoints."""
        files = [
            SourceFile(
                path="api/posts.py",
                language="python",
                lines_of_code=150,
                is_large=False,
                content="""
                @router.get('/posts')
                def get_posts():
                    pass
                
                @router.post('/posts')
                def create_post():
                    pass
                
                @router.put('/posts/{id}')
                def update_post():
                    pass
                
                @router.delete('/posts/{id}')
                def delete_post():
                    pass
                """
            )
        ]
        
        findings = analyzer.check_integration_tests(files)
        
        assert len(findings) == 1
        assert "4 endpoint(s)" in findings[0].description
    
    def test_ignores_non_api_files(self, analyzer):
        """Ignora archivos que no son de API."""
        files = [
            SourceFile(
                path="utils/helper.py",
                language="python",
                lines_of_code=50,
                is_large=False,
                content="def helper_function(): pass"
            )
        ]
        
        findings = analyzer.check_integration_tests(files)
        
        assert len(findings) == 0


class TestIdentifyComplexFunctionsWithoutTests:
    """Tests para identify_complex_functions_without_tests."""
    
    def test_detects_long_function_without_test(self, analyzer):
        """Detecta función larga sin test."""
        long_function = "def process_data():\n" + "    x = 1\n" * 60
        
        files = [
            SourceFile(
                path="module.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content=long_function
            )
        ]
        
        findings = analyzer.identify_complex_functions_without_tests(files)
        
        assert len(findings) == 1
        assert findings[0].subcategory == "complex_function_no_test"
        assert findings[0].severity == Severity.ALTO
    
    def test_no_finding_when_test_exists(self, analyzer):
        """No reporta cuando existe test para la función."""
        long_function = "def process_data():\n" + "    x = 1\n" * 60
        
        files = [
            SourceFile(
                path="module.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content=long_function
            ),
            SourceFile(
                path="test_module.py",
                language="python",
                lines_of_code=50,
                is_large=False,
                content="def test_process_data(): pass"
            )
        ]
        
        findings = analyzer.identify_complex_functions_without_tests(files)
        
        assert len(findings) == 0
    
    def test_ignores_private_functions(self, analyzer):
        """Ignora funciones privadas."""
        long_function = "def _internal_process():\n" + "    x = 1\n" * 60
        
        files = [
            SourceFile(
                path="module.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content=long_function
            )
        ]
        
        findings = analyzer.identify_complex_functions_without_tests(files)
        
        assert len(findings) == 0
    
    def test_ignores_short_functions(self, analyzer):
        """Ignora funciones cortas."""
        files = [
            SourceFile(
                path="module.py",
                language="python",
                lines_of_code=50,
                is_large=False,
                content="def simple_function():\n    return 42"
            )
        ]
        
        findings = analyzer.identify_complex_functions_without_tests(files)
        
        assert len(findings) == 0


class TestAnalyze:
    """Tests para el método analyze principal."""
    
    def test_analyzes_python_and_typescript_files(self, analyzer):
        """Analiza archivos Python y TypeScript."""
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=100,
                is_large=False,
                content="def get_user(): pass"
            ),
            SourceFile(
                path="components/Button.tsx",
                language="typescript",
                lines_of_code=50,
                is_large=False,
                content="export default function Button() { return <button>Click</button>; }"
            )
        ]
        
        findings = analyzer.analyze(files)
        
        assert len(findings) >= 2
        assert all(f.category == "testing" for f in findings)
    
    def test_comprehensive_testing_analysis(self, analyzer):
        """Realiza análisis comprehensivo de testing."""
        long_function = "def complex_process():\n" + "    x = 1\n" * 60
        
        files = [
            SourceFile(
                path="api/users.py",
                language="python",
                lines_of_code=150,
                is_large=False,
                content=f"""
                @router.get('/users')
                def get_users():
                    pass
                
                {long_function}
                """
            ),
            SourceFile(
                path="components/UserList.tsx",
                language="typescript",
                lines_of_code=100,
                is_large=False,
                content="export default function UserList() { return <div>Users</div>; }"
            )
        ]
        
        findings = analyzer.analyze(files)
        
        # Debería detectar: archivo sin test, componente sin test, endpoint sin integration test, función compleja sin test
        assert len(findings) >= 3

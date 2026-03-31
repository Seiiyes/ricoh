"""
Tests para ConfigAnalyzer.

Valida la detección de problemas de configuración en código Backend.
"""

import pytest
from audit_system.analyzers.config_analyzer import ConfigAnalyzer
from audit_system.models import SourceFile, Severity


@pytest.fixture
def analyzer():
    """Fixture que retorna una instancia de ConfigAnalyzer."""
    return ConfigAnalyzer()


class TestCheckEnvDocumentation:
    """Tests para check_env_documentation."""
    
    def test_detects_undocumented_env_var(self, analyzer):
        """Detecta variable de entorno sin documentar."""
        code = """
        DATABASE_URL = os.getenv('DATABASE_URL')
        """
        findings = analyzer.check_env_documentation(code, "config.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "undocumented_env"
        assert findings[0].severity == Severity.BAJO
    
    def test_no_finding_with_comment(self, analyzer):
        """No reporta cuando hay comentario explicativo."""
        code = """
        # DATABASE_URL: PostgreSQL connection string
        DATABASE_URL = os.getenv('DATABASE_URL')
        """
        findings = analyzer.check_env_documentation(code, "config.py")
        
        assert len(findings) == 0
    
    def test_detects_environ_get(self, analyzer):
        """Detecta os.environ.get sin documentar."""
        code = """
        API_KEY = os.environ.get('API_KEY')
        """
        findings = analyzer.check_env_documentation(code, "config.py")
        
        assert len(findings) == 1
    
    def test_ignores_non_config_files(self, analyzer):
        """Ignora archivos que no son de configuración."""
        code = """
        value = os.getenv('SOME_VAR')
        """
        findings = analyzer.check_env_documentation(code, "api/users.py")
        
        assert len(findings) == 0
    
    def test_detects_multiple_undocumented_vars(self, analyzer):
        """Detecta múltiples variables sin documentar."""
        code = """
        DATABASE_URL = os.getenv('DATABASE_URL')
        REDIS_URL = os.getenv('REDIS_URL')
        API_KEY = os.getenv('API_KEY')
        """
        findings = analyzer.check_env_documentation(code, "settings.py")
        
        assert len(findings) == 3


class TestDetectInsecureDefaults:
    """Tests para detect_insecure_defaults."""
    
    def test_detects_debug_true(self, analyzer):
        """Detecta DEBUG=True."""
        code = """
        DEBUG = True
        """
        findings = analyzer.detect_insecure_defaults(code, "config.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "insecure_default"
        assert findings[0].severity == Severity.ALTO
    
    def test_detects_secret_key_with_default(self, analyzer):
        """Detecta SECRET_KEY con valor por defecto."""
        code = """
        SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-123')
        """
        findings = analyzer.detect_insecure_defaults(code, "config.py")
        
        assert len(findings) == 1
    
    def test_detects_password_with_default(self, analyzer):
        """Detecta PASSWORD con valor por defecto."""
        code = """
        DB_PASSWORD = os.getenv('PASSWORD', 'admin123')
        """
        findings = analyzer.detect_insecure_defaults(code, "config.py")
        
        assert len(findings) == 1
    
    def test_detects_allowed_hosts_wildcard(self, analyzer):
        """Detecta ALLOWED_HOSTS con wildcard."""
        code = """
        ALLOWED_HOSTS = ['*']
        """
        findings = analyzer.detect_insecure_defaults(code, "settings.py")
        
        assert len(findings) == 1
    
    def test_detects_cors_allow_all(self, analyzer):
        """Detecta CORS permitiendo todos los orígenes."""
        code = """
        CORS_ALLOW_ALL_ORIGINS = True
        """
        findings = analyzer.detect_insecure_defaults(code, "config.py")
        
        assert len(findings) == 1
    
    def test_ignores_non_config_files(self, analyzer):
        """Ignora archivos que no son de configuración."""
        code = """
        DEBUG = True
        """
        findings = analyzer.detect_insecure_defaults(code, "api/users.py")
        
        assert len(findings) == 0


class TestDetectHardcodedConfig:
    """Tests para detect_hardcoded_config."""
    
    def test_detects_hardcoded_url(self, analyzer):
        """Detecta URL hardcodeada."""
        code = """
        API_URL = "https://api.example.com/v1"
        """
        findings = analyzer.detect_hardcoded_config(code, "module.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "hardcoded_config"
        assert findings[0].severity == Severity.MEDIO
    
    def test_detects_hardcoded_localhost(self, analyzer):
        """Detecta localhost hardcodeado."""
        code = """
        REDIS_HOST = "localhost:6379"
        """
        findings = analyzer.detect_hardcoded_config(code, "module.py")
        
        assert len(findings) == 1
    
    def test_detects_hardcoded_database_url(self, analyzer):
        """Detecta DATABASE_URL hardcodeada."""
        code = """
        DATABASE_URL = "postgresql://user:pass@localhost/db"
        """
        findings = analyzer.detect_hardcoded_config(code, "module.py")
        
        assert len(findings) == 1
    
    def test_no_finding_with_getenv(self, analyzer):
        """No reporta cuando usa getenv."""
        code = """
        API_URL = os.getenv('API_URL', 'https://api.example.com')
        """
        findings = analyzer.detect_hardcoded_config(code, "module.py")
        
        assert len(findings) == 0
    
    def test_ignores_comments(self, analyzer):
        """Ignora URLs en comentarios."""
        code = """
        # Example: https://api.example.com/v1
        API_URL = os.getenv('API_URL')
        """
        findings = analyzer.detect_hardcoded_config(code, "module.py")
        
        assert len(findings) == 0
    
    def test_detects_redis_url(self, analyzer):
        """Detecta REDIS_URL hardcodeada."""
        code = """
        REDIS_URL = "redis://localhost:6379/0"
        """
        findings = analyzer.detect_hardcoded_config(code, "module.py")
        
        assert len(findings) == 1


class TestCheckEnvValidation:
    """Tests para check_env_validation."""
    
    def test_detects_secret_key_without_validation(self, analyzer):
        """Detecta SECRET_KEY sin validación."""
        code = """
        SECRET_KEY = os.getenv('SECRET_KEY')
        """
        findings = analyzer.check_env_validation(code, "config.py")
        
        assert len(findings) == 1
        assert findings[0].subcategory == "no_env_validation"
        assert findings[0].severity == Severity.ALTO
    
    def test_no_finding_with_raise_validation(self, analyzer):
        """No reporta cuando hay validación con raise."""
        code = """
        SECRET_KEY = os.getenv('SECRET_KEY')
        if not SECRET_KEY:
            raise ValueError('SECRET_KEY is required')
        """
        findings = analyzer.check_env_validation(code, "config.py")
        
        assert len(findings) == 0
    
    def test_no_finding_with_assert_validation(self, analyzer):
        """No reporta cuando hay validación con assert."""
        code = """
        SECRET_KEY = os.getenv('SECRET_KEY')
        assert SECRET_KEY, 'SECRET_KEY is required'
        """
        findings = analyzer.check_env_validation(code, "config.py")
        
        assert len(findings) == 0
    
    def test_detects_database_url_without_validation(self, analyzer):
        """Detecta DATABASE_URL sin validación."""
        code = """
        DATABASE_URL = os.getenv('DATABASE_URL')
        """
        findings = analyzer.check_env_validation(code, "settings.py")
        
        assert len(findings) == 1
    
    def test_detects_api_key_without_validation(self, analyzer):
        """Detecta API_KEY sin validación."""
        code = """
        API_KEY = os.getenv('API_KEY')
        """
        findings = analyzer.check_env_validation(code, "config.py")
        
        assert len(findings) == 1
    
    def test_ignores_non_config_files(self, analyzer):
        """Ignora archivos que no son de configuración."""
        code = """
        SECRET_KEY = os.getenv('SECRET_KEY')
        """
        findings = analyzer.check_env_validation(code, "api/users.py")
        
        assert len(findings) == 0
    
    def test_detects_multiple_unvalidated_vars(self, analyzer):
        """Detecta múltiples variables sin validar."""
        code = """
        SECRET_KEY = os.getenv('SECRET_KEY')
        DATABASE_URL = os.getenv('DATABASE_URL')
        API_KEY = os.getenv('API_KEY')
        """
        findings = analyzer.check_env_validation(code, "config.py")
        
        assert len(findings) == 3


class TestAnalyze:
    """Tests para el método analyze principal."""
    
    def test_analyzes_python_files(self, analyzer):
        """Analiza archivos Python."""
        file = SourceFile(
            path="config.py",
            language="python",
            lines_of_code=50,
            is_large=False,
            content="""
            DEBUG = True
            SECRET_KEY = os.getenv('SECRET_KEY')
            API_URL = "https://api.example.com"
            """
        )
        
        findings = analyzer.analyze([file])
        
        assert len(findings) > 0
        assert all(f.category == "configuration" for f in findings)
    
    def test_ignores_non_python_files(self, analyzer):
        """Ignora archivos que no son Python."""
        file = SourceFile(
            path="config.ts",
            language="typescript",
            lines_of_code=50,
            is_large=False,
            content="const DEBUG = true;"
        )
        
        findings = analyzer.analyze([file])
        
        assert len(findings) == 0
    
    def test_analyzes_multiple_files(self, analyzer):
        """Analiza múltiples archivos."""
        files = [
            SourceFile(
                path="config.py",
                language="python",
                lines_of_code=30,
                is_large=False,
                content="DEBUG = True"
            ),
            SourceFile(
                path="settings.py",
                language="python",
                lines_of_code=40,
                is_large=False,
                content='API_URL = "https://api.example.com"'
            )
        ]
        
        findings = analyzer.analyze(files)
        
        assert len(findings) >= 2
    
    def test_comprehensive_config_analysis(self, analyzer):
        """Realiza análisis comprehensivo de configuración."""
        file = SourceFile(
            path="config.py",
            language="python",
            lines_of_code=100,
            is_large=False,
            content="""
            DEBUG = True
            SECRET_KEY = os.getenv('SECRET_KEY', 'default-key')
            DATABASE_URL = os.getenv('DATABASE_URL')
            API_URL = "https://api.example.com"
            REDIS_HOST = "localhost:6379"
            """
        )
        
        findings = analyzer.analyze([file])
        
        # Debería detectar: DEBUG=True, SECRET_KEY con default, DATABASE_URL sin validación, URLs hardcodeadas
        assert len(findings) >= 4

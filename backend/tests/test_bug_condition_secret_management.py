"""
Property-Based Tests: Bug Condition Exploration - Secret Management Vulnerabilities

**CRITICAL**: These tests are EXPECTED TO FAIL on unfixed code.
Failure confirms that the bugs exist.

**DO NOT** attempt to fix the tests or code when they fail.

**NOTE**: These tests encode the expected behavior - they will validate
the fixes when they pass after implementation.

**OBJECTIVE**: Discover counterexamples that demonstrate the bugs exist.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**
"""
import pytest
import os
from hypothesis import given, strategies as st, settings, assume
from services.encryption_service import EncryptionService
from services.jwt_service import JWTService
from services.ricoh_web_client import RicohWebClient
from db.database import DATABASE_URL
import string


@pytest.mark.property
class TestBugConditionSecretManagement:
    """
    Bug Condition Exploration Tests for Secret Management
    
    These tests verify that the system REJECTS insecure secret configurations.
    They are expected to FAIL on unfixed code (which accepts insecure configs).
    """
    
    def test_bug_condition_encryption_key_none_development(self, monkeypatch):
        """
        **Validates: Requirement 2.1**
        
        Bug Condition: EncryptionService accepts ENCRYPTION_KEY=None in development
        Expected Behavior: System SHALL reject with ValueError in ALL environments
        
        Test Strategy: Set ENVIRONMENT=development and ENCRYPTION_KEY=None,
        then verify that initialize() raises ValueError with instructive message.
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (system generates temporary key)
        EXPECTED RESULT ON FIXED CODE: PASS (system raises ValueError)
        """
        # Setup: Remove ENCRYPTION_KEY and set development environment
        monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        
        # Reset the service to force re-initialization
        EncryptionService._initialized = False
        EncryptionService._cipher = None
        
        # Expected Behavior: Should raise ValueError with instructive message
        with pytest.raises(ValueError) as exc_info:
            EncryptionService.initialize()
        
        # Verify error message contains instructions
        error_message = str(exc_info.value)
        assert "ENCRYPTION_KEY" in error_message
        assert "must be set" in error_message.lower()
        assert "Generate one with:" in error_message or "generate" in error_message.lower()
    
    def test_bug_condition_encryption_key_none_production(self, monkeypatch):
        """
        **Validates: Requirement 2.1**
        
        Bug Condition: EncryptionService might accept ENCRYPTION_KEY=None in production
        Expected Behavior: System SHALL reject with ValueError in ALL environments
        
        Test Strategy: Set ENVIRONMENT=production and ENCRYPTION_KEY=None,
        then verify that initialize() raises ValueError.
        
        EXPECTED RESULT ON UNFIXED CODE: PASS (already rejects in production)
        EXPECTED RESULT ON FIXED CODE: PASS (rejects in all environments)
        """
        # Setup: Remove ENCRYPTION_KEY and set production environment
        monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        
        # Reset the service
        EncryptionService._initialized = False
        EncryptionService._cipher = None
        
        # Expected Behavior: Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            EncryptionService.initialize()
        
        error_message = str(exc_info.value)
        assert "ENCRYPTION_KEY" in error_message
    
    @given(
        key_length=st.integers(min_value=32, max_value=64),
        char_type=st.sampled_from(['lowercase', 'uppercase', 'digits', 'mixed_two'])
    )
    @settings(max_examples=20, deadline=None)
    def test_bug_condition_secret_key_low_entropy(self, monkeypatch, key_length, char_type):
        """
        **Validates: Requirement 2.2**
        
        Bug Condition: JWTService accepts SECRET_KEY with low entropy
        Expected Behavior: System SHALL reject keys with < 3 character categories
        
        Test Strategy: Generate keys with only 1-2 character categories
        (e.g., only lowercase, only uppercase, only digits, or two categories)
        and verify that _get_secret_key() raises ValueError.
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (accepts weak keys)
        EXPECTED RESULT ON FIXED CODE: PASS (rejects weak keys)
        """
        # Generate weak keys with insufficient entropy
        if char_type == 'lowercase':
            weak_key = ''.join(['a'] * key_length)
        elif char_type == 'uppercase':
            weak_key = ''.join(['A'] * key_length)
        elif char_type == 'digits':
            weak_key = ''.join(['1'] * key_length)
        elif char_type == 'mixed_two':
            # Mix only 2 categories (still insufficient)
            weak_key = ('a' * (key_length // 2)) + ('1' * (key_length - key_length // 2))
        
        # Setup environment with weak key
        monkeypatch.setenv("SECRET_KEY", weak_key)
        
        # Expected Behavior: Should raise ValueError about insufficient entropy
        with pytest.raises(ValueError) as exc_info:
            JWTService._get_secret_key()
        
        error_message = str(exc_info.value)
        assert "entropy" in error_message.lower() or "complexity" in error_message.lower()
    
    def test_bug_condition_secret_key_only_lowercase(self, monkeypatch):
        """
        **Validates: Requirement 2.2**
        
        Specific Bug Condition: SECRET_KEY with only lowercase letters
        Expected Behavior: System SHALL reject with entropy error
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (accepts key)
        EXPECTED RESULT ON FIXED CODE: PASS (rejects key)
        """
        weak_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # 32 lowercase chars
        monkeypatch.setenv("SECRET_KEY", weak_key)
        
        with pytest.raises(ValueError) as exc_info:
            JWTService._get_secret_key()
        
        error_message = str(exc_info.value)
        assert "entropy" in error_message.lower() or "complexity" in error_message.lower()
        assert "uppercase" in error_message.lower() or "lowercase" in error_message.lower()
    
    def test_bug_condition_secret_key_only_uppercase(self, monkeypatch):
        """
        **Validates: Requirement 2.2**
        
        Specific Bug Condition: SECRET_KEY with only uppercase letters
        Expected Behavior: System SHALL reject with entropy error
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (accepts key)
        EXPECTED RESULT ON FIXED CODE: PASS (rejects key)
        """
        weak_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"  # 32 uppercase chars
        monkeypatch.setenv("SECRET_KEY", weak_key)
        
        with pytest.raises(ValueError) as exc_info:
            JWTService._get_secret_key()
        
        error_message = str(exc_info.value)
        assert "entropy" in error_message.lower() or "complexity" in error_message.lower()
    
    def test_bug_condition_secret_key_only_digits(self, monkeypatch):
        """
        **Validates: Requirement 2.2**
        
        Specific Bug Condition: SECRET_KEY with only digits
        Expected Behavior: System SHALL reject with entropy error
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (accepts key)
        EXPECTED RESULT ON FIXED CODE: PASS (rejects key)
        """
        weak_key = "12345678901234567890123456789012"  # 32 digits
        monkeypatch.setenv("SECRET_KEY", weak_key)
        
        with pytest.raises(ValueError) as exc_info:
            JWTService._get_secret_key()
        
        error_message = str(exc_info.value)
        assert "entropy" in error_message.lower() or "complexity" in error_message.lower()
    
    def test_bug_condition_ricoh_admin_password_empty(self):
        """
        **Validates: Requirement 2.3**
        
        Bug Condition: RicohWebClient accepts empty admin_password
        Expected Behavior: System SHALL reject with ValueError
        
        Test Strategy: Initialize RicohWebClient with admin_password=""
        and verify it raises ValueError.
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (accepts empty password)
        EXPECTED RESULT ON FIXED CODE: PASS (rejects empty password)
        """
        # Expected Behavior: Should raise ValueError for empty password
        with pytest.raises(ValueError) as exc_info:
            RicohWebClient(admin_password="")
        
        error_message = str(exc_info.value)
        assert "RICOH_ADMIN_PASSWORD" in error_message or "password" in error_message.lower()
        assert "must be set" in error_message.lower() or "required" in error_message.lower()
    
    def test_bug_condition_ricoh_admin_password_none(self, monkeypatch):
        """
        **Validates: Requirement 2.3**
        
        Bug Condition: RicohWebClient accepts None admin_password
        Expected Behavior: System SHALL reject with ValueError
        
        Test Strategy: Initialize RicohWebClient without admin_password
        and no RICOH_ADMIN_PASSWORD env var, verify it raises ValueError.
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (accepts None/uses default)
        EXPECTED RESULT ON FIXED CODE: PASS (rejects None)
        """
        # Remove environment variable
        monkeypatch.delenv("RICOH_ADMIN_PASSWORD", raising=False)
        
        # Expected Behavior: Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            RicohWebClient()
        
        error_message = str(exc_info.value)
        assert "RICOH_ADMIN_PASSWORD" in error_message or "password" in error_message.lower()
    
    def test_bug_condition_database_url_not_configured(self, monkeypatch):
        """
        **Validates: Requirement 2.4**
        
        Bug Condition: database.py uses hardcoded DATABASE_URL when not configured
        Expected Behavior: System SHALL reject with ValueError when DATABASE_URL not set
        
        Test Strategy: Remove DATABASE_URL env var and attempt to import database module,
        verify it raises ValueError.
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (uses hardcoded default)
        EXPECTED RESULT ON FIXED CODE: PASS (raises ValueError)
        """
        # Remove DATABASE_URL
        monkeypatch.delenv("DATABASE_URL", raising=False)
        
        # Expected Behavior: Importing database module should raise ValueError
        # Since database.py is already imported, we need to reload it
        import importlib
        import db.database as db_module
        
        with pytest.raises(ValueError) as exc_info:
            importlib.reload(db_module)
        
        error_message = str(exc_info.value)
        assert "DATABASE_URL" in error_message
        assert "must be set" in error_message.lower() or "required" in error_message.lower()
    
    def test_bug_condition_database_url_hardcoded_credentials(self):
        """
        **Validates: Requirement 2.4**
        
        Bug Condition: database.py contains hardcoded credentials in default value
        Expected Behavior: System SHALL NOT provide default with credentials
        
        Test Strategy: Check if DATABASE_URL default contains hardcoded credentials
        like "ricoh_admin:ricoh_secure_2024".
        
        EXPECTED RESULT ON UNFIXED CODE: FAIL (contains hardcoded credentials)
        EXPECTED RESULT ON FIXED CODE: PASS (no hardcoded credentials)
        """
        # Read the database.py source code
        import inspect
        import db.database as db_module
        
        source_file = inspect.getsourcefile(db_module)
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        # Expected Behavior: Source should NOT contain hardcoded credentials
        assert "ricoh_admin:ricoh_secure_2024" not in source_code, \
            "database.py contains hardcoded credentials in default DATABASE_URL"
        
        # Also check that there's no default value with credentials pattern
        assert "postgresql://" not in source_code or \
               ("postgresql://" in source_code and "ricoh_admin" not in source_code), \
            "database.py contains hardcoded database credentials"


@pytest.mark.property
class TestBugConditionDocumentation:
    """
    Documentation tests to capture counterexamples found during exploration.
    
    These tests document the specific bugs found in the unfixed code.
    """
    
    def test_document_encryption_key_temporary_generation(self, monkeypatch):
        """
        COUNTEREXAMPLE DOCUMENTATION:
        
        When ENCRYPTION_KEY is not set in development environment,
        the unfixed code generates a temporary key with warning:
        "⚠️ ENCRYPTION_KEY no configurada, generando clave temporal"
        
        This causes data loss on restart as the key is not persisted.
        """
        monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        
        EncryptionService._initialized = False
        EncryptionService._cipher = None
        
        # On unfixed code, this would succeed and generate temporary key
        # On fixed code, this should raise ValueError
        try:
            EncryptionService.initialize()
            pytest.fail("UNFIXED CODE: Accepted None ENCRYPTION_KEY and generated temporary key")
        except ValueError:
            # Fixed code behavior - this is what we want
            pass
    
    def test_document_secret_key_weak_acceptance(self, monkeypatch):
        """
        COUNTEREXAMPLE DOCUMENTATION:
        
        The unfixed code accepts SECRET_KEY with only lowercase letters:
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" (32 chars, all lowercase)
        
        This key has insufficient entropy and can be cracked by brute force.
        """
        weak_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        monkeypatch.setenv("SECRET_KEY", weak_key)
        
        # On unfixed code, this would succeed
        # On fixed code, this should raise ValueError
        try:
            result = JWTService._get_secret_key()
            pytest.fail(f"UNFIXED CODE: Accepted weak SECRET_KEY: {result}")
        except ValueError:
            # Fixed code behavior
            pass
    
    def test_document_ricoh_password_empty_default(self):
        """
        COUNTEREXAMPLE DOCUMENTATION:
        
        The unfixed code accepts empty admin_password with default value "":
        def __init__(self, timeout: int = 30, admin_user: str = "admin", admin_password: str = "")
        
        This allows authentication attempts with empty password.
        """
        # On unfixed code, this would succeed
        # On fixed code, this should raise ValueError
        try:
            client = RicohWebClient(admin_password="")
            pytest.fail("UNFIXED CODE: Accepted empty admin_password")
        except ValueError:
            # Fixed code behavior
            pass
    
    def test_document_database_url_hardcoded(self):
        """
        COUNTEREXAMPLE DOCUMENTATION:
        
        The unfixed code contains hardcoded DATABASE_URL with credentials:
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet"
        )
        
        This exposes credentials in source code and can be used accidentally in production.
        """
        import inspect
        import db.database as db_module
        
        source_file = inspect.getsourcefile(db_module)
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        # On unfixed code, this would find the hardcoded credentials
        # On fixed code, this should not find them
        if "ricoh_admin:ricoh_secure_2024" in source_code:
            pytest.fail("UNFIXED CODE: Found hardcoded credentials in database.py")

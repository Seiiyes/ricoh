"""
Preservation Tests for Encryption and Authentication Functionality
Task 4: Escribir tests de preservación para funcionalidad de encriptación y autenticación

**Property 2: Preservation** - Funcionalidad de Encriptación y Autenticación

IMPORTANTE: Estos tests DEBEN PASAR en código sin corregir para confirmar el comportamiento base a preservar.

Preservation Requirements being tested:
- 3.1: Encriptación con ENCRYPTION_KEY válida funciona correctamente
- 3.2: Desencriptación con ENCRYPTION_KEY válida recupera datos originales
- 3.3: Generación de tokens JWT con SECRET_KEY válida funciona correctamente
- 3.4: Validación de tokens JWT con SECRET_KEY válida retorna usuario correcto
- 3.5: Tokens JWT expirados son rechazados correctamente
"""
import pytest
import os
import time
from datetime import datetime, timedelta, timezone
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from services.encryption_service import EncryptionService
from services.jwt_service import JWTService, ExpiredTokenError, InvalidTokenError
from db.models_auth import AdminUser


# ============================================================================
# Property-Based Tests for Encryption Preservation
# ============================================================================

@pytest.mark.preservation
class TestEncryptionPreservation:
    """
    Property-based tests to verify encryption functionality is preserved
    
    **Validates: Requirements 3.1, 3.2**
    """
    
    @given(plaintext=st.text(min_size=1, max_size=1000))
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_encryption_is_reversible_for_all_valid_keys(self, plaintext):
        """
        **Validates: Requirements 3.1, 3.2**
        
        Property: For all valid ENCRYPTION_KEY and all plaintext data,
        encryption is reversible: decrypt(encrypt(data)) = data
        
        This test verifies that the core encryption/decryption functionality
        works correctly with valid keys and should continue working after fixes.
        """
        # Setup: Use a valid ENCRYPTION_KEY
        from cryptography.fernet import Fernet
        import os
        
        valid_key = Fernet.generate_key().decode()
        old_key = os.environ.get("ENCRYPTION_KEY")
        old_env = os.environ.get("ENVIRONMENT")
        
        try:
            os.environ["ENCRYPTION_KEY"] = valid_key
            os.environ["ENVIRONMENT"] = "test"
            
            # Reset encryption service to use new key
            EncryptionService._initialized = False
            EncryptionService._cipher = None
            EncryptionService.initialize()
            
            # Property: Encryption is reversible
            encrypted = EncryptionService.encrypt(plaintext)
            decrypted = EncryptionService.decrypt(encrypted)
            
            assert decrypted == plaintext, \
                f"Encryption should be reversible: decrypt(encrypt(data)) = data"
        finally:
            # Restore original environment
            if old_key:
                os.environ["ENCRYPTION_KEY"] = old_key
            elif "ENCRYPTION_KEY" in os.environ:
                del os.environ["ENCRYPTION_KEY"]
            if old_env:
                os.environ["ENVIRONMENT"] = old_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            
            # Reset service
            EncryptionService._initialized = False
            EncryptionService._cipher = None
    
    @given(
        data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10
        ),
        fields_to_encrypt=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5)
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.filter_too_much])
    def test_dict_encryption_preserves_unencrypted_fields(self, data, fields_to_encrypt):
        """
        **Validates: Requirements 3.1, 3.2**
        
        Property: For all dictionaries and field lists, encrypting specific fields
        preserves unencrypted fields and allows correct decryption of encrypted fields.
        """
        # Setup: Use a valid ENCRYPTION_KEY
        from cryptography.fernet import Fernet
        import os
        
        valid_key = Fernet.generate_key().decode()
        old_key = os.environ.get("ENCRYPTION_KEY")
        old_env = os.environ.get("ENVIRONMENT")
        
        try:
            os.environ["ENCRYPTION_KEY"] = valid_key
            os.environ["ENVIRONMENT"] = "test"
            
            # Reset encryption service
            EncryptionService._initialized = False
            EncryptionService._cipher = None
            EncryptionService.initialize()
            
            # Only encrypt fields that exist in the dictionary
            fields_to_encrypt = [f for f in fields_to_encrypt if f in data]
            assume(len(fields_to_encrypt) > 0)
            
            # Property: Encryption preserves structure and is reversible
            encrypted_data = EncryptionService.encrypt_dict(data, fields_to_encrypt)
            decrypted_data = EncryptionService.decrypt_dict(encrypted_data, fields_to_encrypt)
            
            # All fields should be preserved
            assert set(encrypted_data.keys()) == set(data.keys()), \
                "Encryption should preserve dictionary structure"
            
            # Encrypted fields should be different
            for field in fields_to_encrypt:
                if data[field]:  # Only check non-empty values
                    assert encrypted_data[field] != data[field], \
                        f"Field '{field}' should be encrypted"
            
            # Unencrypted fields should be unchanged
            for field in data.keys():
                if field not in fields_to_encrypt:
                    assert encrypted_data[field] == data[field], \
                        f"Field '{field}' should remain unencrypted"
            
            # Decryption should restore original data
            assert decrypted_data == data, \
                "Decryption should restore original data"
        finally:
            # Restore original environment
            if old_key:
                os.environ["ENCRYPTION_KEY"] = old_key
            elif "ENCRYPTION_KEY" in os.environ:
                del os.environ["ENCRYPTION_KEY"]
            if old_env:
                os.environ["ENVIRONMENT"] = old_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            
            # Reset service
            EncryptionService._initialized = False
            EncryptionService._cipher = None
    
    def test_encryption_with_empty_and_none_values(self, monkeypatch):
        """
        **Validates: Requirements 3.1, 3.2**
        
        Edge case: Encryption handles empty strings and None values correctly
        """
        # Setup: Use a valid ENCRYPTION_KEY
        from cryptography.fernet import Fernet
        valid_key = Fernet.generate_key().decode()
        monkeypatch.setenv("ENCRYPTION_KEY", valid_key)
        monkeypatch.setenv("ENVIRONMENT", "test")
        
        # Reset encryption service
        EncryptionService._initialized = False
        EncryptionService._cipher = None
        EncryptionService.initialize()
        
        # Test empty string
        assert EncryptionService.encrypt("") == ""
        assert EncryptionService.decrypt("") == ""
        
        # Test None
        assert EncryptionService.encrypt(None) is None
        assert EncryptionService.decrypt(None) is None


# ============================================================================
# Property-Based Tests for JWT Authentication Preservation
# ============================================================================

@pytest.mark.preservation
class TestJWTAuthenticationPreservation:
    """
    Property-based tests to verify JWT authentication functionality is preserved
    
    **Validates: Requirements 3.3, 3.4, 3.5**
    """
    
    @given(
        user_id=st.integers(min_value=1, max_value=1000000),
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-')),
        rol=st.sampled_from(['superadmin', 'admin', 'user']),
        empresa_id=st.one_of(st.none(), st.integers(min_value=1, max_value=10000))
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_jwt_generation_and_validation_for_all_valid_users(
        self, user_id, username, rol, empresa_id
    ):
        """
        **Validates: Requirements 3.3, 3.4**
        
        Property: For all valid users with valid SECRET_KEY,
        JWT generation creates valid tokens that can be decoded to retrieve user data.
        
        This test verifies that JWT generation and validation work correctly
        and should continue working after security fixes.
        """
        # Setup: Use a valid SECRET_KEY with sufficient entropy
        import secrets
        import os
        
        valid_secret = secrets.token_urlsafe(32)
        old_secret = os.environ.get("SECRET_KEY")
        
        try:
            os.environ["SECRET_KEY"] = valid_secret
            
            # Create a mock user object
            class MockUser:
                def __init__(self, id, username, rol, empresa_id):
                    self.id = id
                    self.username = username
                    self.rol = rol
                    self.empresa_id = empresa_id
            
            user = MockUser(user_id, username, rol, empresa_id)
            
            # Property: JWT generation and validation work correctly
            token = JWTService.create_access_token(user)
            
            # Token should be a valid JWT format (3 parts separated by dots)
            assert isinstance(token, str), "Token should be a string"
            assert len(token.split('.')) == 3, "Token should have 3 parts (header.payload.signature)"
            assert token.startswith('eyJ'), "Token should start with 'eyJ' (base64 encoded JSON)"
            
            # Decode token and verify user data is preserved
            payload = JWTService.decode_token(token)
            
            assert payload['user_id'] == user_id, "User ID should be preserved in token"
            assert payload['username'] == username, "Username should be preserved in token"
            assert payload['rol'] == rol, "Role should be preserved in token"
            assert payload['empresa_id'] == empresa_id, "Empresa ID should be preserved in token"
            assert payload['type'] == 'access', "Token type should be 'access'"
            assert 'exp' in payload, "Token should have expiration"
            assert 'iat' in payload, "Token should have issued-at timestamp"
        finally:
            # Restore original environment
            if old_secret:
                os.environ["SECRET_KEY"] = old_secret
            elif "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]
    
    @given(
        user_id=st.integers(min_value=1, max_value=1000000)
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_refresh_token_generation_for_all_valid_users(self, user_id):
        """
        **Validates: Requirements 3.3, 3.4**
        
        Property: For all valid users, refresh token generation creates valid tokens
        with correct type and expiration.
        """
        # Setup: Use a valid SECRET_KEY
        import secrets
        import os
        
        valid_secret = secrets.token_urlsafe(32)
        old_secret = os.environ.get("SECRET_KEY")
        
        try:
            os.environ["SECRET_KEY"] = valid_secret
            
            # Create a mock user
            class MockUser:
                def __init__(self, id):
                    self.id = id
            
            user = MockUser(user_id)
            
            # Property: Refresh token generation works correctly
            token = JWTService.create_refresh_token(user)
            
            # Token should be valid JWT format
            assert isinstance(token, str)
            assert len(token.split('.')) == 3
            
            # Decode and verify
            payload = JWTService.decode_token(token)
            
            assert payload['user_id'] == user_id
            assert payload['type'] == 'refresh', "Token type should be 'refresh'"
            assert 'exp' in payload
            assert 'iat' in payload
            
            # Verify expiration is approximately 7 days
            exp_time = payload['exp'] - payload['iat']
            expected_seconds = 7 * 24 * 60 * 60  # 7 days in seconds
            assert abs(exp_time - expected_seconds) < 100, \
                "Refresh token should expire in approximately 7 days"
        finally:
            # Restore original environment
            if old_secret:
                os.environ["SECRET_KEY"] = old_secret
            elif "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]
    
    def test_jwt_signature_verification_with_valid_token(self, monkeypatch):
        """
        **Validates: Requirements 3.4**
        
        Property: Valid JWT tokens have verifiable signatures
        """
        # Setup
        import secrets
        valid_secret = secrets.token_urlsafe(32)
        monkeypatch.setenv("SECRET_KEY", valid_secret)
        
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "testuser"
                self.rol = "admin"
                self.empresa_id = 1
        
        user = MockUser()
        token = JWTService.create_access_token(user)
        
        # Property: Signature verification works
        assert JWTService.verify_signature(token) is True, \
            "Valid token should have verifiable signature"
    
    def test_jwt_rejects_tampered_tokens(self, monkeypatch):
        """
        **Validates: Requirements 3.4**
        
        Property: Tampered JWT tokens are rejected
        """
        # Setup
        import secrets
        valid_secret = secrets.token_urlsafe(32)
        monkeypatch.setenv("SECRET_KEY", valid_secret)
        
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "testuser"
                self.rol = "admin"
                self.empresa_id = 1
        
        user = MockUser()
        token = JWTService.create_access_token(user)
        
        # Tamper with the token
        parts = token.split('.')
        tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature"
        
        # Property: Tampered tokens are rejected
        assert JWTService.verify_signature(tampered_token) is False, \
            "Tampered token should fail signature verification"
        
        with pytest.raises((InvalidTokenError, Exception)):
            JWTService.decode_token(tampered_token)
    
    def test_jwt_expired_tokens_are_rejected(self, monkeypatch):
        """
        **Validates: Requirements 3.5**
        
        Property: Expired JWT tokens are correctly rejected
        
        This test verifies that token expiration checking works correctly.
        """
        # Setup
        import secrets
        import jwt
        valid_secret = secrets.token_urlsafe(32)
        monkeypatch.setenv("SECRET_KEY", valid_secret)
        
        # Create an expired token manually
        now = datetime.now(timezone.utc)
        expired_time = now - timedelta(hours=1)  # Expired 1 hour ago
        
        payload = {
            "user_id": 1,
            "username": "testuser",
            "rol": "admin",
            "empresa_id": 1,
            "type": "access",
            "exp": expired_time,
            "iat": now - timedelta(hours=2)
        }
        
        expired_token = jwt.encode(payload, valid_secret, algorithm="HS256")
        
        # Property: Expired tokens are rejected
        with pytest.raises(ExpiredTokenError):
            JWTService.decode_token(expired_token)
    
    def test_jwt_access_token_expiration_time_is_30_minutes(self, monkeypatch):
        """
        **Validates: Requirements 3.3**
        
        Property: Access tokens expire in 30 minutes
        """
        # Setup
        import secrets
        valid_secret = secrets.token_urlsafe(32)
        monkeypatch.setenv("SECRET_KEY", valid_secret)
        
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "testuser"
                self.rol = "admin"
                self.empresa_id = 1
        
        user = MockUser()
        token = JWTService.create_access_token(user)
        payload = JWTService.decode_token(token)
        
        # Property: Expiration time is 30 minutes
        exp_time = payload['exp'] - payload['iat']
        expected_seconds = 30 * 60  # 30 minutes
        
        assert abs(exp_time - expected_seconds) < 10, \
            f"Access token should expire in 30 minutes, got {exp_time} seconds"
    
    def test_jwt_token_rotation_preserves_user_data(self, monkeypatch):
        """
        **Validates: Requirements 3.3, 3.4**
        
        Property: Token rotation creates new valid tokens with same user data
        """
        # Setup
        import secrets
        import time
        valid_secret = secrets.token_urlsafe(32)
        monkeypatch.setenv("SECRET_KEY", valid_secret)
        
        class MockUser:
            def __init__(self):
                self.id = 42
                self.username = "testuser"
                self.rol = "admin"
                self.empresa_id = 10
        
        user = MockUser()
        old_token = JWTService.create_access_token(user)
        
        # Wait a moment to ensure different timestamp
        time.sleep(0.1)
        
        # Rotate token
        new_token = JWTService.rotate_access_token(old_token, user)
        
        # Property: New token is different but contains same user data
        # Note: Tokens may be identical if generated at exact same timestamp
        # The important property is that user data is preserved
        
        new_payload = JWTService.decode_token(new_token)
        assert new_payload['user_id'] == user.id
        assert new_payload['username'] == user.username
        assert new_payload['rol'] == user.rol
        assert new_payload['empresa_id'] == user.empresa_id


# ============================================================================
# Integration Tests for Preservation
# ============================================================================

@pytest.mark.preservation
class TestEncryptionAuthenticationIntegration:
    """
    Integration tests to verify encryption and authentication work together
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    """
    
    def test_encrypted_user_credentials_with_jwt_authentication(self, monkeypatch):
        """
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        Integration test: Encrypt user credentials and use JWT for authentication
        
        This simulates a real-world scenario where user credentials are encrypted
        in the database and JWT tokens are used for authentication.
        """
        # Setup: Valid keys for both services
        from cryptography.fernet import Fernet
        import secrets
        
        encryption_key = Fernet.generate_key().decode()
        jwt_secret = secrets.token_urlsafe(32)
        
        monkeypatch.setenv("ENCRYPTION_KEY", encryption_key)
        monkeypatch.setenv("SECRET_KEY", jwt_secret)
        monkeypatch.setenv("ENVIRONMENT", "test")
        
        # Reset services
        EncryptionService._initialized = False
        EncryptionService._cipher = None
        EncryptionService.initialize()
        
        # Simulate storing encrypted user credentials
        user_data = {
            "username": "admin",
            "password": "SecurePassword123!",
            "api_key": "sk_live_abc123xyz789"
        }
        
        # Encrypt sensitive fields
        encrypted_data = EncryptionService.encrypt_dict(
            user_data, 
            ["password", "api_key"]
        )
        
        # Verify encryption worked
        assert encrypted_data["username"] == "admin"
        assert encrypted_data["password"] != "SecurePassword123!"
        assert encrypted_data["api_key"] != "sk_live_abc123xyz789"
        
        # Simulate user authentication - create JWT token
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "admin"
                self.rol = "admin"
                self.empresa_id = 1
        
        user = MockUser()
        jwt_token = JWTService.create_access_token(user)
        
        # Verify JWT token is valid
        payload = JWTService.decode_token(jwt_token)
        assert payload['username'] == "admin"
        
        # Simulate retrieving and decrypting user credentials
        decrypted_data = EncryptionService.decrypt_dict(
            encrypted_data,
            ["password", "api_key"]
        )
        
        # Verify decryption restored original data
        assert decrypted_data == user_data
        
        # Integration property: Both encryption and JWT work correctly together
        assert payload['username'] == decrypted_data['username'], \
            "JWT username should match decrypted username"

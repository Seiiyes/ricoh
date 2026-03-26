"""
Property-based tests for JWTService using Hypothesis
Tests universal properties that should hold for all inputs
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from services.jwt_service import JWTService
from db.models_auth import AdminUser, Empresa
import jwt
import os


@pytest.mark.property
class TestJWTServiceProperties:
    """Property-based test suite for JWTService"""
    
    @given(
        st.integers(min_value=1, max_value=10000),
        st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.sampled_from(['superadmin', 'admin', 'viewer', 'operator'])
    )
    @settings(max_examples=100)
    def test_property_jwt_signature_validation(self, user_id, username, rol):
        """
        Property 9: JWT Signature Validation
        
        For any valid user data:
        - Generated tokens should validate correctly
        - Tokens with modified signature should be rejected
        - Tokens with wrong SECRET_KEY should be rejected
        - Expired tokens should be rejected with correct message
        """
        # Create mock user
        user = AdminUser(
            id=user_id,
            username=username,
            rol=rol,
            empresa_id=1 if rol != 'superadmin' else None
        )
        
        # Property 1: Valid token validates correctly
        access_token = JWTService.create_access_token(user)
        decoded = JWTService.decode_token(access_token)
        
        assert decoded['user_id'] == user_id, "Token should contain correct user_id"
        assert decoded['username'] == username, "Token should contain correct username"
        assert decoded['rol'] == rol, "Token should contain correct rol"
        assert JWTService.verify_signature(access_token) is True, \
            "Valid token should verify successfully"
        
        # Property 2: Modified signature is rejected
        parts = access_token.split('.')
        if len(parts) == 3:
            # Modify the signature
            modified_token = f"{parts[0]}.{parts[1]}.invalid_signature"
            
            with pytest.raises(Exception):  # Should raise InvalidTokenError or similar
                JWTService.decode_token(modified_token)
        
        # Property 3: Wrong SECRET_KEY is rejected
        wrong_secret = "wrong_secret_key_12345678901234567890"
        try:
            jwt.decode(access_token, wrong_secret, algorithms=["HS256"])
            assert False, "Token with wrong SECRET_KEY should be rejected"
        except jwt.InvalidSignatureError:
            pass  # Expected
        
        # Property 4: Expired token is rejected
        # Create an expired token manually
        expired_payload = {
            'user_id': user_id,
            'username': username,
            'rol': rol,
            'empresa_id': user.empresa_id,
            'exp': datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        
        secret_key = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production_min_32_chars")
        expired_token = jwt.encode(expired_payload, secret_key, algorithm="HS256")
        
        with pytest.raises(Exception):  # Should raise ExpiredTokenError or similar
            JWTService.decode_token(expired_token)
    
    @given(
        st.integers(min_value=1, max_value=10000),
        st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=50)
    def test_property_token_payload_completeness(self, user_id, username):
        """
        Property: Token payload should always contain required fields
        
        For any user, generated tokens should contain:
        - user_id
        - username
        - rol
        - empresa_id (or null for superadmin)
        - exp (expiration)
        - iat (issued at)
        """
        user = AdminUser(
            id=user_id,
            username=username,
            rol='admin',
            empresa_id=1
        )
        
        # Test access token
        access_token = JWTService.create_access_token(user)
        decoded = JWTService.decode_token(access_token)
        
        required_fields = ['user_id', 'username', 'rol', 'empresa_id', 'exp', 'iat']
        for field in required_fields:
            assert field in decoded, f"Token should contain {field}"
        
        # Test refresh token
        refresh_token = JWTService.create_refresh_token(user)
        decoded_refresh = JWTService.decode_token(refresh_token)
        
        assert 'user_id' in decoded_refresh, "Refresh token should contain user_id"
        assert 'type' in decoded_refresh, "Refresh token should contain type"
        assert decoded_refresh['type'] == 'refresh', "Refresh token type should be 'refresh'"
        assert 'exp' in decoded_refresh, "Refresh token should contain exp"
        assert 'iat' in decoded_refresh, "Refresh token should contain iat"
    
    @given(st.integers(min_value=1, max_value=10000))
    @settings(max_examples=50)
    def test_property_token_expiration_times(self, user_id):
        """
        Property: Token expiration times should be correct
        
        - Access token should expire in ~30 minutes
        - Refresh token should expire in ~7 days
        """
        user = AdminUser(
            id=user_id,
            username='testuser',
            rol='admin',
            empresa_id=1
        )
        
        # Test access token expiration (~30 minutes)
        access_token = JWTService.create_access_token(user)
        decoded = JWTService.decode_token(access_token)
        
        exp_time = datetime.fromtimestamp(decoded['exp'])
        iat_time = datetime.fromtimestamp(decoded['iat'])
        duration = (exp_time - iat_time).total_seconds()
        
        # Should be approximately 30 minutes (1800 seconds), allow 10 second tolerance
        assert 1790 <= duration <= 1810, \
            f"Access token should expire in ~30 minutes, got {duration} seconds"
        
        # Test refresh token expiration (~7 days)
        refresh_token = JWTService.create_refresh_token(user)
        decoded_refresh = JWTService.decode_token(refresh_token)
        
        exp_time_refresh = datetime.fromtimestamp(decoded_refresh['exp'])
        iat_time_refresh = datetime.fromtimestamp(decoded_refresh['iat'])
        duration_refresh = (exp_time_refresh - iat_time_refresh).total_seconds()
        
        # Should be approximately 7 days (604800 seconds), allow 60 second tolerance
        assert 604740 <= duration_refresh <= 604860, \
            f"Refresh token should expire in ~7 days, got {duration_refresh} seconds"
    
    @given(st.integers(min_value=1, max_value=10000))
    @settings(max_examples=30)
    def test_property_superadmin_empresa_id_null(self, user_id):
        """
        Property: Superadmin tokens should have empresa_id = null
        
        For any superadmin user, the token should have empresa_id as null
        """
        user = AdminUser(
            id=user_id,
            username='superadmin',
            rol='superadmin',
            empresa_id=None
        )
        
        access_token = JWTService.create_access_token(user)
        decoded = JWTService.decode_token(access_token)
        
        assert decoded['empresa_id'] is None, \
            "Superadmin token should have empresa_id = null"
        assert decoded['rol'] == 'superadmin', \
            "Token should have rol = superadmin"

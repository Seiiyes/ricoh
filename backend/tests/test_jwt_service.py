"""
Unit tests for JWTService
"""
import pytest
import time
from services.jwt_service import JWTService
from db.models_auth import AdminUser


@pytest.mark.unit
class TestJWTService:
    """Test suite for JWTService"""
    
    def test_create_access_token_returns_valid_jwt(self, superadmin_user):
        """Test that create_access_token returns a valid JWT"""
        token = JWTService.create_access_token(superadmin_user)
        
        # JWT should have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3
        # Should start with eyJ (base64 encoded JSON)
        assert token.startswith("eyJ")
    
    def test_create_access_token_includes_user_data(self, superadmin_user):
        """Test that access token includes user data in payload"""
        token = JWTService.create_access_token(superadmin_user)
        payload = JWTService.decode_token(token)
        
        assert payload["user_id"] == superadmin_user.id
        assert payload["username"] == superadmin_user.username
        assert payload["rol"] == superadmin_user.rol
        assert payload["empresa_id"] == superadmin_user.empresa_id
    
    def test_create_refresh_token_returns_valid_jwt(self, superadmin_user):
        """Test that create_refresh_token returns a valid JWT"""
        token = JWTService.create_refresh_token(superadmin_user)
        
        parts = token.split(".")
        assert len(parts) == 3
        assert token.startswith("eyJ")
    
    def test_create_refresh_token_includes_type(self, superadmin_user):
        """Test that refresh token includes type in payload"""
        token = JWTService.create_refresh_token(superadmin_user)
        payload = JWTService.decode_token(token)
        
        assert payload["type"] == "refresh"
        assert payload["user_id"] == superadmin_user.id
    
    def test_decode_token_with_valid_token(self, superadmin_user):
        """Test that decode_token successfully decodes valid token"""
        token = JWTService.create_access_token(superadmin_user)
        payload = JWTService.decode_token(token)
        
        assert payload is not None
        assert "user_id" in payload
        assert "exp" in payload
        assert "iat" in payload
    
    def test_decode_token_with_invalid_signature(self, superadmin_user):
        """Test that decode_token raises error for invalid signature"""
        token = JWTService.create_access_token(superadmin_user)
        # Tamper with the signature
        parts = token.split(".")
        tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature"
        
        with pytest.raises(Exception):
            JWTService.decode_token(tampered_token)
    
    def test_verify_signature_with_valid_token(self, superadmin_user):
        """Test that verify_signature returns True for valid token"""
        token = JWTService.create_access_token(superadmin_user)
        
        assert JWTService.verify_signature(token) is True
    
    def test_verify_signature_with_invalid_token(self):
        """Test that verify_signature returns False for invalid token"""
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.invalid"
        
        assert JWTService.verify_signature(invalid_token) is False
    
    def test_access_token_expiration_time(self, superadmin_user):
        """Test that access token has 30 minute expiration"""
        token = JWTService.create_access_token(superadmin_user)
        payload = JWTService.decode_token(token)
        
        # Calculate expiration time (should be ~30 minutes = 1800 seconds)
        exp_time = payload["exp"] - payload["iat"]
        assert 1790 <= exp_time <= 1810  # Allow small variance
    
    def test_refresh_token_expiration_time(self, superadmin_user):
        """Test that refresh token has 7 day expiration"""
        token = JWTService.create_refresh_token(superadmin_user)
        payload = JWTService.decode_token(token)
        
        # Calculate expiration time (should be ~7 days = 604800 seconds)
        exp_time = payload["exp"] - payload["iat"]
        assert 604700 <= exp_time <= 604900  # Allow small variance

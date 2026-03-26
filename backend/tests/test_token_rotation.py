"""
Tests for Token Rotation
"""
import pytest
import time
from datetime import datetime, timedelta, timezone
from services.jwt_service import JWTService
from unittest.mock import Mock


class TestTokenRotation:
    """Tests para rotación de tokens JWT"""
    
    @pytest.fixture
    def mock_user(self):
        """Mock user for testing"""
        user = Mock()
        user.id = 1
        user.username = "testuser"
        user.rol = "admin"
        user.empresa_id = 1
        return user
    
    def test_should_rotate_token_near_expiration(self, mock_user):
        """Test token debe rotarse cuando está cerca de expirar"""
        # Crear token
        token = JWTService.create_access_token(mock_user)
        
        # Con threshold de 31 minutos, token de 30 min debe rotarse
        should_rotate = JWTService.should_rotate_token(token, rotation_threshold_minutes=31)
        assert should_rotate is True
    
    def test_should_not_rotate_token_far_from_expiration(self, mock_user):
        """Test token NO debe rotarse cuando está lejos de expirar"""
        # Crear token
        token = JWTService.create_access_token(mock_user)
        
        # Con threshold de 5 minutos, token de 30 min NO debe rotarse
        should_rotate = JWTService.should_rotate_token(token, rotation_threshold_minutes=5)
        assert should_rotate is False
    
    def test_rotate_access_token(self, mock_user):
        """Test rotar access token"""
        # Crear token original
        original_token = JWTService.create_access_token(mock_user)
        
        # Esperar 1 segundo para que el timestamp sea diferente
        time.sleep(1)
        
        # Rotar token
        new_token = JWTService.rotate_access_token(original_token, mock_user)
        
        # Tokens deben ser diferentes
        assert new_token != original_token
        
        # Nuevo token debe ser válido
        payload = JWTService.decode_token(new_token)
        assert payload["user_id"] == mock_user.id
        assert payload["username"] == mock_user.username
        assert payload["type"] == "access"
    
    def test_rotate_token_validates_user_id(self, mock_user):
        """Test rotación valida que user_id coincida"""
        # Crear token para user 1
        token = JWTService.create_access_token(mock_user)
        
        # Intentar rotar con user 2
        other_user = Mock()
        other_user.id = 2
        other_user.username = "otheruser"
        other_user.rol = "admin"
        other_user.empresa_id = 1
        
        # Debe fallar
        with pytest.raises(Exception):
            JWTService.rotate_access_token(token, other_user)
    
    def test_get_token_expiration(self, mock_user):
        """Test obtener fecha de expiración del token"""
        # Crear token
        token = JWTService.create_access_token(mock_user)
        
        # Obtener expiración
        expiration = JWTService.get_token_expiration(token)
        
        # Debe ser datetime
        assert isinstance(expiration, datetime)
        
        # Debe ser en el futuro
        assert expiration > datetime.now(timezone.utc)
        
        # Debe ser aproximadamente 30 minutos en el futuro
        time_diff = expiration - datetime.now(timezone.utc)
        assert 29 <= time_diff.total_seconds() / 60 <= 31
    
    def test_rotation_threshold_edge_cases(self, mock_user):
        """Test casos extremos del threshold de rotación"""
        token = JWTService.create_access_token(mock_user)
        
        # Threshold de 0 minutos - siempre debe rotar
        assert JWTService.should_rotate_token(token, rotation_threshold_minutes=0) is False
        
        # Threshold de 30 minutos - siempre debe rotar
        assert JWTService.should_rotate_token(token, rotation_threshold_minutes=30) is True
        
        # Threshold de 60 minutos - siempre debe rotar
        assert JWTService.should_rotate_token(token, rotation_threshold_minutes=60) is True

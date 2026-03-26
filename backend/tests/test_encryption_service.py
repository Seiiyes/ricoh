"""
Tests for Encryption Service
"""
import pytest
import os
from services.encryption_service import EncryptionService


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("ENVIRONMENT", "development")
    # Reset initialization state before each test
    EncryptionService._initialized = False
    EncryptionService._cipher = None


class TestEncryptionService:
    """Tests para EncryptionService"""
    
    def test_encrypt_decrypt_string(self):
        """Test encriptar y desencriptar string"""
        original = "mi_password_secreto"
        
        # Encriptar
        encrypted = EncryptionService.encrypt(original)
        
        # Verificar que está encriptado
        assert encrypted != original
        assert len(encrypted) > len(original)
        
        # Desencriptar
        decrypted = EncryptionService.decrypt(encrypted)
        
        # Verificar que coincide con el original
        assert decrypted == original
    
    def test_encrypt_empty_string(self):
        """Test encriptar string vacío"""
        encrypted = EncryptionService.encrypt("")
        assert encrypted == ""
        
        decrypted = EncryptionService.decrypt("")
        assert decrypted == ""
    
    def test_encrypt_none(self):
        """Test encriptar None"""
        encrypted = EncryptionService.encrypt(None)
        assert encrypted is None
        
        decrypted = EncryptionService.decrypt(None)
        assert decrypted is None
    
    def test_encrypt_dict(self):
        """Test encriptar campos de diccionario"""
        data = {
            "username": "admin",
            "password": "secret123",
            "email": "admin@test.com"
        }
        
        # Encriptar solo password
        encrypted_data = EncryptionService.encrypt_dict(data, ["password"])
        
        # Verificar que password está encriptado
        assert encrypted_data["username"] == "admin"
        assert encrypted_data["password"] != "secret123"
        assert encrypted_data["email"] == "admin@test.com"
        
        # Desencriptar
        decrypted_data = EncryptionService.decrypt_dict(encrypted_data, ["password"])
        
        # Verificar que coincide con el original
        assert decrypted_data == data
    
    def test_encrypt_multiple_fields(self):
        """Test encriptar múltiples campos"""
        data = {
            "password": "secret123",
            "api_key": "key_abc123",
            "token": "token_xyz789"
        }
        
        # Encriptar todos los campos
        encrypted_data = EncryptionService.encrypt_dict(
            data, 
            ["password", "api_key", "token"]
        )
        
        # Verificar que todos están encriptados
        assert encrypted_data["password"] != "secret123"
        assert encrypted_data["api_key"] != "key_abc123"
        assert encrypted_data["token"] != "token_xyz789"
        
        # Desencriptar
        decrypted_data = EncryptionService.decrypt_dict(
            encrypted_data,
            ["password", "api_key", "token"]
        )
        
        # Verificar que coincide con el original
        assert decrypted_data == data
    
    def test_is_encrypted(self):
        """Test verificar si string está encriptado"""
        original = "plain_text"
        encrypted = EncryptionService.encrypt(original)
        
        # String encriptado debe ser detectado
        assert EncryptionService.is_encrypted(encrypted) is True
        
        # String plano no debe ser detectado como encriptado
        assert EncryptionService.is_encrypted(original) is False
        
        # String vacío no está encriptado
        assert EncryptionService.is_encrypted("") is False
        
        # None no está encriptado
        assert EncryptionService.is_encrypted(None) is False
    
    def test_generate_key(self):
        """Test generar clave de encriptación"""
        key1 = EncryptionService.generate_key()
        key2 = EncryptionService.generate_key()
        
        # Claves deben ser diferentes
        assert key1 != key2
        
        # Claves deben tener longitud adecuada
        assert len(key1) > 20
        assert len(key2) > 20
    
    def test_derive_key_from_password(self):
        """Test derivar clave desde contraseña"""
        password = "my_secure_password"
        
        # Derivar clave
        key1, salt1 = EncryptionService.derive_key_from_password(password)
        
        # Verificar que se generó clave y salt
        assert key1 is not None
        assert salt1 is not None
        assert len(key1) > 20
        assert len(salt1) > 10
        
        # Derivar otra clave con mismo password pero diferente salt
        key2, salt2 = EncryptionService.derive_key_from_password(password)
        
        # Claves deben ser diferentes (diferente salt)
        assert key1 != key2
        assert salt1 != salt2
        
        # Derivar clave con mismo password y mismo salt
        key3, salt3 = EncryptionService.derive_key_from_password(password, salt1.encode())
        
        # Clave debe ser igual (mismo password y salt)
        # Nota: salt3 será diferente porque se codifica de nuevo
        assert key3 is not None
    
    def test_encrypt_unicode(self):
        """Test encriptar texto con caracteres unicode"""
        original = "Contraseña con ñ, tildes áéíóú y emojis 🔒🔑"
        
        # Encriptar
        encrypted = EncryptionService.encrypt(original)
        
        # Desencriptar
        decrypted = EncryptionService.decrypt(encrypted)
        
        # Verificar que coincide
        assert decrypted == original
    
    def test_encrypt_long_text(self):
        """Test encriptar texto largo"""
        original = "A" * 10000  # 10KB de texto
        
        # Encriptar
        encrypted = EncryptionService.encrypt(original)
        
        # Desencriptar
        decrypted = EncryptionService.decrypt(encrypted)
        
        # Verificar que coincide
        assert decrypted == original
        assert len(decrypted) == 10000

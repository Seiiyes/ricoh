"""
Unit tests for PasswordService
"""
import pytest
from services.password_service import PasswordService


@pytest.mark.unit
class TestPasswordService:
    """Test suite for PasswordService"""
    
    def test_hash_password_returns_valid_bcrypt_hash(self):
        """Test that hash_password returns a valid bcrypt hash"""
        password = "TestPassword123!"
        password_hash = PasswordService.hash_password(password)
        
        # Bcrypt hash should be 60 characters long
        assert len(password_hash) >= 60
        # Should start with $2b$ (bcrypt identifier)
        assert password_hash.startswith("$2b$")
    
    def test_hash_password_generates_different_hashes(self):
        """Test that same password generates different hashes (salted)"""
        password = "TestPassword123!"
        hash1 = PasswordService.hash_password(password)
        hash2 = PasswordService.hash_password(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
    
    def test_verify_password_with_correct_password(self):
        """Test that verify_password returns True for correct password"""
        password = "TestPassword123!"
        password_hash = PasswordService.hash_password(password)
        
        assert PasswordService.verify_password(password, password_hash) is True
    
    def test_verify_password_with_incorrect_password(self):
        """Test that verify_password returns False for incorrect password"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        password_hash = PasswordService.hash_password(password)
        
        assert PasswordService.verify_password(wrong_password, password_hash) is False
    
    def test_validate_password_strength_valid_password(self):
        """Test that validate_password_strength accepts valid password"""
        password = "ValidPass123!"
        result = PasswordService.validate_password_strength(password)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_password_strength_too_short(self):
        """Test that validate_password_strength rejects short password"""
        password = "Short1!"
        result = PasswordService.validate_password_strength(password)
        
        assert result.is_valid is False
        assert "al menos 8 caracteres" in str(result.errors)
    
    def test_validate_password_strength_no_uppercase(self):
        """Test that validate_password_strength rejects password without uppercase"""
        password = "lowercase123!"
        result = PasswordService.validate_password_strength(password)
        
        assert result.is_valid is False
        assert "mayúscula" in str(result.errors)
    
    def test_validate_password_strength_no_lowercase(self):
        """Test that validate_password_strength rejects password without lowercase"""
        password = "UPPERCASE123!"
        result = PasswordService.validate_password_strength(password)
        
        assert result.is_valid is False
        assert "minúscula" in str(result.errors)
    
    def test_validate_password_strength_no_digit(self):
        """Test that validate_password_strength rejects password without digit"""
        password = "NoDigits!"
        result = PasswordService.validate_password_strength(password)
        
        assert result.is_valid is False
        assert "número" in str(result.errors)
    
    def test_validate_password_strength_no_special_char(self):
        """Test that validate_password_strength rejects password without special char"""
        password = "NoSpecial123"
        result = PasswordService.validate_password_strength(password)
        
        assert result.is_valid is False
        assert "especial" in str(result.errors)
    
    def test_generate_temporary_password_length(self):
        """Test that generate_temporary_password returns 16 character password"""
        password = PasswordService.generate_temporary_password()
        
        assert len(password) == 16
    
    def test_generate_temporary_password_is_valid(self):
        """Test that generated temporary password passes strength validation"""
        password = PasswordService.generate_temporary_password()
        result = PasswordService.validate_password_strength(password)
        
        assert result.is_valid is True
    
    def test_generate_temporary_password_is_unique(self):
        """Test that generate_temporary_password generates unique passwords"""
        password1 = PasswordService.generate_temporary_password()
        password2 = PasswordService.generate_temporary_password()
        
        assert password1 != password2

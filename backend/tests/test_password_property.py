"""
Property-based tests for PasswordService using Hypothesis
Tests universal properties that should hold for all inputs
"""
import pytest
from hypothesis import given, strategies as st, settings
from services.password_service import PasswordService


@pytest.mark.property
class TestPasswordServiceProperties:
    """Property-based test suite for PasswordService"""
    
    @given(st.text(min_size=8, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
    @settings(max_examples=100, deadline=1000)  # Increase deadline for bcrypt
    def test_property_hash_uniqueness_and_verification(self, password):
        """
        Property 2: Password Hashing Uniqueness and Verification
        
        For any password string:
        - Hash should be >= 60 characters
        - Hash should start with "$2b$12$" (bcrypt with 12 rounds)
        - verify_password should return True for original password
        - Two hashes of same password should be different (salted)
        """
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        # Generate hash
        password_hash = PasswordService.hash_password(password)
        
        # Property 1: Hash has correct length
        assert len(password_hash) >= 60, "Hash should be at least 60 characters"
        
        # Property 2: Hash has correct format
        assert password_hash.startswith("$2b$12$"), "Hash should start with $2b$12$ (bcrypt 12 rounds)"
        
        # Property 3: Verification works
        assert PasswordService.verify_password(password, password_hash) is True, \
            "verify_password should return True for original password"
        
        # Property 4: Hashes are unique (salted)
        password_hash2 = PasswordService.hash_password(password)
        assert password_hash != password_hash2, \
            "Two hashes of same password should be different (salted)"
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
    @settings(max_examples=100)
    def test_property_password_strength_requirements(self, password):
        """
        Property 3: Password Strength Requirements
        
        For any password string, validation should:
        - Reject if < 8 characters
        - Reject if no uppercase letter
        - Reject if no lowercase letter
        - Reject if no digit
        - Reject if no special character
        - Accept if all requirements are met
        """
        result = PasswordService.validate_password_strength(password)
        
        # Check length requirement
        if len(password) < 8:
            assert result.is_valid is False, "Should reject passwords < 8 characters"
            # Check that error message exists (may vary in wording)
            assert len(result.errors) > 0, "Should have error messages"
        
        # Check uppercase requirement
        if not any(c.isupper() for c in password):
            assert result.is_valid is False, "Should reject passwords without uppercase"
            assert len(result.errors) > 0, "Should have error messages"
        
        # Check lowercase requirement
        if not any(c.islower() for c in password):
            assert result.is_valid is False, "Should reject passwords without lowercase"
            assert len(result.errors) > 0, "Should have error messages"
        
        # Check digit requirement
        if not any(c.isdigit() for c in password):
            assert result.is_valid is False, "Should reject passwords without digit"
            assert len(result.errors) > 0, "Should have error messages"
        
        # Check special character requirement
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            assert result.is_valid is False, "Should reject passwords without special char"
            assert len(result.errors) > 0, "Should have error messages"
        
        # If all requirements are met, should be valid
        if (len(password) >= 8 and
            any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in special_chars for c in password)):
            assert result.is_valid is True, \
                "Should accept passwords that meet all requirements"
    
    @given(st.text(min_size=8, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))), 
           st.text(min_size=8, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
    @settings(max_examples=50, deadline=1000)  # Increase deadline for bcrypt
    def test_property_wrong_password_never_verifies(self, password1, password2):
        """
        Property: Wrong password should never verify
        
        For any two different passwords, verification should fail
        """
        # Skip if passwords are the same
        if password1 == password2:
            return
        
        # Bcrypt has a 72-byte limit, truncate if necessary
        password1_bytes = password1.encode('utf-8')
        if len(password1_bytes) > 72:
            password1 = password1_bytes[:72].decode('utf-8', errors='ignore')
        
        password_hash = PasswordService.hash_password(password1)
        
        # Wrong password should not verify
        assert PasswordService.verify_password(password2, password_hash) is False, \
            "Wrong password should never verify against hash"
    
    def test_property_generated_passwords_always_valid(self):
        """
        Property: Generated temporary passwords should always be valid
        
        All generated passwords should:
        - Be exactly 16 characters
        - Pass strength validation
        - Be unique
        """
        passwords = set()
        
        for _ in range(50):
            password = PasswordService.generate_temporary_password()
            
            # Property 1: Correct length
            assert len(password) == 16, "Generated password should be 16 characters"
            
            # Property 2: Passes validation
            result = PasswordService.validate_password_strength(password)
            assert result.is_valid is True, \
                f"Generated password should pass validation: {password}"
            
            # Property 3: Uniqueness
            assert password not in passwords, "Generated passwords should be unique"
            passwords.add(password)

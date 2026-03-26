"""
Password Service
Servicio para hashing, validación y generación de contraseñas
"""
import bcrypt
import secrets
import string
from typing import NamedTuple


class ValidationResult(NamedTuple):
    """Result of password validation"""
    is_valid: bool
    errors: list[str]


class PasswordService:
    """Service for password operations"""
    
    # Bcrypt rounds (12 rounds = good balance between security and performance)
    BCRYPT_ROUNDS = 12
    
    # Password requirements
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash password using bcrypt with 12 rounds
        
        Args:
            password: Plain text password
            
        Returns:
            Bcrypt hash (60 characters)
            
        Example:
            >>> hash = PasswordService.hash_password("MyPassword123!")
            >>> len(hash)
            60
            >>> hash.startswith("$2b$12$")
            True
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=cls.BCRYPT_ROUNDS)
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return password_hash.decode('utf-8')
    
    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Bcrypt hash to verify against
            
        Returns:
            True if password matches hash, False otherwise
            
        Example:
            >>> hash = PasswordService.hash_password("MyPassword123!")
            >>> PasswordService.verify_password("MyPassword123!", hash)
            True
            >>> PasswordService.verify_password("WrongPassword", hash)
            False
        """
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False
    
    @classmethod
    def validate_password_strength(cls, password: str) -> ValidationResult:
        """
        Validate password meets requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        - At least 1 special character
        
        Args:
            password: Plain text password to validate
            
        Returns:
            ValidationResult with is_valid flag and list of errors
            
        Example:
            >>> result = PasswordService.validate_password_strength("weak")
            >>> result.is_valid
            False
            >>> len(result.errors) > 0
            True
            
            >>> result = PasswordService.validate_password_strength("StrongPass123!")
            >>> result.is_valid
            True
            >>> result.errors
            []
        """
        errors = []
        
        # Check minimum length
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")
        
        # Check uppercase
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check lowercase
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check digit
        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        # Check special character
        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            errors.append(f"Password must contain at least one special character ({cls.SPECIAL_CHARS})")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    @classmethod
    def generate_temporary_password(cls, length: int = 16) -> str:
        """
        Generate secure random password (16 characters by default)
        
        The generated password will contain:
        - Uppercase letters
        - Lowercase letters
        - Digits
        - Special characters
        
        Args:
            length: Length of password (default: 16)
            
        Returns:
            Secure random password that meets all strength requirements
            
        Example:
            >>> password = PasswordService.generate_temporary_password()
            >>> len(password)
            16
            >>> result = PasswordService.validate_password_strength(password)
            >>> result.is_valid
            True
        """
        if length < cls.MIN_LENGTH:
            length = cls.MIN_LENGTH
        
        # Ensure password contains at least one of each required character type
        password_chars = []
        
        # Add at least one of each required type
        if cls.REQUIRE_UPPERCASE:
            password_chars.append(secrets.choice(string.ascii_uppercase))
        if cls.REQUIRE_LOWERCASE:
            password_chars.append(secrets.choice(string.ascii_lowercase))
        if cls.REQUIRE_DIGIT:
            password_chars.append(secrets.choice(string.digits))
        if cls.REQUIRE_SPECIAL:
            password_chars.append(secrets.choice(cls.SPECIAL_CHARS))
        
        # Fill remaining length with random characters from all categories
        all_chars = string.ascii_letters + string.digits + cls.SPECIAL_CHARS
        remaining_length = length - len(password_chars)
        password_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))
        
        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)

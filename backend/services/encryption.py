"""
Password Encryption Service
Uses Fernet (symmetric encryption) for encrypting network passwords
"""
import os
from cryptography.fernet import Fernet
from typing import Optional


class PasswordEncryptionService:
    """
    Service for encrypting/decrypting network passwords
    Uses Fernet (AES-128 in CBC mode with HMAC for authentication)
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize with encryption key from environment or parameter
        
        Args:
            encryption_key: Base64-encoded Fernet key. If None, reads from ENCRYPTION_KEY env var
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")
            
        if not encryption_key:
            # Generate a new key for development (should be set in production)
            print("WARNING: No ENCRYPTION_KEY found. Generating a new key for this session.")
            print("For production, set ENCRYPTION_KEY environment variable.")
            encryption_key = Fernet.generate_key().decode()
            print(f"Generated key: {encryption_key}")
        
        # Convert string key to bytes if needed
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
            
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext password
        
        Args:
            plaintext: Password in plain text
            
        Returns:
            Base64-encoded encrypted password
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty password")
            
        # Convert to bytes, encrypt, and return as string
        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext password
        
        Args:
            ciphertext: Base64-encoded encrypted password
            
        Returns:
            Decrypted password in plain text
        """
        if not ciphertext:
            raise ValueError("Cannot decrypt empty ciphertext")
            
        # Convert to bytes, decrypt, and return as string
        decrypted_bytes = self.cipher.decrypt(ciphertext.encode())
        return decrypted_bytes.decode()


# Singleton instance
_encryption_service: Optional[PasswordEncryptionService] = None


def get_encryption_service() -> PasswordEncryptionService:
    """
    Get or create the encryption service singleton
    
    Returns:
        PasswordEncryptionService instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = PasswordEncryptionService()
    return _encryption_service

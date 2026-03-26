"""
Encryption Service
Servicio para encriptar/desencriptar datos sensibles en la base de datos
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Servicio para encriptar datos sensibles
    Usa Fernet (AES-128 en modo CBC con HMAC para autenticación)
    """
    
    _cipher = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Inicializar servicio de encriptación con clave del entorno"""
        if cls._initialized:
            return
        
        # Obtener clave del entorno
        encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if not encryption_key:
            # En desarrollo, generar clave temporal
            if os.getenv("ENVIRONMENT", "development") == "development":
                logger.warning("⚠️ ENCRYPTION_KEY no configurada, generando clave temporal")
                logger.warning("⚠️ Esta clave NO debe usarse en producción")
                encryption_key = Fernet.generate_key().decode()
                logger.info(f"🔑 Clave temporal generada: {encryption_key}")
            else:
                raise ValueError(
                    "ENCRYPTION_KEY must be set in production environment. "
                    "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
                )
        
        # Convertir a bytes si es string
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        # Crear cipher
        try:
            cls._cipher = Fernet(encryption_key)
            cls._initialized = True
            logger.info("✅ Servicio de encriptación inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando encriptación: {e}")
            raise
    
    @classmethod
    def encrypt(cls, data: str) -> str:
        """
        Encriptar datos
        
        Args:
            data: String a encriptar
            
        Returns:
            String encriptado en base64
            
        Example:
            >>> encrypted = EncryptionService.encrypt("mi_password_secreto")
            >>> encrypted
            'gAAAAABh...'
        """
        if not cls._initialized:
            cls.initialize()
        
        if not data:
            return data
        
        try:
            # Encriptar
            encrypted_bytes = cls._cipher.encrypt(data.encode('utf-8'))
            
            # Convertir a base64 para almacenar en BD
            encrypted_str = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            
            return encrypted_str
        except Exception as e:
            logger.error(f"❌ Error encriptando datos: {e}")
            raise
    
    @classmethod
    def decrypt(cls, encrypted_data: str) -> str:
        """
        Desencriptar datos
        
        Args:
            encrypted_data: String encriptado en base64
            
        Returns:
            String desencriptado
            
        Example:
            >>> decrypted = EncryptionService.decrypt('gAAAAABh...')
            >>> decrypted
            'mi_password_secreto'
        """
        if not cls._initialized:
            cls.initialize()
        
        if not encrypted_data:
            return encrypted_data
        
        try:
            # Decodificar de base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Desencriptar
            decrypted_bytes = cls._cipher.decrypt(encrypted_bytes)
            
            # Convertir a string
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            return decrypted_str
        except Exception as e:
            logger.error(f"❌ Error desencriptando datos: {e}")
            raise
    
    @classmethod
    def encrypt_dict(cls, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encriptar campos específicos de un diccionario
        
        Args:
            data: Diccionario con datos
            fields_to_encrypt: Lista de campos a encriptar
            
        Returns:
            Diccionario con campos encriptados
            
        Example:
            >>> data = {"username": "admin", "password": "secret"}
            >>> encrypted = EncryptionService.encrypt_dict(data, ["password"])
            >>> encrypted
            {"username": "admin", "password": "gAAAAABh..."}
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = cls.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    @classmethod
    def decrypt_dict(cls, data: dict, fields_to_decrypt: list) -> dict:
        """
        Desencriptar campos específicos de un diccionario
        
        Args:
            data: Diccionario con datos encriptados
            fields_to_decrypt: Lista de campos a desencriptar
            
        Returns:
            Diccionario con campos desencriptados
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = cls.decrypt(decrypted_data[field])
        
        return decrypted_data
    
    @classmethod
    def generate_key(cls) -> str:
        """
        Generar nueva clave de encriptación
        
        Returns:
            Clave en formato string (base64)
            
        Example:
            >>> key = EncryptionService.generate_key()
            >>> print(f"ENCRYPTION_KEY={key}")
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')
    
    @classmethod
    def derive_key_from_password(cls, password: str, salt: bytes = None) -> tuple:
        """
        Derivar clave de encriptación desde una contraseña
        Útil para encriptación basada en contraseña del usuario
        
        Args:
            password: Contraseña del usuario
            salt: Salt para KDF (se genera si no se proporciona)
            
        Returns:
            Tupla (clave_derivada, salt_usado)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return key.decode('utf-8'), base64.urlsafe_b64encode(salt).decode('utf-8')
    
    @classmethod
    def is_encrypted(cls, data: str) -> bool:
        """
        Verificar si un string parece estar encriptado
        
        Args:
            data: String a verificar
            
        Returns:
            True si parece encriptado, False si no
        """
        if not data:
            return False
        
        try:
            # Intentar decodificar de base64
            decoded = base64.urlsafe_b64decode(data.encode('utf-8'))
            
            # Los datos encriptados con Fernet tienen un formato específico
            # Comienzan con un timestamp (8 bytes) + version (1 byte)
            return len(decoded) > 9
        except Exception:
            return False


# Inicializar al importar el módulo
try:
    EncryptionService.initialize()
except Exception as e:
    logger.warning(f"⚠️ No se pudo inicializar EncryptionService: {e}")

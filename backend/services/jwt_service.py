"""
JWT Service
Servicio para generación y validación de tokens JWT
"""
import jwt
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


class InvalidTokenError(Exception):
    """Raised when JWT token is invalid"""
    pass


class ExpiredTokenError(Exception):
    """Raised when JWT token is expired"""
    pass


class JWTService:
    """Service for JWT operations"""
    
    # Token expiration times
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Algorithm
    ALGORITHM = "HS256"
    
    @classmethod
    def _validate_secret_key_entropy(cls, secret_key: str) -> bool:
        """
        Validate SECRET_KEY has minimum entropy
        
        Verifies that the key contains at least 3 of 4 character categories:
        - Uppercase letters (A-Z)
        - Lowercase letters (a-z)
        - Digits (0-9)
        - Special characters (punctuation)
        
        Args:
            secret_key: The SECRET_KEY to validate
            
        Returns:
            True if entropy is sufficient, False otherwise
            
        Example:
            >>> JWTService._validate_secret_key_entropy("Abc123!@#xyz")
            True
            >>> JWTService._validate_secret_key_entropy("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            False
        """
        import string
        
        charset_used = set(secret_key)
        has_upper = any(c in string.ascii_uppercase for c in charset_used)
        has_lower = any(c in string.ascii_lowercase for c in charset_used)
        has_digit = any(c in string.digits for c in charset_used)
        has_special = any(c in string.punctuation for c in charset_used)
        
        categories = sum([has_upper, has_lower, has_digit, has_special])
        return categories >= 3
    
    @classmethod
    def _get_secret_key(cls) -> str:
        """
        Get SECRET_KEY from environment variable
        
        Returns:
            SECRET_KEY string
            
        Raises:
            ValueError: If SECRET_KEY is not set, is too short, or has insufficient entropy
        """
        secret_key = os.getenv("SECRET_KEY")
        
        print(f"[JWT] SECRET_KEY configurada: {bool(secret_key)}, longitud: {len(secret_key) if secret_key else 0}")
        
        if not secret_key:
            raise ValueError("SECRET_KEY environment variable is not set")
        
        if len(secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        # Validate entropy
        if not cls._validate_secret_key_entropy(secret_key):
            raise ValueError(
                "SECRET_KEY has insufficient entropy. "
                "Must contain at least 3 of: uppercase, lowercase, digits, special characters. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        
        return secret_key
    
    @classmethod
    def create_access_token(cls, user: Any) -> str:
        """
        Create access token (30 min expiration)
        
        Payload includes:
            - user_id: int
            - username: str
            - rol: str
            - empresa_id: Optional[int]
            - exp: datetime (30 minutes from now)
            - iat: datetime (issued at)
        
        Args:
            user: AdminUser object with id, username, rol, empresa_id attributes
            
        Returns:
            JWT access token string
            
        Example:
            >>> token = JWTService.create_access_token(user)
            >>> isinstance(token, str)
            True
            >>> len(token) > 0
            True
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "user_id": user.id,
            "username": user.username,
            "rol": user.rol,
            "empresa_id": user.empresa_id,
            "exp": expires_at,
            "iat": now,
            "type": "access"
        }
        
        secret_key = cls._get_secret_key()
        token = jwt.encode(payload, secret_key, algorithm=cls.ALGORITHM)
        
        return token
    
    @classmethod
    def create_refresh_token(cls, user: Any) -> str:
        """
        Create refresh token (7 days expiration)
        
        Payload includes:
            - user_id: int
            - type: "refresh"
            - exp: datetime (7 days from now)
            - iat: datetime (issued at)
        
        Args:
            user: AdminUser object with id attribute
            
        Returns:
            JWT refresh token string
            
        Example:
            >>> token = JWTService.create_refresh_token(user)
            >>> isinstance(token, str)
            True
            >>> len(token) > 0
            True
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "user_id": user.id,
            "type": "refresh",
            "exp": expires_at,
            "iat": now
        }
        
        secret_key = cls._get_secret_key()
        token = jwt.encode(payload, secret_key, algorithm=cls.ALGORITHM)
        
        return token
    
    @classmethod
    def decode_token(cls, token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload dictionary
            
        Raises:
            InvalidTokenError: If signature is invalid
            ExpiredTokenError: If token is expired
            
        Example:
            >>> token = JWTService.create_access_token(user)
            >>> payload = JWTService.decode_token(token)
            >>> "user_id" in payload
            True
            >>> "exp" in payload
            True
        """
        try:
            # Mask token for security - show only first 4 and last 4 characters
            token_preview = f"{token[:4]}...{token[-4:]}" if token and len(token) > 8 else "NONE"
            print(f"[JWT] Decodificando token: {token_preview}")
            secret_key = cls._get_secret_key()
            payload = jwt.decode(token, secret_key, algorithms=[cls.ALGORITHM])
            print(f"[JWT] Token decodificado exitosamente, user_id: {payload.get('user_id')}")
            return payload
        except jwt.ExpiredSignatureError:
            print("[JWT] ERROR: Token expirado")
            raise ExpiredTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            print(f"[JWT] ERROR: Token inválido: {str(e)}")
            raise InvalidTokenError("Invalid token")
        except Exception as e:
            print(f"[JWT] ERROR: Fallo en validación: {type(e).__name__}: {str(e)}")
            raise InvalidTokenError(f"Token validation failed: {str(e)}")
    
    @classmethod
    def verify_signature(cls, token: str) -> bool:
        """
        Verify JWT signature without checking expiration
        
        Args:
            token: JWT token string
            
        Returns:
            True if signature is valid, False otherwise
            
        Example:
            >>> token = JWTService.create_access_token(user)
            >>> JWTService.verify_signature(token)
            True
            >>> JWTService.verify_signature("invalid.token.here")
            False
        """
        try:
            secret_key = cls._get_secret_key()
            # Decode without verifying expiration
            jwt.decode(
                token, 
                secret_key, 
                algorithms=[cls.ALGORITHM],
                options={"verify_exp": False}
            )
            return True
        except Exception:
            return False
    
    @classmethod
    def get_token_expiration(cls, token: str) -> Optional[datetime]:
        """
        Get expiration datetime from token
        
        Args:
            token: JWT token string
            
        Returns:
            Expiration datetime or None if token is invalid
            
        Example:
            >>> token = JWTService.create_access_token(user)
            >>> exp = JWTService.get_token_expiration(token)
            >>> isinstance(exp, datetime)
            True
        """
        try:
            payload = cls.decode_token(token)
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            return None
        except Exception:
            return None
    
    @classmethod
    def should_rotate_token(cls, token: str, rotation_threshold_minutes: int = 5) -> bool:
        """
        Verificar si un token debe ser rotado
        
        Un token debe rotarse si está cerca de expirar (dentro del threshold)
        
        Args:
            token: JWT token string
            rotation_threshold_minutes: Minutos antes de expiración para rotar (default: 5)
            
        Returns:
            True si debe rotarse, False si no
            
        Example:
            >>> token = JWTService.create_access_token(user)
            >>> JWTService.should_rotate_token(token, rotation_threshold_minutes=25)
            True  # Token expira en 30 min, threshold es 25 min
        """
        try:
            expiration = cls.get_token_expiration(token)
            if not expiration:
                return False
            
            # Calcular tiempo restante
            now = datetime.now(timezone.utc)
            time_remaining = expiration - now
            
            # Si queda menos tiempo que el threshold, rotar
            threshold = timedelta(minutes=rotation_threshold_minutes)
            return time_remaining <= threshold
        except Exception:
            return False
    
    @classmethod
    def rotate_access_token(cls, current_token: str, user: Any) -> str:
        """
        Rotar access token
        
        Genera un nuevo access token para el usuario si el token actual está cerca de expirar
        
        Args:
            current_token: Token actual
            user: AdminUser object
            
        Returns:
            Nuevo JWT access token
            
        Raises:
            InvalidTokenError: Si el token actual es inválido
            
        Example:
            >>> old_token = JWTService.create_access_token(user)
            >>> new_token = JWTService.rotate_access_token(old_token, user)
            >>> old_token != new_token
            True
        """
        # Validar token actual
        try:
            payload = cls.decode_token(current_token)
            
            # Verificar que es un access token
            if payload.get("type") != "access":
                raise InvalidTokenError("Token is not an access token")
            
            # Verificar que el user_id coincide
            if payload.get("user_id") != user.id:
                raise InvalidTokenError("Token does not match user")
            
        except ExpiredTokenError:
            # Si el token expiró, igual permitir rotación
            # (útil para rotación automática en el interceptor)
            pass
        
        # Generar nuevo token
        new_token = cls.create_access_token(user)
        
        return new_token

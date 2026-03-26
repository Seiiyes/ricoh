"""
CSRF Protection Middleware
Middleware para proteger contra ataques CSRF (Cross-Site Request Forgery)
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import secrets
import hashlib
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para protección CSRF
    
    Genera tokens CSRF únicos por sesión y los valida en requests mutables (POST, PUT, DELETE, PATCH)
    """
    
    # Métodos que requieren validación CSRF
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
    
    # Rutas excluidas de validación CSRF (ej: login, refresh)
    EXCLUDED_PATHS = {
        "/auth/login",
        "/auth/refresh",
        "/docs",
        "/openapi.json",
        "/redoc"
    }
    
    # Tiempo de expiración del token CSRF (2 horas)
    TOKEN_EXPIRATION_HOURS = 2
    
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        # Cache de tokens en memoria (en producción usar Redis)
        self._token_cache = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate CSRF token if needed"""
        
        # 1. Si es método seguro (GET, HEAD, OPTIONS), no validar
        if request.method not in self.PROTECTED_METHODS:
            response = await call_next(request)
            # Agregar token CSRF al response para que el cliente lo use
            csrf_token = self._generate_csrf_token(request)
            response.headers["X-CSRF-Token"] = csrf_token
            return response
        
        # 2. Si es ruta excluida, no validar
        if request.url.path in self.EXCLUDED_PATHS:
            response = await call_next(request)
            return response
        
        # 3. Validar token CSRF
        try:
            self._validate_csrf_token(request)
        except HTTPException as e:
            logger.warning(f"⚠️ CSRF validation failed: {e.detail}")
            raise
        
        # 4. Procesar request
        response = await call_next(request)
        
        # 5. Generar nuevo token para el siguiente request
        new_csrf_token = self._generate_csrf_token(request)
        response.headers["X-CSRF-Token"] = new_csrf_token
        
        return response
    
    def _generate_csrf_token(self, request: Request) -> str:
        """
        Generar token CSRF único
        
        El token se basa en:
        - Session ID (del JWT o cookie)
        - User Agent
        - Timestamp
        - Secret key
        """
        # Obtener session ID del JWT
        auth_header = request.headers.get("Authorization", "")
        session_id = auth_header.replace("Bearer ", "")[:32] if auth_header else "anonymous"
        
        # Obtener User Agent
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Timestamp actual
        timestamp = datetime.utcnow().isoformat()
        
        # Generar token
        token_data = f"{session_id}:{user_agent}:{timestamp}:{self.secret_key}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Guardar en cache con expiración
        expiration = datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRATION_HOURS)
        self._token_cache[token_hash] = {
            "session_id": session_id,
            "user_agent": user_agent,
            "expires_at": expiration
        }
        
        # Limpiar tokens expirados (simple cleanup)
        self._cleanup_expired_tokens()
        
        return token_hash
    
    def _validate_csrf_token(self, request: Request):
        """
        Validar token CSRF del request
        
        El token puede venir en:
        1. Header X-CSRF-Token
        2. Form field csrf_token
        3. Query parameter csrf_token
        """
        # Obtener token del request
        csrf_token = (
            request.headers.get("X-CSRF-Token") or
            request.query_params.get("csrf_token")
        )
        
        # Si no hay token, rechazar
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "CSRF_TOKEN_MISSING",
                    "message": "CSRF token is required for this operation"
                }
            )
        
        # Verificar que el token existe en cache
        if csrf_token not in self._token_cache:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "CSRF_TOKEN_INVALID",
                    "message": "Invalid CSRF token"
                }
            )
        
        # Verificar que no ha expirado
        token_data = self._token_cache[csrf_token]
        if datetime.utcnow() > token_data["expires_at"]:
            # Remover token expirado
            del self._token_cache[csrf_token]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "CSRF_TOKEN_EXPIRED",
                    "message": "CSRF token has expired"
                }
            )
        
        # Verificar que el User Agent coincide
        current_user_agent = request.headers.get("User-Agent", "unknown")
        if current_user_agent != token_data["user_agent"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "CSRF_TOKEN_MISMATCH",
                    "message": "CSRF token does not match current session"
                }
            )
        
        # Token válido - removerlo para evitar reutilización
        del self._token_cache[csrf_token]
        
        logger.info(f"✅ CSRF token validated for {request.url.path}")
    
    def _cleanup_expired_tokens(self):
        """Limpiar tokens expirados del cache"""
        now = datetime.utcnow()
        expired_tokens = [
            token for token, data in self._token_cache.items()
            if now > data["expires_at"]
        ]
        
        for token in expired_tokens:
            del self._token_cache[token]
        
        if expired_tokens:
            logger.info(f"🧹 Cleaned up {len(expired_tokens)} expired CSRF tokens")

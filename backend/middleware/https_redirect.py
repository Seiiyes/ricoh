"""
HTTPS Redirect Middleware
Middleware para forzar HTTPS en producción
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
import os
import logging

logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware para redirigir HTTP a HTTPS en producción
    
    Solo activo cuando ENVIRONMENT=production y FORCE_HTTPS=true
    """
    
    def __init__(self, app, force_https: bool = None):
        super().__init__(app)
        
        # Determinar si forzar HTTPS
        if force_https is None:
            # Solo en producción y si está explícitamente habilitado
            environment = os.getenv("ENVIRONMENT", "development")
            force_https_env = os.getenv("FORCE_HTTPS", "false").lower() == "true"
            self.force_https = environment == "production" and force_https_env
        else:
            self.force_https = force_https
        
        if self.force_https:
            logger.info("🔒 HTTPS redirect enabled - all HTTP requests will be redirected to HTTPS")
        else:
            logger.info("🔓 HTTPS redirect disabled (development mode)")
    
    async def dispatch(self, request: Request, call_next):
        """Redirect HTTP to HTTPS if enabled"""
        
        # Si no está habilitado, continuar normalmente
        if not self.force_https:
            return await call_next(request)
        
        # Verificar si el request es HTTP
        if request.url.scheme == "http":
            # Construir URL HTTPS
            https_url = request.url.replace(scheme="https")
            
            logger.info(f"🔀 Redirecting HTTP to HTTPS: {request.url} -> {https_url}")
            
            # Redirigir con código 301 (Moved Permanently)
            return RedirectResponse(
                url=str(https_url),
                status_code=301
            )
        
        # Si ya es HTTPS, continuar normalmente
        return await call_next(request)

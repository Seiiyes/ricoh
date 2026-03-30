"""
Authentication Middleware
Middleware para autenticación y autorización con FastAPI
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Callable
from functools import wraps
import logging

from db.database import get_db
from db.models_auth import AdminUser
from services.auth_service import AuthService, AccountDisabledError
from services.jwt_service import InvalidTokenError, ExpiredTokenError


# Configure logging
logger = logging.getLogger(__name__)

# Security scheme for Swagger UI
security = HTTPBearer()


# Error codes
AUTH_TOKEN_MISSING = "AUTH_TOKEN_MISSING"
AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
AUTH_SESSION_INVALID = "AUTH_SESSION_INVALID"
AUTHZ_INSUFFICIENT_PERMISSIONS = "AUTHZ_INSUFFICIENT_PERMISSIONS"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Dependency to get current authenticated user
    
    Extracts token from Authorization header, validates it, and returns user.
    
    Args:
        credentials: HTTP Bearer credentials from header
        db: Database session
        
    Returns:
        AdminUser object
        
    Raises:
        HTTPException: If authentication fails
        
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: AdminUser = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    print("[AUTH] ===== INICIO DE AUTENTICACIÓN =====")
    
    # Extract token
    token = credentials.credentials
    
    # Mask token for security - show only first 4 and last 4 characters
    token_preview = f"{token[:4]}...{token[-4:]}" if token and len(token) > 8 else "NONE"
    
    # Use print for debugging (logger might not be visible)
    print(f"[AUTH] Autenticación iniciada - Token: {token_preview}")
    logger.info(f"🔐 Autenticación iniciada - Token: {token_preview}")
    
    if not token:
        print("[AUTH] ERROR: Token faltante")
        logger.warning("❌ Token faltante")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": AUTH_TOKEN_MISSING,
                "message": "Authorization token is missing"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Validate token
    try:
        print("[AUTH] Validando token...")
        logger.info("🔍 Validando token...")
        user = AuthService.validate_token(db, token)
        print(f"[AUTH] Usuario validado: {user.username} (rol: {user.rol}, activo: {user.is_active})")
        logger.info(f"✅ Usuario validado: {user.username} (rol: {user.rol}, activo: {user.is_active})")
        return user
    except ExpiredTokenError:
        print("[AUTH] ERROR: Token expirado")
        logger.warning("⏰ Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": AUTH_TOKEN_EXPIRED,
                "message": "Token has expired"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    except InvalidTokenError as e:
        print(f"[AUTH] ERROR: Token inválido: {str(e)}")
        logger.warning(f"❌ Token inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": AUTH_TOKEN_INVALID,
                "message": str(e)
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    except AccountDisabledError:
        print("[AUTH] ERROR: Cuenta deshabilitada")
        logger.warning("🚫 Cuenta deshabilitada")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "AUTH_ACCOUNT_DISABLED",
                "message": "Account is disabled"
            }
        )
    except Exception as e:
        print(f"[AUTH] ERROR INESPERADO: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[AUTH] TRACEBACK: {traceback.format_exc()}")
        logger.error(f"💥 Error inesperado en validación: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": AUTH_TOKEN_INVALID,
                "message": "Token validation failed"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_role(allowed_roles: List[str]) -> Callable:
    """
    Decorator to require specific roles for endpoint access
    
    Args:
        allowed_roles: List of allowed roles (e.g., ["superadmin", "admin"])
        
    Returns:
        Decorator function
        
    Usage:
        @app.get("/admin-only")
        @require_role(["superadmin"])
        async def admin_only_route(current_user: AdminUser = Depends(get_current_user)):
            return {"message": "Admin access granted"}
    
    Note: This decorator should be used AFTER the route decorator and
    the endpoint should have current_user: AdminUser = Depends(get_current_user) parameter
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs (injected by Depends)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": AUTH_TOKEN_MISSING,
                        "message": "Authentication required"
                    }
                )
            
            # Check if user has required role
            if current_user.rol not in allowed_roles:
                # Log access denial in audit log
                from services.audit_service import AuditService
                from db.database import SessionLocal
                
                db = SessionLocal()
                try:
                    AuditService.log_action(
                        db=db,
                        user=current_user,
                        accion="acceso_denegado",
                        modulo="authorization",
                        resultado=AuditService.RESULTADO_DENEGADO,
                        detalles={
                            "required_roles": allowed_roles,
                            "user_role": current_user.rol,
                            "endpoint": func.__name__
                        }
                    )
                finally:
                    db.close()
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": AUTHZ_INSUFFICIENT_PERMISSIONS,
                        "message": f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
                    }
                )
            
            # User has required role, proceed
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def get_current_superadmin(
    current_user: AdminUser = Depends(get_current_user)
) -> AdminUser:
    """
    Dependency to get current user and verify they are superadmin
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        AdminUser object (superadmin)
        
    Raises:
        HTTPException: If user is not superadmin
        
    Usage:
        @app.get("/superadmin-only")
        async def superadmin_route(current_user: AdminUser = Depends(get_current_superadmin)):
            return {"message": "Superadmin access granted"}
    """
    if not current_user.is_superadmin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": AUTHZ_INSUFFICIENT_PERMISSIONS,
                "message": "Superadmin access required"
            }
        )
    
    return current_user


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for X-Forwarded-For header (proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take first IP in the list
        return forwarded_for.split(",")[0].strip()
    
    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def get_user_agent(request: Request) -> str:
    """
    Get user agent from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        User agent string
    """
    return request.headers.get("User-Agent", "unknown")

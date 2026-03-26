"""
Authentication Endpoints
Endpoints de autenticación para login, logout, refresh token, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from db.database import get_db
from db.models_auth import AdminUser
from api.auth_schemas import (
    LoginRequest, LoginResponse, RefreshRequest, RefreshResponse,
    ChangePasswordRequest, SuccessResponse, ErrorResponse, AdminUserResponse,
    RotateTokenResponse
)
from services.auth_service import (
    AuthService, InvalidCredentialsError, AccountLockedError, AccountDisabledError
)
from services.jwt_service import InvalidTokenError, ExpiredTokenError, JWTService
from services.rate_limiter_service import RateLimiterService
from middleware.auth_middleware import get_current_user, get_client_ip, get_user_agent


router = APIRouter(prefix="/auth", tags=["Authentication"])


# Rate limiting settings
LOGIN_RATE_LIMIT = 5  # requests
LOGIN_RATE_WINDOW = 60  # seconds (1 minute)
REFRESH_RATE_LIMIT = 10  # requests
REFRESH_RATE_WINDOW = 60  # seconds (1 minute)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful", "model": LoginResponse},
        401: {"description": "Invalid credentials", "model": ErrorResponse},
        403: {"description": "Account locked or disabled", "model": ErrorResponse},
        429: {"description": "Too many requests", "model": ErrorResponse}
    },
    summary="Login",
    description="Authenticate user with username and password. Returns access token and refresh token."
)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and create session
    
    - **username**: Username (required)
    - **password**: Password (required)
    
    Returns:
    - **access_token**: JWT access token (30 min expiration)
    - **refresh_token**: JWT refresh token (7 days expiration)
    - **token_type**: Token type (bearer)
    - **expires_in**: Access token expiration in seconds
    - **user**: User information (without password_hash)
    """
    # Get client info
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Check rate limit
    rate_limit_key = f"login:{client_ip}"
    rate_limit_result = RateLimiterService.check_rate_limit(
        rate_limit_key,
        LOGIN_RATE_LIMIT,
        LOGIN_RATE_WINDOW
    )
    
    if not rate_limit_result.allowed:
        reset_seconds = int((rate_limit_result.reset_at.timestamp() - 
                           rate_limit_result.reset_at.now(rate_limit_result.reset_at.tzinfo).timestamp()))
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Too many login attempts. Try again in {reset_seconds} seconds.",
                "reset_at": rate_limit_result.reset_at.isoformat()
            },
            headers={
                "X-RateLimit-Limit": str(LOGIN_RATE_LIMIT),
                "X-RateLimit-Remaining": str(rate_limit_result.remaining),
                "X-RateLimit-Reset": str(int(rate_limit_result.reset_at.timestamp())),
                "Retry-After": str(reset_seconds)
            }
        )
    
    # Attempt login
    try:
        login_response = AuthService.login(
            db=db,
            username=login_data.username,
            password=login_data.password,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Convert to response model
        return LoginResponse(
            access_token=login_response.access_token,
            refresh_token=login_response.refresh_token,
            token_type=login_response.token_type,
            expires_in=login_response.expires_in,
            user=AdminUserResponse.model_validate(login_response.user)
        )
    
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTH_INVALID_CREDENTIALS",
                "message": "Invalid credentials"
            }
        )
    
    except AccountLockedError as e:
        locked_minutes = int((e.locked_until.timestamp() - 
                            e.locked_until.now(e.locked_until.tzinfo).timestamp()) / 60)
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "AUTH_ACCOUNT_LOCKED",
                "message": f"Account is locked. Try again in {locked_minutes} minutes.",
                "locked_until": e.locked_until.isoformat()
            }
        )
    
    except AccountDisabledError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "AUTH_ACCOUNT_DISABLED",
                "message": "Account is disabled"
            }
        )


@router.post(
    "/logout",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout successful", "model": SuccessResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    },
    summary="Logout",
    description="Invalidate current session and logout user."
)
async def logout(
    request: Request,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user and invalidate session
    
    Requires valid access token in Authorization header.
    """
    # Get token from header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    
    # Get client info
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Logout
    AuthService.logout(
        db=db,
        token=token,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return SuccessResponse(
        success=True,
        message="Sesión cerrada exitosamente"
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Token refreshed successfully", "model": RefreshResponse},
        401: {"description": "Invalid or expired refresh token", "model": ErrorResponse},
        429: {"description": "Too many requests", "model": ErrorResponse}
    },
    summary="Refresh Token",
    description="Generate new access token using refresh token."
)
async def refresh_token(
    request: Request,
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    
    - **refresh_token**: Refresh token (required)
    
    Returns:
    - **access_token**: New JWT access token (30 min expiration)
    - **token_type**: Token type (bearer)
    - **expires_in**: Access token expiration in seconds
    """
    # Check rate limit (by refresh token hash to prevent abuse)
    import hashlib
    token_hash = hashlib.sha256(refresh_data.refresh_token.encode()).hexdigest()[:16]
    rate_limit_key = f"refresh:{token_hash}"
    
    rate_limit_result = RateLimiterService.check_rate_limit(
        rate_limit_key,
        REFRESH_RATE_LIMIT,
        REFRESH_RATE_WINDOW
    )
    
    if not rate_limit_result.allowed:
        reset_seconds = int((rate_limit_result.reset_at.timestamp() - 
                           rate_limit_result.reset_at.now(rate_limit_result.reset_at.tzinfo).timestamp()))
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Too many refresh attempts. Try again in {reset_seconds} seconds.",
                "reset_at": rate_limit_result.reset_at.isoformat()
            },
            headers={
                "X-RateLimit-Limit": str(REFRESH_RATE_LIMIT),
                "X-RateLimit-Remaining": str(rate_limit_result.remaining),
                "X-RateLimit-Reset": str(int(rate_limit_result.reset_at.timestamp())),
                "Retry-After": str(reset_seconds)
            }
        )
    
    # Attempt refresh
    try:
        refresh_response = AuthService.refresh_token(
            db=db,
            refresh_token=refresh_data.refresh_token
        )
        
        return RefreshResponse(
            access_token=refresh_response.access_token,
            token_type=refresh_response.token_type,
            expires_in=refresh_response.expires_in
        )
    
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTH_TOKEN_INVALID",
                "message": "Invalid refresh token"
            }
        )
    
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTH_TOKEN_EXPIRED",
                "message": "Refresh token has expired"
            }
        )
    
    except AccountDisabledError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "AUTH_ACCOUNT_DISABLED",
                "message": "Account is disabled"
            }
        )


@router.get(
    "/me",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User information", "model": AdminUserResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    },
    summary="Get Current User",
    description="Get information about the currently authenticated user."
)
async def get_me(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get current user information
    
    Requires valid access token in Authorization header.
    
    Returns user information without password_hash.
    """
    return AdminUserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Password changed successfully", "model": SuccessResponse},
        400: {"description": "Invalid password", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    },
    summary="Change Password",
    description="Change password for the currently authenticated user."
)
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    - **current_password**: Current password (required)
    - **new_password**: New password (required, must meet strength requirements)
    
    Requires valid access token in Authorization header.
    """
    # Get client info
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Attempt password change
    try:
        AuthService.change_password(
            db=db,
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        return SuccessResponse(
            success=True,
            message="Contraseña actualizada exitosamente"
        )
    
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "AUTH_INVALID_PASSWORD",
                "message": "Current password is incorrect"
            }
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "AUTH_WEAK_PASSWORD",
                "message": str(e)
            }
        )


@router.post(
    "/rotate-token",
    response_model=RotateTokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Token rotated successfully", "model": RotateTokenResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    },
    summary="Rotate Access Token",
    description="Generate new access token if current token is close to expiration."
)
async def rotate_token(
    request: Request,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rotar access token
    
    Genera un nuevo access token si el actual está cerca de expirar (dentro de 5 minutos).
    Útil para mantener sesiones activas sin interrupciones.
    
    Requires valid access token in Authorization header.
    
    Returns:
    - **access_token**: New JWT access token (30 min expiration)
    - **token_type**: Token type (bearer)
    - **expires_in**: Access token expiration in seconds
    - **rotated**: True if token was rotated, False if not needed yet
    """
    # Get current token from header
    auth_header = request.headers.get("Authorization", "")
    current_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    
    if not current_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTH_TOKEN_MISSING",
                "message": "Access token is required"
            }
        )
    
    # Verificar si debe rotarse
    should_rotate = JWTService.should_rotate_token(current_token, rotation_threshold_minutes=5)
    
    if should_rotate:
        # Generar nuevo token
        new_token = JWTService.rotate_access_token(current_token, current_user)
        
        return RotateTokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            rotated=True
        )
    else:
        # No es necesario rotar aún, devolver el mismo token
        return RotateTokenResponse(
            access_token=current_token,
            token_type="bearer",
            expires_in=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            rotated=False
        )

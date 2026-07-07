"""
Authentication Service
Servicio para autenticación, gestión de sesiones y tokens
"""
from sqlalchemy.orm import Session
from typing import Optional, NamedTuple
from datetime import datetime, timedelta, timezone

from db.models_auth import AdminUser, AdminSession
from services.password_service import PasswordService
from services.jwt_service import JWTService, InvalidTokenError, ExpiredTokenError
from services.audit_service import AuditService


class LoginResponse(NamedTuple):
    """Response from login operation"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: AdminUser


class RefreshResponse(NamedTuple):
    """Response from refresh token operation"""
    access_token: str
    token_type: str
    expires_in: int


class InvalidCredentialsError(Exception):
    """Raised when credentials are invalid"""
    pass


class AccountLockedError(Exception):
    """Raised when account is locked"""
    def __init__(self, locked_until: datetime):
        self.locked_until = locked_until
        super().__init__(f"Account locked until {locked_until}")


class AccountDisabledError(Exception):
    """Raised when account is disabled"""
    pass


class AuthService:
    """Service for authentication operations"""
    
    # Account lockout settings
    MAX_FAILED_ATTEMPTS = 999  # Incrementado: no bloquear cuentas en la práctica
    LOCKOUT_DURATION_MINUTES = 1   # Si se llega al límite, bloqueo de solo 1 minuto
    
    @classmethod
    def login(
        cls,
        db: Session,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginResponse:
        """
        Authenticate user and create session
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            LoginResponse with tokens and user info
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            AccountLockedError: If account is locked
            AccountDisabledError: If account is disabled
            
        Example:
            >>> response = AuthService.login(
            ...     db=db,
            ...     username="admin",
            ...     password="SecurePass123!",
            ...     ip_address="192.168.1.100"
            ... )
            >>> response.user.username
            'admin'
            >>> len(response.access_token) > 0
            True
        """
        # Find user by username
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        
        # If user doesn't exist, return generic error (don't reveal if username exists)
        if not user:
            # Log failed attempt
            AuditService.log_action(
                db=db,
                user=None,
                accion="login",
                modulo="auth",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={"username": username, "error": "user_not_found"},
                ip_address=ip_address,
                user_agent=user_agent
            )
            AuditService.log_security_event(
                usuario=username,
                accion="login",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={"error": "user_not_found"},
                ip_address=ip_address
            )
            raise InvalidCredentialsError("Invalid credentials")
        
        # Check if account is disabled
        if not user.is_active:
            AuditService.log_action(
                db=db,
                user=user,
                accion="login",
                modulo="auth",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={"error": "account_disabled"},
                ip_address=ip_address,
                user_agent=user_agent
            )
            AuditService.log_security_event(
                usuario=user.username,
                accion="login",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={"error": "account_disabled"},
                ip_address=ip_address
            )
            raise AccountDisabledError("Account is disabled")
        
        # Check if account is locked
        if user.is_locked():
            AuditService.log_action(
                db=db,
                user=user,
                accion="login",
                modulo="auth",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={"error": "account_locked", "locked_until": user.locked_until.isoformat()},
                ip_address=ip_address,
                user_agent=user_agent
            )
            AuditService.log_security_event(
                usuario=user.username,
                accion="login",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={"error": "account_locked", "locked_until": user.locked_until.isoformat()},
                ip_address=ip_address
            )
            raise AccountLockedError(user.locked_until)
        
        # Verify password
        if not PasswordService.verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts reached
            if user.failed_login_attempts >= cls.MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=cls.LOCKOUT_DURATION_MINUTES
                )
                db.commit()
                
                AuditService.log_action(
                    db=db,
                    user=user,
                    accion="login",
                    modulo="auth",
                    resultado=AuditService.RESULTADO_ERROR,
                    detalles={
                        "error": "invalid_password",
                        "failed_attempts": user.failed_login_attempts,
                        "account_locked": True,
                        "locked_until": user.locked_until.isoformat()
                    },
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                AuditService.log_security_event(
                    usuario=user.username,
                    accion="login",
                    resultado=AuditService.RESULTADO_ERROR,
                    detalles={
                        "error": "invalid_password",
                        "failed_attempts": user.failed_login_attempts,
                        "account_locked": True
                    },
                    ip_address=ip_address
                )
                
                raise AccountLockedError(user.locked_until)
            
            db.commit()
            
            AuditService.log_action(
                db=db,
                user=user,
                accion="login",
                modulo="auth",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={
                    "error": "invalid_password",
                    "failed_attempts": user.failed_login_attempts
                },
                ip_address=ip_address,
                user_agent=user_agent
            )
            AuditService.log_security_event(
                usuario=user.username,
                accion="login",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={
                    "error": "invalid_password",
                    "failed_attempts": user.failed_login_attempts
                },
                ip_address=ip_address
            )
            
            raise InvalidCredentialsError("Invalid credentials")
        
        # Password is correct - reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        
        # Generate tokens
        access_token = JWTService.create_access_token(user)
        refresh_token = JWTService.create_refresh_token(user)
        
        # Calculate expiration times
        access_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(
            days=JWTService.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        # Create session
        session = AdminSession(
            admin_user_id=user.id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
            created_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc)
        )
        
        db.add(session)
        db.commit()
        db.refresh(user)
        
        # Log successful login
        AuditService.log_action(
            db=db,
            user=user,
            accion="login",
            modulo="auth",
            resultado=AuditService.RESULTADO_EXITO,
            detalles={"login_method": "password"},
            ip_address=ip_address,
            user_agent=user_agent
        )
        AuditService.log_security_event(
            usuario=user.username,
            accion="login",
            resultado=AuditService.RESULTADO_EXITO,
            detalles={"login_method": "password"},
            ip_address=ip_address
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user
        )
    
    @classmethod
    def logout(
        cls,
        db: Session,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Invalidate session
        
        Args:
            db: Database session
            token: Access token
            ip_address: Client IP
            user_agent: Client user agent
            
        Example:
            >>> AuthService.logout(db, access_token)
        """
        # Find and delete session
        session = db.query(AdminSession).filter(AdminSession.token == token).first()
        
        if session:
            user = db.query(AdminUser).filter(AdminUser.id == session.admin_user_id).first()
            
            # Delete session
            db.delete(session)
            db.commit()
            
            # Log logout
            if user:
                AuditService.log_action(
                    db=db,
                    user=user,
                    accion="logout",
                    modulo="auth",
                    resultado=AuditService.RESULTADO_EXITO,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                AuditService.log_security_event(
                    usuario=user.username,
                    accion="logout",
                    resultado=AuditService.RESULTADO_EXITO,
                    ip_address=ip_address
                )
    
    @classmethod
    def refresh_token(
        cls,
        db: Session,
        refresh_token: str
    ) -> RefreshResponse:
        """
        Generate new access token from refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            RefreshResponse with new access token
            
        Raises:
            InvalidTokenError: If refresh token is invalid
            ExpiredTokenError: If refresh token is expired
            AccountDisabledError: If account is disabled
            
        Example:
            >>> response = AuthService.refresh_token(db, refresh_token)
            >>> len(response.access_token) > 0
            True
        """
        # Find session by refresh token
        session = db.query(AdminSession).filter(
            AdminSession.refresh_token == refresh_token
        ).first()
        
        if not session:
            raise InvalidTokenError("Invalid refresh token")
        
        # Check if refresh token is expired
        if session.refresh_expires_at < datetime.now(timezone.utc):
            db.delete(session)
            db.commit()
            raise ExpiredTokenError("Refresh token has expired")
        
        # Get user
        user = db.query(AdminUser).filter(AdminUser.id == session.admin_user_id).first()
        
        if not user:
            db.delete(session)
            db.commit()
            raise InvalidTokenError("User not found")
        
        # Check if user is active
        if not user.is_active:
            db.delete(session)
            db.commit()
            raise AccountDisabledError("Account is disabled")
        
        # Generate new access token
        new_access_token = JWTService.create_access_token(user)
        new_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        # Update session
        session.token = new_access_token
        session.expires_at = new_expires_at
        session.last_activity = datetime.now(timezone.utc)
        
        db.commit()
        
        # Log token refresh in security logs
        AuditService.log_security_event(
            usuario=user.username,
            accion="refresh_token",
            resultado=AuditService.RESULTADO_EXITO,
            ip_address=session.ip_address
        )
        
        return RefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=JWTService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @classmethod
    def validate_token(
        cls, 
        db: Session, 
        token: str, 
        client_ip: str, 
        client_ua: str
    ) -> AdminUser:
        """
        Validate JWT and return user with Device Binding and Redis caching
        """
        from services.redis_service import redis_service
        
        # Decode token
        try:
            payload = JWTService.decode_token(token)
        except ExpiredTokenError:
            raise
        except InvalidTokenError:
            raise
        
        user_id = payload.get("user_id")
        if not user_id:
            raise InvalidTokenError("Invalid token payload")
            
        # 1. Cache HIT en Redis
        session_key = f"session:{token}"
        session_data = redis_service.get(session_key)
        
        if session_data:
            saved_ip = session_data.get("ip_address")
            saved_ua = session_data.get("user_agent")
        else:
            # Cache MISS - Fallback a PostgreSQL
            session = db.query(AdminSession).filter(AdminSession.token == token).first()
            if not session:
                raise InvalidTokenError("Session not found")
                
            if session.expires_at < datetime.now(timezone.utc):
                raise ExpiredTokenError("Session expired")
                
            saved_ip = session.ip_address
            saved_ua = session.user_agent
            
            # Registrar en Redis
            ttl = int((session.expires_at - datetime.now(timezone.utc)).total_seconds())
            if ttl > 0:
                redis_service.set(session_key, {
                    "user_id": user_id,
                    "ip_address": saved_ip,
                    "user_agent": saved_ua
                }, ttl=ttl)

        # 2. Control de Huella Digital (Device Binding)
        if saved_ip != client_ip:
            redis_service.delete(session_key)
            db.query(AdminSession).filter(AdminSession.token == token).delete()
            db.commit()
            raise InvalidTokenError("Device binding violation: IP mismatch")
            
        if saved_ua != client_ua:
            redis_service.delete(session_key)
            db.query(AdminSession).filter(AdminSession.token == token).delete()
            db.commit()
            raise InvalidTokenError("Device binding violation: User-Agent mismatch")

        # 3. Obtener Usuario
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            raise InvalidTokenError("User not found")
        if not user.is_active:
            raise AccountDisabledError("Account is disabled")
            
        # Actualizar last_activity en DB relacional
        session = db.query(AdminSession).filter(AdminSession.token == token).first()
        if session:
            session.last_activity = datetime.now(timezone.utc)
            db.commit()
            
        return user
    
    @classmethod
    def change_password(
        cls,
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Change user password
        
        Args:
            db: Database session
            user_id: User ID
            current_password: Current password
            new_password: New password
            ip_address: Client IP
            user_agent: Client user agent
            
        Raises:
            InvalidCredentialsError: If current password is incorrect
            ValueError: If new password doesn't meet requirements
            
        Example:
            >>> AuthService.change_password(
            ...     db, 
            ...     user_id=1, 
            ...     current_password="OldPass123!", 
            ...     new_password="NewPass456!"
            ... )
        """
        # Find user
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not PasswordService.verify_password(current_password, user.password_hash):
            AuditService.log_action(
                db=db,
                user=user,
                accion="cambiar_contraseña",
                modulo="auth",
                resultado=AuditService.RESULTADO_ERROR,
                detalles={"error": "invalid_current_password"},
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise InvalidCredentialsError("Current password is incorrect")
        
        # Validate new password strength
        validation_result = PasswordService.validate_password_strength(new_password)
        if not validation_result.is_valid:
            raise ValueError("; ".join(validation_result.errors))
        
        # Hash new password
        new_password_hash = PasswordService.hash_password(new_password)
        
        # Update password
        user.password_hash = new_password_hash
        db.commit()
        
        # Log password change
        AuditService.log_action(
            db=db,
            user=user,
            accion="cambiar_contraseña",
            modulo="auth",
            resultado=AuditService.RESULTADO_EXITO,
            ip_address=ip_address,
            user_agent=user_agent
        )

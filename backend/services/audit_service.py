"""
Audit Service
Servicio para registro de auditoría de acciones administrativas
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from db.models_auth import AdminAuditLog, AdminUser


class AuditService:
    """Service for audit logging"""
    
    # Valid resultado values
    RESULTADO_EXITO = "exito"
    RESULTADO_ERROR = "error"
    RESULTADO_DENEGADO = "denegado"
    
    VALID_RESULTADOS = [RESULTADO_EXITO, RESULTADO_ERROR, RESULTADO_DENEGADO]
    
    @classmethod
    def log_action(
        cls,
        db: Session,
        user: Optional[AdminUser],
        accion: str,
        modulo: str,
        resultado: str,
        entidad_tipo: Optional[str] = None,
        entidad_id: Optional[int] = None,
        detalles: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """
        Create audit log entry
        
        Args:
            db: Database session
            user: User performing action (can be None for system actions)
            accion: Action name (login, logout, crear, editar, eliminar, etc.)
            modulo: Module name (auth, empresas, admin_users, printers, etc.)
            resultado: Result (exito, error, denegado)
            entidad_tipo: Entity type (empresa, admin_user, printer, etc.)
            entidad_id: Entity ID
            detalles: Additional details (JSON)
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            Created AdminAuditLog object
            
        Raises:
            ValueError: If resultado is not valid
            
        Example:
            >>> audit_log = AuditService.log_action(
            ...     db=db,
            ...     user=current_user,
            ...     accion="login",
            ...     modulo="auth",
            ...     resultado="exito",
            ...     ip_address="192.168.1.100",
            ...     user_agent="Mozilla/5.0..."
            ... )
            >>> audit_log.accion
            'login'
            >>> audit_log.resultado
            'exito'
        """
        # Validate resultado
        if resultado not in cls.VALID_RESULTADOS:
            raise ValueError(
                f"Invalid resultado '{resultado}'. Must be one of: {', '.join(cls.VALID_RESULTADOS)}"
            )
        
        # Create audit log entry
        audit_log = AdminAuditLog(
            admin_user_id=user.id if user else None,
            accion=accion,
            modulo=modulo,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            detalles=detalles or {},
            resultado=resultado,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @classmethod
    def get_user_activity(
        cls,
        db: Session,
        user_id: int,
        limit: int = 100
    ) -> List[AdminAuditLog]:
        """
        Get recent activity for user
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of AdminAuditLog objects ordered by created_at DESC
            
        Example:
            >>> logs = AuditService.get_user_activity(db, user_id=1, limit=50)
            >>> len(logs) <= 50
            True
            >>> all(log.admin_user_id == 1 for log in logs)
            True
        """
        return (
            db.query(AdminAuditLog)
            .filter(AdminAuditLog.admin_user_id == user_id)
            .order_by(AdminAuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
    
    @classmethod
    def get_entity_history(
        cls,
        db: Session,
        entidad_tipo: str,
        entidad_id: int,
        limit: int = 100
    ) -> List[AdminAuditLog]:
        """
        Get audit history for specific entity
        
        Args:
            db: Database session
            entidad_tipo: Entity type (empresa, admin_user, printer, etc.)
            entidad_id: Entity ID
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of AdminAuditLog objects ordered by created_at DESC
            
        Example:
            >>> logs = AuditService.get_entity_history(
            ...     db, 
            ...     entidad_tipo="empresa", 
            ...     entidad_id=1
            ... )
            >>> all(log.entidad_tipo == "empresa" for log in logs)
            True
            >>> all(log.entidad_id == 1 for log in logs)
            True
        """
        return (
            db.query(AdminAuditLog)
            .filter(
                AdminAuditLog.entidad_tipo == entidad_tipo,
                AdminAuditLog.entidad_id == entidad_id
            )
            .order_by(AdminAuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
    
    @classmethod
    def get_recent_logs(
        cls,
        db: Session,
        modulo: Optional[str] = None,
        accion: Optional[str] = None,
        resultado: Optional[str] = None,
        limit: int = 100
    ) -> List[AdminAuditLog]:
        """
        Get recent audit logs with optional filters
        
        Args:
            db: Database session
            modulo: Filter by module (optional)
            accion: Filter by action (optional)
            resultado: Filter by result (optional)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of AdminAuditLog objects ordered by created_at DESC
            
        Example:
            >>> logs = AuditService.get_recent_logs(
            ...     db,
            ...     modulo="auth",
            ...     resultado="error",
            ...     limit=20
            ... )
            >>> len(logs) <= 20
            True
            >>> all(log.modulo == "auth" for log in logs)
            True
        """
        query = db.query(AdminAuditLog)
        
        if modulo:
            query = query.filter(AdminAuditLog.modulo == modulo)
        
        if accion:
            query = query.filter(AdminAuditLog.accion == accion)
        
        if resultado:
            query = query.filter(AdminAuditLog.resultado == resultado)
        
        return query.order_by(AdminAuditLog.created_at.desc()).limit(limit).all()

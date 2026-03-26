"""
Cleanup Expired Sessions Job
Job para limpiar sesiones expiradas de la base de datos
"""
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models_auth import AdminSession

logger = logging.getLogger(__name__)


def cleanup_expired_sessions() -> int:
    """
    Elimina sesiones expiradas de admin_sessions
    
    Returns:
        Número de sesiones eliminadas
        
    Example:
        >>> deleted_count = cleanup_expired_sessions()
        >>> print(f"Deleted {deleted_count} expired sessions")
    """
    db: Session = SessionLocal()
    deleted_count = 0
    
    try:
        now = datetime.now(timezone.utc)
        
        # Query para sesiones expiradas (usa índice en expires_at)
        expired_sessions = db.query(AdminSession).filter(
            AdminSession.expires_at < now
        ).all()
        
        deleted_count = len(expired_sessions)
        
        if deleted_count > 0:
            # Eliminar sesiones expiradas
            db.query(AdminSession).filter(
                AdminSession.expires_at < now
            ).delete(synchronize_session=False)
            
            db.commit()
            
            logger.info(f"Cleanup job: Deleted {deleted_count} expired sessions")
        else:
            logger.debug("Cleanup job: No expired sessions to delete")
        
        return deleted_count
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in cleanup_expired_sessions job: {e}")
        # No re-raise para no afectar el sistema principal
        return 0
        
    finally:
        db.close()


def cleanup_expired_refresh_tokens() -> int:
    """
    Elimina sesiones con refresh tokens expirados
    
    Returns:
        Número de sesiones eliminadas
    """
    db: Session = SessionLocal()
    deleted_count = 0
    
    try:
        now = datetime.now(timezone.utc)
        
        # Query para refresh tokens expirados
        expired_refresh = db.query(AdminSession).filter(
            AdminSession.refresh_expires_at < now
        ).all()
        
        deleted_count = len(expired_refresh)
        
        if deleted_count > 0:
            # Eliminar sesiones con refresh tokens expirados
            db.query(AdminSession).filter(
                AdminSession.refresh_expires_at < now
            ).delete(synchronize_session=False)
            
            db.commit()
            
            logger.info(f"Cleanup job: Deleted {deleted_count} sessions with expired refresh tokens")
        else:
            logger.debug("Cleanup job: No expired refresh tokens to delete")
        
        return deleted_count
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in cleanup_expired_refresh_tokens job: {e}")
        return 0
        
    finally:
        db.close()


def run_cleanup_job():
    """
    Ejecuta ambos jobs de limpieza
    
    Esta función se puede llamar desde un scheduler (APScheduler, Celery, etc.)
    """
    logger.info("Starting session cleanup job...")
    
    # Limpiar sesiones expiradas
    deleted_sessions = cleanup_expired_sessions()
    
    # Limpiar refresh tokens expirados
    deleted_refresh = cleanup_expired_refresh_tokens()
    
    total_deleted = deleted_sessions + deleted_refresh
    
    logger.info(f"Session cleanup job completed. Total deleted: {total_deleted}")
    
    return total_deleted


if __name__ == "__main__":
    # Para testing manual
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Running cleanup job...")
    total = run_cleanup_job()
    print(f"Cleanup completed. Total sessions deleted: {total}")

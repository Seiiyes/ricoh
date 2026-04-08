"""
API endpoints para sincronización de usuarios
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from services.user_sync_service import UserSyncService
from pydantic import BaseModel
from typing import Dict

router = APIRouter(prefix="/api/sync", tags=["sync"])


class SyncStatsResponse(BaseModel):
    """Respuesta con estadísticas de sincronización"""
    users_in_db: int
    users_in_counters: int
    users_missing: int


class SyncResultResponse(BaseModel):
    """Respuesta de sincronización masiva"""
    created: int
    existing: int
    total: int
    errors: int
    message: str


@router.get("/stats", response_model=SyncStatsResponse)
async def get_sync_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas de sincronización de usuarios.
    
    Muestra cuántos usuarios hay en la BD vs cuántos en contadores.
    """
    try:
        stats = UserSyncService.get_sync_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users", response_model=SyncResultResponse)
async def sync_all_users(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Sincronización masiva de usuarios desde contadores.
    
    Crea automáticamente todos los usuarios detectados en contadores
    que no existen en la tabla users.
    
    Args:
        days: Días hacia atrás para considerar usuarios activos (default: 30)
    
    Returns:
        Estadísticas de la sincronización
    """
    try:
        result = UserSyncService.sync_all_users_from_counters(db, days=days)
        
        message = f"Sincronización completada: {result['created']} usuarios creados"
        if result['errors'] > 0:
            message += f", {result['errors']} errores"
        
        return {
            **result,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/from-printer/{printer_id}", response_model=SyncResultResponse)
async def sync_users_from_printer(
    printer_id: int,
    admin_user: str = "admin",
    admin_password: str = "",
    db: Session = Depends(get_db)
):
    """
    Sincroniza usuarios desde la libreta de direcciones de una impresora.
    
    Lee la libreta de direcciones de la impresora y sincroniza usuarios
    con sus rutas SMB reales.
    
    Args:
        printer_id: ID de la impresora
        admin_user: Usuario admin de la impresora (default: admin)
        admin_password: Password admin de la impresora
    
    Returns:
        Estadísticas de la sincronización
    """
    try:
        result = UserSyncService.sync_users_from_printer_addressbook(
            db=db,
            printer_id=printer_id,
            admin_user=admin_user,
            admin_password=admin_password
        )
        
        message = f"Sincronización desde libreta completada: {result['created']} creados, {result['updated']} actualizados"
        if result['errors'] > 0:
            message += f", {result['errors']} errores"
        
        return {
            **result,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

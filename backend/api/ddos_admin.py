"""
DDoS Protection Administration API
Endpoints para administrar la protección contra DDoS
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List
from middleware.auth_middleware import get_current_user
from middleware.ddos_protection import (
    IPBlockList,
    BurstDetector,
    get_ddos_stats,
    cleanup_ddos_data,
    DDoSProtectionConfig
)
from db.models_auth import AdminUser

router = APIRouter(prefix="/admin/ddos", tags=["DDoS Protection Admin"])


class UnblockIPRequest(BaseModel):
    """Request para desbloquear IP"""
    ip: str


class BlockIPRequest(BaseModel):
    """Request para bloquear IP"""
    ip: str
    duration_seconds: int = DDoSProtectionConfig.BLOCK_DURATION


class DDoSStatsResponse(BaseModel):
    """Respuesta con estadísticas de DDoS"""
    blocked_ips: Dict[str, str]
    blocked_count: int
    config: dict


@router.get("/stats", response_model=DDoSStatsResponse)
async def get_stats(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Obtener estadísticas de protección DDoS
    
    **Requiere**: Autenticación como superadmin
    
    **Returns**:
    - **blocked_ips**: Diccionario de IPs bloqueadas con tiempo de desbloqueo
    - **blocked_count**: Número de IPs bloqueadas
    - **config**: Configuración actual de protección DDoS
    """
    # Solo superadmin puede ver estadísticas
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can view DDoS statistics"
        )
    
    return get_ddos_stats()


@router.post("/unblock-ip")
async def unblock_ip(
    request: UnblockIPRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Desbloquear IP manualmente
    
    **Requiere**: Autenticación como superadmin
    
    **Args**:
    - **ip**: Dirección IP a desbloquear
    
    **Returns**:
    - Mensaje de confirmación
    """
    # Solo superadmin puede desbloquear IPs
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can unblock IPs"
        )
    
    IPBlockList.unblock_ip(request.ip)
    
    return {
        "message": f"IP {request.ip} unblocked successfully",
        "ip": request.ip
    }


@router.post("/block-ip")
async def block_ip(
    request: BlockIPRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Bloquear IP manualmente
    
    **Requiere**: Autenticación como superadmin
    
    **Args**:
    - **ip**: Dirección IP a bloquear
    - **duration_seconds**: Duración del bloqueo en segundos (default: 900 = 15 minutos)
    
    **Returns**:
    - Mensaje de confirmación
    """
    # Solo superadmin puede bloquear IPs
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can block IPs"
        )
    
    IPBlockList.block_ip(request.ip, request.duration_seconds)
    
    return {
        "message": f"IP {request.ip} blocked for {request.duration_seconds} seconds",
        "ip": request.ip,
        "duration_seconds": request.duration_seconds
    }


@router.post("/cleanup")
async def cleanup(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Limpiar datos antiguos de protección DDoS
    
    **Requiere**: Autenticación como superadmin
    
    Limpia:
    - Bloqueos de IP expirados
    - Registros de burst antiguos
    - Contadores de rate limit expirados
    
    **Returns**:
    - Estadísticas de limpieza
    """
    # Solo superadmin puede ejecutar limpieza
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can run cleanup"
        )
    
    result = cleanup_ddos_data()
    
    return {
        "message": "Cleanup completed successfully",
        **result
    }


@router.get("/blocked-ips")
async def get_blocked_ips(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Obtener lista de IPs bloqueadas
    
    **Requiere**: Autenticación como superadmin
    
    **Returns**:
    - Lista de IPs bloqueadas con tiempo de desbloqueo
    """
    # Solo superadmin puede ver IPs bloqueadas
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can view blocked IPs"
        )
    
    blocked_ips = IPBlockList.get_blocked_ips()
    
    return {
        "blocked_ips": blocked_ips,
        "count": len(blocked_ips)
    }


@router.get("/config")
async def get_config(
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Obtener configuración de protección DDoS
    
    **Requiere**: Autenticación
    
    **Returns**:
    - Configuración actual de límites y protecciones
    """
    return {
        "global_rate_limit": DDoSProtectionConfig.GLOBAL_RATE_LIMIT,
        "global_rate_window": DDoSProtectionConfig.GLOBAL_RATE_WINDOW,
        "suspicious_rate_limit": DDoSProtectionConfig.SUSPICIOUS_RATE_LIMIT,
        "suspicious_rate_window": DDoSProtectionConfig.SUSPICIOUS_RATE_WINDOW,
        "burst_threshold": DDoSProtectionConfig.BURST_THRESHOLD,
        "burst_window": DDoSProtectionConfig.BURST_WINDOW,
        "block_duration": DDoSProtectionConfig.BLOCK_DURATION,
        "max_payload_size": DDoSProtectionConfig.MAX_PAYLOAD_SIZE,
        "endpoint_limits": DDoSProtectionConfig.ENDPOINT_LIMITS,
        "whitelist_ips": DDoSProtectionConfig.WHITELIST_IPS
    }

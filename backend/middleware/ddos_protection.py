"""
DDoS Protection Middleware
Protección multicapa contra ataques de denegación de servicio distribuido
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from services.rate_limiter_service import RateLimiterService
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import threading
import logging
import hashlib

logger = logging.getLogger(__name__)


class DDoSProtectionConfig:
    """Configuración de protección DDoS"""
    
    # Rate limiting global por IP
    GLOBAL_RATE_LIMIT = 100  # requests por ventana
    GLOBAL_RATE_WINDOW = 60  # segundos (1 minuto)
    
    # Rate limiting agresivo para IPs sospechosas
    SUSPICIOUS_RATE_LIMIT = 20  # requests por ventana
    SUSPICIOUS_RATE_WINDOW = 60  # segundos
    
    # Límites por endpoint
    ENDPOINT_LIMITS = {
        "/auth/login": (5, 60),  # 5 requests por minuto
        "/auth/refresh": (10, 60),  # 10 requests por minuto
        "/discovery/scan": (2, 300),  # 2 scans cada 5 minutos
        "/discovery/sync-users-from-printers": (3, 300),  # 3 syncs cada 5 minutos
    }
    
    # Detección de patrones de ataque
    BURST_THRESHOLD = 30  # requests en burst_window
    BURST_WINDOW = 10  # segundos
    
    # Bloqueo temporal
    BLOCK_DURATION = 900  # 15 minutos
    
    # Whitelist de IPs (localhost, redes internas)
    WHITELIST_IPS = [
        "127.0.0.1",
        "::1",
        "localhost"
    ]
    
    # Tamaño máximo de payload (10MB)
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024


class IPBlockList:
    """Gestión de IPs bloqueadas temporalmente"""
    
    _blocked_ips = {}  # {ip: block_until_datetime}
    _lock = threading.Lock()
    
    @classmethod
    def block_ip(cls, ip: str, duration_seconds: int = DDoSProtectionConfig.BLOCK_DURATION):
        """Bloquear IP temporalmente"""
        with cls._lock:
            block_until = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
            cls._blocked_ips[ip] = block_until
            logger.warning(f"🚫 IP bloqueada: {ip} hasta {block_until.isoformat()}")
    
    @classmethod
    def is_blocked(cls, ip: str) -> bool:
        """Verificar si IP está bloqueada"""
        with cls._lock:
            if ip not in cls._blocked_ips:
                return False
            
            block_until = cls._blocked_ips[ip]
            now = datetime.now(timezone.utc)
            
            if now >= block_until:
                # Bloqueo expirado, remover
                del cls._blocked_ips[ip]
                logger.info(f"✅ IP desbloqueada: {ip}")
                return False
            
            return True
    
    @classmethod
    def unblock_ip(cls, ip: str):
        """Desbloquear IP manualmente"""
        with cls._lock:
            if ip in cls._blocked_ips:
                del cls._blocked_ips[ip]
                logger.info(f"✅ IP desbloqueada manualmente: {ip}")
    
    @classmethod
    def get_blocked_ips(cls) -> dict:
        """Obtener lista de IPs bloqueadas"""
        with cls._lock:
            now = datetime.now(timezone.utc)
            return {
                ip: block_until.isoformat()
                for ip, block_until in cls._blocked_ips.items()
                if now < block_until
            }
    
    @classmethod
    def cleanup_expired(cls) -> int:
        """Limpiar bloqueos expirados"""
        with cls._lock:
            now = datetime.now(timezone.utc)
            expired = [ip for ip, block_until in cls._blocked_ips.items() if now >= block_until]
            
            for ip in expired:
                del cls._blocked_ips[ip]
            
            if expired:
                logger.info(f"🧹 Limpiados {len(expired)} bloqueos expirados")
            
            return len(expired)


class BurstDetector:
    """Detector de ráfagas de requests (burst attacks)"""
    
    _request_times = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
    _lock = threading.Lock()
    
    @classmethod
    def record_request(cls, ip: str) -> bool:
        """
        Registrar request y detectar burst
        
        Returns:
            True si se detecta burst attack, False si es normal
        """
        with cls._lock:
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=DDoSProtectionConfig.BURST_WINDOW)
            
            # Limpiar requests antiguos
            cls._request_times[ip] = [
                ts for ts in cls._request_times[ip]
                if ts > window_start
            ]
            
            # Agregar request actual
            cls._request_times[ip].append(now)
            
            # Verificar si excede threshold
            request_count = len(cls._request_times[ip])
            
            if request_count >= DDoSProtectionConfig.BURST_THRESHOLD:
                logger.warning(
                    f"⚠️ Burst attack detectado: {ip} - "
                    f"{request_count} requests en {DDoSProtectionConfig.BURST_WINDOW}s"
                )
                return True
            
            return False
    
    @classmethod
    def cleanup_old_records(cls, max_age_seconds: int = 300):
        """Limpiar registros antiguos"""
        with cls._lock:
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(seconds=max_age_seconds)
            
            for ip in list(cls._request_times.keys()):
                cls._request_times[ip] = [
                    ts for ts in cls._request_times[ip]
                    if ts > cutoff
                ]
                
                if not cls._request_times[ip]:
                    del cls._request_times[ip]


class DDoSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware de protección contra DDoS"""
    
    async def dispatch(self, request: Request, call_next):
        """Procesar request con protección DDoS"""
        
        # Obtener IP del cliente
        client_ip = self._get_client_ip(request)
        
        print(f"[DDOS] Request de {client_ip} a {request.url.path}")
        
        # 1. Verificar si IP está en whitelist
        if self._is_whitelisted(client_ip):
            print(f"[DDOS] IP {client_ip} en whitelist, permitiendo")
            return await call_next(request)
        
        # 2. Verificar si IP está bloqueada
        if IPBlockList.is_blocked(client_ip):
            print(f"[DDOS] IP {client_ip} BLOQUEADA, retornando 403")
            logger.warning(f"🚫 Request bloqueado de IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "IP_BLOCKED",
                    "message": "Your IP has been temporarily blocked due to suspicious activity",
                    "blocked_ips": IPBlockList.get_blocked_ips()
                }
            )
        
        # 3. Verificar tamaño del payload
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > DDoSProtectionConfig.MAX_PAYLOAD_SIZE:
            logger.warning(f"⚠️ Payload demasiado grande de {client_ip}: {content_length} bytes")
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "PAYLOAD_TOO_LARGE",
                    "message": f"Request payload exceeds maximum size of {DDoSProtectionConfig.MAX_PAYLOAD_SIZE} bytes"
                }
            )
        
        # 4. Detectar burst attacks
        if BurstDetector.record_request(client_ip):
            # Bloquear IP por burst attack
            IPBlockList.block_ip(client_ip)
            logger.error(f"🚨 IP bloqueada por burst attack: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "BURST_ATTACK_DETECTED",
                    "message": "Too many requests in short time. IP blocked temporarily."
                }
            )
        
        # 5. Rate limiting global por IP
        global_key = f"global:{client_ip}"
        global_result = RateLimiterService.check_rate_limit(
            global_key,
            DDoSProtectionConfig.GLOBAL_RATE_LIMIT,
            DDoSProtectionConfig.GLOBAL_RATE_WINDOW
        )
        
        if not global_result.allowed:
            logger.warning(f"⚠️ Rate limit global excedido: {client_ip}")
            return self._rate_limit_response(global_result, DDoSProtectionConfig.GLOBAL_RATE_LIMIT)
        
        # 6. Rate limiting por endpoint específico
        endpoint = request.url.path
        if endpoint in DDoSProtectionConfig.ENDPOINT_LIMITS:
            limit, window = DDoSProtectionConfig.ENDPOINT_LIMITS[endpoint]
            endpoint_key = f"endpoint:{client_ip}:{endpoint}"
            
            endpoint_result = RateLimiterService.check_rate_limit(
                endpoint_key,
                limit,
                window
            )
            
            if not endpoint_result.allowed:
                logger.warning(f"⚠️ Rate limit de endpoint excedido: {client_ip} - {endpoint}")
                return self._rate_limit_response(endpoint_result, limit)
        
        # 7. Agregar headers de rate limit a la respuesta
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(DDoSProtectionConfig.GLOBAL_RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(global_result.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(global_result.reset_at.timestamp()))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP real del cliente (considerando proxies)"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Tomar la primera IP (cliente original)
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fallback a IP directa
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_whitelisted(self, ip: str) -> bool:
        """Verificar si IP está en whitelist"""
        # Verificar whitelist exacta
        if ip in DDoSProtectionConfig.WHITELIST_IPS:
            return True
        
        # Verificar rangos de red privada
        if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
            return True
        
        return False
    
    def _rate_limit_response(self, result, limit: int) -> JSONResponse:
        """Generar respuesta de rate limit excedido"""
        reset_seconds = int(
            (result.reset_at.timestamp() - 
             datetime.now(timezone.utc).timestamp())
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": f"Too many requests. Try again in {reset_seconds} seconds.",
                "reset_at": result.reset_at.isoformat()
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(result.reset_at.timestamp())),
                "Retry-After": str(reset_seconds)
            }
        )


# Funciones de utilidad para administración

def get_ddos_stats() -> dict:
    """Obtener estadísticas de protección DDoS"""
    return {
        "blocked_ips": IPBlockList.get_blocked_ips(),
        "blocked_count": len(IPBlockList.get_blocked_ips()),
        "config": {
            "global_rate_limit": DDoSProtectionConfig.GLOBAL_RATE_LIMIT,
            "global_rate_window": DDoSProtectionConfig.GLOBAL_RATE_WINDOW,
            "burst_threshold": DDoSProtectionConfig.BURST_THRESHOLD,
            "burst_window": DDoSProtectionConfig.BURST_WINDOW,
            "block_duration": DDoSProtectionConfig.BLOCK_DURATION,
            "max_payload_size": DDoSProtectionConfig.MAX_PAYLOAD_SIZE
        }
    }


def cleanup_ddos_data():
    """Limpiar datos antiguos de protección DDoS"""
    blocked_cleaned = IPBlockList.cleanup_expired()
    BurstDetector.cleanup_old_records()
    rate_limit_cleaned = RateLimiterService.cleanup_expired(
        DDoSProtectionConfig.GLOBAL_RATE_WINDOW
    )
    
    logger.info(
        f"🧹 Limpieza DDoS: {blocked_cleaned} IPs desbloqueadas, "
        f"{rate_limit_cleaned} contadores limpiados"
    )
    
    return {
        "blocked_ips_cleaned": blocked_cleaned,
        "rate_limit_counters_cleaned": rate_limit_cleaned
    }

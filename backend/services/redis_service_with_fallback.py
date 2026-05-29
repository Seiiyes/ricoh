"""
Redis Service with Graceful Fallback
Handles caching with Redis when available, falls back to memory for development
"""
import os
import json
import logging
from typing import Optional, Any, Dict
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisService:
    """
    Service for Redis caching and rate limiting
    Gracefully falls back to in-memory storage if Redis is not available
    """
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self._memory_cache: Dict[str, tuple] = {}  # {key: (value, expiry_time)}
        
        # Try to connect to Redis
        try:
            import redis
            
            redis_url = os.getenv("REDIS_URL")
            
            if redis_url:
                # Use REDIS_URL if provided
                self.client = redis.from_url(redis_url, decode_responses=True)
            else:
                # Use individual config variables
                self.client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    db=int(os.getenv("REDIS_DB", 0)),
                    password=os.getenv("REDIS_PASSWORD", None) or None,
                    decode_responses=True,
                    socket_connect_timeout=2,  # Fail fast
                    socket_timeout=2
                )
            
            # Test connection
            self.client.ping()
            self.enabled = True
            logger.info("✅ Redis conectado y operativo")
            
        except ImportError:
            logger.warning("⚠️  Módulo 'redis' no instalado. Usando caché en memoria.")
            logger.warning("   Para instalar: pip install redis hiredis")
            self.enabled = False
            
        except Exception as e:
            logger.warning(f"⚠️  Redis no disponible: {e}")
            logger.warning("   Usando caché en memoria (solo para desarrollo)")
            logger.warning("   Para producción, instalar y configurar Redis")
            self.enabled = False
    
    def _clean_expired_memory_cache(self):
        """Remove expired entries from memory cache"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, expiry) in self._memory_cache.items()
            if expiry and expiry < now
        ]
        for key in expired_keys:
            del self._memory_cache[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            # Memory fallback
            self._clean_expired_memory_cache()
            if key in self._memory_cache:
                value, expiry = self._memory_cache[key]
                if expiry is None or expiry > datetime.now():
                    return value
                else:
                    del self._memory_cache[key]
            return None
        
        # Redis
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error reading from Redis: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)"""
        if not self.enabled:
            # Memory fallback
            expiry = datetime.now() + timedelta(seconds=ttl) if ttl else None
            self._memory_cache[key] = (value, expiry)
            return
        
        # Redis
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled:
            # Memory fallback
            self._memory_cache.pop(key, None)
            return
        
        # Redis
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting from Redis: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (e.g., 'dashboard:*')"""
        if not self.enabled:
            # Memory fallback - simple pattern matching
            pattern_str = pattern.replace('*', '')
            keys_to_delete = [
                k for k in self._memory_cache.keys()
                if pattern_str in k
            ]
            for k in keys_to_delete:
                del self._memory_cache[k]
            logger.debug(f"Invalidated {len(keys_to_delete)} keys matching '{pattern}' from memory")
            return
        
        # Redis
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.debug(f"Invalidated {len(keys)} keys matching '{pattern}' from Redis")
        except Exception as e:
            logger.error(f"Error invalidating pattern from Redis: {e}")
    
    def is_enabled(self) -> bool:
        """Check if Redis is enabled and working"""
        return self.enabled
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            self._clean_expired_memory_cache()
            return {
                "backend": "memory",
                "enabled": False,
                "keys_count": len(self._memory_cache),
                "warning": "Using in-memory cache (not recommended for production)"
            }
        
        try:
            info = self.client.info()
            return {
                "backend": "redis",
                "enabled": True,
                "keys_count": self.client.dbsize(),
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            return {
                "backend": "redis",
                "enabled": False,
                "error": str(e)
            }


# Singleton instance
redis_service = RedisService()


# Decorator for caching
def cache_result(key_prefix: str, ttl: int = 300):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Prefix for cache key (e.g., 'dashboard:kpis')
        ttl: Time to live in seconds (default: 300 = 5 minutes)
    
    Example:
        @cache_result("dashboard:kpis", ttl=300)
        async def get_dashboard_kpis(db: Session):
            # This result will be cached for 5 minutes
            return expensive_query(db)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            key_parts = [key_prefix]
            
            # Add positional args (skip 'self' and 'db' Session objects)
            for arg in args:
                if not hasattr(arg, '__class__') or arg.__class__.__name__ not in ['Session', 'Request']:
                    key_parts.append(str(arg))
            
            # Add keyword args (skip 'db' Session objects)
            for k, v in sorted(kwargs.items()):
                if k != 'db' and not (hasattr(v, '__class__') and v.__class__.__name__ == 'Session'):
                    key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached = redis_service.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached
            
            logger.debug(f"Cache MISS: {cache_key}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Health check function
def check_redis_health() -> dict:
    """
    Check Redis health status
    Returns dict with status information
    """
    return redis_service.get_stats()

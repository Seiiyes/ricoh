"""
Rate Limiter Service
Servicio para limitar requests y prevenir ataques
"""
from typing import Dict, NamedTuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import threading


class RateLimitResult(NamedTuple):
    """Result of rate limit check"""
    allowed: bool
    remaining: int
    reset_at: datetime


class RateLimiterService:
    """Service for rate limiting using in-memory storage"""
    
    # Storage: {key: {window_start: datetime, count: int}}
    _storage: Dict[str, Dict] = defaultdict(dict)
    _lock = threading.Lock()
    
    @classmethod
    def check_rate_limit(
        cls,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> RateLimitResult:
        """
        Check if request is within rate limit
        
        Args:
            key: Unique key (e.g., IP address, user ID)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            RateLimitResult with allowed status, remaining count, and reset time
            
        Example:
            >>> result = RateLimiterService.check_rate_limit("192.168.1.100", 5, 60)
            >>> result.allowed
            True
            >>> result.remaining
            4
        """
        with cls._lock:
            now = datetime.now(timezone.utc)
            
            # Get or initialize counter for this key
            if key not in cls._storage:
                cls._storage[key] = {
                    'window_start': now,
                    'count': 0
                }
            
            counter = cls._storage[key]
            window_start = counter['window_start']
            count = counter['count']
            
            # Check if window has expired
            window_end = window_start + timedelta(seconds=window_seconds)
            if now >= window_end:
                # Reset window
                cls._storage[key] = {
                    'window_start': now,
                    'count': 0
                }
                counter = cls._storage[key]
                count = 0
                window_start = now
                window_end = now + timedelta(seconds=window_seconds)
            
            # Check if limit exceeded
            if count >= max_requests:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=window_end
                )
            
            # Increment counter
            cls._storage[key]['count'] += 1
            
            return RateLimitResult(
                allowed=True,
                remaining=max_requests - count - 1,
                reset_at=window_end
            )
    
    @classmethod
    def increment_counter(cls, key: str, window_seconds: int) -> int:
        """
        Increment request counter
        
        Args:
            key: Unique key
            window_seconds: Time window in seconds
            
        Returns:
            Current count after increment
            
        Example:
            >>> count = RateLimiterService.increment_counter("192.168.1.100", 60)
            >>> count
            1
        """
        with cls._lock:
            now = datetime.now(timezone.utc)
            
            if key not in cls._storage:
                cls._storage[key] = {
                    'window_start': now,
                    'count': 1
                }
                return 1
            
            counter = cls._storage[key]
            window_start = counter['window_start']
            window_end = window_start + timedelta(seconds=window_seconds)
            
            # Check if window has expired
            if now >= window_end:
                cls._storage[key] = {
                    'window_start': now,
                    'count': 1
                }
                return 1
            
            # Increment counter
            cls._storage[key]['count'] += 1
            return cls._storage[key]['count']
    
    @classmethod
    def reset_counter(cls, key: str) -> None:
        """
        Reset request counter
        
        Args:
            key: Unique key
            
        Example:
            >>> RateLimiterService.reset_counter("192.168.1.100")
        """
        with cls._lock:
            if key in cls._storage:
                del cls._storage[key]
    
    @classmethod
    def cleanup_expired(cls, window_seconds: int) -> int:
        """
        Clean up expired counters
        
        Args:
            window_seconds: Time window in seconds
            
        Returns:
            Number of expired counters removed
            
        Example:
            >>> removed = RateLimiterService.cleanup_expired(60)
            >>> removed >= 0
            True
        """
        with cls._lock:
            now = datetime.now(timezone.utc)
            expired_keys = []
            
            for key, counter in cls._storage.items():
                window_start = counter['window_start']
                window_end = window_start + timedelta(seconds=window_seconds)
                
                if now >= window_end:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del cls._storage[key]
            
            return len(expired_keys)
    
    @classmethod
    def get_remaining(cls, key: str, max_requests: int, window_seconds: int) -> int:
        """
        Get remaining requests for key
        
        Args:
            key: Unique key
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Number of remaining requests
            
        Example:
            >>> remaining = RateLimiterService.get_remaining("192.168.1.100", 5, 60)
            >>> remaining >= 0
            True
        """
        with cls._lock:
            if key not in cls._storage:
                return max_requests
            
            now = datetime.now(timezone.utc)
            counter = cls._storage[key]
            window_start = counter['window_start']
            window_end = window_start + timedelta(seconds=window_seconds)
            
            # Check if window has expired
            if now >= window_end:
                return max_requests
            
            count = counter['count']
            remaining = max_requests - count
            
            return max(0, remaining)

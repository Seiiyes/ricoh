"""
Retry strategy for provisioning operations with exponential backoff
"""
from dataclasses import dataclass
from typing import Optional, Literal
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    initial_delay: float = 5.0  # seconds
    max_delay: float = 60.0  # seconds
    max_attempts: int = 5
    backoff_multiplier: float = 2.0
    
    # Error-specific configurations
    badflow_max_attempts: int = 1  # Only retry once after session reset
    connection_max_attempts: int = 3
    connection_delay: float = 10.0  # Fixed delay for connection errors


ErrorType = Literal['BUSY', 'BADFLOW', 'TIMEOUT', 'CONNECTION', 'OTHER']


class RetryStrategy:
    """Implements retry logic with exponential backoff"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        logger.info(f"RetryStrategy initialized: initial_delay={self.config.initial_delay}s, "
                   f"max_delay={self.config.max_delay}s, max_attempts={self.config.max_attempts}, "
                   f"backoff_multiplier={self.config.backoff_multiplier}")
    
    def should_retry(self, error_type: ErrorType, attempt: int) -> tuple[bool, float]:
        """
        Determine if operation should be retried and calculate delay.
        
        Args:
            error_type: Type of error encountered
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Tuple of (should_retry, delay_seconds)
        """
        if error_type == 'BUSY' or error_type == 'TIMEOUT':
            if attempt >= self.config.max_attempts:
                logger.info(f"Max attempts ({self.config.max_attempts}) reached for {error_type}")
                return False, 0.0
            
            # Exponential backoff: delay = initial * (multiplier ^ (attempt - 1))
            delay = self.config.initial_delay * (self.config.backoff_multiplier ** (attempt - 1))
            delay = min(delay, self.config.max_delay)
            
            logger.info(f"Retry {attempt}/{self.config.max_attempts} for {error_type}, delay={delay}s")
            return True, delay
        
        elif error_type == 'BADFLOW':
            if attempt >= self.config.badflow_max_attempts:
                logger.info(f"BADFLOW persists after session reset, not retrying")
                return False, 0.0
            
            logger.info(f"BADFLOW detected, will reset session and retry once")
            return True, 0.0  # No delay, immediate retry after session reset
        
        elif error_type == 'CONNECTION':
            if attempt >= self.config.connection_max_attempts:
                logger.info(f"Max connection attempts ({self.config.connection_max_attempts}) reached")
                return False, 0.0
            
            logger.info(f"Connection error, retry {attempt}/{self.config.connection_max_attempts}, "
                       f"delay={self.config.connection_delay}s")
            return True, self.config.connection_delay
        
        else:  # 'OTHER'
            logger.info(f"Permanent error type: {error_type}, not retrying")
            return False, 0.0
    
    def execute_with_retry(self, operation, error_classifier, operation_name: str = "operation"):
        """
        Execute an operation with retry logic.
        
        Args:
            operation: Callable that returns result or error indicator
            error_classifier: Callable that takes operation result and returns ErrorType
            operation_name: Name for logging
            
        Returns:
            Tuple of (success: bool, result: any, attempts: int)
        """
        attempt = 0
        last_error_type = None
        
        while True:
            attempt += 1
            logger.info(f"Executing {operation_name}, attempt {attempt}")
            
            result = operation()
            error_type = error_classifier(result)
            
            if error_type is None:
                # Success
                logger.info(f"{operation_name} succeeded on attempt {attempt}")
                return True, result, attempt
            
            last_error_type = error_type
            should_retry, delay = self.should_retry(error_type, attempt)
            
            if not should_retry:
                logger.error(f"{operation_name} failed after {attempt} attempts, error: {error_type}")
                return False, result, attempt
            
            if delay > 0:
                logger.info(f"Waiting {delay}s before retry...")
                time.sleep(delay)


def load_retry_config_from_env() -> RetryConfig:
    """Load retry configuration from environment variables"""
    import os
    
    try:
        config = RetryConfig(
            initial_delay=float(os.getenv('RETRY_INITIAL_DELAY', '5.0')),
            max_delay=float(os.getenv('RETRY_MAX_DELAY', '60.0')),
            max_attempts=int(os.getenv('RETRY_MAX_ATTEMPTS', '5')),
            backoff_multiplier=float(os.getenv('RETRY_BACKOFF_MULTIPLIER', '2.0')),
            badflow_max_attempts=int(os.getenv('RETRY_BADFLOW_MAX_ATTEMPTS', '1')),
            connection_max_attempts=int(os.getenv('RETRY_CONNECTION_MAX_ATTEMPTS', '3')),
            connection_delay=float(os.getenv('RETRY_CONNECTION_DELAY', '10.0'))
        )
        
        # Validate configuration values
        if config.initial_delay <= 0:
            logger.warning(f"Invalid RETRY_INITIAL_DELAY ({config.initial_delay}), using default 5.0")
            config.initial_delay = 5.0
        
        if config.max_delay <= 0:
            logger.warning(f"Invalid RETRY_MAX_DELAY ({config.max_delay}), using default 60.0")
            config.max_delay = 60.0
        
        if config.max_attempts <= 0:
            logger.warning(f"Invalid RETRY_MAX_ATTEMPTS ({config.max_attempts}), using default 5")
            config.max_attempts = 5
        
        if config.backoff_multiplier <= 1.0:
            logger.warning(f"Invalid RETRY_BACKOFF_MULTIPLIER ({config.backoff_multiplier}), using default 2.0")
            config.backoff_multiplier = 2.0
        
        logger.info(f"Loaded retry configuration from environment: {config}")
        return config
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error loading retry configuration from environment: {e}, using defaults")
        return RetryConfig()

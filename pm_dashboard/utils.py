import os
import json
import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union
from redis import Redis, ConnectionError, TimeoutError
from redis.exceptions import RedisError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variable for generic function typing
F = TypeVar('F', bound=Callable[..., Any])

class RedisManager:
    """
    Redis connection manager with connection pooling and basic caching utilities.
    """
    _instance = None
    _redis_client = None
    _is_connected = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Redis connection using environment variables."""
        self.redis_url = os.getenv('REDIS_URL')
        self.enabled = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
        
        if not self.redis_url or not self.enabled:
            logger.warning("Redis is disabled or REDIS_URL not set")
            return
            
        try:
            self._redis_client = Redis.from_url(
                self.redis_url,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                decode_responses=True
            )
            # Test the connection
            self._redis_client.ping()
            self._is_connected = True
            logger.info("Successfully connected to Redis")
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._is_connected = False
    
    @property
    def client(self) -> Optional[Redis]:
        """Get the Redis client instance."""
        return self._redis_client if self._is_connected else None
    
    def is_connected(self) -> bool:
        """Check if the Redis connection is active."""
        if not self._is_connected or not self._redis_client:
            return False
        try:
            self._redis_client.ping()
            return True
        except RedisError:
            self._is_connected = False
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis."""
        if not self.is_connected():
            return None
        try:
            value = self._redis_client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a value in Redis with optional expiration in seconds."""
        if not self.is_connected():
            return False
        try:
            if not isinstance(value, (str, int, float, bool)):
                value = json.dumps(value)
            return bool(self._redis_client.set(key, value, ex=ex))
        except (TypeError, RedisError) as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        if not self.is_connected() or not keys:
            return 0
        try:
            return self._redis_client.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return 0
    
    def clear_cache(self, pattern: str = '*') -> int:
        """Clear cache entries matching a pattern."""
        if not self.is_connected():
            return 0
        try:
            keys = self._redis_client.keys(pattern)
            if keys:
                return self._redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Redis clear_cache error: {e}")
            return 0

def cache_result(ttl: int = 300, key_prefix: str = "cache:"):
    """
    Decorator to cache the result of a function.
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            redis = RedisManager()
            if not redis.is_connected():
                return func(*args, **kwargs)
                
            # Create a unique cache key based on function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get cached result
            cached = redis.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
                
            # Call the function and cache the result
            result = func(*args, **kwargs)
            if result is not None:
                redis.set(cache_key, result, ex=ttl)
                
            return result
        return wrapper  # type: ignore
    return decorator

# Initialize the Redis manager when the module is imported
redis_manager = RedisManager()
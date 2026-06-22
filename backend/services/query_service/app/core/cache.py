import json
import logging
from typing import Optional, Any
import time

logger = logging.getLogger("query_service.cache")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class MemoryCache:
    """Fallback in-memory cache with TTL."""
    def __init__(self):
        self._store = {}

    def get(self, key: str) -> Optional[str]:
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if expiry is not None and time.time() > expiry:
            del self._store[key]
            return None
        return val

    def set(self, key: str, value: str, ttl: int = 300) -> None:
        expiry = time.time() + ttl if ttl else None
        self._store[key] = (value, expiry)

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

class ResultCache:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.fallback_cache = MemoryCache()
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.Redis.from_url(redis_url, socket_timeout=1.0)
                # Test connection
                self.redis_client.ping()
                logger.info("Successfully connected to Redis cache.")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis, falling back to in-memory cache. Error: {e}")
                self.redis_client = None
        else:
            logger.info("Redis not configured, using in-memory cache.")

    def get(self, key: str) -> Optional[Any]:
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data.decode("utf-8"))
            else:
                data = self.fallback_cache.get(key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        try:
            serialized = json.dumps(value)
            if self.redis_client:
                self.redis_client.set(key, serialized, ex=ttl)
            else:
                self.fallback_cache.set(key, serialized, ttl=ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

# Global cache instance
import os
redis_host = os.getenv("REDIS_HOST", "")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_url = f"redis://{redis_host}:{redis_port}/0" if redis_host else None
cache = ResultCache(redis_url)

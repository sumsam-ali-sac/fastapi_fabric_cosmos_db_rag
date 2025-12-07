"""
Caching layer abstraction for flexible cache implementation
"""

import hashlib
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, TypeVar

from azure.cosmos.exceptions import CosmosHttpResponseError

T = TypeVar("T")


class CacheBackend(ABC):
    """Abstract cache backend"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete from cache"""

    @abstractmethod
    async def clear(self) -> bool:
        """Clear entire cache"""


class CosmosDBCache(CacheBackend):
    """Cosmos DB implementation of cache backend"""

    def __init__(self, cache_service):
        self.cache_service = cache_service

    async def get(self, key: str) -> Optional[Any]:
        """Get from Cosmos DB cache"""
        try:
            item = await self.cache_service.get_item(key)
            return item
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set in Cosmos DB cache"""
        try:
            cache_item = {"id": key, "data": value}
            if ttl:
                cache_item["ttl"] = ttl
            await self.cache_service.upsert_item(cache_item)
            return True
        except CosmosHttpResponseError as e:
            if e.status_code == 409:
                raise ValueError("Cache key already exists") from e
            raise

    async def delete(self, key: str) -> bool:
        """Delete from cache"""
        try:
            await self.cache_service.delete_item(key)
            return True
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                return False
            raise

    async def clear(self) -> bool:
        """Clear cache - query and delete all"""
        try:
            query = "SELECT c.id FROM c"
            items = await self.cache_service.query_items(query)
            for item in items:
                await self.cache_service.delete_item(item["id"])
            return True
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                return False
            raise


class CacheKeyBuilder:
    """Helper to build consistent cache keys"""

    @staticmethod
    def build(prefix: str, *args, **kwargs) -> str:
        """Build cache key from components"""
        key_parts = [prefix] + list(args)

        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])

        key_string = ":".join(str(p) for p in key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


class CacheDecorator:
    """Decorator for caching function results"""

    def __init__(self, cache_backend: CacheBackend, ttl: Optional[int] = None):
        self.cache = cache_backend
        self.ttl = ttl

    def __call__(self, func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            cache_key = CacheKeyBuilder.build(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await self.cache.set(cache_key, result, self.ttl)
            return result

        return wrapper

"""
Repository implementations for data access layer
"""

import logging
from typing import Any, Dict, List, Optional

from azure.cosmos.exceptions import CosmosHttpResponseError

from config import Settings
from core.base import BaseRepository
from database.cosmos_service import CosmosService

logger = logging.getLogger(__name__)


class DocumentRepository(BaseRepository):
    """Repository for document operations"""

    def __init__(self, cosmos_service: CosmosService, settings: Settings):
        self.cosmos_service = cosmos_service
        self.settings = settings

    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            return await self.cosmos_service.get_item(item_id)
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to get document {item_id}: %s", str(e))
            return None

    async def get_all(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all documents with pagination"""
        try:
            query = "SELECT * FROM c OFFSET @skip LIMIT @limit"
            return await self.cosmos_service.query_items(
                query,
                [{"name": "@skip", "value": skip}, {"name": "@limit", "value": limit}],
            )
        except CosmosHttpResponseError as e:
            logger.error("Failed to get documents: %s", str(e))
            return []

    async def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create new document"""
        try:
            return await self.cosmos_service.upsert_item(item)
        except CosmosHttpResponseError as e:
            logger.error("Failed to create document: %s", str(e))
            raise

    async def update(self, item_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Update document"""
        try:
            item["id"] = item_id
            return await self.cosmos_service.upsert_item(item)
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to update document {item_id}: %s", str(e))
            raise

    async def delete(self, item_id: str) -> bool:
        """Delete document"""
        try:
            await self.cosmos_service.delete_item(item_id)
            return True
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to delete document {item_id}: %s", str(e))
            return False

    async def exists(self, item_id: str) -> bool:
        """Check if document exists"""
        try:
            item = await self.get_by_id(item_id)
            return item is not None
        except CosmosHttpResponseError:
            return False

    async def vector_search(
        self,
        embedding: List[float],
        similarity_score: float = None,
        num_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search documents by vector"""
        return await self.cosmos_service.vector_search(
            embedding, similarity_score, num_results
        )


class CacheRepository(BaseRepository):
    """Repository for cache operations"""

    def __init__(self, cosmos_service: CosmosService):
        self.cosmos_service = cosmos_service

    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get cache entry by ID"""
        try:
            return await self.cosmos_service.get_item(item_id)
        except CosmosHttpResponseError:
            return None

    async def get_all(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all cache entries"""
        query = "SELECT * FROM c OFFSET @skip LIMIT @limit"
        try:
            return await self.cosmos_service.query_items(
                query,
                [{"name": "@skip", "value": skip}, {"name": "@limit", "value": limit}],
            )
        except CosmosHttpResponseError as e:
            logger.error("Failed to get cache entries: %s", str(e))
            return []

    async def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create cache entry"""
        try:
            return await self.cosmos_service.upsert_item(item)
        except CosmosHttpResponseError as e:
            logger.error("Failed to create cache entry: %s", str(e))
            raise

    async def update(self, item_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Update cache entry"""
        item["id"] = item_id
        try:
            return await self.cosmos_service.upsert_item(item)
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to update cache entry {item_id}: %s", str(e))
            raise

    async def delete(self, item_id: str) -> bool:
        """Delete cache entry"""
        try:
            await self.cosmos_service.delete_item(item_id)
            return True
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to delete cache entry {item_id}: %s", str(e))
            return False

    async def exists(self, item_id: str) -> bool:
        """Check if cache entry exists"""
        item = await self.get_by_id(item_id)
        return item is not None

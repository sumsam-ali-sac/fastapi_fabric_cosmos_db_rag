"""
Enhanced Cosmos DB service for database operations
"""

import logging
from typing import Any, Dict, List

from azure.cosmos.aio import ContainerProxy

from config import Settings
from exceptions import DatabaseConnectionError, VectorSearchError

logger = logging.getLogger(__name__)


class CosmosService:
    """Service for Cosmos DB operations"""

    def __init__(self, container: ContainerProxy, settings: Settings):
        self.container = container
        self.settings = settings

    async def vector_search(
        self,
        embedding: List[float],
        similarity_score: float = None,
        num_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search in Cosmos DB

        Args:
            embedding: Vector embedding to search
            similarity_score: Minimum similarity threshold (uses settings default if None)
            num_results: Number of results to return

        Returns:
            List of search results with similarity scores
        """

        if similarity_score is None:
            similarity_score = self.settings.min_similarity_score

        try:
            query = f"""
            SELECT TOP @num_results 
                   c.overview ,
                   VectorDistance(c.{self.settings.cosmos_vector_property_name}, @embedding) AS similarity_score
            FROM c
            WHERE VectorDistance(c.{self.settings.cosmos_vector_property_name}, @embedding) > @similarity_score
            ORDER BY VectorDistance(c.{self.settings.cosmos_vector_property_name}, @embedding)
            """
            parameters = [
                {"name": "@embedding", "value": embedding},
                {"name": "@num_results", "value": num_results},
                {"name": "@similarity_score", "value": similarity_score},
            ]

            logger.info(
                "Executing vector search with similarity_score=%s, num_results=%s",
                similarity_score,
                num_results,
            )
            logger.debug("Query: %s", query)
            results_iterable = self.container.query_items(
                query=query,
                parameters=parameters,
            )
            results = [item async for item in results_iterable]
            formatted_results = [
                {"SimilarityScore": result.pop("SimilarityScore"), "document": result}
                for result in results
            ]
            logger.info("Vector search completed, found %d results", len(results))
            return formatted_results

        except Exception as e:
            logger.error("Vector search failed: %s", str(e))
            raise VectorSearchError(f"Vector search failed: {str(e)}") from e

    async def get_item(self, item_id: str, partition_key: str = None) -> Dict[str, Any]:
        """Get item by ID"""
        try:
            return await self.container.read_item(
                item=item_id, partition_key=partition_key or item_id
            )
        except Exception as e:
            logger.error("Failed to get item: %s", str(e))
            raise

    async def upsert_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert item into container"""
        try:
            return await self.container.upsert_item(item)
        except Exception as e:
            logger.error("Failed to upsert item: %s", str(e))
            raise DatabaseConnectionError(f"Upsert failed: {str(e)}") from e

    async def query_items(
        self, query: str, parameters: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute SQL query"""

        try:
            results = []
            async for item in self.container.query_items(
                query=query, parameters=parameters or []
            ):
                results.append(item)

            return results
        except Exception as e:
            logger.error("Query failed: %s", str(e))
            raise

    async def delete_item(self, item_id: str, partition_key: str = None) -> None:
        """Delete item from container"""
        try:
            await self.container.delete_item(
                item=item_id, partition_key=partition_key or item_id
            )
            logger.info("Deleted item: %s", item_id)
        except Exception as e:
            logger.error("Failed to delete item: %s", str(e))
            raise

    async def batch_upsert(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch upsert items"""
        results = []
        for item in items:
            try:
                result = await self.upsert_item(item)
                results.append(result)
            except (DatabaseConnectionError, VectorSearchError) as e:
                logger.error("Failed to upsert item %s: %s", item.get("id"), str(e))

        logger.info("Batch upserted %s items", len(results))
        return results

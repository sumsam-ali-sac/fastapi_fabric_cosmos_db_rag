"""
Chat service orchestrating chat operations with RAG + Caching
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from config import Settings
from database.cosmos_service import CosmosService
from services.base_chat_service import BaseChatService
from services.openai_service import CompletionService, OpenAIService

logger = logging.getLogger(__name__)


class ChatService(BaseChatService):
    """Orchestrates chat operations with RAG and semantic caching"""

    def __init__(
        self,
        vector_store_service: CosmosService,
        cache_service: CosmosService,
        embedding_service: OpenAIService,
        completion_service: CompletionService,
        settings: Settings,
    ):
        self.vector_store_service = vector_store_service
        self.cache_service = cache_service
        self.embedding_service = embedding_service
        self.completion_service = completion_service
        self.settings = settings

    async def get_cached_response(
        self, embedding: List[float]
    ) -> Optional[Dict[str, Any]]:
        """Check semantic cache for similar past queries"""
        try:
            results = await self.cache_service.vector_search(
                embedding=embedding,
                similarity_score=self.settings.cache_similarity_threshold,
                num_results=1,
            )

            if results:
                item = results[0]
                logger.info("Cache hit with similarity %0.4f", item["SimilarityScore"])
                # Reconstruct expected cached format
                cached_completion = {
                    "choices": [
                        {"message": {"content": item["document"]["completion"]}}
                    ],
                    "model": item["document"].get("model", "cached-model"),
                    "usage": {
                        "prompt_tokens": item["document"].get("prompt_tokens", 0),
                        "completion_tokens": item["document"].get(
                            "completion_tokens", 0
                        ),
                        "total_tokens": item["document"].get("total_tokens", 0),
                    },
                }
                return {
                    "completion_obj": cached_completion,
                    "sources": [],  # No sources in cache
                }
            return None

        except (ValueError, KeyError, AttributeError) as e:
            logger.warning("Cache lookup failed: %s", e)
            return None

    async def get_chat_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get recent chat history (for context injection)"""
        limit = limit or self.settings.chat_history_limit

        try:
            query = """
            SELECT TOP @limit c.prompt, c.completion
            FROM c
            ORDER BY c._ts DESC
            """
            items = await self.cache_service.query_items(
                query=query, parameters=[{"name": "@limit", "value": limit}]
            )
            # Format as alternating user/assistant messages
            history = []
            for item in reversed(items):  # oldest first
                history.append({"role": "user", "content": item["prompt"]})
                history.append({"role": "assistant", "content": item["completion"]})
            return history
        except (ValueError, KeyError, AttributeError) as e:
            logger.error("Failed to fetch chat history: %s", e)
            return []

    async def cache_response(
        self,
        prompt: str,
        embedding: List[float],
        completion: Dict[str, Any],
        sources: List[Dict[str, Any]],
    ) -> None:
        """Cache successful response for future semantic reuse"""
        try:
            content = completion["choices"][0]["message"]["content"]
            usage = completion.get("usage", {})

            cache_item = {
                "id": str(uuid.uuid4()),
                "prompt": prompt,
                "vector": embedding,
                "completion": content,
                "model": completion.get("model", "unknown"),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "sources_count": len(sources),
            }

            await self.cache_service.upsert_item(cache_item)

        except (ValueError, KeyError, AttributeError) as e:
            logger.error("Failed to cache response: %s", e)

    async def chat(
        self, message: str, use_cache: bool = True, num_results: int = 5
    ) -> Tuple[str, bool, List[Dict[str, Any]]]:
        """
        Main chat entrypoint with optional caching and RAG

        Returns:
            (response_text: str, from_cache: bool, sources: List[Dict])
        """

        embedding = await self.embedding_service.generate_embedding(message)

        if use_cache:
            cached = await self.get_cached_response(embedding)
            if cached:
                return (
                    cached["completion_obj"]["choices"][0]["message"]["content"],
                    True,
                    cached["sources"],
                )

        # Step 3: RAG + Generation
        response_text, sources = await self.generate_response(
            message, num_results, embedding
        )

        return response_text, False, sources

    async def generate_response(
        self,
        message: str,
        num_results: int,
        embedding: List[float],
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate fresh response using RAG"""

        search_results = await self.vector_store_service.vector_search(
            embedding=embedding,
            num_results=min(num_results, self.settings.max_search_results),
            similarity_score=self.settings.min_similarity_score,
        )

        # Extract clean documents
        documents = [
            {
                "content": doc["document"].get("text", "")
                or doc["document"].get("content", ""),
                "source": doc["document"].get("source", "unknown"),
                "similarity_score": doc["SimilarityScore"],
            }
            for doc in search_results
        ]

        # Get recent conversation history
        chat_history = await self.get_chat_history()

        # Generate completion
        completion = await self.completion_service.generate_completion(
            user_prompt=message,
            search_results=documents,
            chat_history=chat_history,
        )

        response_text = completion["choices"][0]["message"]["content"]

        # Cache for future use
        await self.cache_response(message, embedding, completion, search_results)

        return response_text, search_results

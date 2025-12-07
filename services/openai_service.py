"""
Azure OpenAI service for AI operations
"""

import logging
from typing import Any, Dict, List

from openai import AsyncAzureOpenAI

from config import Settings
from exceptions import CompletionError, EmbeddingGenerationError

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for Azure OpenAI operations"""

    def __init__(self, openai_client: AsyncAzureOpenAI, settings: Settings):
        self.client = openai_client
        self.settings = settings

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text

        Args:
            text: Text to embed

        Returns:
            Vector embedding
        """
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.settings.openai_embeddings_model,
                dimensions=self.settings.openai_embeddings_dimensions,
            )
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {str(e)}")


class CompletionService:
    """Service for generating completions"""

    def __init__(self, openai_client: AsyncAzureOpenAI, settings: Settings):
        self.client = openai_client
        self.settings = settings

    async def generate_completion(
        self,
        user_prompt: str,
        search_results: List[Dict[str, Any]],
        chat_history: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate completion with RAG context

        Args:
            user_prompt: User's input message
            search_results: Retrieved documents from vector search
            chat_history: Previous chat messages for context

        Returns:
            Completion response from OpenAI
        """
        try:
            system_prompt = """
            You are an intelligent assistant for movies. You are designed to provide helpful answers 
            to user questions about movies in your database.
            - Only answer questions related to the information provided
            - Provide at least 3 candidate movie answers in a list
            - Be concise but friendly
            - Write two lines of whitespace between each answer in the list
            """

            messages = [{"role": "system", "content": system_prompt}]

            # Add chat history
            if chat_history:
                for chat in chat_history:
                    messages.append(
                        {
                            "role": "user",
                            "content": f"{chat.get('prompt', '')} {chat.get('completion', '')}",
                        }
                    )

            # Add user prompt
            messages.append({"role": "user", "content": user_prompt})

            # Add context from search results
            if search_results:
                context = "\n\n".join(
                    [f"Document: {str(result)}" for result in search_results]
                )
                messages.append({"role": "system", "content": f"Context:\n{context}"})

            response = await self.client.chat.completions.create(
                model=self.settings.openai_completions_model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
            )

            logger.info(
                f"Generated completion with {response.usage.total_tokens} tokens"
            )
            return response.model_dump()

        except Exception as e:
            logger.error(f"Completion generation failed: {e}")
            raise CompletionError(f"Failed to generate completion: {str(e)}")

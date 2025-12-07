"""
Restructured routes for API versioning support
FastAPI routes organized by version
"""

from fastapi import APIRouter, Depends, HTTPException

from config import Settings
from core.logger import get_logger
from database.cosmos_service import CosmosService
from dependencies import (
    CosmosDBClient,
    OpenAIClients,
    get_cosmos_client,
    get_openai_clients,
    get_settings_dep,
)
from exceptions import ApplicationError
from models import ChatRequest, ChatResponse
from services.chat_service import ChatService
from services.openai_service import CompletionService, OpenAIService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(
    request: ChatRequest,
    cosmos_client: CosmosDBClient = Depends(get_cosmos_client),
    openai_clients: OpenAIClients = Depends(get_openai_clients),
    settings: Settings = Depends(get_settings_dep),
):
    """
    Send a chat message and get movie recommendations

    Args:
        message: Your question about movies
        use_cache: Whether to use cached responses (default: true)
        num_results: Number of movie results (1-20, default: 5)

    Returns:
        - response: Assistant's response
        - from_cache: Whether response was cached
        - sources: Retrieved source documents
    """
    try:
        vector_store = CosmosService(cosmos_client.movies_container, settings)
        logger.info("Connected to Cosmos DB vector store container")
        cache_service = CosmosService(cosmos_client.cache_container, settings)
        logger.info("Connected to Cosmos DB cache container")
        embedding_service = OpenAIService(openai_clients.embeddings_client, settings)
        logger.info("Initialized OpenAI embedding service")
        completion_service = CompletionService(
            openai_clients.completions_client, settings
        )
        logger.info("Initialized OpenAI completion service")

        chat_service = ChatService(
            vector_store, cache_service, embedding_service, completion_service, settings
        )
        logger.info("Initialized chat service")

        response_text, from_cache, sources = await chat_service.chat(
            message=request.message,
            use_cache=request.use_cache,
            num_results=request.num_results,
        )

        return ChatResponse(
            response=response_text,
            from_cache=from_cache,
            sources=sources if sources else None,
        )

    except ApplicationError as e:
        logger.error("Application error: %s", e.message)
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error("Unexpected error in chat endpoint: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error") from e

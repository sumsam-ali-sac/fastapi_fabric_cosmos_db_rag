"""
Service tests
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from config import Settings
from database.cosmos_service import CosmosService
from services.chat_service import ChatService


@pytest.fixture
def mock_settings():
    """Mock settings"""
    settings = MagicMock(spec=Settings)
    settings.min_similarity_score = 0.02
    settings.cache_similarity_threshold = 0.99
    settings.max_search_results = 20
    settings.chat_history_limit = 3
    return settings


@pytest.fixture
def mock_cosmos_service():
    """Mock Cosmos service"""
    return AsyncMock(spec=CosmosService)


@pytest.mark.asyncio
async def test_chat_service_initialization(mock_cosmos_service, mock_settings):
    """Test ChatService initialization"""
    embedding_service = AsyncMock()
    completion_service = AsyncMock()

    service = ChatService(
        mock_cosmos_service,
        mock_cosmos_service,
        embedding_service,
        completion_service,
        mock_settings,
    )

    assert service.vector_store_service is not None
    assert service.embedding_service is not None


@pytest.mark.asyncio
async def test_get_cached_response_not_found(mock_cosmos_service, mock_settings):
    """Test cache lookup when not found"""
    embedding_service = AsyncMock()
    completion_service = AsyncMock()

    mock_cosmos_service.vector_search = AsyncMock(return_value=[])

    service = ChatService(
        mock_cosmos_service,
        mock_cosmos_service,
        embedding_service,
        completion_service,
        mock_settings,
    )

    result = await service.get_cached_response([0.1] * 1536)
    assert result is None

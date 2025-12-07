"""
Pytest configuration and fixtures
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_cosmos_client():
    """Mock Cosmos DB client"""
    mock = AsyncMock()
    mock.is_connected = True
    mock.health_check = AsyncMock(return_value={"movies": True, "cache": True})
    return mock


@pytest.fixture
def mock_openai_clients():
    """Mock OpenAI clients"""
    mock = MagicMock()
    mock.completions_client = AsyncMock()
    mock.embeddings_client = AsyncMock()
    return mock


@pytest.fixture
def mock_embedding():
    """Mock embedding vector"""
    return [0.1] * 1536

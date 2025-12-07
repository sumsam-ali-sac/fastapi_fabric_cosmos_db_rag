"""
Endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.mark.asyncio
async def test_root():
    """Test root endpoint"""
    client = TestClient(app)
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Cosmos DB RAG Chat API" in response.json()["message"]


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "containers" in data


def test_chat_invalid_message():
    """Test chat with invalid message"""
    client = TestClient(app)
    response = client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == 422  # Validation error


def test_chat_missing_required_field():
    """Test chat with missing field"""
    client = TestClient(app)
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422

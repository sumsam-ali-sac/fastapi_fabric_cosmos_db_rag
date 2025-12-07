"""
Routes for API versioning support
FastAPI routes organized by version
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from core.logger import get_logger
from dependencies import (
    CosmosDBClient,
    get_cosmos_client,
)
from models import HealthResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Cosmos DB RAG Chat API - v1",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat - Send a chat message",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation",
        },
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(cosmos_client: CosmosDBClient = Depends(get_cosmos_client)):
    """
    Check API and database health

    Returns:
        - status: Overall health status
        - database: Database name
        - containers: Container connectivity status
    """
    try:
        container_status = await cosmos_client.health_check()

        all_healthy = all(container_status.values())
        status = (
            "healthy"
            if all_healthy
            else ("degraded" if any(container_status.values()) else "unhealthy")
        )

        return HealthResponse(
            status=status,
            database=cosmos_client.settings.cosmos_database_name,
            containers=container_status,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(
            status_code=503, detail={"error": "Service unhealthy", "detail": str(e)}
        ) from e

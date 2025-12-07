"""
FastAPI application entry point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.chat_router import router as chat_router
from api.v1.health_router import router as health_router
from config import get_settings
from core.logger import get_logger
from core.middleware import (
    ErrorHandlingMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from dependencies import get_cosmos_client, get_openai_clients

# Configure logging
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    logger.info("Starting up FastAPI application...")
    # Initialize clients on startup
    cosmos_client = await get_cosmos_client()
    openai_clients = await get_openai_clients()  # noqa: F841

    logger.info("Application startup complete")

    yield

    logger.info("Shutting down FastAPI application...")
    if cosmos_client:
        await cosmos_client.close()

    logger.info("Application shutdown complete")


# Create FastAPI app
settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description="FastAPI application for Fabric Cosmos DB with RAG and vector search",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add custom middleware for enhanced request tracking and logging
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


app.include_router(health_router)
app.include_router(chat_router)

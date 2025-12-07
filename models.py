"""
Enhanced Pydantic models with better structure and validation
Pydantic models for request/response validation
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    message: str = Field(
        ..., min_length=1, max_length=5000, description="User's chat message"
    )
    use_cache: bool = Field(default=True, description="Whether to use cached responses")
    num_results: int = Field(
        default=5, ge=1, le=20, description="Number of search results"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""

    response: str = Field(description="Assistant's response")
    from_cache: bool = Field(description="Whether response was from cache")
    sources: Optional[List[Dict]] = Field(
        default=None, description="Retrieved source documents"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""

    status: str = Field(description="Health status: healthy, degraded, or unhealthy")
    database: str = Field(description="Database name")
    containers: Dict[str, bool] = Field(description="Container connectivity status")
    timestamp: str = Field(description="Health check timestamp")


class ErrorResponse(BaseModel):
    """Response model for error responses"""

    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")
    request_id: Optional[str] = Field(
        default=None, description="Request ID for tracking"
    )


class Document(BaseModel):
    """Document model for database items"""

    id: str = Field(description="Document ID")
    vector: List[float] = Field(description="Vector embedding")
    similarity_score: Optional[float] = Field(
        default=None, description="Similarity score"
    )


class CacheItem(BaseModel):
    """Cache item model"""

    id: str = Field(description="Cache entry ID")
    prompt: str = Field(description="Original prompt")
    completion: str = Field(description="Completion response")
    vector: List[float] = Field(description="Prompt vector")
    model: str = Field(description="Model used")
    prompt_tokens: int = Field(description="Prompt tokens used")
    completion_tokens: int = Field(description="Completion tokens used")
    total_tokens: int = Field(description="Total tokens used")


class PaginationParams(BaseModel):
    """Pagination parameters"""

    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items per page")


class SortOrder(str, Enum):
    """Sort order enum"""

    ASC = "asc"
    DESC = "desc"


class DocumentQueryParams(BaseModel):
    """Parameters for document queries"""

    search: Optional[str] = Field(None, max_length=500, description="Search term")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: SortOrder = Field(default=SortOrder.ASC)

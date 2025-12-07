"""
Query filtering and search abstractions
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SortOrder(str, Enum):
    """Sort order enum"""

    ASC = "asc"
    DESC = "desc"


class FilterParams(BaseModel):
    """Base filter parameters"""

    search: Optional[str] = Field(None, description="Search query")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: SortOrder = Field(default=SortOrder.ASC, description="Sort order")


class VectorSearchParams(FilterParams):
    """Parameters for vector search"""

    min_similarity: float = Field(default=0.02, ge=0.0, le=1.0)
    max_results: int = Field(default=5, ge=1, le=100)

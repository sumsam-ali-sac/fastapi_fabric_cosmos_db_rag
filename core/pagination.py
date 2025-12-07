"""
Pagination utilities for list endpoints
"""

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters"""

    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(
        default=10, ge=1, le=100, description="Number of items to return"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Number of items returned")

    @property
    def total_pages(self) -> int:
        """Calculate total pages"""
        return (self.total + self.limit - 1) // self.limit

    @property
    def has_more(self) -> bool:
        """Check if there are more items"""
        return (self.skip + self.limit) < self.total

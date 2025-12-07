"""
Base classes and abstract interfaces for repository pattern
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for data access layer"""

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[T]:
        """Get item by ID"""

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
        """Get all items with pagination"""

    @abstractmethod
    async def create(self, item: T) -> T:
        """Create new item"""

    @abstractmethod
    async def update(self, item_id: str, item: T) -> T:
        """Update existing item"""

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete item"""

    @abstractmethod
    async def exists(self, item_id: str) -> bool:
        """Check if item exists"""


class BaseService(ABC, Generic[T]):
    """Abstract base service for business logic"""

    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute service operation"""

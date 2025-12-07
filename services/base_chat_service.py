"""
Base chat service with extensible architecture
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class BaseChatService(ABC):
    """Abstract base for chat services"""

    @abstractmethod
    async def get_cached_response(
        self, embedding: List[float]
    ) -> Dict[str, Any] | None:
        """Get cached response"""

    @abstractmethod
    async def generate_response(
        self, message: str, num_results: int, embedding: List[float]
    ) -> Tuple[str, List]:
        """Generate response"""

    @abstractmethod
    async def chat(
        self, message: str, use_cache: bool, num_results: int
    ) -> Tuple[str, bool, List]:
        """Execute chat operation"""

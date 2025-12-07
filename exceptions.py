"""
Enhanced custom exception definitions with better hierarchy and context
"""

from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(str, Enum):
    """Error code enum for consistency"""

    DB_CONNECTION_FAILED = "DB_CONNECTION_FAILED"
    EMBEDDING_FAILED = "EMBEDDING_FAILED"
    VECTOR_SEARCH_FAILED = "VECTOR_SEARCH_FAILED"
    COMPLETION_FAILED = "COMPLETION_FAILED"
    INVALID_REQUEST = "INVALID_REQUEST"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ApplicationError(Exception):
    """Base application exception with error codes and context"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": self.message,
            "error_code": self.error_code.value,
            "status_code": self.status_code,
            "context": self.context if self.context else None,
        }


class DatabaseConnectionError(ApplicationError):
    """Database connection error"""

    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message,
            status_code=503,
            error_code=ErrorCode.DB_CONNECTION_FAILED,
            context=context,
        )


class EmbeddingGenerationError(ApplicationError):
    """Embedding generation error"""

    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message,
            status_code=500,
            error_code=ErrorCode.EMBEDDING_FAILED,
            context=context,
        )


class VectorSearchError(ApplicationError):
    """Vector search error"""

    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message,
            status_code=500,
            error_code=ErrorCode.VECTOR_SEARCH_FAILED,
            context=context,
        )


class CompletionError(ApplicationError):
    """Completion generation error"""

    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message,
            status_code=500,
            error_code=ErrorCode.COMPLETION_FAILED,
            context=context,
        )


class InvalidRequestError(ApplicationError):
    """Invalid request error"""

    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message,
            status_code=400,
            error_code=ErrorCode.INVALID_REQUEST,
            context=context,
        )


class ResourceNotFoundError(ApplicationError):
    """Resource not found error"""

    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(
            message,
            status_code=404,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            context=context,
        )


class RateLimitExceededError(ApplicationError):
    """Rate limit exceeded error"""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        context: Optional[Dict] = None,
    ):
        super().__init__(
            message,
            status_code=429,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            context={**(context or {}), "retry_after": retry_after},
        )

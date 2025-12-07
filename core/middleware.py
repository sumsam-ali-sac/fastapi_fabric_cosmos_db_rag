"""
Custom middleware for logging, error handling, and request tracking
"""

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.logger import RequestLogger, get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests"""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request and response details"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.state.request_id
        req_logger = RequestLogger(request_id, logger)

        # Log request
        req_logger.log_request(request.method, request.url.path)

        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            req_logger.log_response(response.status_code, duration_ms)
            return response
        except Exception as exc:
            req_logger.log_error(exc)
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except (ValueError, TypeError, KeyError, AttributeError, LookupError) as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                "Unhandled exception: %s",
                str(exc),
                extra={"request_id": request_id},
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "request_id": request_id},
            )

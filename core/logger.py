"""
Centralized logging configuration and utilities
"""

import json
import logging
import sys
from datetime import datetime
from typing import Dict, Optional


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class RequestLogger:
    """Logger for request/response tracking"""

    def __init__(self, request_id: str, logger: logging.Logger):
        self.request_id = request_id
        self.logger = logger

    def log_request(self, method: str, path: str, params: Optional[Dict] = None):
        """Log incoming request"""
        self.logger.info(
            f"Request {self.request_id} started",
            extra={
                "request_id": self.request_id,
                "method": method,
                "path": path,
                "params": params,
            },
        )

    def log_response(self, status_code: int, duration_ms: float):
        """Log outgoing response"""
        self.logger.info(
            f"Request {self.request_id} completed",
            extra={
                "request_id": self.request_id,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )

    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log error with context"""
        self.logger.error(
            f"Request {self.request_id} error: {str(error)}",
            extra={
                "request_id": self.request_id,
                "error_type": type(error).__name__,
                "context": context,
            },
            exc_info=True,
        )

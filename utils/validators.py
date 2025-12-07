"""
Input validation utilities and validators
"""

import re
from typing import List

from exceptions import InvalidRequestError


class InputValidator:
    """Utility class for input validation"""

    @staticmethod
    def validate_message(
        message: str, min_length: int = 1, max_length: int = 5000
    ) -> str:
        """Validate user message"""
        if not message or not message.strip():
            raise InvalidRequestError("Message cannot be empty")

        message = message.strip()

        if len(message) < min_length:
            raise InvalidRequestError(
                f"Message must be at least {min_length} characters"
            )

        if len(message) > max_length:
            raise InvalidRequestError(f"Message cannot exceed {max_length} characters")

        return message

    @staticmethod
    def validate_embedding(
        embedding: List[float], expected_dimension: int
    ) -> List[float]:
        """Validate embedding vector"""
        if not isinstance(embedding, list):
            raise InvalidRequestError("Embedding must be a list")

        if len(embedding) != expected_dimension:
            raise InvalidRequestError(
                f"Embedding dimension mismatch. Expected {expected_dimension}, got {len(embedding)}"
            )
        if not all(isinstance(x, (int, float)) for x in embedding):
            raise InvalidRequestError("Embedding must contain only numeric values")
        return embedding

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise InvalidRequestError("Invalid email format")
        return email.lower()

    @staticmethod
    def validate_number_in_range(
        value: int, min_val: int, max_val: int, field_name: str
    ) -> int:
        """Validate number is within range"""
        if not min_val <= value <= max_val:
            raise InvalidRequestError(
                f"{field_name} must be between {min_val} and {max_val}"
            )
        return value


class PaginationValidator:
    """Utility for pagination validation"""

    @staticmethod
    def validate_pagination(skip: int, limit: int, max_limit: int = 100) -> tuple:
        """Validate pagination parameters"""
        if skip < 0:
            raise InvalidRequestError("skip must be >= 0")

        if limit < 1 or limit > max_limit:
            raise InvalidRequestError(f"limit must be between 1 and {max_limit}")

        return skip, limit

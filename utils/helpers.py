"""
Helper functions and utilities
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class IDGenerator:
    """Generate consistent IDs"""

    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID"""
        return str(uuid.uuid4())

    @staticmethod
    def generate_request_id() -> str:
        """Generate request ID"""
        return f"req_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_trace_id() -> str:
        """Generate trace ID for distributed tracing"""
        return f"trace_{uuid.uuid4().hex[:16]}"


class DictHelper:
    """Dictionary helper functions"""

    @staticmethod
    def deep_get(dictionary: Dict, *keys, default: Any = None) -> Any:
        """Get nested dictionary value safely"""
        current = dictionary
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    @staticmethod
    def safe_merge(*dicts: Dict) -> Dict:
        """Safely merge multiple dictionaries"""
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result

    @staticmethod
    def filter_none(dictionary: Dict) -> Dict:
        """Remove None values from dictionary"""
        return {k: v for k, v in dictionary.items() if v is not None}


class DateTimeHelper:
    """DateTime helper functions"""

    @staticmethod
    def get_utc_now() -> datetime:
        """Get current UTC datetime"""
        return datetime.utcnow()

    @staticmethod
    def to_iso_string(dt: Optional[datetime] = None) -> str:
        """Convert datetime to ISO format string"""
        dt = dt or datetime.utcnow()
        return dt.isoformat()

    @staticmethod
    def from_iso_string(iso_string: str) -> datetime:
        """Parse ISO format string to datetime"""
        return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))

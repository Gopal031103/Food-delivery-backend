"""Utility functions for validation and common operations."""
import logging
import re
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationUtils:
    """Validation utility functions."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', phone)
        # Check if it has at least 10 digits
        return len(phone_digits) >= 10
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Returns: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if not any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/~`" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, None


class DataUtils:
    """Data utility functions."""
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Sanitize string input by removing leading/trailing spaces."""
        if isinstance(text, str):
            return text.strip()
        return text
    
    @staticmethod
    def format_currency(amount: float, currency: str = "$") -> str:
        """Format amount as currency."""
        return f"{currency}{amount:.2f}"
    
    @staticmethod
    def get_current_timestamp() -> datetime:
        """Get current UTC timestamp."""
        return datetime.utcnow()


class ResponseUtils:
    """Utility functions for response formatting."""
    
    @staticmethod
    def success_response(data: any, message: str = "Success") -> dict:
        """Format success response."""
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": DataUtils.get_current_timestamp()
        }
    
    @staticmethod
    def error_response(
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ) -> dict:
        """Format error response."""
        response = {
            "success": False,
            "message": message,
            "status_code": status_code,
            "timestamp": DataUtils.get_current_timestamp()
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response


class PaginationUtils:
    """Utility functions for pagination."""
    
    @staticmethod
    def get_pagination_params(skip: int = 0, limit: int = 10) -> tuple[int, int]:
        """
        Get validated pagination parameters.
        
        Args:
            skip: Number of records to skip (default 0)
            limit: Number of records to return (default 10, max 100)
        
        Returns:
            Tuple of (skip, limit)
        """
        skip = max(0, skip)
        limit = min(100, max(1, limit))
        return skip, limit
    
    @staticmethod
    def create_pagination_response(
        items: list,
        total: int,
        skip: int,
        limit: int
    ) -> dict:
        """Create paginated response."""
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "current_page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_previous": current_page > 1
        }

"""Custom exceptions and exception handlers."""
import logging
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class APIException(HTTPException):
    """Base API exception."""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.timestamp = datetime.utcnow()


class ValidationException(APIException):
    """Raised when validation fails."""
    
    def __init__(
        self,
        detail: str,
        error_code: str = "VALIDATION_ERROR",
        headers: Optional[dict] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code,
            headers=headers
        )


class ResourceNotFoundException(APIException):
    """Raised when a resource is not found."""
    
    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        headers: Optional[dict] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            headers=headers
        )


class UnauthorizedException(APIException):
    """Raised when user is not authenticated."""
    
    def __init__(
        self,
        detail: str = "Authentication required",
        error_code: str = "UNAUTHORIZED",
        headers: Optional[dict] = None
    ):
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            headers=headers
        )


class ForbiddenException(APIException):
    """Raised when user doesn't have permission."""
    
    def __init__(
        self,
        detail: str = "Access denied",
        error_code: str = "FORBIDDEN",
        headers: Optional[dict] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            headers=headers
        )


class DuplicateResourceException(APIException):
    """Raised when trying to create a duplicate resource."""
    
    def __init__(
        self,
        detail: str = "Resource already exists",
        error_code: str = "DUPLICATE_RESOURCE",
        headers: Optional[dict] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_code=error_code,
            headers=headers
        )


class DatabaseException(APIException):
    """Raised when database operation fails."""
    
    def __init__(
        self,
        detail: str = "Database operation failed",
        error_code: str = "DATABASE_ERROR",
        headers: Optional[dict] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            headers=headers
        )
        logger.error(f"Database error: {detail}")


class InternalServerException(APIException):
    """Raised for internal server errors."""
    
    def __init__(
        self,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR",
        headers: Optional[dict] = None
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            headers=headers
        )
        logger.error(f"Internal error: {detail}")

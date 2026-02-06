"""
Custom Exception Classes

Centralized exception handling for the application.

Interview Insight:
Custom exceptions provide:
1. Clear error categorization
2. Consistent error responses
3. Easier debugging (stack traces show specific exception type)
4. Clean separation between HTTP layer and business logic
"""

from typing import Any


class InsightForgeException(Exception):
    """
    Base exception for all InsightForge errors.
    
    All custom exceptions inherit from this, allowing:
    - Catch all app errors with: except InsightForgeException
    - Add common functionality (logging, metrics) in one place
    """
    
    def __init__(
        self,
        message: str = "An error occurred",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# ============================================================
# Authentication & Authorization Exceptions
# ============================================================

class AuthenticationError(InsightForgeException):
    """User is not authenticated (401)."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Email or password is incorrect."""
    
    def __init__(self):
        super().__init__(message="Invalid email or password")


class TokenExpiredError(AuthenticationError):
    """JWT token has expired."""
    
    def __init__(self):
        super().__init__(message="Token has expired")


class InvalidTokenError(AuthenticationError):
    """JWT token is invalid or malformed."""
    
    def __init__(self):
        super().__init__(message="Invalid token")


class AuthorizationError(InsightForgeException):
    """User is authenticated but not authorized (403)."""
    
    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(message=message)


# ============================================================
# Resource Exceptions
# ============================================================

class NotFoundError(InsightForgeException):
    """Requested resource was not found (404)."""
    
    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message=message, details={"resource": resource})


class AlreadyExistsError(InsightForgeException):
    """Resource already exists (409 Conflict)."""
    
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            details={"resource": resource, "field": field},
        )


# ============================================================
# Validation Exceptions
# ============================================================

class ValidationError(InsightForgeException):
    """Input validation failed (422)."""
    
    def __init__(self, message: str, field: str | None = None):
        details = {"field": field} if field else {}
        super().__init__(message=message, details=details)


# ============================================================
# Business Logic Exceptions
# ============================================================

class UsageLimitExceededError(InsightForgeException):
    """Organization has exceeded usage limits."""
    
    def __init__(self, limit_type: str, current: int, maximum: int):
        super().__init__(
            message=f"Usage limit exceeded for {limit_type}",
            details={
                "limit_type": limit_type,
                "current": current,
                "maximum": maximum,
            },
        )


class OrganizationLimitError(UsageLimitExceededError):
    """Specific limit errors for organization resources."""
    pass

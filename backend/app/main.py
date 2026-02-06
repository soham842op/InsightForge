"""
FastAPI Application Entry Point

This is where everything comes together.

Interview Insight:
- Application factory pattern (create_app) enables testing with different configs
- Exception handlers convert our custom exceptions to HTTP responses
- Middleware adds cross-cutting concerns (CORS, logging, etc.)
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InsightForgeException,
    NotFoundError,
    ValidationError,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    This is the modern way to handle startup/shutdown events in FastAPI.
    
    Use cases:
    - Initialize database connection pools
    - Load ML models into memory
    - Set up background task queues
    - Clean up resources on shutdown
    """
    # Startup
    print(f"Starting {settings.app_name}...")
    # TODO: Initialize database, Redis, etc.
    
    yield  # Application runs here
    
    # Shutdown
    print(f"Shutting down {settings.app_name}...")
    # TODO: Close connections, flush queues


def create_app() -> FastAPI:
    """
    Application factory.
    
    Best Practice:
    Using a factory function instead of a global app object allows:
    - Different configurations for testing
    - Multiple app instances if needed
    - Cleaner dependency management
    """
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered analytics platform for business and data teams",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.debug else None,  # Disable docs in prod
        redoc_url="/api/redoc" if settings.debug else None,
    )
    
    # Configure CORS
    # Interview Insight: CORS is crucial for web security
    # It prevents malicious sites from making requests to your API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js dev server
            # Add production frontend URL here
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Register routes
    # TODO: Add routers as we build them
    # app.include_router(auth_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint.
        
        Best Practice:
        Every production service needs a health check endpoint for:
        - Load balancer health checks
        - Kubernetes liveness/readiness probes
        - Monitoring systems
        """
        return {
            "status": "healthy",
            "service": settings.app_name,
            "environment": settings.environment,
        }
    
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers to convert exceptions to HTTP responses.
    
    Interview Insight:
    This pattern centralizes error handling, ensuring:
    - Consistent error response format
    - No leaking of internal error details to clients
    - Proper HTTP status codes
    """
    
    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": exc.message, "type": "authentication_error"},
        )
    
    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(
        request: Request, exc: AuthorizationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": exc.message, "type": "authorization_error"},
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": exc.message,
                "type": "not_found",
                "details": exc.details,
            },
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": exc.message,
                "type": "validation_error",
                "details": exc.details,
            },
        )
    
    @app.exception_handler(InsightForgeException)
    async def general_error_handler(
        request: Request, exc: InsightForgeException
    ) -> JSONResponse:
        """Catch-all for any InsightForge exception not handled above."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.message, "type": "server_error"},
        )


# Create the app instance
app = create_app()

"""
Wesza API - AI-powered no-code mobile app platform.

This module initializes the FastAPI application with middleware,
routing, and lifecycle management.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.api.v1 import auth, apps, ai
from app.database import init_db

# Configure structured logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown logic.
    
    Yields:
        None: Yields control back to FastAPI after initialization.
    """
    # Startup
    logger.info("Starting Wesza API", version=settings.VERSION)
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Wesza API")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    Returns:
        FastAPI: Configured FastAPI application.
    """
    application = FastAPI(
        title="Wesza API",
        description="AI-powered no-code mobile app platform that generates offline-capable PWAs",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    application.include_router(apps.router, prefix="/api/v1/apps", tags=["Applications"])
    application.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])

    # Exception handlers
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with structured logging."""
        logger.warning(
            "Validation error",
            path=request.url.path,
            errors=exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @application.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with structured logging."""
        logger.error(
            "Unexpected error",
            path=request.url.path,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    return application


# Create the application instance
app = create_application()


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Status and version information.
    """
    logger.debug("Health check requested")
    return {"status": "ok", "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENV == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )

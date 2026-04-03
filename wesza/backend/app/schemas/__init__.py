"""Pydantic schemas for request/response validation."""

from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    TokenData,
)
from app.schemas.app import (
    AppCreate,
    AppResponse,
    AppUpdate,
    AppListResponse,
)
from app.schemas.ai import (
    PromptRequest,
    TemplateResponse,
    CodeGenerationRequest,
    CodeGenerationResponse,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "RegisterResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenData",
    # App
    "AppCreate",
    "AppResponse",
    "AppUpdate",
    "AppListResponse",
    # AI
    "PromptRequest",
    "TemplateResponse",
    "CodeGenerationRequest",
    "CodeGenerationResponse",
]

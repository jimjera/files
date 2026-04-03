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
from app.schemas.template import (
    TemplateCreate,
    TemplateResponse as TemplateSchemaResponse,
    TemplateUpdate,
    TemplateListResponse,
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
    # Template
    "TemplateCreate",
    "TemplateSchemaResponse",
    "TemplateUpdate",
    "TemplateListResponse",
    # AI
    "PromptRequest",
    "TemplateResponse",
    "CodeGenerationRequest",
    "CodeGenerationResponse",
]

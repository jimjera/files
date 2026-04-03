"""
AI orchestration schemas for request/response validation.

This module defines Pydantic models for AI prompt processing,
template generation, and code generation with proper validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    """
    Request schema for AI prompt processing.
    
    Attributes:
        prompt: Natural language description of desired app.
        modules: Optional list of specific modules to include.
        offline_enabled: Whether to enable offline mode.
    """
    
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=4000,
        description="Natural language app description",
    )
    modules: Optional[List[str]] = Field(
        default=None,
        description="Specific modules to include",
    )
    offline_enabled: bool = Field(
        default=True,
        description="Enable offline mode",
    )


class TemplateResponse(BaseModel):
    """
    Response schema for template generation.
    
    Attributes:
        template_id: Generated template UUID.
        vertical: Detected industry/use case.
        config_json: Generated configuration schema.
        confidence: AI confidence score (0-1).
        message: Status message.
    """
    
    template_id: Optional[str] = Field(None, description="Template UUID")
    vertical: str = Field(..., description="Detected vertical")
    config_json: Dict[str, Any] = Field(..., description="Generated config")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    message: str = Field(default="Template generated successfully")


class CodeGenerationRequest(BaseModel):
    """
    Request schema for code generation.
    
    Attributes:
        config_json: Template configuration JSON.
        complexity: App complexity level (simple, complex).
        include_offline: Whether to include service worker.
    """
    
    config_json: Dict[str, Any] = Field(..., description="Template configuration")
    complexity: str = Field(
        default="simple",
        pattern="^(simple|complex)$",
        description="App complexity level",
    )
    include_offline: bool = Field(
        default=True,
        description="Include service worker for offline support",
    )


class CodeGenerationResponse(BaseModel):
    """
    Response schema for code generation.
    
    Attributes:
        files: Dictionary of generated files (filename: content).
        service_worker: Service worker code if included.
        deploy_url: Public URL after deployment.
        generation_time_ms: Time taken to generate code.
    """
    
    files: Dict[str, str] = Field(..., description="Generated files")
    service_worker: Optional[str] = Field(None, description="Service worker code")
    deploy_url: Optional[str] = Field(None, description="Public deployment URL")
    generation_time_ms: int = Field(..., description="Generation time in ms")


class IntentClassificationResponse(BaseModel):
    """
    Response schema for intent classification.
    
    Attributes:
        vertical: Detected industry/use case category.
        use_case: Specific use case description.
        modules: Recommended modules for this intent.
        confidence: AI confidence score (0-1).
    """
    
    vertical: str = Field(..., description="Industry category")
    use_case: str = Field(..., description="Specific use case")
    modules: List[str] = Field(..., description="Recommended modules")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

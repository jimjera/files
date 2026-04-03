"""
Template schemas for request/response validation.

This module defines Pydantic models for template creation, retrieval,
and management with proper validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    """
    Request schema for creating a new template.

    Attributes:
        name: Template name.
        vertical: Industry/use case category.
        description: Optional template description.
        schema_json: JSON schema defining template structure.
        prompt_template: Optional example prompt.
        is_active: Whether template is available for use.
    """

    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    vertical: str = Field(..., min_length=1, max_length=100, description="Industry category")
    description: Optional[str] = Field(None, description="Template description")
    schema_json: Dict[str, Any] = Field(..., description="JSON schema for template")
    prompt_template: Optional[str] = Field(None, description="Example prompt")
    is_active: bool = Field(default=True, description="Whether template is active")


class TemplateResponse(BaseModel):
    """
    Response schema for template operations.

    Attributes:
        id: Template UUID.
        name: Template name.
        vertical: Industry/use case category.
        description: Template description.
        schema_json: JSON schema.
        prompt_template: Example prompt.
        is_active: Whether template is active.
        created_at: Creation timestamp.
    """

    id: str = Field(..., description="Template UUID")
    name: str = Field(..., description="Template name")
    vertical: str = Field(..., description="Industry category")
    description: Optional[str] = Field(None, description="Template description")
    schema_json: Dict[str, Any] = Field(..., description="JSON schema")
    prompt_template: Optional[str] = Field(None, description="Example prompt")
    is_active: bool = Field(..., description="Whether template is active")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class TemplateUpdate(BaseModel):
    """
    Request schema for updating a template.

    Attributes:
        name: Optional new template name.
        vertical: Optional updated category.
        description: Optional updated description.
        schema_json: Optional updated schema.
        prompt_template: Optional updated prompt.
        is_active: Optional active status toggle.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New template name",
    )
    vertical: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated industry category",
    )
    description: Optional[str] = Field(None, description="Updated description")
    schema_json: Optional[Dict[str, Any]] = Field(None, description="Updated schema")
    prompt_template: Optional[str] = Field(None, description="Updated prompt")
    is_active: Optional[bool] = Field(None, description="Active status")


class TemplateListResponse(BaseModel):
    """
    Response schema for listing templates.

    Attributes:
        templates: List of template responses.
        total: Total number of templates.
    """

    templates: List[TemplateResponse] = Field(..., description="List of templates")
    total: int = Field(..., description="Total count")

"""
Application schemas for request/response validation.

This module defines Pydantic models for app creation, retrieval,
and management with proper validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AppCreate(BaseModel):
    """
    Request schema for creating a new app.
    
    Attributes:
        name: Application name.
        template_id: Optional template UUID to use.
        config_json: Optional custom configuration.
        offline_enabled: Whether to enable offline mode.
    """
    
    name: str = Field(..., min_length=1, max_length=255, description="App name")
    template_id: Optional[str] = Field(None, description="Template UUID")
    config_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom configuration JSON",
    )
    offline_enabled: bool = Field(
        default=True,
        description="Enable offline mode",
    )


class AppResponse(BaseModel):
    """
    Response schema for app operations.
    
    Attributes:
        id: App UUID.
        user_id: Owner's UUID.
        name: App name.
        template_id: Template UUID if used.
        config_json: App configuration.
        status: App status (draft, generated, deployed).
        offline_enabled: Whether offline mode is enabled.
        deploy_url: Public PWA URL if deployed.
        created_at: Creation timestamp.
    """
    
    id: str = Field(..., description="App UUID")
    user_id: str = Field(..., description="Owner UUID")
    name: str = Field(..., description="App name")
    template_id: Optional[str] = Field(None, description="Template UUID")
    config_json: Dict[str, Any] = Field(..., description="App configuration")
    status: str = Field(..., description="App status")
    offline_enabled: bool = Field(..., description="Offline mode enabled")
    deploy_url: Optional[str] = Field(None, description="Public PWA URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        """Pydantic model configuration."""
        
        from_attributes = True


class AppUpdate(BaseModel):
    """
    Request schema for updating an app.
    
    Attributes:
        name: Optional new app name.
        config_json: Optional updated configuration.
        status: Optional status update.
        offline_enabled: Optional offline mode toggle.
    """
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New app name",
    )
    config_json: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated configuration",
    )
    status: Optional[str] = Field(
        None,
        description="App status",
    )
    offline_enabled: Optional[bool] = Field(
        None,
        description="Offline mode enabled",
    )


class AppListResponse(BaseModel):
    """
    Response schema for listing apps.
    
    Attributes:
        apps: List of app responses.
        total: Total number of apps.
    """
    
    apps: List[AppResponse] = Field(..., description="List of apps")
    total: int = Field(..., description="Total count")

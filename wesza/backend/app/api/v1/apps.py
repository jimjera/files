"""
Applications API endpoints.

This module provides endpoints for creating, retrieving, updating,
and managing generated applications.
"""

import structlog
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.app import App
from app.models.user import User
from app.schemas.app import (
    AppCreate,
    AppResponse,
    AppUpdate,
    AppListResponse,
)
from app.middleware.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/",
    response_model=AppResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new app",
    description="Create a new application from a prompt or template.",
)
async def create_app(
    request: AppCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new application.
    
    Args:
        request: App creation request.
        current_user: Authenticated user.
        db: Database session.
        
    Returns:
        AppResponse: Created app information.
    """
    new_app = App(
        user_id=current_user.id,
        name=request.name,
        template_id=request.template_id,
        config_json=request.config_json or {},
        offline_enabled=request.offline_enabled,
        status="draft",
    )
    
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    
    logger.info("App created", app_id=str(new_app.id), user_id=str(current_user.id))
    
    return AppResponse(
        id=str(new_app.id),
        user_id=str(new_app.user_id),
        name=new_app.name,
        template_id=str(new_app.template_id) if new_app.template_id else None,
        config_json=new_app.config_json,
        status=new_app.status,
        offline_enabled=new_app.offline_enabled,
        deploy_url=new_app.deploy_url,
        created_at=new_app.created_at,
    )


@router.get(
    "/",
    response_model=AppListResponse,
    summary="List user apps",
    description="Get all applications owned by the current user.",
)
async def list_apps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all apps owned by the current user.
    
    Args:
        current_user: Authenticated user.
        db: Database session.
        
    Returns:
        AppListResponse: List of apps with total count.
    """
    result = await db.execute(select(App).where(App.user_id == current_user.id))
    apps = result.scalars().all()
    
    app_responses = [
        AppResponse(
            id=str(app.id),
            user_id=str(app.user_id),
            name=app.name,
            template_id=str(app.template_id) if app.template_id else None,
            config_json=app.config_json,
            status=app.status,
            offline_enabled=app.offline_enabled,
            deploy_url=app.deploy_url,
            created_at=app.created_at,
        )
        for app in apps
    ]
    
    return AppListResponse(apps=app_responses, total=len(app_responses))


@router.get(
    "/{app_id}",
    response_model=AppResponse,
    summary="Get app by ID",
    description="Retrieve a specific application by its ID.",
)
async def get_app(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific app by ID.
    
    Args:
        app_id: App UUID.
        current_user: Authenticated user.
        db: Database session.
        
    Returns:
        AppResponse: App information.
        
    Raises:
        HTTPException: If app not found or not owned by user.
    """
    import uuid
    
    try:
        app_uuid = uuid.UUID(app_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid app ID format",
        )
    
    result = await db.execute(select(App).where(App.id == app_uuid))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found",
        )
    
    # Verify ownership
    if app.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this app",
        )
    
    return AppResponse(
        id=str(app.id),
        user_id=str(app.user_id),
        name=app.name,
        template_id=str(app.template_id) if app.template_id else None,
        config_json=app.config_json,
        status=app.status,
        offline_enabled=app.offline_enabled,
        deploy_url=app.deploy_url,
        created_at=app.created_at,
    )


@router.patch(
    "/{app_id}",
    response_model=AppResponse,
    summary="Update app",
    description="Update an existing application.",
)
async def update_app(
    app_id: str,
    request: AppUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an app.
    
    Args:
        app_id: App UUID.
        request: Update request.
        current_user: Authenticated user.
        db: Database session.
        
    Returns:
        AppResponse: Updated app information.
        
    Raises:
        HTTPException: If app not found or not owned by user.
    """
    import uuid
    
    try:
        app_uuid = uuid.UUID(app_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid app ID format",
        )
    
    result = await db.execute(select(App).where(App.id == app_uuid))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found",
        )
    
    if app.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this app",
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)
    
    await db.commit()
    await db.refresh(app)
    
    logger.info("App updated", app_id=str(app.id))
    
    return AppResponse(
        id=str(app.id),
        user_id=str(app.user_id),
        name=app.name,
        template_id=str(app.template_id) if app.template_id else None,
        config_json=app.config_json,
        status=app.status,
        offline_enabled=app.offline_enabled,
        deploy_url=app.deploy_url,
        created_at=app.created_at,
    )

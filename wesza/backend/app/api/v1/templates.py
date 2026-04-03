"""
Templates API endpoints.

This module provides endpoints for creating, retrieving, updating,
and managing reusable app templates.
"""

import structlog
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.template import Template
from app.models.user import User
from app.schemas.template import (
    TemplateCreate,
    TemplateSchemaResponse as TemplateResponse,
    TemplateUpdate,
    TemplateListResponse,
)
from app.middleware.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new template",
    description="Create a new reusable application template.",
)
async def create_template(
    request: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new template.

    Args:
        request: Template creation request.
        current_user: Authenticated user.
        db: Database session.

    Returns:
        TemplateResponse: Created template information.
    """
    new_template = Template(
        name=request.name,
        vertical=request.vertical,
        description=request.description,
        schema_json=request.schema_json,
        prompt_template=request.prompt_template,
        is_active=request.is_active,
    )

    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)

    logger.info("Template created", template_id=str(new_template.id))

    return TemplateResponse(
        id=str(new_template.id),
        name=new_template.name,
        vertical=new_template.vertical,
        description=new_template.description,
        schema_json=new_template.schema_json,
        prompt_template=new_template.prompt_template,
        is_active=new_template.is_active,
        created_at=new_template.created_at,
    )


@router.get(
    "/",
    response_model=TemplateListResponse,
    summary="List templates",
    description="Get all available templates.",
)
async def list_templates(
    db: AsyncSession = Depends(get_db),
):
    """
    List all available templates.

    Args:
        db: Database session.

    Returns:
        TemplateListResponse: List of templates with total count.
    """
    result = await db.execute(select(Template).where(Template.is_active == True))
    templates = result.scalars().all()

    template_responses = [
        TemplateResponse(
            id=str(template.id),
            name=template.name,
            vertical=template.vertical,
            description=template.description,
            schema_json=template.schema_json,
            prompt_template=template.prompt_template,
            is_active=template.is_active,
            created_at=template.created_at,
        )
        for template in templates
    ]

    return TemplateListResponse(templates=template_responses, total=len(template_responses))


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Get template by ID",
    description="Retrieve a specific template by its ID.",
)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific template by ID.

    Args:
        template_id: Template UUID.
        db: Database session.

    Returns:
        TemplateResponse: Template information.

    Raises:
        HTTPException: If template not found.
    """
    import uuid

    try:
        template_uuid = uuid.UUID(template_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template ID format",
        )

    result = await db.execute(select(Template).where(Template.id == template_uuid))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        vertical=template.vertical,
        description=template.description,
        schema_json=template.schema_json,
        prompt_template=template.prompt_template,
        is_active=template.is_active,
        created_at=template.created_at,
    )


@router.patch(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Update template",
    description="Update an existing template.",
)
async def update_template(
    template_id: str,
    request: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a template.

    Args:
        template_id: Template UUID.
        request: Update request.
        current_user: Authenticated user.
        db: Database session.

    Returns:
        TemplateResponse: Updated template information.

    Raises:
        HTTPException: If template not found.
    """
    import uuid

    try:
        template_uuid = uuid.UUID(template_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template ID format",
        )

    result = await db.execute(select(Template).where(Template.id == template_uuid))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)

    logger.info("Template updated", template_id=str(template.id))

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        vertical=template.vertical,
        description=template.description,
        schema_json=template.schema_json,
        prompt_template=template.prompt_template,
        is_active=template.is_active,
        created_at=template.created_at,
    )

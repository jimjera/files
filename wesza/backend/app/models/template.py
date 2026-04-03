"""
Template model for storing reusable app templates.

This module defines the Template SQLAlchemy model with fields for
storing vertical-specific templates and their JSON schemas.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.app import App


class Template(Base):
    """
    Template model for storing reusable application templates.
    
    Attributes:
        id: Unique identifier (UUID).
        name: Template name.
        vertical: Industry/use case category (e.g., 'logistics', 'hr').
        description: Template description.
        schema_json: JSON schema defining template structure.
        prompt_template: Example prompt for this template.
        is_active: Whether template is available for use.
        created_at: Template creation timestamp.
        apps: Relationship to apps created from this template.
    """
    
    __tablename__ = "templates"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    vertical: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    schema_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    prompt_template: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    
    # Relationships
    apps: Mapped[list["App"]] = relationship(
        back_populates="template",
    )
    
    def __repr__(self) -> str:
        """Return string representation of template."""
        return f"<Template(id={self.id}, name={self.name}, vertical={self.vertical})>"

"""
App model for storing generated application metadata.

This module defines the App SQLAlchemy model with fields for
tracking generated PWAs, their configuration, and deployment status.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.template import Template


class App(Base):
    """
    App model for storing generated application information.
    
    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to user who created the app.
        name: Application name.
        template_id: Optional foreign key to template used.
        config_json: Generated template configuration (JSONB).
        status: App status (draft, generated, deployed).
        offline_enabled: Whether offline mode is enabled.
        deploy_url: Public PWA URL after deployment.
        created_at: App creation timestamp.
        owner: Relationship to user.
        template: Relationship to template.
    """
    
    __tablename__ = "apps"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("templates.id"),
        nullable=True,
    )
    config_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )
    offline_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    deploy_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    
    # Relationships
    owner: Mapped["User"] = relationship(
        back_populates="apps",
    )
    template: Mapped[Optional["Template"]] = relationship(
        back_populates="apps",
    )
    
    def __repr__(self) -> str:
        """Return string representation of app."""
        return f"<App(id={self.id}, name={self.name}, status={self.status})>"

"""
User model for authentication and authorization.

This module defines the User SQLAlchemy model with fields for
email authentication, password hashing, and analytics consent.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.app import App


class User(Base):
    """
    User model for storing user account information.
    
    Attributes:
        id: Unique identifier (UUID).
        email: User's email address (unique, indexed).
        password_hash: Bcrypt hashed password.
        consent_analytics: Whether user consents to analytics tracking.
        created_at: Account creation timestamp.
        apps: Relationship to user's generated apps.
    """
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    consent_analytics: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    
    # Relationships
    apps: Mapped[list["App"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """Return string representation of user."""
        return f"<User(id={self.id}, email={self.email})>"

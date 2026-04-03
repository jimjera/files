"""
Authentication schemas for request/response validation.

This module defines Pydantic models for user registration, login,
and token management with proper validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Request schema for user registration.
    
    Attributes:
        email: User's email address.
        password: User's password (min 8 characters).
        consent_analytics: Whether user consents to analytics.
    """
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
    )
    consent_analytics: bool = Field(
        default=True,
        description="Consent to analytics tracking",
    )


class RegisterResponse(BaseModel):
    """
    Response schema for user registration.
    
    Attributes:
        user_id: Created user's UUID.
        email: User's email address.
        created_at: Account creation timestamp.
        message: Success message.
    """
    
    user_id: str = Field(..., description="User UUID")
    email: EmailStr = Field(..., description="User email")
    created_at: datetime = Field(..., description="Creation timestamp")
    message: str = Field(default="User registered successfully")


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    
    Attributes:
        email: User's email address.
        password: User's password.
    """
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """
    Response schema for user login.
    
    Attributes:
        access_token: JWT access token.
        token_type: Token type (bearer).
        expires_in: Token expiration time in seconds.
        user_id: User's UUID.
        email: User's email address.
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user_id: str = Field(..., description="User UUID")
    email: EmailStr = Field(..., description="User email")


class TokenData(BaseModel):
    """
    Schema for decoded JWT token data.
    
    Attributes:
        sub: Subject (user ID) from token.
        exp: Expiration timestamp.
        iat: Issued at timestamp.
    """
    
    sub: str = Field(..., description="Subject (user ID)")
    exp: Optional[datetime] = Field(None, description="Expiration timestamp")
    iat: Optional[datetime] = Field(None, description="Issued at timestamp")

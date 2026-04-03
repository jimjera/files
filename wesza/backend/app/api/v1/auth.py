"""
Authentication API endpoints.

This module provides user registration, login, and token management
endpoints for the Wesza API.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)
from app.services.auth import hash_password, verify_password, create_access_token
from app.config import settings

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password.",
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    
    Args:
        request: Registration request with email and password.
        db: Database session.
        
    Returns:
        RegisterResponse: Created user information.
        
    Raises:
        HTTPException: If email already exists.
    """
    # Check if user already exists
    from sqlalchemy import select
    
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.warning("Registration attempt with existing email", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = hash_password(request.password)
    
    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        consent_analytics=request.consent_analytics,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info("New user registered", user_id=str(new_user.id))
    
    return RegisterResponse(
        user_id=str(new_user.id),
        email=new_user.email,
        created_at=new_user.created_at,
        message="User registered successfully",
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user and return JWT access token.",
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return access token.
    
    Args:
        request: Login request with email and password.
        db: Database session.
        
    Returns:
        LoginResponse: Access token and user information.
        
    Raises:
        HTTPException: If credentials are invalid.
    """
    from sqlalchemy import select
    
    # Fetch user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        logger.warning("Failed login attempt", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=None,  # Use default from settings
    )
    
    logger.info("User logged in", user_id=str(user.id))
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        email=user.email,
    )

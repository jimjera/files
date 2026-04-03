"""
Authentication middleware for JWT token validation.

This module provides dependencies for securing API endpoints
with JWT authentication.
"""

import structlog
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.services.auth import decode_access_token

logger = structlog.get_logger()

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    This dependency validates the JWT token and retrieves the user
    from the database. It should be used to protect authenticated
    endpoints.
    
    Args:
        credentials: HTTP Bearer token credentials.
        db: Database session.
        
    Returns:
        User: Authenticated user object.
        
    Raises:
        HTTPException: If token is missing, invalid, or user not found.
    """
    if not credentials:
        logger.warning("Missing authentication credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Decode token
    token_data = decode_access_token(token)
    
    if not token_data:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    import uuid
    
    try:
        user_id = uuid.UUID(token_data.sub)
    except ValueError:
        logger.warning("Invalid user ID in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning("User not found", user_id=token_data.sub)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    This dependency is useful for endpoints that work for both
    authenticated and anonymous users.
    
    Args:
        credentials: HTTP Bearer token credentials.
        db: Database session.
        
    Returns:
        Optional[User]: Authenticated user or None.
    """
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

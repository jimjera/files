"""
Authentication service for user management.

This module provides password hashing, JWT token creation/verification,
and user authentication utilities.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.schemas.auth import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash.
        
    Returns:
        str: Bcrypt hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify.
        hashed_password: Bcrypt hashed password.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token (should include 'sub' for user ID).
        expires_delta: Optional custom expiration time.
        
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token to decode.
        
    Returns:
        TokenData: Decoded token data, or None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        sub: str = payload.get("sub")
        if sub is None:
            return None
        
        exp_timestamp = payload.get("exp")
        iat_timestamp = payload.get("iat")
        
        exp = datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
        iat = datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None
        
        return TokenData(sub=sub, exp=exp, iat=iat)
    
    except JWTError:
        return None


def verify_password_and_get_user(
    email: str,
    password: str,
) -> Optional[dict]:
    """
    Verify user credentials and return user info.
    
    Args:
        email: User's email address.
        password: Plain text password.
        
    Returns:
        Optional[dict]: User info dict if valid, None otherwise.
        
    Note:
        This function should be called with a database session
        to fetch the actual user from the database.
    """
    # This is a placeholder - actual implementation requires DB access
    # Should fetch user by email, then verify password
    return None

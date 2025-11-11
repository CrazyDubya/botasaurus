"""
Authentication Router
====================

API endpoints for authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from .schemas import UserCreate, UserLogin, Token, UserResponse
from .service import AuthService
from .dependencies import get_current_user
from ..core.database.models import User


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data: User registration data

    Returns:
        Token with access and refresh tokens
    """
    service = AuthService(db)
    return service.register(user_data)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get access tokens.

    Args:
        credentials: User login credentials

    Returns:
        Token with access and refresh tokens
    """
    service = AuthService(db)
    return service.login(credentials)


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        New access and refresh tokens
    """
    service = AuthService(db)
    return service.refresh_token(refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(refresh_token: str, db: Session = Depends(get_db)):
    """
    Logout and invalidate refresh token.

    Args:
        refresh_token: Refresh token to invalidate
    """
    service = AuthService(db)
    service.logout(refresh_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Get current user information.

    Requires authentication.

    Returns:
        Current user data
    """
    return user

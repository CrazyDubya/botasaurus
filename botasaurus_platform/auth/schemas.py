"""Authentication Pydantic schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    user_id: UUID
    email: str


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    plan: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(min_length=8, max_length=100)


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)

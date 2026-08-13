"""
Pydantic schemas for User model.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


class Token(BaseModel):
    """Token schema for authentication."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: str
    exp: int
    type: str = "access"


class PasswordUpdate(BaseModel):
    """Schema for updating password."""
    current_password: str
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )

        return v


class UserBase(BaseModel):
    """Base schema for User model."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

    @field_validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        return v

    @field_validator("full_name")
    def validate_full_name(cls, v):
        """Validate full name format."""
        if v and len(v) > 255:
            raise ValueError("Full name must be less than 256 characters")
        return v


class UserCreate(UserBase):
    """Schema for creating a new User."""
    password: str

    @field_validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase, lowercase, digit, and special character
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )

        return v


class UserUpdate(BaseModel):
    """Schema for updating a User."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    @field_validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        if v and (len(v) < 3 or len(v) > 50):
            raise ValueError("Username must be between 3 and 50 characters")
        return v

    @field_validator("full_name")
    def validate_full_name(cls, v):
        """Validate full name format."""
        if v and len(v) > 255:
            raise ValueError("Full name must be less than 256 characters")
        return v


class UserInDBBase(UserBase):
    """Base schema with ID for database operations."""
    id: int

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for returning User data (without password)."""
    pass


class UserWithPassword(UserInDBBase):
    """Schema for returning User data with password hash."""
    hashed_password: str

    class Config:
        from_attributes = True

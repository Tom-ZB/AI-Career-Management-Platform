"""
Career profile management routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.dependencies import get_db, get_current_user
from backend.crud import career_profile as crud_career_profile
from backend.crud import cv as crud_cv
from backend.schemas import career_profile as schemas_career_profile
from backend.schemas import cv as schemas_cv
from backend.schemas.user import User

router = APIRouter()


@router.get("/me", response_model=schemas_career_profile.CareerProfile)
async def get_career_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's career profile."""
    profile = crud_career_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        profile = crud_career_profile.get_or_create_by_user_id(db, user_id=current_user.id)
    return profile


@router.patch("/me", response_model=schemas_career_profile.CareerProfile)
async def update_career_profile(
    profile_update: schemas_career_profile.CareerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's career profile."""
    existing = crud_career_profile.get_by_user_id(db, user_id=current_user.id)
    if not existing:
        return crud_career_profile.create(
            db, obj_in=schemas_career_profile.CareerProfileCreate(user_id=current_user.id)
        )
    return crud_career_profile.update_by_user_id(db, user_id=current_user.id, obj_in=profile_update)


@router.post("/", response_model=schemas_career_profile.CareerProfile, status_code=status.HTTP_201_CREATED)
async def create_career_profile(
    profile_data: schemas_career_profile.CareerProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new career profile."""
    profile_data.user_id = current_user.id
    return crud_career_profile.create(db, obj_in=profile_data)
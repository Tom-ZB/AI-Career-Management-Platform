"""
User management routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user, get_current_active_superuser
from backend.crud import user as crud_user
from backend.schemas.user import User, UserUpdate, PasswordUpdate

router = APIRouter()


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's profile.
    """
    return current_user


@router.patch("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.
    """
    updated_user = crud_user.update(
        db=db,
        db_obj=current_user,
        obj_in=user_update
    )
    return updated_user


@router.put("/password", response_model=User)
async def update_password(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's password.
    """
    # Verify current password
    from backend.core.security import verify_password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    updated_user = crud_user.update_password(
        db=db, user_id=current_user.id, password=password_update.new_password
    )
    return updated_user


@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Retrieve users (superuser only).
    """
    return crud_user.get_multi(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific user by ID.
    """
    if not current_user.is_superuser and str(user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own account",
        )

    db_user = crud_user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user
"""
Follow-ups API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.follow_up import (
    FollowUpCreate, FollowUpUpdate, FollowUpResponse, FollowUpListResponse,
)
from backend.crud.follow_up import (
    get_follow_up, get_follow_ups, create_follow_up,
    update_follow_up, delete_follow_up,
)

router = APIRouter()


@router.get("/", response_model=List[FollowUpListResponse])
def list_follow_ups(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    application_id: Optional[int] = None,
    priority: Optional[int] = None,
    overdue_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all follow-ups for the current user."""
    return get_follow_ups(
        db, user_id=current_user.id,
        skip=skip, limit=limit,
        status=status, application_id=application_id,
        priority=priority, overdue_only=overdue_only,
    )


@router.post("/", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED)
def create_new_follow_up(
    follow_up_data: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new follow-up."""
    return create_follow_up(db, user_id=current_user.id, follow_up_data=follow_up_data)


@router.get("/{follow_up_id}", response_model=FollowUpResponse)
def get_follow_up_by_id(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific follow-up."""
    follow_up = get_follow_up(db, follow_up_id=follow_up_id, user_id=current_user.id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up


@router.put("/{follow_up_id}", response_model=FollowUpResponse)
def update_follow_up_by_id(
    follow_up_id: int,
    follow_up_data: FollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a follow-up."""
    follow_up = update_follow_up(
        db, follow_up_id=follow_up_id, user_id=current_user.id,
        follow_up_data=follow_up_data,
    )
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up


@router.delete("/{follow_up_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_follow_up_by_id(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a follow-up."""
    success = delete_follow_up(db, follow_up_id=follow_up_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Follow-up not found")


@router.put("/{follow_up_id}/complete", response_model=FollowUpResponse)
def complete_follow_up(
    follow_up_id: int,
    outcome: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a follow-up as completed."""
    follow_up = update_follow_up(
        db, follow_up_id=follow_up_id, user_id=current_user.id,
        follow_up_data=FollowUpUpdate(status="completed", outcome=outcome),
    )
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up
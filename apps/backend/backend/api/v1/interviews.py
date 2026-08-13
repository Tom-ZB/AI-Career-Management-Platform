"""
Interviews API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.interview import (
    InterviewCreate, InterviewUpdate, InterviewResponse, InterviewListResponse,
)
from backend.crud.interview import (
    get_interview, get_interviews, create_interview,
    update_interview, delete_interview,
)

router = APIRouter()


@router.get("/", response_model=List[InterviewListResponse])
def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    application_id: Optional[int] = None,
    upcoming_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all interviews for the current user."""
    return get_interviews(
        db, user_id=current_user.id,
        skip=skip, limit=limit,
        status=status, application_id=application_id,
        upcoming_only=upcoming_only,
    )


@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_new_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new interview."""
    return create_interview(db, user_id=current_user.id, interview_data=interview_data)


@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview_by_id(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific interview."""
    interview = get_interview(db, interview_id=interview_id, user_id=current_user.id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.put("/{interview_id}", response_model=InterviewResponse)
def update_interview_by_id(
    interview_id: int,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an interview."""
    interview = update_interview(
        db, interview_id=interview_id, user_id=current_user.id,
        interview_data=interview_data,
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_by_id(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an interview."""
    success = delete_interview(db, interview_id=interview_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Interview not found")


@router.post("/{interview_id}/prep", response_model=dict)
async def generate_interview_prep(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI interview preparation questions and tips."""
    from backend.services.ai.interview_service import AIInterviewService
    service = AIInterviewService(db)
    return await service.generate_prep(current_user.id, interview_id)
"""
Job Applications API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.job_application import (
    JobApplicationCreate, JobApplicationUpdate,
    JobApplicationResponse, JobApplicationListResponse,
)
from backend.crud.job_application import (
    get_application, get_applications, create_application,
    update_application, delete_application, get_application_stats,
)

router = APIRouter()


@router.get("/", response_model=List[JobApplicationListResponse])
def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    job_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, pattern="^(created_at|application_date|updated_at)$"),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all job applications for the current user."""
    return get_applications(
        db, user_id=current_user.id,
        skip=skip, limit=limit,
        status=status, job_id=job_id,
        search=search, sort_by=sort_by, sort_order=sort_order,
    )


@router.post("/", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_new_application(
    app_data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job application."""
    return create_application(db, user_id=current_user.id, app_data=app_data)


@router.get("/stats", response_model=dict)
def get_application_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get application statistics."""
    return get_application_stats(db, user_id=current_user.id)


@router.get("/{app_id}", response_model=JobApplicationResponse)
def get_application_by_id(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific application."""
    app = get_application(db, app_id=app_id, user_id=current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.put("/{app_id}", response_model=JobApplicationResponse)
def update_application_by_id(
    app_id: int,
    app_data: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an application."""
    app = update_application(db, app_id=app_id, user_id=current_user.id, app_data=app_data)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_by_id(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an application."""
    success = delete_application(db, app_id=app_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Application not found")


@router.put("/{app_id}/status", response_model=JobApplicationResponse)
def update_application_status(
    app_id: int,
    status: str = Query(..., description="New application status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Quick status update for an application."""
    app = update_application(
        db, app_id=app_id, user_id=current_user.id,
        app_data=JobApplicationUpdate(status=status)
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app
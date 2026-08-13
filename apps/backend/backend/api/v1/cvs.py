"""
CV management API endpoints.
"""
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.models.cv import CV
from backend.schemas.cv import (
    CVCreate, CVUpdate, CVResponse, CVListResponse,
    CVAnalysisResponse, CVGenerationRequest, CVGenerationResponse,
)
from backend.crud.cv import (
    get_cv, get_cvs, create_cv, update_cv, delete_cv,
    set_master_cv,
)
from backend.services.document_parser import DocumentParser

router = APIRouter()


def extract_text_from_file(file_path: str, content_type: Optional[str] = None) -> str:
    """Extract text content from PDF, DOCX, or TXT file."""
    path = Path(file_path)
    if not path.exists():
        return ""

    try:
        with open(path, "rb") as f:
            file_bytes = f.read()

        return DocumentParser.parse(file_bytes, content_type, path.name)
    except Exception:
        return ""


@router.get("/", response_model=List[CVListResponse])
def list_cvs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_master: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all CVs for the current user."""
    return get_cvs(
        db, user_id=current_user.id,
        skip=skip, limit=limit,
        is_master=is_master, search=search,
    )


@router.post("/", response_model=CVResponse, status_code=status.HTTP_201_CREATED)
def create_new_cv(
    cv_data: CVCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new CV record."""
    return create_cv(db, user_id=current_user.id, cv_data=cv_data)


@router.get("/{cv_id}", response_model=CVResponse)
def get_cv_by_id(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific CV by ID."""
    cv = get_cv(db, cv_id=cv_id, user_id=current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.put("/{cv_id}", response_model=CVResponse)
def update_cv_by_id(
    cv_id: int,
    cv_data: CVUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a CV."""
    cv = update_cv(db, cv_id=cv_id, user_id=current_user.id, cv_data=cv_data)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cv_by_id(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a CV."""
    success = delete_cv(db, cv_id=cv_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="CV not found")


@router.post("/{cv_id}/set-master", response_model=CVResponse)
def set_as_master(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set a CV as the master CV."""
    cv = set_master_cv(db, cv_id=cv_id, user_id=current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.post("/upload", response_model=CVResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv_file(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a CV file and parse it."""
    import os
    from datetime import datetime
    from backend.models.cv import CV
    from backend.schemas.cv import CVCreate

    # Create uploads directory if not exists
    upload_dir = "uploads/cvs"
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Extract text content from file
    content_text = extract_text_from_file(file_path, file.content_type or "")

    # Determine file extension
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else "pdf"
    if file_ext not in ["pdf", "docx", "txt", "rtf", "odt"]:
        file_ext = "pdf"

    # Create CV record
    cv_data = CVCreate(
        user_id=current_user.id,
        title=title or file.filename,
        file_name=file.filename,
        file_path=file_path,
        file_type=file_ext,
        file_size=len(content),
        uploaded_at=datetime.utcnow(),
        content_text=content_text[:100000] if content_text else None,  # Limit to 100KB
    )

    from backend.crud.cv import create_cv
    cv = create_cv(db, user_id=current_user.id, cv_data=cv_data)
    return cv


@router.post("/{cv_id}/analyze", response_model=CVAnalysisResponse)
async def analyze_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run AI analysis on a CV."""
    from backend.services.ai.cv_service import AICVService
    service = AICVService(db)
    return await service.analyze_cv(current_user.id, cv_id)


@router.post("/generate", response_model=CVGenerationResponse)
async def generate_tailored_cv(
    request: CVGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a tailored CV for a specific job."""
    from backend.services.ai.cv_service import AICVService
    service = AICVService(db)
    return await service.generate_tailored_cv(current_user.id, request)
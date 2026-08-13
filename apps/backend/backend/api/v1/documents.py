"""
Document management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse,
)
from backend.crud.document import (
    get_document, get_documents, create_document, update_document, delete_document,
)

router = APIRouter()


@router.get("/", response_model=List[DocumentListResponse])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    document_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents for the current user."""
    return get_documents(
        db, user_id=current_user.id,
        skip=skip, limit=limit,
        document_type=document_type, search=search,
    )


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_new_document(
    doc_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new document record."""
    return create_document(db, user_id=current_user.id, doc_data=doc_data)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document_by_id(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific document."""
    doc = get_document(db, doc_id=doc_id, user_id=current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document_by_id(
    doc_id: int,
    doc_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a document."""
    doc = update_document(db, doc_id=doc_id, user_id=current_user.id, doc_data=doc_data)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_by_id(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document."""
    success = delete_document(db, doc_id=doc_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document file."""
    import os
    from datetime import datetime
    from backend.models.document import Document, DocumentType
    from backend.schemas.document import DocumentCreate

    # Create uploads directory if not exists
    upload_dir = "uploads/documents"
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Determine document type
    doc_type = DocumentType(document_type) if document_type else DocumentType.OTHER

    # Create document record
    doc_data = DocumentCreate(
        user_id=current_user.id,
        document_type=doc_type,
        title=title or file.filename,
        description=description,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        storage_path=file_path,
        uploaded_at=datetime.utcnow(),
    )

    from backend.crud.document import create_document
    doc = create_document(db, user_id=current_user.id, doc_data=doc_data)
    return doc


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a document file."""
    # TODO: Implement file download
    pass
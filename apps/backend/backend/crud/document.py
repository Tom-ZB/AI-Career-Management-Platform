"""
CRUD operations for Document model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.crud.base import CRUDBase
from backend.models.document import Document
from backend.schemas.document import DocumentCreate, DocumentUpdate


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    """
    CRUD operations for Document model.
    """

    def get_by_user_id(self, db: Session, *, user_id: int) -> List[Document]:
        """
        Get all documents for a user.
        """
        return db.query(Document).filter(Document.user_id == user_id).all()

    def get_by_document_type(self, db: Session, *, user_id: int, document_type: str) -> List[Document]:
        """
        Get all documents of a specific type for a user.
        """
        from backend.models.document import DocumentType

        type_enum = DocumentType(document_type)
        return (
            db.query(Document)
            .filter(
                Document.user_id == user_id,
                Document.document_type == type_enum
            )
            .all()
        )

    def get_by_related_entity(self, db: Session, *, related_entity_type: str, related_entity_id: int) -> List[Document]:
        """
        Get all documents related to a specific entity.
        """
        return (
            db.query(Document)
            .filter(
                Document.related_entity_type == related_entity_type,
                Document.related_entity_id == related_entity_id
            )
            .all()
        )

    def get_by_filename(self, db: Session, *, user_id: int, filename: str) -> Optional[Document]:
        """
        Get a document by filename for a user.
        """
        return (
            db.query(Document)
            .filter(
                Document.user_id == user_id,
                Document.file_name == filename
            )
            .first()
        )

    def create(self, db: Session, *, obj_in: DocumentCreate) -> Document:
        """
        Create a new document.
        """
        # Check if user already has a document with the same filename
        existing_doc = self.get_by_filename(
            db,
            user_id=obj_in.user_id,
            filename=obj_in.file_name
        )
        if existing_doc:
            raise ValueError(
                f"Document with filename '{obj_in.file_name}' already exists for user {obj_in.user_id}"
            )

        db_obj = Document(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Document, obj_in: DocumentUpdate) -> Document:
        """
        Update a document.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        # If updating filename, check for conflicts
        if "file_name" in update_data:
            existing_doc = self.get_by_filename(
                db,
                user_id=db_obj.user_id,
                filename=update_data["file_name"]
            )
            if existing_doc and existing_doc.id != db_obj.id:
                raise ValueError(
                    f"Document with filename '{update_data['file_name']}' already exists for user {db_obj.user_id}"
                )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_documents_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        document_type: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
        filename_contains: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """
        Get documents with various filters.
        """
        from backend.models.document import DocumentType

        query = db.query(Document).filter(Document.user_id == user_id)

        if document_type:
            query = query.filter(Document.document_type == DocumentType(document_type))

        if related_entity_type:
            query = query.filter(Document.related_entity_type == related_entity_type)

        if related_entity_id:
            query = query.filter(Document.related_entity_id == related_entity_id)

        # Support both 'search' and 'filename_contains' parameter names
        search_term = search or filename_contains
        if search_term:
            query = query.filter(Document.file_name.contains(search_term))

        return query.offset(skip).limit(limit).all()

    def delete(self, db: Session, *, id: int) -> Optional[Document]:
        """
        Delete a document and clean up file from storage.
        """
        from backend.utils.storage import delete_file
        import os

        document = db.query(Document).get(id)
        if document:
            # Try to delete the actual file from storage
            try:
                file_path = os.path.join(os.getcwd(), document.file_path)
                if os.path.exists(file_path):
                    delete_file(file_path)
            except Exception as e:
                # Log the error but don't prevent the deletion of the record
                print(f"Error deleting file {document.file_path}: {e}")

            # Delete the record from the database
            db.delete(document)
            db.commit()
        return document

    def get_total_size_by_user(self, db: Session, *, user_id: int) -> int:
        """
        Get total size of all documents for a user.
        """
        result = (
            db.query(func.sum(Document.file_size))
            .filter(Document.user_id == user_id)
            .scalar()
        )
        return result or 0

    def get_document_stats(self, db: Session, *, user_id: int) -> dict:
        """
        Get document statistics for a user.
        """
        from sqlalchemy import func
        from backend.models.document import DocumentType

        total_docs = self.count(db, filters={"user_id": user_id})

        # Count by type
        type_counts = {}
        for doc_type in DocumentType:
            count = db.query(Document).filter(
                Document.user_id == user_id,
                Document.document_type == doc_type
            ).count()
            type_counts[doc_type.value] = count

        # Get total size
        total_size = self.get_total_size_by_user(db, user_id=user_id)

        return {
            "total_documents": total_docs,
            "by_type": type_counts,
            "total_size_bytes": total_size
        }


# Create document CRUD instance
document = CRUDDocument(Document)


# ============================================================
# Convenience functions for API routers
# ============================================================

def get_document(db: Session, doc_id: int, user_id: int) -> Optional[Document]:
    """Get a document by ID for a specific user."""
    return (
        db.query(Document)
        .filter(Document.id == doc_id, Document.user_id == user_id)
        .first()
    )


def get_documents(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    **filters,
) -> List[Document]:
    """Get documents with filters."""
    return document.get_documents_with_filters(
        db, user_id=user_id, skip=skip, limit=limit, **filters
    )


def create_document(db: Session, user_id: int, doc_data: DocumentCreate) -> Document:
    """Create a new document."""
    data = doc_data.model_dump()
    data['user_id'] = user_id
    return document.create(db, obj_in=DocumentCreate(**data))


def update_document(
    db: Session,
    doc_id: int,
    user_id: int,
    doc_data: DocumentUpdate,
) -> Optional[Document]:
    """Update a document."""
    doc = get_document(db, doc_id=doc_id, user_id=user_id)
    if not doc:
        return None
    return document.update(db, db_obj=doc, obj_in=doc_data)


def delete_document(db: Session, doc_id: int, user_id: int) -> bool:
    """Delete a document."""
    return bool(document.delete(db, id=doc_id))

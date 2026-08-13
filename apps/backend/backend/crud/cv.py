"""
CRUD operations for CV model - Extended functions for API.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.crud.base import CRUDBase
from backend.models.cv import CV
from backend.schemas.cv import CVCreate, CVUpdate


class CRUDCVExtended(CRUDBase[CV, CVCreate, CVUpdate]):
    """Extended CRUD operations for CV model."""

    def get_cv(self, db: Session, *, cv_id: int, user_id: int) -> Optional[CV]:
        """Get a CV by ID for a specific user."""
        return (
            db.query(CV)
            .filter(CV.id == cv_id, CV.user_id == user_id)
            .first()
        )

    def get_cvs(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        is_master: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[CV]:
        """Get CVs with filters."""
        query = db.query(CV).filter(CV.user_id == user_id)

        if is_master is not None:
            query = query.filter(CV.is_master == is_master)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    CV.title.ilike(search_term),
                    CV.description.ilike(search_term),
                )
            )

        return query.order_by(CV.created_at.desc()).offset(skip).limit(limit).all()

    def create_cv(self, db: Session, *, user_id: int, cv_data: CVCreate) -> CV:
        """Create a new CV."""
        # If setting as master, unset other master CVs
        if cv_data.is_master:
            db.query(CV).filter(
                CV.user_id == user_id,
                CV.is_master == True
            ).update({"is_master": False})

        db_obj = CV(**cv_data.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_cv(
        self,
        db: Session,
        *,
        cv_id: int,
        user_id: int,
        cv_data: CVUpdate,
    ) -> Optional[CV]:
        """Update a CV."""
        cv = self.get_cv(db, cv_id=cv_id, user_id=user_id)
        if not cv:
            return None

        update_data = cv_data.model_dump(exclude_unset=True)

        # If setting as master, unset other master CVs
        if update_data.get("is_master"):
            db.query(CV).filter(
                CV.user_id == user_id,
                CV.is_master == True,
                CV.id != cv_id,
            ).update({"is_master": False})

        for field, value in update_data.items():
            setattr(cv, field, value)

        db.add(cv)
        db.commit()
        db.refresh(cv)
        return cv

    def delete_cv(self, db: Session, *, cv_id: int, user_id: int) -> bool:
        """Delete a CV."""
        cv = self.get_cv(db, cv_id=cv_id, user_id=user_id)
        if not cv:
            return False

        db.delete(cv)
        db.commit()
        return True

    def set_master_cv(self, db: Session, *, cv_id: int, user_id: int) -> Optional[CV]:
        """Set a CV as the master CV."""
        cv = self.get_cv(db, cv_id=cv_id, user_id=user_id)
        if not cv:
            return None

        # Unset other master CVs
        db.query(CV).filter(
            CV.user_id == user_id,
            CV.is_master == True,
        ).update({"is_master": False})

        # Set this CV as master
        cv.is_master = True
        db.add(cv)
        db.commit()
        db.refresh(cv)
        return cv


# Create instance (name must match crud/__init__.py)
cv = CRUDCVExtended(CV)
cv_crud = cv


# Convenience functions for API
def get_cv(db: Session, cv_id: int, user_id: int) -> Optional[CV]:
    return cv_crud.get_cv(db, cv_id=cv_id, user_id=user_id)


def get_cvs(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    is_master: Optional[bool] = None,
    search: Optional[str] = None,
) -> List[CV]:
    return cv_crud.get_cvs(
        db, user_id=user_id, skip=skip, limit=limit,
        is_master=is_master, search=search,
    )


def create_cv(db: Session, user_id: int, cv_data: CVCreate) -> CV:
    return cv_crud.create_cv(db, user_id=user_id, cv_data=cv_data)


def update_cv(
    db: Session,
    cv_id: int,
    user_id: int,
    cv_data: CVUpdate,
) -> Optional[CV]:
    return cv_crud.update_cv(db, cv_id=cv_id, user_id=user_id, cv_data=cv_data)


def delete_cv(db: Session, cv_id: int, user_id: int) -> bool:
    return cv_crud.delete_cv(db, cv_id=cv_id, user_id=user_id)


def set_master_cv(db: Session, cv_id: int, user_id: int) -> Optional[CV]:
    return cv_crud.set_master_cv(db, cv_id=cv_id, user_id=user_id)
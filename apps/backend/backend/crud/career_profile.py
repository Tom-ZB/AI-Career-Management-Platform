"""
CRUD operations for CareerProfile model.
"""
from typing import Optional
from sqlalchemy.orm import Session
from backend.crud.base import CRUDBase
from backend.models.career_profile import CareerProfile
from backend.schemas.career_profile import CareerProfileCreate, CareerProfileUpdate


class CRUDCareerProfile(CRUDBase[CareerProfile, CareerProfileCreate, CareerProfileUpdate]):
    """
    CRUD operations for CareerProfile model.
    """

    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[CareerProfile]:
        """
        Get a career profile by user ID.
        """
        return db.query(CareerProfile).filter(CareerProfile.user_id == user_id).first()

    def create(self, db: Session, *, obj_in: CareerProfileCreate) -> CareerProfile:
        """
        Create a new career profile.
        """
        # Check if user already has a career profile
        existing_profile = self.get_by_user_id(db, user_id=obj_in.user_id)
        if existing_profile:
            raise ValueError(f"User {obj_in.user_id} already has a career profile")

        db_obj = CareerProfile(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_by_user_id(
        self,
        db: Session,
        *,
        user_id: int,
        obj_in: CareerProfileUpdate
    ) -> Optional[CareerProfile]:
        """
        Update a career profile by user ID.
        """
        db_obj = self.get_by_user_id(db, user_id=user_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_or_create_by_user_id(self, db: Session, *, user_id: int) -> CareerProfile:
        """
        Get or create a career profile for a user.
        """
        db_obj = self.get_by_user_id(db, user_id=user_id)
        if not db_obj:
            db_obj = CareerProfile(
                user_id=user_id,
                full_name="",
                title="",
                summary=""
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


# Create career profile CRUD instance
career_profile = CRUDCareerProfile(CareerProfile)

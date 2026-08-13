"""
Base CRUD operations for all models.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with default methods for Create, Read, Update, Delete.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class.
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with optional filters.
        """
        query = db.query(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.
        """
        query = db.query(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        return query.count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        """
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Update a record.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Delete a record by ID.
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def delete_multi(self, db: Session, *, ids: List[int]) -> int:
        """
        Delete multiple records by IDs.
        """
        deleted = db.query(self.model).filter(self.model.id.in_(ids)).delete()
        db.commit()
        return deleted

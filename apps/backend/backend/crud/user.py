"""
CRUD operations for User model.
"""
from typing import Optional
from sqlalchemy.orm import Session
from backend.crud.base import CRUDBase
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.
    Includes additional methods specific to user management.
    """

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get a user by email.
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Get a user by username.
        """
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.
        """
        from backend.core.security import get_password_hash

        # Hash the password before creating the user
        hashed_password = get_password_hash(obj_in.password)

        # Create user object with hashed password
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            hashed_password=hashed_password,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(self, db: Session, *, user_id: int, password: str) -> User:
        """
        Update user password with hashed password.
        """
        from backend.core.security import get_password_hash

        user = self.get(db=db, id=user_id)
        if user:
            hashed_password = get_password_hash(password)
            user.hashed_password = hashed_password
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email and password.
        """
        from backend.core.security import verify_password

        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def activate_user(self, db: Session, *, user_id: int) -> User:
        """
        Activate a user account.
        """
        user = self.get(db=db, id=user_id)
        if user:
            user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def deactivate_user(self, db: Session, *, user_id: int) -> User:
        """
        Deactivate a user account.
        """
        user = self.get(db=db, id=user_id)
        if user:
            user.is_active = False
            db.add(user)
            db.commit()
            db.refresh(user)
        return user


# Create user CRUD instance
user = CRUDUser(User)


# Convenience functions for API
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return user.get(db, id=user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return user.get_by_email(db, email=email)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return user.get_by_username(db, username=username)

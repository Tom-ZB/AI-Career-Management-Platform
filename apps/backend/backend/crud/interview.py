"""
CRUD operations for Interview model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.crud.base import CRUDBase
from backend.models.interview import Interview
from backend.schemas.interview import InterviewCreate, InterviewUpdate


class CRUDInterview(CRUDBase[Interview, InterviewCreate, InterviewUpdate]):
    """
    CRUD operations for Interview model.
    """

    def get_by_user_id(self, db: Session, *, user_id: int) -> List[Interview]:
        """
        Get all interviews for a user.
        """
        return db.query(Interview).filter(Interview.user_id == user_id).all()

    def get_by_application_id(self, db: Session, *, application_id: int) -> List[Interview]:
        """
        Get all interviews for a job application.
        """
        return db.query(Interview).filter(Interview.application_id == application_id).all()

    def get_upcoming_interviews(self, db: Session, *, user_id: int) -> List[Interview]:
        """
        Get upcoming interviews for a user (scheduled or rescheduled).
        """
        from backend.models.interview import InterviewStatus
        from sqlalchemy import func

        return (
            db.query(Interview)
            .filter(
                Interview.user_id == user_id,
                Interview.status.in_([InterviewStatus.SCHEDULED, InterviewStatus.RESCHEDULED]),
                Interview.scheduled_at >= func.now()
            )
            .order_by(Interview.scheduled_at.asc())
            .all()
        )

    def get_past_interviews(self, db: Session, *, user_id: int) -> List[Interview]:
        """
        Get past interviews for a user (completed, cancelled, no_show).
        """
        from backend.models.interview import InterviewStatus
        from sqlalchemy import func

        return (
            db.query(Interview)
            .filter(
                Interview.user_id == user_id,
                Interview.status.in_([
                    InterviewStatus.COMPLETED,
                    InterviewStatus.CANCELLED,
                    InterviewStatus.NO_SHOW
                ]),
                Interview.scheduled_at < func.now()
            )
            .order_by(Interview.scheduled_at.desc())
            .all()
        )

    def get_by_status(self, db: Session, *, user_id: int, status: str) -> List[Interview]:
        """
        Get interviews by status for a user.
        """
        from backend.models.interview import InterviewStatus

        status_enum = InterviewStatus(status)
        return (
            db.query(Interview)
            .filter(
                Interview.user_id == user_id,
                Interview.status == status_enum
            )
            .all()
        )

    def get_by_type(self, db: Session, *, user_id: int, interview_type: str) -> List[Interview]:
        """
        Get interviews by type for a user.
        """
        from backend.models.interview import InterviewType

        type_enum = InterviewType(interview_type)
        return (
            db.query(Interview)
            .filter(
                Interview.user_id == user_id,
                Interview.interview_type == type_enum
            )
            .all()
        )

    def create(self, db: Session, *, obj_in: InterviewCreate) -> Interview:
        """
        Create a new interview.
        """
        # Check for conflicting scheduled interviews at the same time
        conflicting_interview = (
            db.query(Interview)
            .filter(
                Interview.user_id == obj_in.user_id,
                Interview.scheduled_at == obj_in.scheduled_at,
                Interview.status.in_([
                    "scheduled", "rescheduled"
                ])
            )
            .first()
        )

        if conflicting_interview:
            raise ValueError(
                f"Conflicting interview already scheduled at {obj_in.scheduled_at} "
                f"for user {obj_in.user_id}"
            )

        db_obj = Interview(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Interview, obj_in: InterviewUpdate) -> Interview:
        """
        Update an interview.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        # Check for conflicting scheduled interviews at the same time (if scheduled time changed)
        if "scheduled_at" in update_data and update_data["scheduled_at"] != db_obj.scheduled_at:
            conflicting_interview = (
                db.query(Interview)
                .filter(
                    Interview.user_id == db_obj.user_id,
                    Interview.scheduled_at == update_data["scheduled_at"],
                    Interview.id != db_obj.id,  # Exclude current interview
                    Interview.status.in_([
                        "scheduled", "rescheduled"
                    ])
                )
                .first()
            )

            if conflicting_interview:
                raise ValueError(
                    f"Conflicting interview already scheduled at {update_data['scheduled_at']} "
                    f"for user {db_obj.user_id}"
                )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_interviews_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        status: Optional[str] = None,
        interview_type: Optional[str] = None,
        application_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        upcoming_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        """
        Get interviews with various filters.
        """
        from backend.models.interview import InterviewStatus, InterviewType
        from sqlalchemy import func

        query = db.query(Interview).filter(Interview.user_id == user_id)

        if upcoming_only:
            query = query.filter(
                Interview.status.in_([InterviewStatus.SCHEDULED, InterviewStatus.RESCHEDULED]),
                Interview.scheduled_at >= func.now()
            )

        if status:
            query = query.filter(Interview.status == InterviewStatus(status))

        if interview_type:
            query = query.filter(Interview.interview_type == InterviewType(interview_type))

        if application_id:
            query = query.filter(Interview.application_id == application_id)

        if start_date:
            query = query.filter(Interview.scheduled_at >= start_date)

        if end_date:
            query = query.filter(Interview.scheduled_at <= end_date)

        return query.offset(skip).limit(limit).all()

    def cancel_interview(self, db: Session, *, interview_id: int) -> Interview:
        """
        Cancel an interview by updating its status.
        """
        from backend.models.interview import InterviewStatus

        db_obj = self.get(db, id=interview_id)
        if db_obj:
            db_obj.status = InterviewStatus.CANCELLED
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def reschedule_interview(
        self,
        db: Session,
        *,
        interview_id: int,
        new_scheduled_at: str
    ) -> Interview:
        """
        Reschedule an interview to a new time.
        """
        from backend.models.interview import InterviewStatus
        from datetime import datetime

        db_obj = self.get(db, id=interview_id)
        if db_obj:
            # Check for conflicts with the new time
            conflicting_interview = (
                db.query(Interview)
                .filter(
                    Interview.user_id == db_obj.user_id,
                    Interview.scheduled_at == new_scheduled_at,
                    Interview.id != interview_id,
                    Interview.status.in_([
                        "scheduled", "rescheduled"
                    ])
                )
                .first()
            )

            if conflicting_interview:
                raise ValueError(
                    f"Conflicting interview already scheduled at {new_scheduled_at} "
                    f"for user {db_obj.user_id}"
                )

            db_obj.scheduled_at = datetime.fromisoformat(new_scheduled_at)
            db_obj.status = InterviewStatus.RESCHEDULED
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


# Create interview CRUD instance
interview = CRUDInterview(Interview)


# Convenience functions for API
def get_interview(db: Session, interview_id: int, user_id: int) -> Optional[Interview]:
    """Get an interview by ID for a specific user."""
    return (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == user_id)
        .first()
    )


def get_interviews(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    **filters,
) -> List[Interview]:
    """Get interviews with filters."""
    return interview.get_interviews_with_filters(
        db, user_id=user_id, skip=skip, limit=limit, **filters
    )


def create_interview(db: Session, user_id: int, interview_data: InterviewCreate) -> Interview:
    """Create a new interview."""
    data = interview_data.model_dump()
    data['user_id'] = user_id
    return interview.create(db, obj_in=InterviewCreate(**data))


def update_interview(
    db: Session,
    interview_id: int,
    user_id: int,
    interview_data: InterviewUpdate,
) -> Optional[Interview]:
    """Update an interview."""
    int_obj = get_interview(db, interview_id=interview_id, user_id=user_id)
    if not int_obj:
        return None
    return interview.update(db, db_obj=int_obj, obj_in=interview_data)


def delete_interview(db: Session, interview_id: int, user_id: int) -> bool:
    """Delete an interview."""
    int_obj = get_interview(db, interview_id=interview_id, user_id=user_id)
    if not int_obj:
        return False
    db.delete(int_obj)
    db.commit()
    return True


# ============================================================
# Convenience functions for API routers
# ============================================================

def get_interview(db: Session, interview_id: int, user_id: int) -> Optional[Interview]:
    """Get an interview by ID for a specific user."""
    return (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == user_id)
        .first()
    )


def get_interviews(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    **filters,
) -> List[Interview]:
    """Get interviews with filters."""
    return interview.get_interviews_with_filters(
        db, user_id=user_id, skip=skip, limit=limit, **filters
    )


def create_interview(db: Session, user_id: int, interview_data: InterviewCreate) -> Interview:
    """Create a new interview."""
    data = interview_data.model_dump()
    data['user_id'] = user_id
    return interview.create(db, obj_in=InterviewCreate(**data))


def update_interview(
    db: Session,
    interview_id: int,
    user_id: int,
    interview_data: InterviewUpdate,
) -> Optional[Interview]:
    """Update an interview."""
    int_obj = get_interview(db, interview_id=interview_id, user_id=user_id)
    if not int_obj:
        return None
    return interview.update(db, db_obj=int_obj, obj_in=interview_data)


def delete_interview(db: Session, interview_id: int, user_id: int) -> bool:
    """Delete an interview."""
    int_obj = get_interview(db, interview_id=interview_id, user_id=user_id)
    if not int_obj:
        return False
    db.delete(int_obj)
    db.commit()
    return True

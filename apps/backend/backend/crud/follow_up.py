"""
CRUD operations for FollowUp model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.crud.base import CRUDBase
from backend.models.follow_up import FollowUp
from backend.schemas.follow_up import FollowUpCreate, FollowUpUpdate


class CRUDFollowUp(CRUDBase[FollowUp, FollowUpCreate, FollowUpUpdate]):
    """
    CRUD operations for FollowUp model.
    """

    def get_by_user_id(self, db: Session, *, user_id: int) -> List[FollowUp]:
        """
        Get all follow-ups for a user.
        """
        return db.query(FollowUp).filter(FollowUp.user_id == user_id).all()

    def get_pending_follow_ups(self, db: Session, *, user_id: int) -> List[FollowUp]:
        """
        Get pending follow-ups for a user.
        """
        from backend.models.follow_up import FollowUpStatus
        from sqlalchemy import func

        return (
            db.query(FollowUp)
            .filter(
                FollowUp.user_id == user_id,
                FollowUp.status == FollowUpStatus.PENDING,
                FollowUp.scheduled_at <= func.now()
            )
            .order_by(FollowUp.scheduled_at.asc())
            .all()
        )

    def get_scheduled_follow_ups(self, db: Session, *, user_id: int) -> List[FollowUp]:
        """
        Get scheduled (upcoming) follow-ups for a user.
        """
        from backend.models.follow_up import FollowUpStatus
        from sqlalchemy import func

        return (
            db.query(FollowUp)
            .filter(
                FollowUp.user_id == user_id,
                FollowUp.status == FollowUpStatus.PENDING,
                FollowUp.scheduled_at > func.now()
            )
            .order_by(FollowUp.scheduled_at.asc())
            .all()
        )

    def get_by_application_id(self, db: Session, *, application_id: int) -> List[FollowUp]:
        """
        Get all follow-ups for a job application.
        """
        return (
            db.query(FollowUp)
            .filter(FollowUp.application_id == application_id)
            .order_by(FollowUp.scheduled_at.desc())
            .all()
        )

    def get_by_interview_id(self, db: Session, *, interview_id: int) -> List[FollowUp]:
        """
        Get all follow-ups for an interview.
        """
        return (
            db.query(FollowUp)
            .filter(FollowUp.interview_id == interview_id)
            .order_by(FollowUp.scheduled_at.desc())
            .all()
        )

    def get_by_status(self, db: Session, *, user_id: int, status: str) -> List[FollowUp]:
        """
        Get follow-ups by status for a user.
        """
        from backend.models.follow_up import FollowUpStatus

        status_enum = FollowUpStatus(status)
        return (
            db.query(FollowUp)
            .filter(
                FollowUp.user_id == user_id,
                FollowUp.status == status_enum
            )
            .all()
        )

    def get_by_type(self, db: Session, *, user_id: int, follow_up_type: str) -> List[FollowUp]:
        """
        Get follow-ups by type for a user.
        """
        from backend.models.follow_up import FollowUpType

        type_enum = FollowUpType(follow_up_type)
        return (
            db.query(FollowUp)
            .filter(
                FollowUp.user_id == user_id,
                FollowUp.follow_up_type == type_enum
            )
            .all()
        )

    def create(self, db: Session, *, obj_in: FollowUpCreate) -> FollowUp:
        """
        Create a new follow-up.
        """
        # Check for conflicting follow-ups at the same time
        conflicting_follow_up = (
            db.query(FollowUp)
            .filter(
                FollowUp.user_id == obj_in.user_id,
                FollowUp.scheduled_at == obj_in.scheduled_at,
                FollowUp.status == "pending"
            )
            .first()
        )

        if conflicting_follow_up:
            raise ValueError(
                f"Conflicting follow-up already scheduled at {obj_in.scheduled_at} "
                f"for user {obj_in.user_id}"
            )

        db_obj = FollowUp(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: FollowUp, obj_in: FollowUpUpdate) -> FollowUp:
        """
        Update a follow-up.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        # Check for conflicting scheduled follow-ups at the same time (if scheduled time changed)
        if "scheduled_at" in update_data and update_data["scheduled_at"] != db_obj.scheduled_at:
            conflicting_follow_up = (
                db.query(FollowUp)
                .filter(
                    FollowUp.user_id == db_obj.user_id,
                    FollowUp.scheduled_at == update_data["scheduled_at"],
                    FollowUp.id != db_obj.id,  # Exclude current follow-up
                    FollowUp.status == "pending"
                )
                .first()
            )

            if conflicting_follow_up:
                raise ValueError(
                    f"Conflicting follow-up already scheduled at {update_data['scheduled_at']} "
                    f"for user {db_obj.user_id}"
                )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_follow_ups_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        status: Optional[str] = None,
        follow_up_type: Optional[str] = None,
        application_id: Optional[int] = None,
        interview_id: Optional[int] = None,
        priority: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        overdue_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[FollowUp]:
        """
        Get follow-ups with various filters.
        """
        from backend.models.follow_up import FollowUpStatus, FollowUpType
        from sqlalchemy import func

        query = db.query(FollowUp).filter(FollowUp.user_id == user_id)

        if overdue_only:
            query = query.filter(
                FollowUp.status == FollowUpStatus.PENDING,
                FollowUp.scheduled_at < func.now()
            )

        if status:
            query = query.filter(FollowUp.status == FollowUpStatus(status))

        if follow_up_type:
            query = query.filter(FollowUp.follow_up_type == FollowUpType(follow_up_type))

        if application_id:
            query = query.filter(FollowUp.application_id == application_id)

        if interview_id:
            query = query.filter(FollowUp.interview_id == interview_id)

        if priority is not None:
            query = query.filter(FollowUp.priority == priority)

        if start_date:
            query = query.filter(FollowUp.scheduled_at >= start_date)

        if end_date:
            query = query.filter(FollowUp.scheduled_at <= end_date)

        return query.offset(skip).limit(limit).all()

    def mark_completed(self, db: Session, *, follow_up_id: int) -> FollowUp:
        """
        Mark a follow-up as completed.
        """
        from backend.models.follow_up import FollowUpStatus
        from sqlalchemy import func

        db_obj = self.get(db, id=follow_up_id)
        if db_obj:
            db_obj.status = FollowUpStatus.COMPLETED
            db_obj.completed_at = func.now()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def mark_missed(self, db: Session, *, follow_up_id: int) -> FollowUp:
        """
        Mark a follow-up as missed.
        """
        from backend.models.follow_up import FollowUpStatus

        db_obj = self.get(db, id=follow_up_id)
        if db_obj:
            db_obj.status = FollowUpStatus.MISSED
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_overdue_follow_ups(self, db: Session, *, user_id: int) -> List[FollowUp]:
        """
        Get overdue follow-ups for a user (pending and past due).
        """
        from backend.models.follow_up import FollowUpStatus
        from sqlalchemy import func

        return (
            db.query(FollowUp)
            .filter(
                FollowUp.user_id == user_id,
                FollowUp.status == FollowUpStatus.PENDING,
                FollowUp.scheduled_at < func.now()
            )
            .order_by(FollowUp.scheduled_at.asc())
            .all()
        )

    def get_follow_up_stats(self, db: Session, *, user_id: int) -> dict:
        """
        Get follow-up statistics for a user.
        """
        from backend.models.follow_up import FollowUpStatus

        total_follow_ups = self.count(db, filters={"user_id": user_id})

        stats = {}
        for status in FollowUpStatus:
            count = db.query(FollowUp).filter(
                FollowUp.user_id == user_id,
                FollowUp.status == status
            ).count()
            stats[status.value] = count

        return {
            "total": total_follow_ups,
            **stats
        }


# Create follow-up CRUD instance
follow_up = CRUDFollowUp(FollowUp)


# ============================================================
# Convenience functions for API routers
# ============================================================

def get_follow_up(db: Session, follow_up_id: int, user_id: int) -> Optional[FollowUp]:
    """Get a follow-up by ID for a specific user."""
    return (
        db.query(FollowUp)
        .filter(FollowUp.id == follow_up_id, FollowUp.user_id == user_id)
        .first()
    )


def get_follow_ups(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    **filters,
) -> List[FollowUp]:
    """Get follow-ups with filters."""
    return follow_up.get_follow_ups_with_filters(
        db, user_id=user_id, skip=skip, limit=limit, **filters
    )


def create_follow_up(db: Session, user_id: int, follow_up_data: FollowUpCreate) -> FollowUp:
    """Create a new follow-up."""
    data = follow_up_data.model_dump()
    data['user_id'] = user_id
    return follow_up.create(db, obj_in=FollowUpCreate(**data))


def update_follow_up(
    db: Session,
    follow_up_id: int,
    user_id: int,
    follow_up_data: FollowUpUpdate,
) -> Optional[FollowUp]:
    """Update a follow-up."""
    fu = get_follow_up(db, follow_up_id=follow_up_id, user_id=user_id)
    if not fu:
        return None
    return follow_up.update(db, db_obj=fu, obj_in=follow_up_data)


def delete_follow_up(db: Session, follow_up_id: int, user_id: int) -> bool:
    """Delete a follow-up."""
    fu = get_follow_up(db, follow_up_id=follow_up_id, user_id=user_id)
    if not fu:
        return False
    db.delete(fu)
    db.commit()
    return True

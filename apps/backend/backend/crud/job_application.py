"""
CRUD operations for JobApplication model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.crud.base import CRUDBase
from backend.models.job_application import JobApplication
from backend.schemas.job_application import JobApplicationCreate, JobApplicationUpdate


class CRUDJobApplication(CRUDBase[JobApplication, JobApplicationCreate, JobApplicationUpdate]):
    """
    CRUD operations for JobApplication model.
    """

    def get_by_user_id(self, db: Session, *, user_id: int) -> List[JobApplication]:
        """
        Get all job applications for a user.
        """
        return db.query(JobApplication).filter(JobApplication.user_id == user_id).all()

    def get_by_user_and_job_opportunity(
        self,
        db: Session,
        *,
        user_id: int,
        job_opportunity_id: int
    ) -> Optional[JobApplication]:
        """
        Get a job application by user ID and job opportunity ID.
        """
        return (
            db.query(JobApplication)
            .filter(
                JobApplication.user_id == user_id,
                JobApplication.job_opportunity_id == job_opportunity_id
            )
            .first()
        )

    def get_by_status(self, db: Session, *, user_id: int, status: str) -> List[JobApplication]:
        """
        Get job applications by status for a user.
        """
        from backend.models.job_application import ApplicationStatus

        status_enum = ApplicationStatus(status)
        return (
            db.query(JobApplication)
            .filter(
                JobApplication.user_id == user_id,
                JobApplication.status == status_enum
            )
            .all()
        )

    def get_applications_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        status: Optional[str] = None,
        job_id: Optional[int] = None,
        job_opportunity_id: Optional[int] = None,
        cv_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobApplication]:
        """
        Get job applications with various filters.
        """
        from backend.models.job_application import ApplicationStatus
        from backend.models.job_opportunity import JobOpportunity
        from sqlalchemy import desc, asc

        query = db.query(JobApplication).filter(JobApplication.user_id == user_id)

        if status:
            query = query.filter(JobApplication.status == ApplicationStatus(status))

        # Support both 'job_id' and 'job_opportunity_id' parameter names
        job_filter_id = job_id or job_opportunity_id
        if job_filter_id:
            query = query.filter(JobApplication.job_opportunity_id == job_filter_id)

        if cv_id:
            query = query.filter(JobApplication.cv_id == cv_id)

        # Search by job title or company (join with JobOpportunity)
        if search:
            search_term = f"%{search}%"
            query = query.join(JobOpportunity).filter(
                or_(
                    JobOpportunity.title.ilike(search_term),
                    JobOpportunity.company.ilike(search_term),
                )
            )

        # Apply sorting
        if sort_by:
            sort_column = getattr(JobApplication, sort_by, JobApplication.created_at)
            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: JobApplicationCreate) -> JobApplication:
        """
        Create a new job application.
        """
        # Check if user already applied to this job opportunity
        existing_application = self.get_by_user_and_job_opportunity(
            db,
            user_id=obj_in.user_id,
            job_opportunity_id=obj_in.job_opportunity_id
        )
        if existing_application:
            raise ValueError(
                f"User {obj_in.user_id} has already applied to job opportunity {obj_in.job_opportunity_id}"
            )

        db_obj = JobApplication(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: JobApplication, obj_in: JobApplicationUpdate) -> JobApplication:
        """
        Update a job application.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(self, db: Session, *, application_id: int, status: str) -> JobApplication:
        """
        Update the status of a job application.
        """
        from backend.models.job_application import ApplicationStatus

        db_obj = self.get(db, id=application_id)
        if db_obj:
            status_enum = ApplicationStatus(status)
            db_obj.status = status_enum
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_application_stats(self, db: Session, *, user_id: int) -> dict:
        """
        Get application statistics for a user.
        """
        from backend.models.job_application import ApplicationStatus

        total_applications = self.count(db, filters={"user_id": user_id})

        stats = {}
        for status in ApplicationStatus:
            count = db.query(JobApplication).filter(
                JobApplication.user_id == user_id,
                JobApplication.status == status
            ).count()
            stats[status.value] = count

        return {
            "total": total_applications,
            **stats
        }

    def get_recent_applications(
        self,
        db: Session,
        *,
        user_id: int,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobApplication]:
        """
        Get recent job applications for a user.
        """
        from sqlalchemy import func

        return (
            db.query(JobApplication)
            .filter(
                JobApplication.user_id == user_id,
                JobApplication.created_at >= func.date_sub(func.now(), days)
            )
            .order_by(JobApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create job application CRUD instance
job_application = CRUDJobApplication(JobApplication)


# ============================================================
# Convenience functions for API routers
# ============================================================

def get_application(db: Session, app_id: int, user_id: int) -> Optional[JobApplication]:
    """Get an application by ID for a specific user."""
    return (
        db.query(JobApplication)
        .filter(JobApplication.id == app_id, JobApplication.user_id == user_id)
        .first()
    )


def get_applications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    **filters,
) -> List[JobApplication]:
    """Get applications with filters."""
    return job_application.get_applications_with_filters(
        db, user_id=user_id, skip=skip, limit=limit, **filters
    )


def create_application(db: Session, user_id: int, app_data: JobApplicationCreate) -> JobApplication:
    """Create a new application."""
    data = app_data.model_dump()
    data['user_id'] = user_id
    return job_application.create(db, obj_in=JobApplicationCreate(**data))


def update_application(
    db: Session,
    app_id: int,
    user_id: int,
    app_data: JobApplicationUpdate,
) -> Optional[JobApplication]:
    """Update an application."""
    app = get_application(db, app_id=app_id, user_id=user_id)
    if not app:
        return None
    return job_application.update(db, db_obj=app, obj_in=app_data)


def delete_application(db: Session, app_id: int, user_id: int) -> bool:
    """Delete an application."""
    app = get_application(db, app_id=app_id, user_id=user_id)
    if not app:
        return False
    db.delete(app)
    db.commit()
    return True


def get_application_stats(db: Session, user_id: int) -> dict:
    """Get application statistics."""
    return job_application.get_application_stats(db, user_id=user_id)

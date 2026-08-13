"""
CRUD operations for JobOpportunity model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from backend.crud.base import CRUDBase
from backend.models.job_opportunity import JobOpportunity
from backend.schemas.job_opportunity import JobOpportunityCreate, JobOpportunityUpdate


class CRUDJobOpportunity(CRUDBase[JobOpportunity, JobOpportunityCreate, JobOpportunityUpdate]):
    """
    CRUD operations for JobOpportunity model.
    """

    def get_by_user_id(self, db: Session, *, user_id: int) -> List[JobOpportunity]:
        """
        Get all job opportunities for a user.
        """
        return db.query(JobOpportunity).filter(JobOpportunity.user_id == user_id).all()

    def get_by_company_and_title(
        self,
        db: Session,
        *,
        company: Optional[str],
        title: str,
        user_id: int
    ) -> Optional[JobOpportunity]:
        """
        Get a job opportunity by company and title for a specific user.
        Handles NULL/empty company values correctly.
        """
        from sqlalchemy import or_, and_

        # Handle NULL/empty company - treat them as equivalent
        if company is not None and company != '':
            # Company is provided and not empty
            company_condition = or_(
                and_(JobOpportunity.company.is_(None), company is None),
                and_(JobOpportunity.company == '', company == ''),
                JobOpportunity.company == company
            )
        else:
            # Company is None or empty - match against NULL or empty strings
            company_condition = or_(
                JobOpportunity.company.is_(None),
                JobOpportunity.company == ''
            )

        return (
            db.query(JobOpportunity)
            .filter(
                company_condition,
                JobOpportunity.title == title,
                JobOpportunity.user_id == user_id
            )
            .first()
        )

    def search_by_keywords(
        self,
        db: Session,
        *,
        user_id: int,
        keywords: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[JobOpportunity]:
        """
        Search job opportunities by keywords in title, company, description, requirements.
        """
        query = db.query(JobOpportunity).filter(JobOpportunity.user_id == user_id)

        # Create a search condition for each keyword
        search_conditions = []
        for keyword in keywords:
            search_condition = or_(
                JobOpportunity.title.ilike(f"%{keyword}%"),
                JobOpportunity.company.ilike(f"%{keyword}%"),
                JobOpportunity.description.ilike(f"%{keyword}%"),
                JobOpportunity.requirements.ilike(f"%{keyword}%")
            )
            search_conditions.append(search_condition)

        # Combine all search conditions with AND
        if search_conditions:
            combined_condition = search_conditions[0]
            for condition in search_conditions[1:]:
                combined_condition = and_(combined_condition, condition)
            query = query.filter(combined_condition)

        return query.offset(skip).limit(limit).all()

    def filter_by_status(
        self,
        db: Session,
        *,
        user_id: int,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobOpportunity]:
        """
        Filter job opportunities by status for a user.
        """
        from backend.models.job_opportunity import JobStatus

        status_enum = JobStatus(status)
        return (
            db.query(JobOpportunity)
            .filter(
                JobOpportunity.user_id == user_id,
                JobOpportunity.status == status_enum
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def filter_by_job_type(
        self,
        db: Session,
        *,
        user_id: int,
        job_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobOpportunity]:
        """
        Filter job opportunities by job type for a user.
        """
        from backend.models.job_opportunity import JobType

        job_type_enum = JobType(job_type)
        return (
            db.query(JobOpportunity)
            .filter(
                JobOpportunity.user_id == user_id,
                JobOpportunity.job_type == job_type_enum
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: JobOpportunityCreate, user_id: int) -> JobOpportunity:
        """
        Create a new job opportunity.
        """
        # Check if user already has a job opportunity with the same title and company
        # Handle None/empty company values properly
        company_to_check = obj_in.company.strip() if obj_in.company and obj_in.company.strip() else None

        existing_job = self.get_by_company_and_title(
            db,
            company=company_to_check,
            title=obj_in.title.strip(),
            user_id=user_id
        )

        if existing_job:
            raise ValueError(
                f"Job opportunity with title '{obj_in.title}' at company '{obj_in.company or 'No company'}' "
                f"already exists for user {user_id}"
            )

        # Convert boolean is_remote to integer for database storage
        job_data = obj_in.model_dump()
        if 'is_remote' in job_data:
            job_data['is_remote'] = int(job_data['is_remote'])

        db_obj = JobOpportunity(**job_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: JobOpportunity, obj_in: JobOpportunityUpdate) -> JobOpportunity:
        """
        Update a job opportunity.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        # Convert boolean is_remote to integer for database if present
        if 'is_remote' in update_data:
            update_data['is_remote'] = int(update_data['is_remote'])

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_jobs_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        company: Optional[str] = None,
        is_remote: Optional[bool] = None,
        search: Optional[str] = None,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> List[JobOpportunity]:
        """
        Get job opportunities with various filters.
        """
        from backend.models.job_opportunity import JobStatus, JobType
        from sqlalchemy import desc, asc

        query = db.query(JobOpportunity).filter(JobOpportunity.user_id == user_id)

        if status:
            try:
                query = query.filter(JobOpportunity.status == JobStatus(status))
            except ValueError:
                # Invalid status value - return empty list
                return []

        if job_type:
            try:
                query = query.filter(JobOpportunity.job_type == JobType(job_type))
            except ValueError:
                # Invalid job_type value - return empty list
                return []

        if company:
            query = query.filter(JobOpportunity.company.ilike(f"%{company}%"))

        if is_remote is not None:
            query = query.filter(JobOpportunity.is_remote == (1 if is_remote else 0))

        # Support both 'search' and 'search_query' parameter names
        search_term = search or search_query
        if search_term:
            query = query.filter(
                or_(
                    JobOpportunity.title.ilike(f"%{search_term}%"),
                    JobOpportunity.company.ilike(f"%{search_term}%"),
                    JobOpportunity.description.ilike(f"%{search_term}%"),
                    JobOpportunity.requirements.ilike(f"%{search_term}%")
                )
            )

        # Apply sorting
        if sort_by:
            sort_column = getattr(JobOpportunity, sort_by, JobOpportunity.created_at)
            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

        return query.offset(skip).limit(limit).all()


# Create job opportunity CRUD instance
job_opportunity = CRUDJobOpportunity(JobOpportunity)


# ============================================================
# Convenience functions for API routers
# ============================================================

def get_job(db: Session, job_id: int, user_id: int) -> Optional[JobOpportunity]:
    """Get a job by ID for a specific user."""
    return (
        db.query(JobOpportunity)
        .filter(JobOpportunity.id == job_id, JobOpportunity.user_id == user_id)
        .first()
    )


def get_jobs(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    **filters,
) -> List[JobOpportunity]:
    """Get jobs with filters."""
    return job_opportunity.get_jobs_with_filters(
        db, user_id=user_id, skip=skip, limit=limit, **filters
    )


def create_job(db: Session, user_id: int, job_data: JobOpportunityCreate) -> JobOpportunity:
    """Create a new job opportunity."""
    return job_opportunity.create(db, obj_in=job_data, user_id=user_id)


def update_job(
    db: Session,
    job_id: int,
    user_id: int,
    job_data: JobOpportunityUpdate,
) -> Optional[JobOpportunity]:
    """Update a job opportunity."""
    job = get_job(db, job_id=job_id, user_id=user_id)
    if not job:
        return None
    return job_opportunity.update(db, db_obj=job, obj_in=job_data)


def delete_job(db: Session, job_id: int, user_id: int) -> bool:
    """Delete a job opportunity."""
    job = get_job(db, job_id=job_id, user_id=user_id)
    if not job:
        return False
    db.delete(job)
    db.commit()
    return True


def get_job_stats(db: Session, user_id: int) -> dict:
    """Get job statistics."""
    return job_opportunity.get_jobs_with_filters(db, user_id=user_id)

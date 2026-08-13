"""
CRUD operations for CVJobMatch model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.crud.base import CRUDBase
from backend.models.cv_job_match import CVJobMatch
from backend.schemas.cv_job_match import CVJobMatchCreate, CVJobMatchUpdate


class CRUDCVJobMatch(CRUDBase[CVJobMatch, CVJobMatchCreate, CVJobMatchUpdate]):
    """
    CRUD operations for CVJobMatch model.
    """

    def get_by_user_id(self, db: Session, *, user_id: int) -> List[CVJobMatch]:
        """
        Get all CV-job matches for a user.
        """
        return db.query(CVJobMatch).filter(CVJobMatch.user_id == user_id).all()

    def get_by_cv_and_job(
        self,
        db: Session,
        *,
        user_id: int,
        cv_id: int,
        job_opportunity_id: int
    ) -> Optional[CVJobMatch]:
        """
        Get a CV-job match by CV ID and job opportunity ID for a user.
        """
        return (
            db.query(CVJobMatch)
            .filter(
                CVJobMatch.user_id == user_id,
                CVJobMatch.cv_id == cv_id,
                CVJobMatch.job_opportunity_id == job_opportunity_id
            )
            .first()
        )

    def get_matches_by_cv(self, db: Session, *, cv_id: int) -> List[CVJobMatch]:
        """
        Get all matches for a specific CV.
        """
        return db.query(CVJobMatch).filter(CVJobMatch.cv_id == cv_id).all()

    def get_matches_by_job(self, db: Session, *, job_opportunity_id: int) -> List[CVJobMatch]:
        """
        Get all matches for a specific job opportunity.
        """
        return db.query(CVJobMatch).filter(CVJobMatch.job_opportunity_id == job_opportunity_id).all()

    def get_top_matches_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        limit: int = 10
    ) -> List[CVJobMatch]:
        """
        Get top matching jobs for a user's CVs (highest match scores).
        """
        return (
            db.query(CVJobMatch)
            .filter(CVJobMatch.user_id == user_id)
            .order_by(CVJobMatch.match_score.desc())
            .limit(limit)
            .all()
        )

    def get_matches_by_score_range(
        self,
        db: Session,
        *,
        user_id: int,
        min_score: float,
        max_score: float
    ) -> List[CVJobMatch]:
        """
        Get matches within a specific score range for a user.
        """
        return (
            db.query(CVJobMatch)
            .filter(
                CVJobMatch.user_id == user_id,
                CVJobMatch.match_score >= min_score,
                CVJobMatch.match_score <= max_score
            )
            .order_by(CVJobMatch.match_score.desc())
            .all()
        )

    def create(self, db: Session, *, obj_in: CVJobMatchCreate) -> CVJobMatch:
        """
        Create a new CV-job match.
        """
        # Check if match already exists
        existing_match = self.get_by_cv_and_job(
            db,
            user_id=obj_in.user_id,
            cv_id=obj_in.cv_id,
            job_opportunity_id=obj_in.job_opportunity_id
        )
        if existing_match:
            raise ValueError(
                f"CV-job match already exists for user {obj_in.user_id}, "
                f"CV {obj_in.cv_id}, and job opportunity {obj_in.job_opportunity_id}"
            )

        db_obj = CVJobMatch(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: CVJobMatch, obj_in: CVJobMatchUpdate) -> CVJobMatch:
        """
        Update a CV-job match.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_matches_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        cv_id: Optional[int] = None,
        job_opportunity_id: Optional[int] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        sort_by: str = "match_score",
        order: str = "desc",
        skip: int = 0,
        limit: int = 100
    ) -> List[CVJobMatch]:
        """
        Get matches with various filters.
        """
        from sqlalchemy import desc, asc

        query = db.query(CVJobMatch).filter(CVJobMatch.user_id == user_id)

        if cv_id:
            query = query.filter(CVJobMatch.cv_id == cv_id)

        if job_opportunity_id:
            query = query.filter(CVJobMatch.job_opportunity_id == job_opportunity_id)

        if min_score is not None:
            query = query.filter(CVJobMatch.match_score >= min_score)

        if max_score is not None:
            query = query.filter(CVJobMatch.match_score <= max_score)

        # Apply sorting
        if sort_by == "match_score":
            if order == "desc":
                query = query.order_by(desc(CVJobMatch.match_score))
            else:
                query = query.order_by(asc(CVJobMatch.match_score))
        elif sort_by == "created_at":
            if order == "desc":
                query = query.order_by(desc(CVJobMatch.created_at))
            else:
                query = query.order_by(asc(CVJobMatch.created_at))

        return query.offset(skip).limit(limit).all()

    def get_match_statistics(self, db: Session, *, user_id: int) -> dict:
        """
        Get match statistics for a user.
        """
        from sqlalchemy import func

        # Total matches
        total_matches = self.count(db, filters={"user_id": user_id})

        # Average match score
        avg_score = (
            db.query(func.avg(CVJobMatch.match_score))
            .filter(CVJobMatch.user_id == user_id)
            .scalar()
        ) or 0.0

        # High matches (score >= 80)
        high_matches = (
            db.query(CVJobMatch)
            .filter(
                CVJobMatch.user_id == user_id,
                CVJobMatch.match_score >= 80
            )
            .count()
        )

        # Medium matches (score >= 60 and < 80)
        medium_matches = (
            db.query(CVJobMatch)
            .filter(
                CVJobMatch.user_id == user_id,
                CVJobMatch.match_score >= 60,
                CVJobMatch.match_score < 80
            )
            .count()
        )

        # Low matches (score < 60)
        low_matches = (
            db.query(CVJobMatch)
            .filter(
                CVJobMatch.user_id == user_id,
                CVJobMatch.match_score < 60
            )
            .count()
        )

        return {
            "total_matches": total_matches,
            "average_score": round(avg_score, 2),
            "high_matches": high_matches,  # 80-100
            "medium_matches": medium_matches,  # 60-79
            "low_matches": low_matches  # 0-59
        }

    def get_top_matches_for_cv(
        self,
        db: Session,
        *,
        cv_id: int,
        limit: int = 10
    ) -> List[CVJobMatch]:
        """
        Get top matching jobs for a specific CV.
        """
        return (
            db.query(CVJobMatch)
            .filter(CVJobMatch.cv_id == cv_id)
            .order_by(CVJobMatch.match_score.desc())
            .limit(limit)
            .all()
        )

    def get_cv_improvement_suggestions(
        self,
        db: Session,
        *,
        cv_id: int
    ) -> dict:
        """
        Get improvement suggestions based on match analysis for a CV.
        """
        from sqlalchemy import func

        # Get all matches for this CV
        matches = self.get_matches_by_cv(db, cv_id=cv_id)

        if not matches:
            return {}

        # Calculate average scores for different categories
        total_skills = sum(m.skills_match_score or 0 for m in matches if m.skills_match_score is not None)
        total_experience = sum(m.experience_match_score or 0 for m in matches if m.experience_match_score is not None)
        total_education = sum(m.education_match_score or 0 for m in matches if m.education_match_score is not None)
        total_keywords = sum(m.keywords_match_score or 0 for m in matches if m.keywords_match_score is not None)

        count = len(matches)
        avg_skills = total_skills / count if count > 0 else 0
        avg_experience = total_experience / count if count > 0 else 0
        avg_education = total_education / count if count > 0 else 0
        avg_keywords = total_keywords / count if count > 0 else 0

        return {
            "skills_score": round(avg_skills, 2),
            "experience_score": round(avg_experience, 2),
            "education_score": round(avg_education, 2),
            "keywords_score": round(avg_keywords, 2),
            "recommendations": [
                f"Focus on improving skills match (current avg: {avg_skills:.1f}/100)" if avg_skills < 70 else "",
                f"Highlight more relevant experience (current avg: {avg_experience:.1f}/100)" if avg_experience < 70 else "",
                f"Emphasize educational qualifications (current avg: {avg_education:.1f}/100)" if avg_education < 70 else "",
                f"Include more relevant keywords (current avg: {avg_keywords:.1f}/100)" if avg_keywords < 70 else ""
            ]
        }


# Create CV-job match CRUD instance
cv_job_match = CRUDCVJobMatch(CVJobMatch)

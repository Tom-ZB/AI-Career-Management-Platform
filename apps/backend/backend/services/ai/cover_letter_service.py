"""
AI Cover Letter Service - Generate tailored cover letters.
"""
from typing import Optional
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate

from backend.services.ai.llm_factory import LLMFactory
from backend.models.cv import CV
from backend.models.job_opportunity import JobOpportunity
from backend.models.job_application import JobApplication
from backend.models.career_profile import CareerProfile
from backend.schemas.cv_job_match import CoverLetterRequest, CoverLetterResponse


COVER_LETTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a professional cover letter writer. Write a compelling,
    personalized cover letter that connects the candidate's experience to the job requirements.

    The cover letter should:
    - Be professional and enthusiastic
    - Highlight 2-3 specific experiences that match the job
    - Be concise (300-400 words)
    - Include a clear call to action
    - Use the {tone} tone"""),
    ("human", """Write a cover letter for:

    CANDIDATE PROFILE:
    {profile_data}

    JOB TITLE: {job_title}
    COMPANY: {company}

    JOB DESCRIPTION:
    {job_description}

    ADDITIONAL NOTES:
    {additional_notes}"""),
])


class AICoverLetterService:
    """Service for AI-powered cover letter generation."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMFactory.get_llm(temperature=0.7)

    async def generate(self, user_id: int, request: CoverLetterRequest) -> CoverLetterResponse:
        """
        Generate a tailored cover letter.

        Args:
            user_id: The authenticated user's ID
            request: Cover letter request with cv_id and job_id

        Returns:
            CoverLetterResponse with generated cover letter
        """
        cv = self.db.query(CV).filter(CV.id == request.cv_id, CV.user_id == user_id).first()
        if not cv:
            raise ValueError("CV not found")

        job = (
            self.db.query(JobOpportunity)
            .filter(JobOpportunity.id == request.job_id, JobOpportunity.user_id == user_id)
            .first()
        )
        if not job:
            raise ValueError("Job opportunity not found")

        profile = (
            self.db.query(CareerProfile)
            .filter(CareerProfile.user_id == user_id)
            .first()
        )

        profile_data = {
            "full_name": profile.full_name if profile else "Candidate",
            "title": profile.title if profile else "",
            "summary": profile.summary if profile else "",
            "skills": profile.skills if profile else [],
            "work_experience": profile.work_experience if profile else [],
        }

        # Generate cover letter
        chain = COVER_LETTER_PROMPT | self.llm
        result = await chain.ainvoke({
            "profile_data": str(profile_data),
            "job_title": job.title,
            "company": job.company or "the company",
            "job_description": (job.description or "")[:4000],
            "tone": request.tone or "professional",
            "additional_notes": request.additional_notes or "None",
        })

        # Save to application if exists
        application = (
            self.db.query(JobApplication)
            .filter(
                JobApplication.job_opportunity_id == job.id,
                JobApplication.user_id == user_id,
            )
            .first()
        )

        if application:
            application.cover_letter_content = result.content
            application.cover_letter_ai_generated = True
            self.db.commit()

        return CoverLetterResponse(
            content=result.content,
            cv_id=cv.id,
            job_id=job.id,
            job_title=job.title,
            company=job.company or "",
            application_id=application.id if application else None,
        )
"""
AI Interview Service - Interview preparation and question generation.
"""
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.services.ai.llm_factory import LLMFactory
from backend.models.interview import Interview
from backend.models.job_application import JobApplication


INTERVIEW_PREP_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert interview coach. Generate comprehensive interview
    preparation materials based on the job and interview details.

    Provide:
    1. Common questions for this interview type and role
    2. Role-specific technical questions (if applicable)
    3. Behavioral questions relevant to the position
    4. Questions the candidate should ask the interviewer
    5. Preparation tips specific to this interview
    6. Key points to emphasize based on the job description

    Return a structured JSON object with these sections."""),
    ("human", """Generate interview preparation for:

    INTERVIEW TYPE: {interview_type}
    JOB TITLE: {job_title}
    COMPANY: {company}
    JOB DESCRIPTION: {job_description}
    CANDIDATE BACKGROUND: {candidate_background}"""),
])


class AIInterviewService:
    """Service for AI-powered interview preparation."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMFactory.get_llm(temperature=0.7)

    async def generate_prep(self, user_id: int, interview_id: int) -> dict:
        """
        Generate interview preparation materials.

        Args:
            user_id: The authenticated user's ID
            interview_id: The interview ID to prepare for

        Returns:
            Dictionary with preparation materials
        """
        interview = (
            self.db.query(Interview)
            .filter(Interview.id == interview_id, Interview.user_id == user_id)
            .first()
        )
        if not interview:
            raise ValueError("Interview not found")

        application = (
            self.db.query(JobApplication)
            .filter(JobApplication.id == interview.application_id)
            .first()
        )

        if not application:
            raise ValueError("Associated application not found")

        from backend.models.job_opportunity import JobOpportunity
        from backend.models.career_profile import CareerProfile

        job = (
            self.db.query(JobOpportunity)
            .filter(JobOpportunity.id == application.job_opportunity_id)
            .first()
        )

        profile = (
            self.db.query(CareerProfile)
            .filter(CareerProfile.user_id == user_id)
            .first()
        )

        candidate_background = str({
            "title": profile.title if profile else "",
            "skills": profile.skills if profile else [],
            "experience": profile.work_experience if profile else [],
        })

        chain = INTERVIEW_PREP_PROMPT | self.llm | JsonOutputParser()
        result = await chain.ainvoke({
            "interview_type": interview.interview_type.value,
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "Unknown",
            "job_description": (job.description or "")[:4000] if job else "",
            "candidate_background": candidate_background,
        })

        # Save prep to interview
        interview.ai_prep_questions = result
        interview.ai_prep_tips = result.get("preparation_tips", "")
        self.db.commit()

        return result
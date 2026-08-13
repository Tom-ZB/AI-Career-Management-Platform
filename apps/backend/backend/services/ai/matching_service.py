"""
AI Matching Service - CV to Job Description matching.
"""
from typing import Dict
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.services.ai.llm_factory import LLMFactory
from backend.models.cv import CV
from backend.models.job_opportunity import JobOpportunity
from backend.models.cv_job_match import CVJobMatch
from backend.schemas.cv_job_match import MatchRequest, MatchResponse, CoverLetterRequest, CoverLetterResponse


# CV-Job Matching Prompt
MATCHING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert recruitment AI. Analyze how well a candidate's CV
    matches a job description. Be thorough and objective.

    Evaluate the match on these dimensions (score 0-100 for each):
    1. Skills Match: How well do the candidate's skills match the required skills?
    2. Experience Match: How relevant is the candidate's experience?
    3. Education Match: Does the candidate meet the education requirements?
    4. Keywords Match: How well do the keywords align?

    Also provide:
    - Overall match score (0-100)
    - Strengths: What makes this candidate a good fit
    - Gaps: What requirements are not met
    - Recommendation: Should they apply? (strong_match/good_match/possible/reach)
    - Tips: Specific suggestions to improve the match

    Return a JSON object with the analysis."""),
    ("human", """Match this CV against the job description:

    CV CONTENT:
    {cv_content}

    JOB DESCRIPTION:
    {job_description}

    JOB REQUIREMENTS:
    {job_requirements}"""),
])

# Cover Letter Prompt
COVER_LETTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a professional cover letter writer. Write a compelling,
    personalized cover letter that connects the candidate's experience to the job requirements.

    The cover letter should:
    - Be professional and enthusiastic
    - Highlight 2-3 specific experiences that match the job
    - Address the hiring manager if possible
    - Be concise (300-400 words)
    - Include a clear call to action"""),
    ("human", """Write a cover letter for:

    CANDIDATE PROFILE:
    {profile_data}

    JOB TITLE: {job_title}
    COMPANY: {company}

    JOB DESCRIPTION:
    {job_description}

    MATCH ANALYSIS:
    {match_analysis}"""),
])


class AIMatchingService:
    """Service for AI-powered CV-Job matching."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMFactory.get_llm(temperature=0.3)

    async def match(self, user_id: int, request: MatchRequest) -> MatchResponse:
        """
        Match a CV against a job description.

        Args:
            user_id: The authenticated user's ID
            request: Match request with cv_id and job_id

        Returns:
            MatchResponse with detailed matching analysis
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

        cv_content = cv.content_text or cv.ai_summary or ""
        job_description = job.description or ""
        job_requirements = job.requirements or ""

        # Run matching analysis
        chain = MATCHING_PROMPT | self.llm | JsonOutputParser()
        result = await chain.ainvoke({
            "cv_content": cv_content[:5000],
            "job_description": job_description[:5000],
            "job_requirements": job_requirements[:3000],
        })

        # Save match result to database
        match = CVJobMatch(
            user_id=user_id,
            cv_id=cv.id,
            job_opportunity_id=job.id,
            match_score=result.get("overall_score", 0),
            skills_match_score=result.get("skills_match", {}).get("score", 0),
            experience_match_score=result.get("experience_match", {}).get("score", 0),
            education_match_score=result.get("education_match", {}).get("score", 0),
            keywords_match_score=result.get("keywords_match", {}).get("score", 0),
            match_details=result,
            ai_analysis=result,
            ai_recommendation=result.get("recommendation", ""),
        )
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)

        return MatchResponse(
            match_id=match.id,
            cv_id=cv.id,
            job_id=job.id,
            overall_score=result.get("overall_score", 0),
            skills_score=result.get("skills_match", {}).get("score", 0),
            experience_score=result.get("experience_match", {}).get("score", 0),
            education_score=result.get("education_match", {}).get("score", 0),
            keywords_score=result.get("keywords_match", {}).get("score", 0),
            strengths=result.get("strengths", []),
            gaps=result.get("gaps", []),
            recommendation=result.get("recommendation", ""),
            tips=result.get("tips", []),
            details=result,
        )


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
        from backend.models.career_profile import CareerProfile

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

        # Get existing match analysis if available
        match = (
            self.db.query(CVJobMatch)
            .filter(
                CVJobMatch.cv_id == cv.id,
                CVJobMatch.job_opportunity_id == job.id,
            )
            .order_by(CVJobMatch.created_at.desc())
            .first()
        )

        match_analysis = str(match.ai_analysis) if match else "No prior analysis available"

        # Generate cover letter
        chain = COVER_LETTER_PROMPT | self.llm
        result = await chain.ainvoke({
            "profile_data": str(profile_data),
            "job_title": job.title,
            "company": job.company or "the company",
            "job_description": (job.description or "")[:4000],
            "match_analysis": match_analysis,
        })

        # Save cover letter to application if exists
        from backend.models.job_application import JobApplication
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
            company=job.company,
            application_id=application.id if application else None,
        )
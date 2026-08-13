"""
AI CV Service - CV analysis, parsing, and generation.
"""
from typing import Dict, Optional
from pathlib import Path
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.config import settings
from backend.services.ai.llm_factory import LLMFactory
from backend.models.cv import CV
from backend.schemas.cv import CVAnalysisResponse, CVGenerationRequest, CVGenerationResponse
from backend.services.document_parser import DocumentParser


def extract_text_from_file(file_path: str, content_type: Optional[str] = None) -> str:
    """
    Extract text content from a local file (PDF, DOCX, or TXT).

    Args:
        file_path: Path to the file
        content_type: MIME type of the file (optional)

    Returns:
        Extracted text content
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read file bytes
    with open(path, "rb") as f:
        file_bytes = f.read()

    # Parse using DocumentParser
    file_name = path.name
    return DocumentParser.parse(file_bytes, content_type, file_name)


# CV Analysis Prompt
CV_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert CV/resume analyst. Analyze the given CV content and provide structured feedback.

    Evaluate the CV on these dimensions (score 1-10 for each):
    1. Structure & Formatting: Is the CV well-organized and easy to read?
    2. Content Quality: Are the descriptions clear, impactful, and quantify achievements?
    3. Keywords & ATS Optimization: Does it include relevant keywords for ATS systems?
    4. Length & Conciseness: Is the length appropriate?
    5. Grammar & Language: Are there any grammar or language issues?

    Also provide:
    - Strengths: What the CV does well
    - Weaknesses: Areas for improvement
    - Suggestions: Specific actionable improvements
    - Keywords: Important keywords found in the CV
    - Overall Score: 0-100

    Return the analysis as a JSON object."""),
    ("human", "Analyze this CV:\n\n{cv_content}"),
])

# CV Generation Prompt
CV_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert CV writer. Create a tailored CV that highlights
    the most relevant experience and skills for a specific job.

    Use the candidate's master profile information and tailor it to match the job requirements.
    The CV should be professional, ATS-friendly, and highlight the best matches between
    the candidate's background and the job requirements."""),
    ("human", """Create a tailored CV based on:

    CANDIDATE PROFILE:
    {profile_data}

    JOB DESCRIPTION:
    {job_description}

    Generate a structured CV in JSON format with sections:
    - professional_summary
    - skills (array of relevant skills)
    - work_experience (array of tailored experience entries)
    - education
    - certifications
    - key_achievements"""),
])


class AICVService:
    """Service for AI-powered CV operations."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMFactory.get_llm(temperature=0.3)

    async def analyze_cv(self, user_id: int, cv_id: int) -> CVAnalysisResponse:
        """
        Analyze a CV and provide structured feedback.

        Args:
            user_id: The authenticated user's ID
            cv_id: The CV ID to analyze

        Returns:
            CVAnalysisResponse with detailed analysis
        """
        cv = self.db.query(CV).filter(CV.id == cv_id, CV.user_id == user_id).first()
        if not cv:
            raise ValueError("CV not found")

        # Get CV content
        cv_content = cv.content_text or ""

        # If no content is available directly, try to extract from file if present
        if not cv_content and cv.file_path:
            try:
                # Try to extract text from the uploaded file (local path)
                cv_content = extract_text_from_file(cv.file_path, cv.file_type)

            except FileNotFoundError:
                raise ValueError(f"CV file not found at: {cv.file_path}")
            except Exception as e:
                # If we can't extract content from file, raise an error
                raise ValueError(f"Failed to parse CV file: {str(e)}. Please ensure the file is a valid PDF or DOCX document.")

        if not cv_content:
            raise ValueError("CV has no parseable content")

        # Run AI analysis
        chain = CV_ANALYSIS_PROMPT | self.llm | JsonOutputParser()
        result = await chain.ainvoke({"cv_content": cv_content[:8000]})  # Limit input size

        # Update CV with analysis results - save extracted text content too
        if not cv.content_text and cv_content:
            cv.content_text = cv_content[:100000]  # Limit to 100KB

        # Handle keywords - AI might return as string or list
        keywords = result.get("keywords", [])
        if isinstance(keywords, str):
            # If it's a comma-separated string, convert to list
            keywords = [k.strip() for k in keywords.split(",") if k.strip()]
        elif not isinstance(keywords, list):
            keywords = []

        cv.ai_keywords = keywords

        # Handle ai_summary - must be a string for Text column
        summary_value = result.get("summary", result.get("strengths", result.get("Strengths", "")))
        if isinstance(summary_value, list):
            # Convert list of strings to a single joined string
            cv.ai_summary = "\n".join(summary_value) if summary_value else ""
        else:
            cv.ai_summary = str(summary_value) if summary_value else ""

        # Handle ai_score - ensure it's an integer
        score_value = result.get("overall_score", result.get("Overall Score", 0))
        try:
            cv.ai_score = int(score_value) if score_value else 0
        except (ValueError, TypeError):
            cv.ai_score = 0

        cv.ai_parsed_data = result
        self.db.commit()

        return CVAnalysisResponse(
            cv_id=cv_id,
            overall_score=result.get("overall_score", result.get("Overall Score", 0)),
            dimensions=result.get("dimensions", {}),
            strengths=result.get("strengths", result.get("Strengths", [])),
            weaknesses=result.get("weaknesses", result.get("Weaknesses", [])),
            suggestions=result.get("suggestions", result.get("Suggestions", [])),
            keywords=keywords,
        )

    async def generate_tailored_cv(
        self, user_id: int, request: CVGenerationRequest
    ) -> CVGenerationResponse:
        """
        Generate a tailored CV for a specific job.

        Args:
            user_id: The authenticated user's ID
            request: CV generation request with profile and job info

        Returns:
            CVGenerationResponse with the generated CV
        """
        # Get profile data
        from backend.models.career_profile import CareerProfile
        profile = (
            self.db.query(CareerProfile)
            .filter(CareerProfile.user_id == user_id)
            .first()
        )

        if not profile:
            raise ValueError("Career profile not found. Please create one first.")

        # Get job description
        from backend.models.job_opportunity import JobOpportunity
        job = (
            self.db.query(JobOpportunity)
            .filter(
                JobOpportunity.id == request.job_id,
                JobOpportunity.user_id == user_id,
            )
            .first()
        )

        if not job:
            raise ValueError("Job opportunity not found")

        profile_data = {
            "full_name": profile.full_name,
            "title": profile.title,
            "summary": profile.summary,
            "skills": profile.skills,
            "experience_years": profile.experience_years,
            "work_experience": profile.work_experience,
            "education": profile.education,
        }

        job_description = job.description or ""
        if job.requirements:
            job_description += f"\n\nRequirements:\n{job.requirements}"

        # Generate tailored CV
        chain = CV_GENERATION_PROMPT | self.llm | JsonOutputParser()
        result = await chain.ainvoke({
            "profile_data": str(profile_data),
            "job_description": job_description[:6000],
        })

        # Create a new CV record
        new_cv = CV(
            user_id=user_id,
            career_profile_id=profile.id,
            title=f"Tailored CV - {job.title} at {job.company}",
            description=f"AI-generated tailored CV for {job.title} position",
            is_ai_generated=True,
            target_job_title=job.title,
            target_company=job.company,
            ai_parsed_data=result,
            content_text=str(result),
        )
        self.db.add(new_cv)
        self.db.commit()
        self.db.refresh(new_cv)

        return CVGenerationResponse(
            cv_id=new_cv.id,
            title=new_cv.title,
            content=result,
            generated_for={
                "job_id": job.id,
                "job_title": job.title,
                "company": job.company,
            },
        )
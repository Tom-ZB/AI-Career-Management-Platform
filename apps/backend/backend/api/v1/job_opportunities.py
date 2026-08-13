"""
Job Opportunities API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.job_opportunity import (
    JobOpportunityCreate, JobOpportunityUpdate,
    JobOpportunityResponse, JobOpportunityListResponse,
)
from backend.crud.job_opportunity import (
    get_job, get_jobs, create_job, update_job, delete_job,
    get_job_stats,
)

router = APIRouter()


@router.get("/", response_model=List[JobOpportunityListResponse])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    company: Optional[str] = None,
    search: Optional[str] = None,
    is_remote: Optional[bool] = None,
    sort_by: Optional[str] = Query(None, pattern="^(created_at|title|company|deadline)$"),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all job opportunities for the current user with optional filters."""
    return get_jobs(
        db, user_id=current_user.id,
        skip=skip, limit=limit,
        status=status, job_type=job_type,
        company=company, search=search,
        is_remote=is_remote,
        sort_by=sort_by, sort_order=sort_order,
    )


@router.post("/", response_model=JobOpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_new_job(
    job_data: JobOpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job opportunity."""
    return create_job(db, user_id=current_user.id, job_data=job_data)


@router.get("/stats", response_model=dict)
def get_job_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get job opportunity statistics."""
    return get_job_stats(db, user_id=current_user.id)


@router.get("/{job_id}", response_model=JobOpportunityResponse)
def get_job_by_id(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific job opportunity."""
    job = get_job(db, job_id=job_id, user_id=current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job opportunity not found")
    return job


@router.put("/{job_id}", response_model=JobOpportunityResponse)
def update_job_by_id(
    job_id: int,
    job_data: JobOpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a job opportunity."""
    job = update_job(db, job_id=job_id, user_id=current_user.id, job_data=job_data)
    if not job:
        raise HTTPException(status_code=404, detail="Job opportunity not found")
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_by_id(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job opportunity."""
    success = delete_job(db, job_id=job_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job opportunity not found")


@router.post("/{job_id}/analyze", response_model=dict)
async def analyze_job_description(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run AI analysis on a job description."""
    from backend.models.job_opportunity import JobOpportunity
    from backend.services.ai.llm_factory import LLMFactory
    from langchain_core.prompts import ChatPromptTemplate

    job = db.query(JobOpportunity).filter(
        JobOpportunity.id == job_id,
        JobOpportunity.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    llm = LLMFactory.get_llm()
    prompt = ChatPromptTemplate.from_template("""Analyze this job description and provide:
    1. Key skills required
    2. Experience level needed
    3. Key responsibilities
    4. Company insights (if available)
    5. Application tips

    Job Description:
    {job_description}

    Requirements:
    {requirements}

    Provide a structured analysis in JSON format.""")

    chain = prompt | llm
    result = await chain.ainvoke({
        "job_description": job.description or "",
        "requirements": job.requirements or ""
    })

    return {
        "job_id": job_id,
        "title": job.title,
        "company": job.company,
        "analysis": result.content
    }
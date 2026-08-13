"""
API v1 Router - Aggregates all endpoint routers.
"""
from fastapi import APIRouter
from backend.api.v1 import (
    auth,
    users,
    career_profiles,
    cvs,
    documents,
    job_opportunities,
    job_applications,
    interviews,
    follow_ups,
    ai,
    analytics,
    export,
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.auth_router, prefix="/auth", tags=["Authentication"])

# Users
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Career Profiles
api_router.include_router(career_profiles.router, prefix="/profiles", tags=["Career Profiles"])

# CVs
api_router.include_router(cvs.router, prefix="/cvs", tags=["CVs"])

# Documents
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

# Job Opportunities
api_router.include_router(job_opportunities.router, prefix="/jobs", tags=["Job Opportunities"])

# Job Applications
api_router.include_router(job_applications.router, prefix="/applications", tags=["Job Applications"])

# Interviews
api_router.include_router(interviews.router, prefix="/interviews", tags=["Interviews"])

# Follow-ups
api_router.include_router(follow_ups.router, prefix="/follow-ups", tags=["Follow-ups"])

# AI Features
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])

# Analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Export
api_router.include_router(export.router, prefix="/export", tags=["Export"])
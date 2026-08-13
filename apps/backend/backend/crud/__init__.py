"""
Package initialization for CRUD operations.
"""
from backend.crud.user import user
from backend.crud.career_profile import career_profile
from backend.crud.cv import cv
from backend.crud.job_opportunity import job_opportunity
from backend.crud.job_application import job_application
from backend.crud.interview import interview
from backend.crud.follow_up import follow_up
from backend.crud.document import document
from backend.crud.cv_job_match import cv_job_match
from backend.crud.chat_message import chat_message

__all__ = [
    "user",
    "career_profile",
    "cv",
    "job_opportunity",
    "job_application",
    "interview",
    "follow_up",
    "document",
    "cv_job_match",
    "chat_message",
]

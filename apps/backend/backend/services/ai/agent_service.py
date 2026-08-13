"""
AI Agent Service - Executes AI agent actions on user data.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.services.ai.llm_factory import LLMFactory
from backend.models.ai_agent_actions import AIAgentAction


# Agent Action Prompt
AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI Career Management Agent. You can perform actions on
    the user's career data to help them manage their job search.

    Available action types:
    1. "summarize_applications" - Summarize recent job applications
    2. "suggest_follow_ups" - Suggest follow-ups for stale applications
    3. "analyze_trends" - Analyze application trends and patterns
    4. "recommend_jobs" - Recommend which jobs to prioritize
    5. "identify_skill_gaps" - Identify skills gaps from job descriptions
    6. "optimize_schedule" - Optimize interview/follow-up schedule

    When performing an action, you should:
    1. Understand what data is needed
    2. Analyze the data
    3. Provide actionable insights and recommendations
    4. Be specific and data-driven

    Current date: {current_date}"""),
    ("human", "Perform this action: {action_type}\n\nAdditional context: {context}"),
])


class AIAgentService:
    """Service for AI agent actions."""

    # Define available actions and their descriptions
    AVAILABLE_ACTIONS = {
        "summarize_applications": "Summarize recent job applications and their status",
        "suggest_follow_ups": "Suggest follow-ups for applications that haven't had recent activity",
        "analyze_trends": "Analyze application trends (response rate, interview rate, etc.)",
        "recommend_jobs": "Recommend which jobs to prioritize based on match scores and deadlines",
        "identify_skill_gaps": "Identify skills gaps by analyzing job descriptions of target roles",
        "optimize_schedule": "Optimize upcoming interview and follow-up schedule",
    }

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMFactory.get_llm(temperature=0.5)

    async def execute_action(
        self, user_id: int, action_type: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute an AI agent action.

        Args:
            user_id: The authenticated user's ID
            action_type: Type of action to perform
            params: Optional parameters for the action

        Returns:
            Dictionary with action results
        """
        if action_type not in self.AVAILABLE_ACTIONS:
            raise ValueError(f"Unknown action type: {action_type}. Available: {list(self.AVAILABLE_ACTIONS.keys())}")

        # Log the action
        action_log = AIAgentAction(
            user_id=user_id,
            session_id=f"agent_{user_id}",
            action_type=action_type,
            action_input=params or {},
            action_status="running",
        )
        self.db.add(action_log)
        self.db.commit()

        try:
            # Gather relevant data based on action type
            context = await self._gather_context(user_id, action_type, params)

            # Execute the action with AI
            from datetime import datetime
            chain = AGENT_PROMPT | self.llm | JsonOutputParser()
            result = await chain.ainvoke({
                "action_type": action_type,
                "context": str(context),
                "current_date": datetime.utcnow().strftime("%Y-%m-%d"),
            })

            # Update action log
            action_log.action_output = result
            action_log.action_status = "completed"
            action_log.completed_at = datetime.utcnow()
            self.db.commit()

            return {
                "action_type": action_type,
                "description": self.AVAILABLE_ACTIONS[action_type],
                "result": result,
                "status": "completed",
            }

        except Exception as e:
            # Update action log with error
            action_log.action_status = "failed"
            action_log.action_output = {"error": str(e)}
            self.db.commit()
            raise

    async def _gather_context(
        self, user_id: int, action_type: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Gather relevant data for the action."""
        from backend.models.job_application import JobApplication
        from backend.models.job_opportunity import JobOpportunity
        from backend.models.interview import Interview
        from backend.models.follow_up import FollowUp
        from backend.models.cv_job_match import CVJobMatch
        from datetime import datetime, timedelta

        context = {}

        if action_type in ["summarize_applications", "analyze_trends", "recommend_jobs"]:
            # Get applications with job info
            applications = (
                self.db.query(JobApplication)
                .filter(JobApplication.user_id == user_id)
                .order_by(JobApplication.created_at.desc())
                .limit(50)
                .all()
            )
            context["applications"] = [
                {
                    "id": a.id,
                    "status": a.status.value if a.status else None,
                    "application_date": str(a.application_date) if a.application_date else None,
                    "job_id": a.job_opportunity_id,
                }
                for a in applications
            ]

        if action_type in ["recommend_jobs", "identify_skill_gaps"]:
            # Get jobs with match scores
            jobs = (
                self.db.query(JobOpportunity)
                .filter(JobOpportunity.user_id == user_id)
                .all()
            )
            context["jobs"] = [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company,
                    "status": j.status.value if j.status else None,
                    "deadline": str(j.deadline) if j.deadline else None,
                    "description": (j.description or "")[:500],
                }
                for j in jobs
            ]

        if action_type in ["suggest_follow_ups", "optimize_schedule"]:
            # Get follow-ups and interviews
            follow_ups = (
                self.db.query(FollowUp)
                .filter(FollowUp.user_id == user_id, FollowUp.status == "pending")
                .all()
            )
            interviews = (
                self.db.query(Interview)
                .filter(
                    Interview.user_id == user_id,
                    Interview.scheduled_at >= datetime.utcnow(),
                )
                .order_by(Interview.scheduled_at.asc())
                .all()
            )
            context["follow_ups"] = [
                {"id": f.id, "type": f.follow_up_type.value, "scheduled_at": str(f.scheduled_at)}
                for f in follow_ups
            ]
            context["upcoming_interviews"] = [
                {"id": i.id, "type": i.interview_type.value, "scheduled_at": str(i.scheduled_at)}
                for i in interviews
            ]

        if action_type == "identify_skill_gaps":
            # Get user's skills
            from backend.models.career_profile import CareerProfile
            profile = (
                self.db.query(CareerProfile)
                .filter(CareerProfile.user_id == user_id)
                .first()
            )
            context["user_skills"] = profile.skills if profile else []

        return context
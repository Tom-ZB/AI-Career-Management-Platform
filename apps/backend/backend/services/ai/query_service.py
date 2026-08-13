"""
AI Natural Language Query Service - Converts natural language to database queries.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.services.ai.llm_factory import LLMFactory


# NL to SQL Prompt
NL_TO_SQL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI that converts natural language questions about a user's
    career data into SQL queries. The database uses MySQL.

    Here are the relevant tables and their columns:

    Table: job_applications
    - id, user_id, job_opportunity_id, cv_id, status, application_date, deadline,
      cover_letter_content, notes, referral_source, created_at, updated_at
    - status values: 'draft', 'applied', 'screening', 'interview', 'offer', 'accepted', 'rejected', 'withdrawn'

    Table: job_opportunities
    - id, user_id, title, company, location, job_type, is_remote,
      salary_min, salary_max, salary_currency, description, requirements,
      source, source_url, status, deadline, created_at, updated_at
    - job_type values: 'full_time', 'part_time', 'contract', 'internship', 'freelance', 'temporary'
    - status values: 'open', 'closed', 'archived'

    Table: interviews
    - id, user_id, application_id, interview_type, title, scheduled_at,
      duration_minutes, status, rating, feedback, created_at
    - interview_type values: 'phone', 'video', 'onsite', 'technical', 'behavioral', 'case_study', 'final_round'
    - status values: 'scheduled', 'completed', 'cancelled', 'rescheduled', 'no_show'

    Table: cvs
    - id, user_id, career_profile_id, title, version, is_master, is_ai_generated,
      file_name, ai_score, created_at, updated_at

    Table: follow_ups
    - id, user_id, application_id, interview_id, follow_up_type, title,
      priority, scheduled_at, status, created_at
    - priority: 1=Low, 2=Medium, 3=High
    - status values: 'pending', 'completed', 'missed', 'cancelled'

    Table: career_profiles
    - id, user_id, full_name, title, summary, skills, experience_years, education, work_experience

    CRITICAL RULES:
    1. ALWAYS include "user_id = {user_id}" in WHERE clause
    2. ALWAYS use parameterized queries with :param_name syntax
    3. Return ONLY a valid SQL query, nothing else
    4. For COUNT queries, use COUNT(*) as count
    5. Limit results to 100 by default unless specified otherwise
    6. Use proper MySQL date functions: NOW(), CURDATE(), DATE_SUB(), etc.

    Respond with a JSON object containing:
    - sql: The SQL query string
    - explanation: Brief explanation of what the query does
    - params: Any parameters that need to be bound (besides user_id)"""),
    ("human", "User question: {question}\n\nUser ID: {user_id}"),
])


class AIQueryService:
    """Service for natural language database queries."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMFactory.get_llm(temperature=0.1)

    async def query(self, user_id: int, question: str) -> Dict[str, Any]:
        """
        Convert natural language to SQL and execute.

        Args:
            user_id: The authenticated user's ID
            question: Natural language question about career data

        Returns:
            Dictionary with query results and explanation
        """
        # Generate SQL from natural language
        chain = NL_TO_SQL_PROMPT | self.llm | JsonOutputParser()
        result = await chain.ainvoke({
            "question": question,
            "user_id": user_id,
        })

        sql = result.get("sql", "")
        explanation = result.get("explanation", "")
        params = result.get("params", {})

        # Execute the query safely
        try:
            # Add user_id to params
            params["user_id"] = user_id

            # Execute query
            query_result = self.db.execute(text(sql), params)
            rows = query_result.fetchall()

            # Convert to list of dicts
            columns = query_result.keys()
            data = [dict(zip(columns, row)) for row in rows]

            return {
                "question": question,
                "explanation": explanation,
                "sql": sql,
                "results": data,
                "count": len(data),
            }
        except Exception as e:
            return {
                "question": question,
                "explanation": explanation,
                "sql": sql,
                "error": str(e),
                "results": [],
                "count": 0,
            }
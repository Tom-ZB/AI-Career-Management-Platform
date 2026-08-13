"""
Seed data script for development.
Run: python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from backend.database import SessionLocal, init_db
from backend.core.security import get_password_hash
from backend.models.user import User
from backend.models.career_profile import CareerProfile
from backend.models.cv import CV
from backend.models.job_opportunity import JobOpportunity, JobStatus, JobType
from backend.models.job_application import JobApplication, ApplicationStatus
from backend.models.interview import Interview, InterviewType, InterviewStatus
from backend.models.follow_up import FollowUp, FollowUpType, FollowUpStatus
from backend.models.document import Document, DocumentType
from backend.models.chat_message import ChatMessage, MessageRole
from backend.models.cv_job_match import CVJobMatch


def seed_database():
    """Seed the database with sample data for development."""
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).first():
            print("⚠️  Database already has data. Skipping seed.")
            return

        print("🌱 Seeding database...")

        # ============================================================
        # 1. Create Demo User
        # ============================================================
        user = User(
            email="demo@aicareer.com",
            username="demo",
            hashed_password=get_password_hash("Demo123456!"),
            full_name="Tom Zhang",
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"  ✅ Created user: {user.username} (ID: {user.id})")

        # ============================================================
        # 2. Create Career Profile
        # ============================================================
        profile = CareerProfile(
            user_id=user.id,
            full_name="Tom Zhang",
            title="Senior Full-Stack Engineer",
            summary="Experienced full-stack engineer with 8+ years of expertise in Python, React, and cloud technologies. Passionate about building scalable applications and mentoring teams.",
            skills=["Python", "TypeScript", "React", "FastAPI", "PostgreSQL", "MySQL", "Docker", "AWS", "Azure", "LangChain", "CI/CD", "Git"],
            experience_years=8,
            education=[
                {"institution": "Peking University", "degree": "M.S.", "field": "Computer Science", "start": "2013", "end": "2016"},
                {"institution": "Wuhan University", "degree": "B.S.", "field": "Software Engineering", "start": "2009", "end": "2013"},
            ],
            work_experience=[
                {"company": "TechCorp Inc.", "position": "Senior Full-Stack Engineer", "start": "2021-03", "end": "Present", "description": "Lead development of microservices architecture serving 10M+ users. Built AI-powered recommendation engine."},
                {"company": "StartupXYZ", "position": "Full-Stack Engineer", "start": "2018-06", "end": "2021-02", "description": "Developed SaaS platform from 0 to 1. Implemented real-time collaboration features."},
                {"company": "DataSoft Ltd.", "position": "Backend Engineer", "start": "2016-07", "end": "2018-05", "description": "Built data pipelines processing 1TB+ daily. Designed REST APIs for internal tools."},
            ],
            contact_info={"phone": "+86 138-xxxx-xxxx", "city": "Beijing", "country": "China"},
            social_links={"linkedin": "https://linkedin.com/in/tomzhang", "github": "https://github.com/tomzhang"},
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        print(f"  ✅ Created career profile: {profile.title}")

        # ============================================================
        # 3. Create CVs
        # ============================================================
        master_cv = CV(
            user_id=user.id,
            career_profile_id=profile.id,
            title="Master CV - Full Stack Engineer",
            version="1.0",
            description="Complete master CV with all experience",
            is_master=True,
            content_text="Tom Zhang - Senior Full-Stack Engineer. 8+ years experience in Python, React, cloud. MS from Peking University.",
        )
        db.add(master_cv)

        tailored_cv = CV(
            user_id=user.id,
            career_profile_id=profile.id,
            title="Tailored CV - AI Engineer",
            version="1.0",
            description="Tailored for AI/ML engineering positions",
            is_master=False,
            is_ai_generated=True,
            target_job_title="AI Engineer",
            content_text="Tom Zhang - AI Engineer. Expert in LangChain, LLM integration, and building AI-powered applications.",
        )
        db.add(tailored_cv)
        db.commit()
        print(f"  ✅ Created 2 CVs")

        # ============================================================
        # 4. Create Job Opportunities
        # ============================================================
        jobs_data = [
            {
                "title": "Senior AI Engineer",
                "company": "ByteDance",
                "location": "Beijing, China",
                "job_type": JobType.FULL_TIME,
                "is_remote": False,
                "salary_min": 500000,
                "salary_max": 800000,
                "salary_currency": "CNY",
                "description": "Build AI-powered content recommendation systems. Work with LLMs and NLP to improve user experience.",
                "requirements": "5+ years experience in AI/ML. Strong Python skills. Experience with LangChain, transformers, and RAG systems.",
                "source": "LinkedIn",
                "status": JobStatus.OPEN,
            },
            {
                "title": "Full-Stack Engineer",
                "company": "Alibaba Cloud",
                "location": "Hangzhou, China",
                "job_type": JobType.FULL_TIME,
                "is_remote": False,
                "salary_min": 400000,
                "salary_max": 600000,
                "salary_currency": "CNY",
                "description": "Develop cloud management platform. Build scalable microservices and frontend dashboards.",
                "requirements": "3+ years full-stack experience. React, Python/FastAPI, PostgreSQL. Cloud experience preferred.",
                "source": "Company Website",
                "status": JobStatus.OPEN,
            },
            {
                "title": "Tech Lead - Platform Engineering",
                "company": "Tencent",
                "location": "Shenzhen, China",
                "job_type": JobType.FULL_TIME,
                "is_remote": False,
                "salary_min": 600000,
                "salary_max": 1000000,
                "salary_currency": "CNY",
                "description": "Lead a team of 8 engineers building internal developer platform. Drive architecture decisions.",
                "requirements": "8+ years experience. Team leadership. System design. Cloud-native architecture.",
                "source": "Referral",
                "status": JobStatus.OPEN,
            },
            {
                "title": "Backend Engineer (Contract)",
                "company": "Remote Startup",
                "location": "Remote",
                "job_type": JobType.CONTRACT,
                "is_remote": True,
                "salary_min": 200000,
                "salary_max": 350000,
                "salary_currency": "USD",
                "description": "Build API services for fintech platform. 6-month contract with possible extension.",
                "requirements": "Strong Python, FastAPI, database design. Remote work experience.",
                "source": "Indeed",
                "status": JobStatus.CLOSED,
            },
        ]

        jobs = []
        for job_data in jobs_data:
            job = JobOpportunity(user_id=user.id, **job_data)
            db.add(job)
            jobs.append(job)

        db.commit()
        print(f"  ✅ Created {len(jobs)} job opportunities")

        # ============================================================
        # 5. Create Applications
        # ============================================================
        apps_data = [
            {"job": jobs[0], "cv": tailored_cv, "status": ApplicationStatus.INTERVIEW, "days_ago": 14},
            {"job": jobs[1], "cv": master_cv, "status": ApplicationStatus.APPLIED, "days_ago": 7},
            {"job": jobs[2], "cv": master_cv, "status": ApplicationStatus.SCREENING, "days_ago": 10},
            {"job": jobs[3], "cv": master_cv, "status": ApplicationStatus.REJECTED, "days_ago": 30},
        ]

        applications = []
        for app_data in apps_data:
            app = JobApplication(
                user_id=user.id,
                job_opportunity_id=app_data["job"].id,
                cv_id=app_data["cv"].id,
                status=app_data["status"],
                application_date=datetime.utcnow() - timedelta(days=app_data["days_ago"]),
                notes=f"Applied via {app_data['job'].source}",
            )
            db.add(app)
            applications.append(app)

        db.commit()
        print(f"  ✅ Created {len(applications)} applications")

        # ============================================================
        # 6. Create Interviews
        # ============================================================
        interviews_data = [
            {
                "application": applications[0],
                "type": InterviewType.TECHNICAL,
                "title": "Technical Interview - AI/ML",
                "scheduled_at": datetime.utcnow() + timedelta(days=3),
                "interviewer_name": "Dr. Li Wei",
                "interviewer_title": "AI Team Lead",
                "status": InterviewStatus.SCHEDULED,
            },
            {
                "application": applications[0],
                "type": InterviewType.BEHAVIORAL,
                "title": "Behavioral Interview",
                "scheduled_at": datetime.utcnow() + timedelta(days=5),
                "interviewer_name": "Zhang Ming",
                "interviewer_title": "HR Manager",
                "status": InterviewStatus.SCHEDULED,
            },
            {
                "application": applications[3],
                "type": InterviewType.PHONE,
                "title": "Phone Screen",
                "scheduled_at": datetime.utcnow() - timedelta(days=25),
                "interviewer_name": "Recruiter",
                "status": InterviewStatus.COMPLETED,
                "rating": 3,
                "feedback": "Good technical skills but not enough cloud experience.",
            },
        ]

        for int_data in interviews_data:
            interview = Interview(
                user_id=user.id,
                application_id=int_data["application"].id,
                **{k: v for k, v in int_data.items() if k != "application"},
            )
            db.add(interview)

        db.commit()
        print(f"  ✅ Created {len(interviews_data)} interviews")

        # ============================================================
        # 7. Create Follow-ups
        # ============================================================
        follow_ups_data = [
            {
                "application": applications[1],
                "type": FollowUpType.FOLLOW_UP_EMAIL,
                "title": "Follow up on application",
                "scheduled_at": datetime.utcnow() + timedelta(days=2),
                "priority": 2,
            },
            {
                "application": applications[2],
                "type": FollowUpType.THANK_YOU,
                "title": "Send thank you email",
                "scheduled_at": datetime.utcnow() - timedelta(days=1),
                "status": FollowUpStatus.COMPLETED,
                "priority": 3,
            },
        ]

        for fu_data in follow_ups_data:
            fu = FollowUp(
                user_id=user.id,
                application_id=fu_data["application"].id,
                **{k: v for k, v in fu_data.items() if k != "application"},
            )
            db.add(fu)

        db.commit()
        print(f"  ✅ Created {len(follow_ups_data)} follow-ups")

        # ============================================================
        # 8. Create CV-Job Match
        # ============================================================
        match = CVJobMatch(
            user_id=user.id,
            cv_id=tailored_cv.id,
            job_opportunity_id=jobs[0].id,
            match_score=85.5,
            skills_match_score=90.0,
            experience_match_score=80.0,
            education_match_score=85.0,
            keywords_match_score=87.0,
            ai_recommendation="strong_match",
        )
        db.add(match)
        db.commit()
        print(f"  ✅ Created 1 CV-Job match")

        # ============================================================
        # 9. Create Chat Messages
        # ============================================================
        messages = [
            {"role": MessageRole.USER, "content": "How can I improve my CV for AI engineering roles?"},
            {"role": MessageRole.ASSISTANT, "content": "Based on your profile, I recommend highlighting your LangChain and LLM integration experience. Consider adding specific metrics from your AI projects, such as model accuracy improvements or processing time reductions."},
            {"role": MessageRole.USER, "content": "What skills should I focus on learning?"},
            {"role": MessageRole.ASSISTANT, "content": "Given the current AI job market, I recommend focusing on: 1) RAG (Retrieval-Augmented Generation) systems, 2) Prompt engineering, 3) MLOps and model deployment, 4) Vector databases like Pinecone or Weaviate."},
        ]

        session_id = f"session_{user.id}_demo"
        for msg_data in messages:
            msg = ChatMessage(
                user_id=user.id,
                session_id=session_id,
                conversation_title="Career Advice for AI Roles",
                **msg_data,
            )
            db.add(msg)

        db.commit()
        print(f"  ✅ Created {len(messages)} chat messages")

        print("\n" + "=" * 50)
        print("✅ Database seeding complete!")
        print("=" * 50)
        print(f"\n📧 Login: demo@aicareer.com")
        print(f"🔑 Password: Demo123456!")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize tables first
    init_db()
    # Then seed
    seed_database()
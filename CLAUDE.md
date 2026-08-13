# AI Career Management Platform

## Project Overview
A full-stack AI-powered career management platform for personal career management, CV management, job application tracking, and AI-assisted job seeking.

## Tech Stack
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Backend**: Python + FastAPI + SQLAlchemy 2.x + Alembic
- **Database**: MySQL (local dev) / PostgreSQL (production)
- **AI**: LangChain + DeepSeek/OpenAI/Anthropic
- **Storage**: Local (dev) / Azure Blob Storage (prod)
- **Deployment**: Vercel (frontend) + Azure (backend)

## Project Structure
```
apps/
├── backend/          # FastAPI backend
│   ├── backend/
│   │   ├── api/v1/   # API endpoints (auth, users, cvs, jobs, applications, interviews, follow_ups, documents, ai, analytics, export)
│   │   ├── core/     # Security (JWT, password hashing)
│   │   ├── crud/     # CRUD operations for all models
│   │   ├── models/   # SQLAlchemy models (11 models)
│   │   ├── schemas/  # Pydantic schemas for all models
│   │   ├── services/ # Business logic (AI, storage, export)
│   │   │   └── ai/   # AI services (chat, cv, matching, cover_letter, interview, query, agent)
│   │   ├── config.py # Pydantic settings
│   │   ├── database.py # DB connection
│   │   ├── dependencies.py # Auth dependencies
│   │   └── main.py   # FastAPI app entry
│   ├── alembic/      # Migration config
│   ├── database/     # SQL schema
│   ├── seed.py       # Seed data script
│   ├── run.py        # Startup script
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── .env          # Environment config
└── frontend/         # React frontend (Vite + TypeScript + Tailwind)
    ├── src/
    │   ├── components/  # UI components, layout, auth
    │   ├── context/     # AuthContext
    │   ├── lib/         # Utilities
    │   ├── pages/       # All pages
    │   ├── services/    # API clients
    │   └── types/       # TypeScript types
    ├── Dockerfile
    ├── nginx.conf
    └── package.json
```

## Database Models (11)
1. **User** - Authentication & user management
2. **CareerProfile** - Master career profile (1:1 with User)
3. **CV** - Multiple CV versions (Master + Tailored)
4. **JobOpportunity** - Job listings
5. **JobApplication** - Application tracking
6. **Interview** - Interview scheduling & feedback
7. **FollowUp** - Follow-up activities
8. **Document** - Uploaded files metadata
9. **CVJobMatch** - AI matching results
10. **ChatMessage** - AI chatbot conversations
11. **AIAgentAction** - AI agent action logs

## Running Locally
```bash
# Backend
cd apps/backend
pip install -r requirements.txt
# Configure .env with DATABASE_URL and LLM API keys
python run.py          # Start FastAPI server on port 8000
python seed.py         # Seed demo data

# Frontend
cd apps/frontend
npm install
npm run dev            # Start Vite dev server on port 5173
```

## API Endpoints
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login (OAuth2)
- `GET /api/v1/users/me` - Current user
- `GET /api/v1/profiles/` - Career profile
- `GET/POST /api/v1/cvs/` - CV management
- `GET/POST /api/v1/jobs/` - Job opportunities
- `GET/POST /api/v1/applications/` - Applications
- `GET/POST /api/v1/interviews/` - Interviews
- `GET/POST /api/v1/follow-ups/` - Follow-ups
- `GET/POST /api/v1/documents/` - Documents
- `POST /api/v1/ai/chat` - AI chatbot
- `POST /api/v1/ai/analyze-cv/{id}` - CV analysis
- `POST /api/v1/ai/match` - CV-Job matching
- `POST /api/v1/ai/generate-cv` - Generate tailored CV
- `POST /api/v1/ai/generate-cover-letter` - Generate cover letter
- `POST /api/v1/ai/query` - Natural language query
- `GET /api/v1/analytics/dashboard` - Dashboard data

## Demo Credentials
- Email: demo@aicareer.com
- Password: Demo123456!

## Development Status
- [x] Database schema & models
- [x] CRUD operations
- [x] Pydantic schemas
- [x] API endpoints (all routers)
- [x] Authentication (JWT)
- [x] AI services (chat, CV analysis, matching, cover letter, interview prep, NL query, agent)
- [x] Storage service (local + Azure)
- [x] Export service (PDF + CSV)
- [x] Docker configuration
- [x] Seed data script
- [x] Frontend (React + TypeScript + Vite + Tailwind)
- [ ] Tests
- [ ] Production deployment
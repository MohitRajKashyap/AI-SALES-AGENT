# AI Sales Agent SaaS

> **Production-ready AI-powered B2B sales automation platform**  
> Built by **Mohit Raj Kashyap** — B.Tech CSE (AI/ML)

An end-to-end sales pipeline automation system using a **LangGraph multi-agent workflow** that crawls company websites, discovers leads, scores them, writes personalized cold emails, and manages follow-up sequences — all driven by GPT-4o.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL, Alembic |
| **Task Queue** | Celery + Redis |
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, React Query |
| **AI** | OpenAI GPT-4o, LangGraph, LangChain |
| **Vector DB** | Qdrant (semantic search) |
| **Payments** | Stripe |
| **DevOps** | Docker, Docker Compose |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Next.js Frontend                    │
│  Landing | Auth | Dashboard | Leads | Campaigns | CRM   │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                         │
│  Auth | Workspaces | Leads | Campaigns | Emails | Admin  │
└──────┬───────────────┬───────────────────┬──────────────┘
       │               │                   │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────────▼──────────┐
│ PostgreSQL  │ │    Redis    │ │       Qdrant        │
│  (primary)  │ │  (celery)   │ │  (vector search)    │
└─────────────┘ └─────────────┘ └────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              LangGraph Agent Workflow                    │
│  Website Analyzer → Lead Finder → Lead Scorer →         │
│  Email Generator → Follow-Up Planner → CRM Analytics    │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
ai-sales-agent/
├── backend/
│   ├── app/
│   │   ├── agents/              # AI agent implementations
│   │   │   ├── website_analyzer.py
│   │   │   ├── lead_finder.py
│   │   │   ├── email_generator.py
│   │   │   └── workflow.py      # LangGraph orchestration
│   │   ├── api/v1/endpoints/    # FastAPI route handlers
│   │   ├── core/                # Config, security, logging
│   │   ├── db/                  # Database session & base
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── repositories/        # Data access layer
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── tasks/               # Celery async tasks
│   │   └── utils/               # Email, helpers
│   ├── alembic/                 # DB migrations
│   ├── tests/
│   │   ├── unit/
│   │   ├── api/
│   │   └── integration/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── auth/            # Login, Register
│   │   │   ├── dashboard/       # All dashboard pages
│   │   │   └── onboarding/
│   │   ├── components/layout/   # Sidebar, etc.
│   │   ├── lib/api.ts           # Axios API client
│   │   ├── store/auth.ts        # Zustand auth store
│   │   └── types/index.ts       # TypeScript types
│   ├── package.json
│   └── tailwind.config.js
├── scripts/seed.py              # Sample data seeder
├── docker-compose.yml
└── .env.example
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### 1. Clone and configure

```bash
git clone <repo-url>
cd ai-sales-agent
cp .env.example .env
# Edit .env — set SECRET_KEY and OPENAI_API_KEY at minimum
```

### 2. Start all services

```bash
docker compose up -d
```

### 3. Seed sample data (optional)

```bash
cd backend
pip install -r requirements.txt
python ../scripts/seed.py
# Login: demo@aisalesagent.com / demo1234
```

### 4. Open the app

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1/docs |
| Qdrant UI | http://localhost:6333/dashboard |

---

## Development Setup (without Docker)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Copy and configure .env
cp ../.env.example .env

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000

# In a new terminal — start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Frontend
cd ../frontend
cp .env.local.example .env.local
npm install
npm run dev
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | JWT signing key (min 32 chars) |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `ASYNC_DATABASE_URL` | ✅ | Async PostgreSQL URL (asyncpg) |
| `REDIS_URL` | ✅ | Redis connection string |
| `QDRANT_URL` | ✅ | Qdrant server URL |
| `STRIPE_SECRET_KEY` | ⬜ | Stripe secret (for billing) |
| `SMTP_HOST` | ⬜ | SMTP host (for email sending) |

---

## Running Tests

```bash
cd backend

# Install test deps (aiosqlite for in-memory test DB)
pip install aiosqlite pytest-asyncio

# All tests
pytest

# With coverage
pytest --cov=app tests/
```

---

## API Overview

Full docs at `http://localhost:8000/api/v1/docs`

| Endpoint | Description |
|---|---|
| `POST /auth/register` | Create account |
| `POST /auth/login` | Get JWT tokens |
| `GET /workspaces` | List workspaces |
| `POST /workspaces/{id}/analyze` | Analyze a website with AI |
| `POST /workspaces/{id}/leads/generate` | AI lead generation |
| `GET /workspaces/{id}/leads` | List leads (paginated) |
| `POST /workspaces/{id}/campaigns` | Create campaign |
| `POST /workspaces/{id}/emails/generate` | Generate personalized email |
| `POST /workspaces/{id}/pipeline/run` | Run full 6-agent pipeline |
| `GET /workspaces/{id}/analytics/dashboard` | Dashboard metrics |
| `POST /workspaces/{id}/search` | Semantic vector search |
| `POST /billing/checkout` | Stripe checkout session |
| `GET /track/open/{id}` | Email open tracking pixel |

---

## Subscription Plans

| Feature | Free | Pro ($49/mo) | Enterprise ($199/mo) |
|---|---|---|---|
| Leads/month | 50 | 2,000 | Unlimited |
| Emails/month | 100 | 5,000 | Unlimited |
| Workspaces | 1 | 5 | Unlimited |
| AI agents | ✅ | ✅ | ✅ + custom models |
| Analytics | Basic | Advanced | Full |

---

## Resume Description

> **AI Sales Agent SaaS** — Full-stack B2B sales automation platform (Python/FastAPI + Next.js 15)  
> Architected a LangGraph multi-agent system (Website Analyzer → Lead Finder → Lead Scorer → Email Generator → Follow-Up Planner) powered by GPT-4o for end-to-end sales pipeline automation. Implemented async PostgreSQL with SQLAlchemy, Qdrant vector search for semantic lead discovery, Celery for background task processing, JWT auth, Stripe subscription billing, and email open/click tracking. Deployed via Docker Compose with Redis, Qdrant, and PostgreSQL.  
> **Stack:** Python, FastAPI, LangGraph, OpenAI, PostgreSQL, Redis, Qdrant, Next.js 15, TypeScript, Tailwind CSS, Docker

---

## Future Enhancements

- LinkedIn integration for lead enrichment
- Email provider integrations (SendGrid, AWS SES, Mailgun)
- A/B testing for subject lines
- AI reply detection and response drafting
- CRM integrations (Salesforce, HubSpot)
- Multi-language email generation
- WhatsApp/SMS outreach channels
- Zapier/Make webhook integrations

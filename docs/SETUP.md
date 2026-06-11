# Setup Guide

## Prerequisites

| Tool | Minimum Version |
|---|---|
| Docker | 24.x |
| Docker Compose | v2 |
| Python | 3.12 (for local dev) |
| Node.js | 20.x (for local dev) |
| OpenAI API key | — |

---

## Option A — Docker (Recommended)

The fastest way to run the full stack.

```bash
# 1. Clone
git clone <repo-url>
cd ai-sales-agent

# 2. Configure environment
cp .env.example .env
```

Open `.env` and set at minimum:
```
SECRET_KEY=your-random-secret-key-at-least-32-characters
OPENAI_API_KEY=sk-...
POSTGRES_PASSWORD=yourpassword
DATABASE_URL=postgresql://postgres:yourpassword@postgres:5432/ai_sales_agent
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@postgres:5432/ai_sales_agent
```

```bash
# 3. Start all services
docker compose up -d

# 4. Watch logs
docker compose logs -f backend

# 5. Seed demo data
docker compose exec backend python /app/../scripts/seed.py
```

Open http://localhost:3000 — login with `demo@aisalesagent.com` / `demo1234`

---

## Option B — Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for website crawling)
playwright install chromium

# Configure environment
cp ../.env.example .env
# Edit .env with your values

# Start PostgreSQL and Redis (via Docker for convenience)
docker run -d --name pg -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=ai_sales_agent -p 5432:5432 postgres:16-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

# Run migrations
alembic upgrade head

# Seed data
python ../scripts/seed.py

# Start API server
uvicorn app.main:app --reload --port 8000
```

In a second terminal:
```bash
cd backend
source venv/bin/activate
# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info -c 2

# In a third terminal — start Celery beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend
cp .env.local.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

npm install
npm run dev
```

Open http://localhost:3000

---

## Database Migrations

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "describe_your_change"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

---

## Running Tests

```bash
cd backend
pip install aiosqlite  # needed for in-memory SQLite test DB

# Run all tests
pytest

# Specific test file
pytest tests/api/test_auth.py -v

# With coverage
pytest --cov=app tests/ --cov-report=html
open htmlcov/index.html
```

---

## Production Deployment

### Environment hardening

1. Set `DEBUG=false`
2. Use a strong random `SECRET_KEY` (32+ chars)
3. Set `BACKEND_CORS_ORIGINS` to your actual frontend domain
4. Use a managed PostgreSQL (e.g. AWS RDS, Supabase, Neon)
5. Use a managed Redis (e.g. Redis Cloud, Upstash)
6. Use Qdrant Cloud or self-hosted Qdrant with persistent volume

### Docker production build

```bash
# Build production images
docker compose -f docker-compose.yml build

# Run with production env
docker compose --env-file .env.production up -d
```

### Nginx reverse proxy (example)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

### Recommended cloud stack

| Service | Provider |
|---|---|
| Container hosting | AWS ECS / Railway / Render |
| PostgreSQL | Neon / Supabase / AWS RDS |
| Redis | Upstash / Redis Cloud |
| Qdrant | Qdrant Cloud |
| CDN/TLS | Cloudflare |

---

## Stripe Setup

1. Create a Stripe account at stripe.com
2. Get your secret key from the dashboard
3. Create two products: Pro ($49/mo) and Enterprise ($199/mo)
4. Copy the price IDs into `.env`
5. Set up a webhook endpoint pointing to `https://yourdomain.com/api/v1/billing/webhook`
6. Add events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
7. Copy the webhook signing secret into `STRIPE_WEBHOOK_SECRET`

---

## Email Sending Setup (Optional)

For real email delivery, configure SMTP in `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@yourdomain.com
```

For production, use a transactional email service like **SendGrid**, **AWS SES**, or **Mailgun** — edit `app/utils/email_utils.py` to call their SDK instead of SMTP.

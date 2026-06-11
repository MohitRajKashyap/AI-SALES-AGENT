# API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/api/v1/docs`

All authenticated endpoints require: `Authorization: Bearer <access_token>`

---

## Authentication

### Register
`POST /auth/register`
```json
{ "email": "user@example.com", "password": "securepass", "full_name": "John Doe" }
```
**Response 201:**
```json
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer" }
```

### Login
`POST /auth/login`
```json
{ "email": "user@example.com", "password": "securepass" }
```

### Refresh Token
`POST /auth/refresh`
```json
{ "refresh_token": "eyJ..." }
```

### Get Current User
`GET /auth/me` 🔒

### Update Profile
`PATCH /auth/me` 🔒
```json
{ "full_name": "New Name", "avatar_url": "https://..." }
```

---

## Workspaces

### Create Workspace
`POST /workspaces` 🔒
```json
{ "name": "Acme Corp", "website": "https://acme.com", "industry": "SaaS" }
```

### List Workspaces
`GET /workspaces` 🔒

### Get Workspace
`GET /workspaces/{workspace_id}` 🔒

### Update Workspace
`PATCH /workspaces/{workspace_id}` 🔒

---

## Company Analysis (Website Analyzer Agent)

### Analyze Website
`POST /workspaces/{workspace_id}/analyze` 🔒

Triggers the Website Analyzer AI agent. Crawls the URL and extracts structured business intelligence.
```json
{ "website_url": "https://stripe.com" }
```
**Response:**
```json
{
  "id": "uuid",
  "company_name": "Stripe",
  "industry": "FinTech / Payments",
  "services": ["Payment processing", "Fraud detection", "Billing"],
  "products": ["Stripe Payments", "Stripe Connect", "Radar"],
  "target_customers": ["SaaS companies", "Marketplaces", "E-commerce"],
  "pain_points": ["Complex payment integration", "Global compliance", "Fraud losses"]
}
```

---

## Leads

### Generate Leads (Lead Finder + Scorer Agents)
`POST /workspaces/{workspace_id}/leads/generate` 🔒
```json
{ "company_id": "uuid", "count": 10 }
```
Runs Lead Finder and Lead Scorer agents, stores results, indexes in Qdrant.

### List Leads
`GET /workspaces/{workspace_id}/leads?page=1&page_size=20&status=hot` 🔒

**Query params:** `page`, `page_size`, `status` (hot|warm|cold|converted|disqualified)

### Get Lead
`GET /workspaces/{workspace_id}/leads/{lead_id}` 🔒

### Update Lead
`PATCH /workspaces/{workspace_id}/leads/{lead_id}` 🔒
```json
{ "status": "warm", "notes": "Showed interest", "tags": ["priority", "q4"] }
```

### Delete Lead
`DELETE /workspaces/{workspace_id}/leads/{lead_id}` 🔒

---

## Campaigns

### Create Campaign
`POST /workspaces/{workspace_id}/campaigns` 🔒
```json
{
  "name": "Q4 Enterprise Push",
  "goal": "Book 20 demos",
  "daily_limit": 50,
  "email_style": "professional",
  "followup_days": [3, 7, 14],
  "target_industry": "Enterprise SaaS"
}
```

### List Campaigns
`GET /workspaces/{workspace_id}/campaigns` 🔒

### Update Campaign
`PATCH /workspaces/{workspace_id}/campaigns/{campaign_id}` 🔒

### Pause Campaign
`POST /workspaces/{workspace_id}/campaigns/{campaign_id}/pause` 🔒

### Resume Campaign
`POST /workspaces/{workspace_id}/campaigns/{campaign_id}/resume` 🔒

### Delete Campaign
`DELETE /workspaces/{workspace_id}/campaigns/{campaign_id}` 🔒

---

## Emails

### Generate Email (Email Generator Agent)
`POST /workspaces/{workspace_id}/emails/generate` 🔒
```json
{
  "lead_id": "uuid",
  "campaign_id": "uuid",
  "email_type": "cold",
  "email_style": "professional",
  "custom_goal": "Book a 15-minute call"
}
```
**Email types:** `cold` | `followup` | `meeting_request` | `product_intro`  
**Email styles:** `professional` | `friendly` | `startup` | `enterprise`

### List Emails
`GET /workspaces/{workspace_id}/emails?page=1&page_size=20` 🔒

---

## Analytics

### Dashboard Metrics
`GET /workspaces/{workspace_id}/analytics/dashboard` 🔒
```json
{
  "total_leads": 142,
  "emails_sent": 380,
  "replies": 28,
  "meetings_booked": 9,
  "conversion_rate": 3.52,
  "hot_leads": 31,
  "warm_leads": 58,
  "active_campaigns": 3
}
```

### Daily Analytics
`GET /workspaces/{workspace_id}/analytics/daily?days=30` 🔒

### Campaign Performance
`GET /workspaces/{workspace_id}/analytics/campaigns` 🔒

---

## AI Agent Workflow

### Run Full Pipeline
`POST /workspaces/{workspace_id}/pipeline/run` 🔒

Runs all 6 agents in sequence: Website Analyzer → Lead Finder → Lead Scorer → Email Generator → Follow-Up Planner.
```json
{ "website_url": "https://targetcompany.com" }
```
**Response:**
```json
{
  "status": "completed",
  "company_profile": { ... },
  "leads_found": 10,
  "emails_generated": 5,
  "errors": []
}
```

### Agent Logs
`GET /workspaces/{workspace_id}/agent-logs?limit=20` 🔒

---

## Vector Search

### Semantic Search
`POST /workspaces/{workspace_id}/search` 🔒
```json
{
  "query": "fintech companies with payment problems",
  "collection": "leads",
  "limit": 5
}
```
**Collections:** `companies` | `leads` | `emails`

---

## Billing

### Create Checkout Session
`POST /billing/checkout` 🔒
```json
{ "plan": "pro", "success_url": "https://...", "cancel_url": "https://..." }
```

### Get Subscription
`GET /billing/subscription` 🔒

### Stripe Webhook
`POST /billing/webhook` (no auth — Stripe signature verified)

---

## Email Tracking

### Open Tracking Pixel
`GET /track/open/{tracking_id}` — Returns 1x1 GIF, records open event

### Click Tracking
`GET /track/click/{tracking_id}?url=https://...` — Records click, redirects to URL

---

## Admin (Superuser only)

### Platform Stats
`GET /admin/stats` 🔒👑

### List All Users
`GET /admin/users` 🔒👑

### Deactivate User
`PATCH /admin/users/{user_id}/deactivate` 🔒👑

### Activate User
`PATCH /admin/users/{user_id}/activate` 🔒👑

---

## Error Responses

| Status | Meaning |
|---|---|
| `400` | Bad request / validation error |
| `401` | Missing or invalid JWT token |
| `403` | Insufficient permissions |
| `404` | Resource not found |
| `409` | Conflict (e.g. duplicate email) |
| `422` | Pydantic validation error |
| `500` | Internal server error |

```json
{ "detail": "Human-readable error message" }
```

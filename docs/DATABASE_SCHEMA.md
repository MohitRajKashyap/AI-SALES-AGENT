# Database Schema

## Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────────┐
│     users       │       │     subscriptions     │
├─────────────────┤       ├──────────────────────┤
│ id (PK)         │──┐    │ id (PK)              │
│ email (UNIQUE)  │  │    │ user_id (FK→users)   │
│ hashed_password │  └───▶│ stripe_customer_id   │
│ full_name       │       │ stripe_subscription_id│
│ avatar_url      │       │ plan                 │
│ is_active       │       │ status               │
│ is_superuser    │       │ current_period_start │
│ role            │       │ current_period_end   │
│ created_at      │       └──────────────────────┘
│ updated_at      │
└────────┬────────┘
         │ owner_id
         ▼
┌─────────────────────┐       ┌────────────────────────┐
│     workspaces      │       │   workspace_members    │
├─────────────────────┤       ├────────────────────────┤
│ id (PK)             │──────▶│ id (PK)               │
│ name                │       │ workspace_id (FK)      │
│ slug (UNIQUE)       │       │ user_id (FK→users)     │
│ logo_url            │       │ role                   │
│ website             │       │ created_at             │
│ industry            │       └────────────────────────┘
│ owner_id (FK→users) │
│ settings (JSON)     │
│ created_at          │
└──────────┬──────────┘
           │
    ┌──────┼────────────────────────────┐
    │      │                            │
    ▼      ▼                            ▼
┌───────────────┐  ┌────────────────┐  ┌────────────────────┐
│   companies   │  │   campaigns    │  │     analytics      │
├───────────────┤  ├────────────────┤  ├────────────────────┤
│ id (PK)       │  │ id (PK)        │  │ id (PK)            │
│ workspace_id  │  │ workspace_id   │  │ workspace_id       │
│ website_url   │  │ name           │  │ date               │
│ company_name  │  │ description    │  │ emails_sent        │
│ industry      │  │ status         │  │ emails_opened      │
│ services      │  │ goal           │  │ replies            │
│ products      │  │ daily_limit    │  │ meetings_booked    │
│ target_customers│ │ email_style    │  │ new_leads          │
│ pain_points   │  │ followup_days  │  │ conversions        │
│ raw_content   │  │ target_industry│  └────────────────────┘
│ qdrant_id     │  │ settings       │
│ created_at    │  │ created_at     │
└───────┬───────┘  └───────┬────────┘
        │                  │
        ▼                  │
┌───────────────┐          │
│     leads     │          │
├───────────────┤          │
│ id (PK)       │◀─────────┘ (campaign emails link here)
│ workspace_id  │
│ company_id    │──▶ companies
│ company_name  │
│ website       │           ┌──────────────────────┐
│ industry      │           │       emails         │
│ email         │           ├──────────────────────┤
│ linkedin      │◀──────────│ id (PK)              │
│ first_name    │           │ campaign_id (FK)     │
│ last_name     │           │ lead_id (FK→leads)   │
│ job_title     │           │ subject              │
│ phone         │           │ body                 │
│ lead_score    │           │ email_type           │
│ status        │           │ email_style          │
│ tags (JSON)   │           │ status               │
│ notes         │           │ sent_at              │
│ qdrant_id     │           │ opened_at            │
│ created_at    │           │ replied_at           │
└───────────────┘           │ followup_day         │
                            │ tracking_id (UNIQUE) │
┌──────────────────────┐    │ qdrant_id            │
│     agent_logs       │    │ created_at           │
├──────────────────────┤    └──────────────────────┘
│ id (PK)              │
│ workspace_id         │
│ agent_type           │
│ status               │
│ input_data (JSON)    │
│ output_data (JSON)   │
│ error_message        │
│ tokens_used          │
│ duration_seconds     │
│ created_at           │
│ completed_at         │
└──────────────────────┘
```

---

## Tables Reference

### users
Stores all platform users. `is_superuser=true` grants admin access.

| Column | Type | Notes |
|---|---|---|
| id | VARCHAR(36) | UUID v4 |
| email | VARCHAR(255) | Unique, indexed |
| hashed_password | VARCHAR(255) | bcrypt |
| full_name | VARCHAR(255) | |
| is_active | BOOLEAN | Soft delete flag |
| is_superuser | BOOLEAN | Admin access |
| role | ENUM | admin/owner/member |

### workspaces
Isolated tenant units. Each user can belong to multiple workspaces.

| Column | Type | Notes |
|---|---|---|
| slug | VARCHAR(255) | URL-safe unique identifier |
| settings | JSON | Flexible workspace config |
| owner_id | FK→users | Workspace creator |

### leads
Core prospect data. Linked to a workspace and optionally to a company profile.

| Column | Type | Notes |
|---|---|---|
| lead_score | INTEGER | 0–100, AI-assigned |
| status | ENUM | hot/warm/cold/converted/disqualified |
| qdrant_id | VARCHAR(36) | Vector DB reference |
| tags | JSON | Array of string tags |

### emails
Individual email records, linked to both a campaign and a lead.

| Column | Type | Notes |
|---|---|---|
| tracking_id | VARCHAR(36) | Unique UUID for open/click tracking |
| email_type | ENUM | cold/followup/meeting_request/product_intro |
| status | ENUM | draft/queued/sent/opened/replied/bounced/failed |
| followup_day | INTEGER | Day offset (3, 7, 14) for follow-up sequence |

### agent_logs
Full audit trail for every AI agent execution.

| Column | Type | Notes |
|---|---|---|
| agent_type | ENUM | website_analyzer/lead_finder/lead_scorer/email_generator/followup_planner/crm_analytics |
| tokens_used | INTEGER | OpenAI token consumption |
| duration_seconds | FLOAT | Execution time |
| input_data | JSON | Agent inputs |
| output_data | JSON | Agent outputs |

### analytics
Daily roll-up metrics per workspace for dashboard charts.

One row per workspace per day. Incremented by the analytics service as events occur.

---

## Indexes

- `users.email` — unique index for login lookup
- `workspaces.slug` — unique index for URL routing
- `workspace_members(workspace_id, user_id)` — unique composite for access control
- `emails.tracking_id` — unique index for tracking pixel lookups

---

## Enums

```sql
-- User roles
CREATE TYPE userrole AS ENUM ('admin', 'owner', 'member');

-- Subscription
CREATE TYPE subscriptionplan AS ENUM ('free', 'pro', 'enterprise');
CREATE TYPE subscriptionstatus AS ENUM ('active', 'cancelled', 'past_due', 'trialing');

-- Leads
CREATE TYPE leadstatus AS ENUM ('hot', 'warm', 'cold', 'converted', 'disqualified');

-- Campaigns
CREATE TYPE campaignstatus AS ENUM ('draft', 'active', 'paused', 'completed', 'deleted');

-- Emails
CREATE TYPE emailtype AS ENUM ('cold', 'followup', 'meeting_request', 'product_intro');
CREATE TYPE emailstyle AS ENUM ('professional', 'friendly', 'startup', 'enterprise');
CREATE TYPE emailstatus AS ENUM ('draft', 'queued', 'sent', 'opened', 'replied', 'bounced', 'failed');

-- Agents
CREATE TYPE agenttype AS ENUM ('website_analyzer', 'lead_finder', 'lead_scorer', 'email_generator', 'followup_planner', 'crm_analytics');
CREATE TYPE agentstatus AS ENUM ('running', 'completed', 'failed');
```

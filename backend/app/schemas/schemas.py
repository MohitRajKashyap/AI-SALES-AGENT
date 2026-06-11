from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import re

from app.models.models import (
    UserRole, SubscriptionPlan, SubscriptionStatus,
    LeadStatus, CampaignStatus, EmailType, EmailStyle, EmailStatus,
    AgentType, AgentStatus
)


# ─── Base ─────────────────────────────────────────────────────────────────────

class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    role: UserRole
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


# ─── Workspace ────────────────────────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Workspace name cannot be empty")
        return v.strip()


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    owner_id: str
    created_at: datetime


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None


class MemberInvite(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER


# ─── Company ──────────────────────────────────────────────────────────────────

class CompanyAnalyzeRequest(BaseModel):
    website_url: str

    @field_validator("website_url")
    @classmethod
    def valid_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class CompanyProfile(BaseModel):
    company_name: str
    industry: str
    services: List[str]
    products: List[str]
    target_customers: List[str]
    pain_points: List[str]


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    website_url: str
    company_name: Optional[str]
    industry: Optional[str]
    services: Optional[List[str]]
    products: Optional[List[str]]
    target_customers: Optional[List[str]]
    pain_points: Optional[List[str]]
    created_at: datetime


# ─── Leads ────────────────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    company_name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = []


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    company_id: Optional[str]
    company_name: str
    website: Optional[str]
    industry: Optional[str]
    email: Optional[str]
    linkedin: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    job_title: Optional[str]
    phone: Optional[str]
    lead_score: int
    status: LeadStatus
    tags: Optional[List[str]]
    notes: Optional[str]
    created_at: datetime


class LeadUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[LeadStatus] = None


class LeadGenerateRequest(BaseModel):
    company_id: str
    count: int = 10

    @field_validator("count")
    @classmethod
    def valid_count(cls, v):
        if v < 1 or v > 50:
            raise ValueError("Count must be between 1 and 50")
        return v


# ─── Campaigns ────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    goal: Optional[str] = None
    daily_limit: int = 50
    email_style: EmailStyle = EmailStyle.PROFESSIONAL
    followup_days: List[int] = [3, 7, 14]
    target_industry: Optional[str] = None


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    status: CampaignStatus
    goal: Optional[str]
    daily_limit: int
    email_style: EmailStyle
    followup_days: List[int]
    target_industry: Optional[str]
    created_at: datetime


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    daily_limit: Optional[int] = None
    email_style: Optional[EmailStyle] = None
    followup_days: Optional[List[int]] = None
    target_industry: Optional[str] = None


# ─── Emails ───────────────────────────────────────────────────────────────────

class EmailGenerateRequest(BaseModel):
    lead_id: str
    campaign_id: Optional[str] = None
    email_type: EmailType = EmailType.COLD
    email_style: EmailStyle = EmailStyle.PROFESSIONAL
    followup_day: Optional[int] = None
    custom_goal: Optional[str] = None


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    campaign_id: Optional[str]
    lead_id: str
    subject: str
    body: str
    email_type: EmailType
    email_style: EmailStyle
    status: EmailStatus
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    replied_at: Optional[datetime]
    followup_day: Optional[int]
    created_at: datetime


# ─── Analytics ────────────────────────────────────────────────────────────────

class DashboardMetrics(BaseModel):
    total_leads: int
    emails_sent: int
    replies: int
    meetings_booked: int
    conversion_rate: float
    hot_leads: int
    warm_leads: int
    active_campaigns: int


class DailyAnalytics(BaseModel):
    date: str
    emails_sent: int
    emails_opened: int
    replies: int
    new_leads: int
    meetings_booked: int


class CampaignPerformance(BaseModel):
    campaign_id: str
    campaign_name: str
    emails_sent: int
    open_rate: float
    reply_rate: float


# ─── Agent ────────────────────────────────────────────────────────────────────

class AgentLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    agent_type: AgentType
    status: AgentStatus
    input_data: Optional[dict]
    output_data: Optional[dict]
    error_message: Optional[str]
    tokens_used: int
    duration_seconds: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]


# ─── Vector Search ────────────────────────────────────────────────────────────

class VectorSearchRequest(BaseModel):
    query: str
    collection: str
    limit: int = 5

    @field_validator("collection")
    @classmethod
    def valid_collection(cls, v):
        if v not in ("companies", "leads", "emails"):
            raise ValueError("Collection must be one of: companies, leads, emails")
        return v


class VectorSearchResult(BaseModel):
    id: str
    score: float
    payload: dict


# ─── Pagination ───────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


# ─── Admin ────────────────────────────────────────────────────────────────────

class AdminUserList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    role: UserRole
    created_at: datetime


class AdminStats(BaseModel):
    total_users: int
    total_workspaces: int
    total_leads: int
    total_emails: int
    total_campaigns: int

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import time
from datetime import datetime, timezone

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.models import (
    User, Company, Lead, Campaign, Email,
    AgentLog, AgentType, AgentStatus, LeadStatus,
    CampaignStatus, EmailStatus
)
from app.repositories.repositories import (
    CompanyRepository, LeadRepository, CampaignRepository,
    EmailRepository, AgentLogRepository
)
from app.schemas.schemas import (
    CompanyAnalyzeRequest, CompanyResponse,
    LeadCreate, LeadResponse, LeadUpdate, LeadGenerateRequest,
    CampaignCreate, CampaignResponse, CampaignUpdate,
    EmailGenerateRequest, EmailResponse,
    DashboardMetrics, DailyAnalytics, CampaignPerformance,
    VectorSearchRequest, VectorSearchResult, AgentLogResponse,
    PaginatedResponse
)
from app.agents.website_analyzer import WebsiteAnalyzerAgent
from app.agents.lead_finder import LeadFinderAgent, LeadScorerAgent
from app.agents.email_generator import EmailGeneratorAgent
from app.agents.workflow import run_full_pipeline
from app.services.analytics_service import AnalyticsService
from app.services.vector_service import VectorService

router = APIRouter()


# ─── Company / Website Analyzer ───────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/analyze", response_model=CompanyResponse)
async def analyze_website(
    workspace_id: str,
    data: CompanyAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CompanyRepository(db)
    log_repo = AgentLogRepository(db)
    start = time.time()

    log = await log_repo.create({
        "workspace_id": workspace_id,
        "agent_type": AgentType.WEBSITE_ANALYZER,
        "status": AgentStatus.RUNNING,
        "input_data": {"url": data.website_url},
    })

    try:
        agent = WebsiteAnalyzerAgent()
        profile = await agent.analyze(data.website_url)

        company = await repo.create({
            "workspace_id": workspace_id,
            "website_url": data.website_url,
            "company_name": profile.company_name,
            "industry": profile.industry,
            "services": profile.services,
            "products": profile.products,
            "target_customers": profile.target_customers,
            "pain_points": profile.pain_points,
        })

        vector_svc = VectorService()
        try:
            qdrant_id = await vector_svc.upsert_company(company.id, profile.model_dump(), workspace_id)
            company.qdrant_id = qdrant_id
            db.add(company)
        except Exception:
            pass

        await log_repo.update(log, {
            "status": AgentStatus.COMPLETED,
            "output_data": profile.model_dump(),
            "duration_seconds": time.time() - start,
            "completed_at": datetime.now(timezone.utc),
        })

        return company
    except Exception as e:
        await log_repo.update(log, {
            "status": AgentStatus.FAILED,
            "error_message": str(e),
            "duration_seconds": time.time() - start,
        })
        raise HTTPException(status_code=500, detail=str(e))


# ─── Leads ────────────────────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/leads/generate", response_model=List[LeadResponse])
async def generate_leads(
    workspace_id: str,
    data: LeadGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_repo = CompanyRepository(db)
    lead_repo = LeadRepository(db)
    log_repo = AgentLogRepository(db)

    company = await company_repo.get(data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    from app.schemas.schemas import CompanyProfile
    profile = CompanyProfile(
        company_name=company.company_name or "",
        industry=company.industry or "",
        services=company.services or [],
        products=company.products or [],
        target_customers=company.target_customers or [],
        pain_points=company.pain_points or [],
    )

    log = await log_repo.create({
        "workspace_id": workspace_id,
        "agent_type": AgentType.LEAD_FINDER,
        "status": AgentStatus.RUNNING,
        "input_data": {"company_id": data.company_id, "count": data.count},
    })

    start = time.time()
    try:
        finder = LeadFinderAgent()
        scorer = LeadScorerAgent()
        raw_leads = await finder.find_leads(profile, count=data.count)

        analytics = AnalyticsService(db)
        vector_svc = VectorService()
        saved_leads = []

        for raw in raw_leads:
            score, status, _ = await scorer.score_lead(raw, profile)
            lead = await lead_repo.create({
                "workspace_id": workspace_id,
                "company_id": company.id,
                "company_name": raw.get("company_name", ""),
                "website": raw.get("website"),
                "industry": raw.get("industry"),
                "email": raw.get("email"),
                "linkedin": raw.get("linkedin"),
                "first_name": raw.get("first_name"),
                "last_name": raw.get("last_name"),
                "job_title": raw.get("job_title"),
                "lead_score": score,
                "status": status,
            })

            try:
                qdrant_id = await vector_svc.upsert_lead(lead.id, raw, workspace_id)
                lead.qdrant_id = qdrant_id
                db.add(lead)
            except Exception:
                pass

            await analytics.record_new_lead(workspace_id)
            saved_leads.append(lead)

        await log_repo.update(log, {
            "status": AgentStatus.COMPLETED,
            "output_data": {"count": len(saved_leads)},
            "duration_seconds": time.time() - start,
            "completed_at": datetime.now(timezone.utc),
        })

        return saved_leads
    except Exception as e:
        await log_repo.update(log, {"status": AgentStatus.FAILED, "error_message": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workspaces/{workspace_id}/leads", response_model=PaginatedResponse)
async def list_leads(
    workspace_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[LeadStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = LeadRepository(db)
    skip = (page - 1) * page_size
    leads, total = await repo.get_by_workspace(workspace_id, skip=skip, limit=page_size, status=status)
    pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=[LeadResponse.model_validate(l) for l in leads],
        total=total, page=page, page_size=page_size, pages=pages
    )


@router.get("/workspaces/{workspace_id}/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    workspace_id: str, lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = LeadRepository(db)
    lead = await repo.get(lead_id)
    if not lead or lead.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/workspaces/{workspace_id}/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    workspace_id: str, lead_id: str, data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = LeadRepository(db)
    lead = await repo.get(lead_id)
    if not lead or lead.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Lead not found")
    return await repo.update(lead, data.model_dump(exclude_none=True))


@router.delete("/workspaces/{workspace_id}/leads/{lead_id}", status_code=204)
async def delete_lead(
    workspace_id: str, lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = LeadRepository(db)
    lead = await repo.get(lead_id)
    if not lead or lead.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Lead not found")
    await repo.delete(lead_id)


# ─── Campaigns ────────────────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/campaigns", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    workspace_id: str, data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CampaignRepository(db)
    return await repo.create({"workspace_id": workspace_id, **data.model_dump()})


@router.get("/workspaces/{workspace_id}/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CampaignRepository(db)
    return await repo.get_by_workspace(workspace_id)


@router.patch("/workspaces/{workspace_id}/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    workspace_id: str, campaign_id: str, data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CampaignRepository(db)
    campaign = await repo.get(campaign_id)
    if not campaign or campaign.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return await repo.update(campaign, data.model_dump(exclude_none=True))


@router.post("/workspaces/{workspace_id}/campaigns/{campaign_id}/pause")
async def pause_campaign(
    workspace_id: str, campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CampaignRepository(db)
    campaign = await repo.get(campaign_id)
    if not campaign or campaign.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await repo.update(campaign, {"status": CampaignStatus.PAUSED})
    return {"message": "Campaign paused"}


@router.post("/workspaces/{workspace_id}/campaigns/{campaign_id}/resume")
async def resume_campaign(
    workspace_id: str, campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CampaignRepository(db)
    campaign = await repo.get(campaign_id)
    if not campaign or campaign.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await repo.update(campaign, {"status": CampaignStatus.ACTIVE})
    return {"message": "Campaign resumed"}


@router.delete("/workspaces/{workspace_id}/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(
    workspace_id: str, campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CampaignRepository(db)
    campaign = await repo.get(campaign_id)
    if not campaign or campaign.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await repo.update(campaign, {"status": CampaignStatus.DELETED})


# ─── Emails ───────────────────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/emails/generate", response_model=EmailResponse)
async def generate_email(
    workspace_id: str,
    data: EmailGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lead_repo = LeadRepository(db)
    email_repo = EmailRepository(db)
    company_repo = CompanyRepository(db)

    lead = await lead_repo.get(data.lead_id)
    if not lead or lead.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Lead not found")

    sender_company = {}
    if lead.company_id:
        company = await company_repo.get(lead.company_id)
        if company:
            sender_company = {
                "company_name": company.company_name,
                "industry": company.industry,
                "services": company.services or [],
                "pain_points": company.pain_points or [],
            }

    agent = EmailGeneratorAgent()
    lead_dict = {
        "company_name": lead.company_name,
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "job_title": lead.job_title,
        "industry": lead.industry,
    }

    result = await agent.generate_email(
        sender_company=sender_company,
        lead=lead_dict,
        email_type=data.email_type,
        email_style=data.email_style,
        campaign_goal=data.custom_goal,
        followup_day=data.followup_day,
    )

    email = await email_repo.create({
        "lead_id": lead.id,
        "campaign_id": data.campaign_id,
        "subject": result["subject"],
        "body": result["body"],
        "email_type": data.email_type,
        "email_style": data.email_style,
        "followup_day": data.followup_day,
    })

    return email


@router.get("/workspaces/{workspace_id}/emails", response_model=PaginatedResponse)
async def list_emails(
    workspace_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.models import Email, Lead
    result = await db.execute(
        select(Email)
        .join(Lead, Lead.id == Email.lead_id)
        .where(Lead.workspace_id == workspace_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(Email.created_at.desc())
    )
    emails = result.scalars().all()

    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count(Email.id))
        .join(Lead, Lead.id == Email.lead_id)
        .where(Lead.workspace_id == workspace_id)
    )
    total = count_result.scalar_one()
    pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=[EmailResponse.model_validate(e) for e in emails],
        total=total, page=page, page_size=page_size, pages=pages
    )


# ─── Analytics ────────────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/analytics/dashboard", response_model=DashboardMetrics)
async def get_dashboard(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_dashboard_metrics(workspace_id)


@router.get("/workspaces/{workspace_id}/analytics/daily", response_model=List[DailyAnalytics])
async def get_daily_analytics(
    workspace_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_daily_analytics(workspace_id, days)


@router.get("/workspaces/{workspace_id}/analytics/campaigns", response_model=List[CampaignPerformance])
async def get_campaign_performance(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_campaign_performance(workspace_id)


# ─── Agent Logs ───────────────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/agent-logs", response_model=List[AgentLogResponse])
async def get_agent_logs(
    workspace_id: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = AgentLogRepository(db)
    return await repo.get_by_workspace(workspace_id, limit=limit)


# ─── Full Pipeline ────────────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/pipeline/run")
async def run_pipeline(
    workspace_id: str,
    data: CompanyAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    result = await run_full_pipeline(data.website_url, workspace_id)
    return {
        "status": result["current_step"],
        "company_profile": result["company_profile"],
        "leads_found": len(result.get("scored_leads") or []),
        "emails_generated": len(result.get("emails") or []),
        "errors": result.get("errors", []),
    }


# ─── Vector Search ────────────────────────────────────────────────────────────

@router.post("/workspaces/{workspace_id}/search", response_model=List[VectorSearchResult])
async def vector_search(
    workspace_id: str,
    data: VectorSearchRequest,
    current_user: User = Depends(get_current_user),
):
    svc = VectorService()
    results = await svc.search(data.collection, data.query, workspace_id, data.limit)
    return [VectorSearchResult(**r) for r in results]

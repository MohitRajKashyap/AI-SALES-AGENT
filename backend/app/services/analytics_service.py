from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.repositories.repositories import (
    LeadRepository, EmailRepository, CampaignRepository, AnalyticsRepository
)
from app.schemas.schemas import DashboardMetrics, DailyAnalytics, CampaignPerformance
from app.models.models import Lead, Email, Campaign, Analytics, LeadStatus, EmailStatus, CampaignStatus


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lead_repo = LeadRepository(db)
        self.email_repo = EmailRepository(db)
        self.campaign_repo = CampaignRepository(db)
        self.analytics_repo = AnalyticsRepository(db)

    async def get_dashboard_metrics(self, workspace_id: str) -> DashboardMetrics:
        total_leads = await self.lead_repo.count(filters=[Lead.workspace_id == workspace_id])

        email_stats = await self.email_repo.get_stats(workspace_id)
        emails_sent = email_stats.get(EmailStatus.SENT, 0) + email_stats.get(EmailStatus.OPENED, 0) + email_stats.get(EmailStatus.REPLIED, 0)
        replies = email_stats.get(EmailStatus.REPLIED, 0)

        lead_status_counts = await self.lead_repo.count_by_status(workspace_id)
        hot_leads = lead_status_counts.get(LeadStatus.HOT, 0)
        warm_leads = lead_status_counts.get(LeadStatus.WARM, 0)
        converted = lead_status_counts.get(LeadStatus.CONVERTED, 0)

        active_campaigns = await self.campaign_repo.count_active(workspace_id)

        conversion_rate = (converted / total_leads * 100) if total_leads > 0 else 0.0

        result = await self.db.execute(
            select(func.sum(Analytics.meetings_booked))
            .where(Analytics.workspace_id == workspace_id)
        )
        meetings_booked = result.scalar_one() or 0

        return DashboardMetrics(
            total_leads=total_leads,
            emails_sent=emails_sent,
            replies=replies,
            meetings_booked=meetings_booked,
            conversion_rate=round(conversion_rate, 2),
            hot_leads=hot_leads,
            warm_leads=warm_leads,
            active_campaigns=active_campaigns,
        )

    async def get_daily_analytics(self, workspace_id: str, days: int = 30) -> list[DailyAnalytics]:
        records = await self.analytics_repo.get_daily_range(workspace_id, days)
        return [
            DailyAnalytics(
                date=r.date.strftime("%Y-%m-%d"),
                emails_sent=r.emails_sent,
                emails_opened=r.emails_opened,
                replies=r.replies,
                new_leads=r.new_leads,
                meetings_booked=r.meetings_booked,
            )
            for r in records
        ]

    async def get_campaign_performance(self, workspace_id: str) -> list[CampaignPerformance]:
        campaigns = await self.campaign_repo.get_by_workspace(workspace_id)
        results = []

        for campaign in campaigns:
            emails, total = await self.email_repo.get_by_campaign(campaign.id, limit=1000)
            sent = sum(1 for e in emails if e.status in (EmailStatus.SENT, EmailStatus.OPENED, EmailStatus.REPLIED))
            opened = sum(1 for e in emails if e.status in (EmailStatus.OPENED, EmailStatus.REPLIED))
            replied = sum(1 for e in emails if e.status == EmailStatus.REPLIED)

            open_rate = (opened / sent * 100) if sent > 0 else 0
            reply_rate = (replied / sent * 100) if sent > 0 else 0

            results.append(CampaignPerformance(
                campaign_id=campaign.id,
                campaign_name=campaign.name,
                emails_sent=sent,
                open_rate=round(open_rate, 2),
                reply_rate=round(reply_rate, 2),
            ))

        return results

    async def record_email_sent(self, workspace_id: str):
        record = await self.analytics_repo.get_or_create_today(workspace_id)
        record.emails_sent += 1
        self.db.add(record)

    async def record_email_opened(self, workspace_id: str):
        record = await self.analytics_repo.get_or_create_today(workspace_id)
        record.emails_opened += 1
        self.db.add(record)

    async def record_reply(self, workspace_id: str):
        record = await self.analytics_repo.get_or_create_today(workspace_id)
        record.replies += 1
        self.db.add(record)

    async def record_new_lead(self, workspace_id: str):
        record = await self.analytics_repo.get_or_create_today(workspace_id)
        record.new_leads += 1
        self.db.add(record)

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, timezone

from app.repositories.base import BaseRepository
from app.models.models import (
    User, Workspace, WorkspaceMember, Lead, Campaign,
    Email, Analytics, AgentLog, Company, Subscription,
    LeadStatus, CampaignStatus, EmailStatus
)


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, db: AsyncSession):
        super().__init__(Workspace, db)

    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        result = await self.db.execute(select(Workspace).where(Workspace.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: str) -> List[Workspace]:
        result = await self.db.execute(
            select(Workspace).where(Workspace.owner_id == owner_id)
        )
        return result.scalars().all()

    async def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        result = await self.db.execute(
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
        )
        return result.scalars().all()


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db: AsyncSession):
        super().__init__(Company, db)

    async def get_by_workspace(self, workspace_id: str) -> List[Company]:
        result = await self.db.execute(
            select(Company).where(Company.workspace_id == workspace_id)
            .order_by(Company.created_at.desc())
        )
        return result.scalars().all()


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, db: AsyncSession):
        super().__init__(Lead, db)

    async def get_by_workspace(
        self, workspace_id: str, skip: int = 0, limit: int = 20,
        status: Optional[LeadStatus] = None
    ) -> tuple[List[Lead], int]:
        filters = [Lead.workspace_id == workspace_id]
        if status:
            filters.append(Lead.status == status)
        return await self.get_multi(skip=skip, limit=limit, filters=filters)

    async def count_by_status(self, workspace_id: str) -> dict:
        result = await self.db.execute(
            select(Lead.status, func.count(Lead.id))
            .where(Lead.workspace_id == workspace_id)
            .group_by(Lead.status)
        )
        return {row[0]: row[1] for row in result.fetchall()}

    async def get_hot_leads(self, workspace_id: str, limit: int = 10) -> List[Lead]:
        result = await self.db.execute(
            select(Lead)
            .where(and_(Lead.workspace_id == workspace_id, Lead.status == LeadStatus.HOT))
            .order_by(Lead.lead_score.desc())
            .limit(limit)
        )
        return result.scalars().all()


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db: AsyncSession):
        super().__init__(Campaign, db)

    async def get_by_workspace(self, workspace_id: str) -> List[Campaign]:
        result = await self.db.execute(
            select(Campaign).where(Campaign.workspace_id == workspace_id)
            .order_by(Campaign.created_at.desc())
        )
        return result.scalars().all()

    async def count_active(self, workspace_id: str) -> int:
        result = await self.db.execute(
            select(func.count(Campaign.id))
            .where(and_(
                Campaign.workspace_id == workspace_id,
                Campaign.status == CampaignStatus.ACTIVE
            ))
        )
        return result.scalar_one()


class EmailRepository(BaseRepository[Email]):
    def __init__(self, db: AsyncSession):
        super().__init__(Email, db)

    async def get_by_lead(self, lead_id: str) -> List[Email]:
        result = await self.db.execute(
            select(Email).where(Email.lead_id == lead_id)
            .order_by(Email.created_at.asc())
        )
        return result.scalars().all()

    async def get_by_campaign(self, campaign_id: str, skip: int = 0, limit: int = 20) -> tuple[List[Email], int]:
        filters = [Email.campaign_id == campaign_id]
        return await self.get_multi(skip=skip, limit=limit, filters=filters)

    async def count_sent_today(self, workspace_id: str) -> int:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.count(Email.id))
            .join(Lead, Lead.id == Email.lead_id)
            .where(and_(
                Lead.workspace_id == workspace_id,
                Email.status == EmailStatus.SENT,
                Email.sent_at >= today
            ))
        )
        return result.scalar_one()

    async def get_stats(self, workspace_id: str) -> dict:
        result = await self.db.execute(
            select(Email.status, func.count(Email.id))
            .join(Lead, Lead.id == Email.lead_id)
            .where(Lead.workspace_id == workspace_id)
            .group_by(Email.status)
        )
        return {row[0]: row[1] for row in result.fetchall()}


class AnalyticsRepository(BaseRepository[Analytics]):
    def __init__(self, db: AsyncSession):
        super().__init__(Analytics, db)

    async def get_daily_range(self, workspace_id: str, days: int = 30) -> List[Analytics]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(Analytics)
            .where(and_(
                Analytics.workspace_id == workspace_id,
                Analytics.date >= cutoff
            ))
            .order_by(Analytics.date.asc())
        )
        return result.scalars().all()

    async def get_or_create_today(self, workspace_id: str) -> Analytics:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(Analytics).where(and_(
                Analytics.workspace_id == workspace_id,
                Analytics.date == today
            ))
        )
        record = result.scalar_one_or_none()
        if not record:
            record = await self.create({
                "workspace_id": workspace_id,
                "date": today,
            })
        return record


class AgentLogRepository(BaseRepository[AgentLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AgentLog, db)

    async def get_by_workspace(self, workspace_id: str, limit: int = 20) -> List[AgentLog]:
        result = await self.db.execute(
            select(AgentLog)
            .where(AgentLog.workspace_id == workspace_id)
            .order_by(AgentLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db: AsyncSession):
        super().__init__(Subscription, db)

    async def get_by_user(self, user_id: str) -> Optional[Subscription]:
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
        )
        return result.scalar_one_or_none()

#!/usr/bin/env python3
"""
Seed the database with sample data for development/demo purposes.
Run: python scripts/seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.models import (
    User, Workspace, WorkspaceMember, Lead, Campaign, Analytics,
    UserRole, SubscriptionPlan, SubscriptionStatus,
    LeadStatus, CampaignStatus, EmailStyle, Subscription
)
from datetime import datetime, timezone, timedelta
import random


SAMPLE_LEADS = [
    {"company_name": "Stripe", "industry": "FinTech", "first_name": "Patrick", "last_name": "Collison", "job_title": "CEO", "email": "patrick@stripe.com", "website": "https://stripe.com", "lead_score": 92, "status": LeadStatus.HOT},
    {"company_name": "Notion", "industry": "SaaS", "first_name": "Ivan", "last_name": "Zhao", "job_title": "CEO", "email": "ivan@notion.so", "website": "https://notion.so", "lead_score": 85, "status": LeadStatus.HOT},
    {"company_name": "Linear", "industry": "SaaS", "first_name": "Karri", "last_name": "Saarinen", "job_title": "CEO", "email": "karri@linear.app", "website": "https://linear.app", "lead_score": 78, "status": LeadStatus.WARM},
    {"company_name": "Vercel", "industry": "DevTools", "first_name": "Guillermo", "last_name": "Rauch", "job_title": "CEO", "email": "rauch@vercel.com", "website": "https://vercel.com", "lead_score": 71, "status": LeadStatus.WARM},
    {"company_name": "Figma", "industry": "Design Tools", "first_name": "Dylan", "last_name": "Field", "job_title": "CEO", "email": "dylan@figma.com", "website": "https://figma.com", "lead_score": 65, "status": LeadStatus.WARM},
    {"company_name": "Retool", "industry": "SaaS", "first_name": "David", "last_name": "Hsu", "job_title": "CEO", "email": "david@retool.com", "website": "https://retool.com", "lead_score": 55, "status": LeadStatus.WARM},
    {"company_name": "Postman", "industry": "DevTools", "first_name": "Abhinav", "last_name": "Asthana", "job_title": "CEO", "email": "abhinav@postman.com", "website": "https://postman.com", "lead_score": 42, "status": LeadStatus.COLD},
    {"company_name": "Supabase", "industry": "DevTools", "first_name": "Paul", "last_name": "Copplestone", "job_title": "CEO", "email": "paul@supabase.io", "website": "https://supabase.com", "lead_score": 38, "status": LeadStatus.COLD},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Create demo user
        user = User(
            email="demo@aisalesagent.com",
            hashed_password=get_password_hash("demo1234"),
            full_name="Mohit Raj Kashyap",
            is_active=True,
            role=UserRole.OWNER,
        )
        db.add(user)
        await db.flush()

        # Subscription
        sub = Subscription(
            user_id=user.id,
            plan=SubscriptionPlan.PRO,
            status=SubscriptionStatus.ACTIVE,
        )
        db.add(sub)

        # Workspace
        workspace = Workspace(
            name="Acme Corp",
            slug="acme-corp",
            owner_id=user.id,
            website="https://acme.com",
            industry="SaaS",
        )
        db.add(workspace)
        await db.flush()

        # Workspace member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=UserRole.OWNER,
        )
        db.add(member)

        # Leads
        for lead_data in SAMPLE_LEADS:
            lead = Lead(workspace_id=workspace.id, **lead_data)
            db.add(lead)

        # Campaign
        campaign = Campaign(
            workspace_id=workspace.id,
            name="Q1 SaaS Outreach",
            description="Targeting SaaS founders and CTOs",
            status=CampaignStatus.ACTIVE,
            goal="Book 20 demo calls",
            daily_limit=50,
            email_style=EmailStyle.PROFESSIONAL,
            followup_days=[3, 7, 14],
            target_industry="SaaS",
        )
        db.add(campaign)

        # Analytics (last 14 days)
        for i in range(14):
            day = datetime.now(timezone.utc) - timedelta(days=i)
            analytics = Analytics(
                workspace_id=workspace.id,
                date=day.replace(hour=0, minute=0, second=0, microsecond=0),
                emails_sent=random.randint(20, 80),
                emails_opened=random.randint(8, 35),
                replies=random.randint(2, 12),
                meetings_booked=random.randint(0, 3),
                new_leads=random.randint(3, 15),
            )
            db.add(analytics)

        await db.commit()
        print("✅ Sample data seeded successfully!")
        print(f"   Email: demo@aisalesagent.com")
        print(f"   Password: demo1234")
        print(f"   Workspace: Acme Corp")


if __name__ == "__main__":
    asyncio.run(seed())

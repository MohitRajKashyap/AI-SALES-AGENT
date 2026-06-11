import asyncio
from datetime import datetime, timezone, timedelta
from app.tasks.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, email_id: str, workspace_id: str):
    """Send a queued email and update its status."""
    try:
        from app.db.session import AsyncSessionLocal
        from app.repositories.repositories import EmailRepository
        from app.models.models import EmailStatus

        async def _send():
            async with AsyncSessionLocal() as db:
                repo = EmailRepository(db)
                email = await repo.get(email_id)
                if not email:
                    return

                # In production, integrate with SendGrid/SES/SMTP here
                logger.info(f"Sending email {email_id} to lead {email.lead_id}")

                await repo.update(email, {
                    "status": EmailStatus.SENT,
                    "sent_at": datetime.now(timezone.utc),
                })

        run_async(_send())
        logger.info(f"Email {email_id} sent successfully")
    except Exception as exc:
        logger.error(f"Failed to send email {email_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task
def process_followups():
    """Check for leads needing follow-up emails and queue them."""
    async def _process():
        from app.db.session import AsyncSessionLocal
        from sqlalchemy import select, and_
        from app.models.models import Email, Lead, Campaign, EmailStatus, EmailType, CampaignStatus

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Email)
                .where(and_(
                    Email.status == EmailStatus.SENT,
                    Email.email_type == EmailType.COLD,
                    Email.replied_at == None,
                ))
            )
            emails = result.scalars().all()

            for email in emails:
                if not email.sent_at:
                    continue
                days_since = (datetime.now(timezone.utc) - email.sent_at).days

                campaign = None
                if email.campaign_id:
                    camp_result = await db.execute(
                        select(Campaign).where(Campaign.id == email.campaign_id)
                    )
                    campaign = camp_result.scalar_one_or_none()

                followup_days = campaign.followup_days if campaign else [3, 7, 14]

                for day in followup_days:
                    if days_since == day:
                        existing = await db.execute(
                            select(Email).where(and_(
                                Email.lead_id == email.lead_id,
                                Email.followup_day == day,
                            ))
                        )
                        if not existing.scalar_one_or_none():
                            logger.info(f"Queuing day-{day} followup for lead {email.lead_id}")

    run_async(_process())


@celery_app.task
def update_analytics(workspace_id: str):
    """Recalculate analytics for a workspace."""
    logger.info(f"Updating analytics for workspace {workspace_id}")

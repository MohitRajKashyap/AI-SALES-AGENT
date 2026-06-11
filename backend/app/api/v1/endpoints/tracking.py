from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.models import Email, EmailStatus

router = APIRouter()

# 1x1 transparent GIF for open tracking pixel
TRACKING_PIXEL = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
    b"\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
    b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
)


@router.get("/track/open/{tracking_id}")
async def track_open(
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Record email open event via tracking pixel."""
    result = await db.execute(
        select(Email).where(Email.tracking_id == tracking_id)
    )
    email = result.scalar_one_or_none()

    if email and email.status not in (EmailStatus.OPENED, EmailStatus.REPLIED):
        email.status = EmailStatus.OPENED
        email.opened_at = datetime.now(timezone.utc)
        db.add(email)

        # Update analytics
        from app.services.analytics_service import AnalyticsService
        from app.models.models import Lead
        lead_result = await db.execute(select(Lead).where(Lead.id == email.lead_id))
        lead = lead_result.scalar_one_or_none()
        if lead:
            svc = AnalyticsService(db)
            await svc.record_email_opened(lead.workspace_id)

        await db.commit()

    return Response(content=TRACKING_PIXEL, media_type="image/gif")


@router.get("/track/click/{tracking_id}")
async def track_click(
    tracking_id: str,
    url: str,
    db: AsyncSession = Depends(get_db),
):
    """Record email link click and redirect."""
    result = await db.execute(
        select(Email).where(Email.tracking_id == tracking_id)
    )
    email = result.scalar_one_or_none()

    if email and email.status not in (EmailStatus.REPLIED,):
        email.status = EmailStatus.OPENED
        if not email.opened_at:
            email.opened_at = datetime.now(timezone.utc)
        db.add(email)
        await db.commit()

    # Validate and redirect
    if url.startswith(("http://", "https://")):
        return RedirectResponse(url=url)
    return Response(status_code=400, content="Invalid URL")

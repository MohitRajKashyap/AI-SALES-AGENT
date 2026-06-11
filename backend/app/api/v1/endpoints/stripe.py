from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.stripe_service import StripeService
from app.models.models import User, SubscriptionPlan
from app.core.config import settings

router = APIRouter()


class CheckoutRequest(BaseModel):
    plan: SubscriptionPlan
    success_url: str = "http://localhost:3000/dashboard/settings?checkout=success"
    cancel_url: str = "http://localhost:3000/dashboard/settings?checkout=cancel"


@router.post("/checkout")
async def create_checkout_session(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StripeService(db)
    url = await service.create_checkout_session(
        user_id=current_user.id,
        plan=data.plan,
        success_url=data.success_url,
        cancel_url=data.cancel_url,
    )
    return {"checkout_url": url}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    service = StripeService(db)
    return await service.handle_webhook(payload, sig_header)


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.repositories import SubscriptionRepository
    repo = SubscriptionRepository(db)
    sub = await repo.get_by_user(current_user.id)
    if not sub:
        return {"plan": "free", "status": "active"}
    return {
        "plan": sub.plan,
        "status": sub.status,
        "current_period_end": sub.current_period_end,
    }

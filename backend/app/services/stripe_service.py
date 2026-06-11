import stripe
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.repositories import SubscriptionRepository, UserRepository
from app.models.models import SubscriptionPlan, SubscriptionStatus

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    SubscriptionPlan.PRO: settings.STRIPE_PRO_PRICE_ID,
    SubscriptionPlan.ENTERPRISE: settings.STRIPE_ENTERPRISE_PRICE_ID,
}


class StripeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sub_repo = SubscriptionRepository(db)
        self.user_repo = UserRepository(db)

    async def create_checkout_session(self, user_id: str, plan: SubscriptionPlan, success_url: str, cancel_url: str) -> str:
        if plan == SubscriptionPlan.FREE:
            raise HTTPException(status_code=400, detail="Cannot checkout free plan")

        price_id = PLAN_PRICE_MAP.get(plan)
        if not price_id:
            raise HTTPException(status_code=400, detail="Invalid plan")

        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        subscription = await self.sub_repo.get_by_user(user_id)

        customer_id = None
        if subscription and subscription.stripe_customer_id:
            customer_id = subscription.stripe_customer_id

        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={"user_id": user_id},
            )
            customer_id = customer.id
            if subscription:
                await self.sub_repo.update(subscription, {"stripe_customer_id": customer_id})

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user_id, "plan": plan.value},
        )
        return session.url

    async def handle_webhook(self, payload: bytes, sig_header: str):
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            await self._handle_checkout_complete(session)

        elif event["type"] == "customer.subscription.updated":
            sub = event["data"]["object"]
            await self._handle_subscription_update(sub)

        elif event["type"] == "customer.subscription.deleted":
            sub = event["data"]["object"]
            await self._handle_subscription_deleted(sub)

        return {"received": True}

    async def _handle_checkout_complete(self, session: dict):
        user_id = session.get("metadata", {}).get("user_id")
        plan_str = session.get("metadata", {}).get("plan", "free")
        stripe_sub_id = session.get("subscription")

        if not user_id:
            return

        plan = SubscriptionPlan(plan_str)
        subscription = await self.sub_repo.get_by_user(user_id)

        update_data = {
            "plan": plan,
            "status": SubscriptionStatus.ACTIVE,
            "stripe_subscription_id": stripe_sub_id,
            "stripe_customer_id": session.get("customer"),
        }

        if subscription:
            await self.sub_repo.update(subscription, update_data)
        else:
            await self.sub_repo.create({"user_id": user_id, **update_data})

    async def _handle_subscription_update(self, stripe_sub: dict):
        stripe_sub_id = stripe_sub.get("id")
        from sqlalchemy import select
        from app.models.models import Subscription
        result = await self.db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            status_map = {
                "active": SubscriptionStatus.ACTIVE,
                "past_due": SubscriptionStatus.PAST_DUE,
                "canceled": SubscriptionStatus.CANCELLED,
                "trialing": SubscriptionStatus.TRIALING,
            }
            new_status = status_map.get(stripe_sub.get("status"), SubscriptionStatus.ACTIVE)
            await self.sub_repo.update(subscription, {"status": new_status})

    async def _handle_subscription_deleted(self, stripe_sub: dict):
        stripe_sub_id = stripe_sub.get("id")
        from sqlalchemy import select
        from app.models.models import Subscription
        result = await self.db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            await self.sub_repo.update(subscription, {
                "status": SubscriptionStatus.CANCELLED,
                "plan": SubscriptionPlan.FREE,
            })

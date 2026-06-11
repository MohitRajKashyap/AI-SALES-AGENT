from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_superuser
from app.models.models import User, Workspace, Lead, Email, Campaign
from app.schemas.schemas import AdminUserList, AdminStats
from app.repositories.repositories import UserRepository

router = APIRouter()


@router.get("/stats", response_model=AdminStats)
async def admin_stats(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    async def count(model):
        r = await db.execute(select(func.count(model.id)))
        return r.scalar_one()

    return AdminStats(
        total_users=await count(User),
        total_workspaces=await count(Workspace),
        total_leads=await count(Lead),
        total_emails=await count(Email),
        total_campaigns=await count(Campaign),
    )


@router.get("/users", response_model=List[AdminUserList])
async def list_users(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()).limit(100))
    return result.scalars().all()


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if user:
        await repo.update(user, {"is_active": False})
    return {"message": "User deactivated"}


@router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if user:
        await repo.update(user, {"is_active": True})
    return {"message": "User activated"}

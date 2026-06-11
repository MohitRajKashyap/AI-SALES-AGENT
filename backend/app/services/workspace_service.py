import re
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repositories import WorkspaceRepository
from app.schemas.schemas import WorkspaceCreate, WorkspaceUpdate, MemberInvite
from app.models.models import Workspace, WorkspaceMember, User, UserRole


def slugify(name: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


class WorkspaceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkspaceRepository(db)

    async def create_workspace(self, data: WorkspaceCreate, owner: User) -> Workspace:
        base_slug = slugify(data.name)
        slug = base_slug
        counter = 1
        while await self.repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        workspace = await self.repo.create({
            "name": data.name,
            "slug": slug,
            "website": data.website,
            "industry": data.industry,
            "owner_id": owner.id,
        })

        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner.id,
            role=UserRole.OWNER,
        )
        self.db.add(member)
        await self.db.flush()

        return workspace

    async def get_workspace(self, workspace_id: str, user: User) -> Workspace:
        workspace = await self.repo.get(workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        await self._check_access(workspace, user)
        return workspace

    async def update_workspace(self, workspace_id: str, data: WorkspaceUpdate, user: User) -> Workspace:
        workspace = await self.get_workspace(workspace_id, user)
        return await self.repo.update(workspace, data.model_dump(exclude_none=True))

    async def get_user_workspaces(self, user: User) -> list[Workspace]:
        return await self.repo.get_user_workspaces(user.id)

    async def _check_access(self, workspace: Workspace, user: User):
        if user.is_superuser:
            return
        from sqlalchemy import select
        from app.models.models import WorkspaceMember
        result = await self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace.id,
                WorkspaceMember.user_id == user.id
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=403, detail="Access denied to this workspace")

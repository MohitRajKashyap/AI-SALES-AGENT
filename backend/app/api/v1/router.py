from fastapi import APIRouter
from app.api.v1.endpoints import auth, workspaces, main_endpoints, admin, stripe, tracking

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(main_endpoints.router, prefix="", tags=["Core"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(stripe.router, prefix="/billing", tags=["Billing"])
api_router.include_router(tracking.router, prefix="", tags=["Tracking"])

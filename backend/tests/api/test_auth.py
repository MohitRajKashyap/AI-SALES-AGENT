import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.base import Base

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client):
    # Register
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    })
    # Login
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    @pytest.mark.asyncio
    async def test_register(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "password": "newpass123",
            "full_name": "New User"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        await client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "testpass123",
            "full_name": "First User"
        })
        resp = await client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "testpass456",
            "full_name": "Second User"
        })
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        await client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "password": "loginpass123",
            "full_name": "Login User"
        })
        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "loginpass123"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me(self, client, auth_headers):
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 403


class TestWorkspaces:
    @pytest.mark.asyncio
    async def test_create_workspace(self, client, auth_headers):
        resp = await client.post("/api/v1/workspaces", json={
            "name": "Test Company",
            "industry": "SaaS"
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Company"
        assert "slug" in data
        return data["id"]

    @pytest.mark.asyncio
    async def test_list_workspaces(self, client, auth_headers):
        resp = await client.get("/api/v1/workspaces", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

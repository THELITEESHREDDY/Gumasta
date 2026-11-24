import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import StaticPool
from sqlalchemy import event

import app.models

from app.main import app as fastapi_app
from app.db.base import Base
from app.db.session import get_db


@pytest_asyncio.fixture
async def client():

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool
    )

    @event.listens_for(engine.sync_engine, "connect")
    def enable_foreign_keys(connection, record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://test"
        ) as test_client:
            yield test_client

    finally:
        fastapi_app.dependency_overrides.pop(get_db, None)
        await engine.dispose()

@pytest_asyncio.fixture
async def create_authenticated_user(client):

    async def create_user(email: str):

        user_data = {
            "name": "Test User",
            "email": email,
            "mobile": "9876543210",
            "password": "TestPassword123"
        }

        response = await client.post(
            "/auth/register",
            json=user_data
        )

        assert response.status_code == 201

        user = response.json()

        response = await client.post(
            "/auth/login",
            data={
                "username": email,
                "password": user_data["password"]
            }
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        return {
            "user": user,
            "headers": {
                "Authorization": f"Bearer {token}"
            }
        }

    return create_user
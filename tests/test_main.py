import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
import models
from database import DATABASE_URL
from main import app


@pytest.fixture(scope="module", autouse=True)
async def setup_database() -> None:
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.anyio
async def test_create_and_get() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/recipes",
            json={
                "title": "Тест",
                "cooking_time": 10,
                "ingredients": "ингредиенты",
                "description": "описание",
            },
        )
        assert resp.status_code == 201
        recipe_id = resp.json()["id"]
        resp_list = await ac.get("/recipes")
        assert resp_list.status_code == 200
        assert len(resp_list.json()) >= 1
        resp_detail = await ac.get(f"/recipes/{recipe_id}")
        assert resp_detail.status_code == 200
        assert resp_detail.json()["views"] == 1

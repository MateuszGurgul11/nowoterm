import httpx
import pytest

from app.main import app
from app.schemas import PagePayload


@pytest.mark.asyncio
async def test_health_and_login_page_are_available() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/health/live")
        login = await client.get("/admin/login")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert login.status_code == 200
    assert "Zaloguj się" in login.text
    assert 'name="email"' in login.text


@pytest.mark.asyncio
async def test_export_requires_token() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/export/site")

    assert response.status_code == 401


def test_page_schema_rejects_invalid_slug() -> None:
    with pytest.raises(ValueError):
        PagePayload(
            slug="Nie poprawny slug",
            title="Tytuł",
            seo_title="Tytuł SEO",
            seo_description="Opis strony przeznaczony dla wyników wyszukiwania.",
        )


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/admin/login",
            data={"email": "nieistnieje@example.com", "password": "zle-haslo"},
        )

    assert response.status_code == 401
    assert "Nieprawidłowy email lub hasło" in response.text

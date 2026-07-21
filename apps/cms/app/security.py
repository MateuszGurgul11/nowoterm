import secrets
from typing import Annotated

import httpx
from fastapi import Header, HTTPException, Request, status

from app.config import get_settings


async def authenticate_supabase(email: str, password: str) -> str | None:
    """Zwraca email użytkownika po udanym logowaniu przez Supabase Auth, inaczej None."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        return None

    url = f"{settings.supabase_url.rstrip('/')}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": settings.supabase_publishable_key,
        "Content-Type": "application/json",
    }
    payload = {"email": email.strip(), "password": password}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError:
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    user = data.get("user") or {}
    return str(user.get("email") or email.strip())


def require_admin(request: Request) -> str:
    username = request.session.get("admin_username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Zaloguj się do panelu CMS.",
        )
    if not request.session.get("csrf_token"):
        request.session["csrf_token"] = secrets.token_urlsafe(32)
    return str(username)


def require_export_token(
    x_export_token: Annotated[str | None, Header()] = None,
) -> None:
    expected = get_settings().export_token
    if not expected or not x_export_token or not secrets.compare_digest(expected, x_export_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy token eksportu.",
        )

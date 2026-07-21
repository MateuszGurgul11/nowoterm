from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import admin, content, export, health, media

settings = get_settings()
app = FastAPI(
    title="Novoterm CMS",
    version="0.1.0",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url=None,
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="strict",
    https_only=settings.environment == "production",
    max_age=60 * 60 * 8,
)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)
app.include_router(health.router)
app.include_router(export.router)
app.include_router(content.router)
app.include_router(media.router)
app.include_router(admin.router)


@app.exception_handler(StarletteHTTPException)
async def redirect_unauthenticated_admin(request: Request, exc: StarletteHTTPException) -> Response:
    # niezalogowane wejście na stronę panelu trafia na ekran logowania zamiast na goły JSON 401
    is_admin_page = request.url.path.startswith("/admin") and not request.url.path.startswith(
        "/admin/login"
    )
    if exc.status_code == 401 and is_admin_page:
        return RedirectResponse(f"/admin/login?next={request.url.path}", status_code=303)
    return await http_exception_handler(request, exc)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse("/admin", status_code=302)

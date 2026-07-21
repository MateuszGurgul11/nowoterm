import json
import secrets
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.models import ContentStatus, Media, Page, Project
from app.routers.content import apply_payload, commit_or_conflict
from app.schemas import PagePayload, ProjectPayload
from app.security import authenticate_supabase, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")
Session = Annotated[AsyncSession, Depends(get_session)]


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def ensure_csrf(request: Request, token: str) -> None:
    expected = request.session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(expected, token):
        raise HTTPException(status_code=403, detail="Nieprawidłowy token formularza.")


def parse_optional_decimal(raw: str | None) -> Decimal | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        return Decimal(str(raw).strip().replace(",", "."))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Nieprawidłowa wartość metrażu.") from exc


def parse_optional_date(raw: str | None) -> date | None:
    if raw is None or not str(raw).strip():
        return None
    return date.fromisoformat(str(raw).strip())


def parse_optional_uuid(raw: str | None) -> UUID | None:
    if raw is None or not str(raw).strip():
        return None
    return UUID(str(raw).strip())


async def media_context(session: AsyncSession) -> list[dict[str, Any]]:
    rows = list((await session.scalars(select(Media).order_by(Media.created_at.desc()))).all())
    return [
        {
            "id": str(item.id),
            "url": item.public_url,
            "file_name": item.file_name,
            "alt_text": item.alt_text,
        }
        for item in rows
    ]


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse, response_model=None)
async def login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
) -> HTMLResponse | RedirectResponse:
    authenticated_email = await authenticate_supabase(email, password)
    if not authenticated_email:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Nieprawidłowy email lub hasło."},
            status_code=401,
        )

    request.session.clear()
    request.session["admin_username"] = authenticated_email
    request.session["csrf_token"] = secrets.token_urlsafe(32)
    return redirect("/admin")


@router.post("/logout")
async def logout(request: Request, csrf_token: Annotated[str, Form()]) -> RedirectResponse:
    ensure_csrf(request, csrf_token)
    request.session.clear()
    return redirect("/admin/login")


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    session: Session,
    _: str = Depends(require_admin),
) -> HTMLResponse:
    page_count = await session.scalar(select(func.count()).select_from(Page))
    project_count = await session.scalar(select(func.count()).select_from(Project))
    pages = list(
        (await session.scalars(select(Page).order_by(Page.updated_at.desc()).limit(12))).all()
    )
    projects = list(
        (
            await session.scalars(
                select(Project).order_by(Project.sort_order.asc(), Project.updated_at.desc())
            )
        ).all()
    )
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "page_count": page_count or 0,
            "project_count": project_count or 0,
            "pages": pages,
            "projects": projects,
            "csrf_token": request.session["csrf_token"],
        },
    )


@router.get("/media", response_class=HTMLResponse)
async def media_library(
    request: Request,
    session: Session,
    _: str = Depends(require_admin),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "media.html",
        {
            "media_items": await media_context(session),
            "csrf_token": request.session["csrf_token"],
        },
    )


@router.get("/pages/new", response_class=HTMLResponse)
@router.get("/pages/{page_id}/edit", response_class=HTMLResponse)
async def page_form(
    request: Request,
    session: Session,
    page_id: UUID | None = None,
    _: str = Depends(require_admin),
) -> HTMLResponse:
    page = await session.get(Page, page_id) if page_id else None
    if page_id and page is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono strony.")
    content = page.content if page else {"blocks": []}
    if "blocks" not in content:
        content = {"blocks": []}
    return templates.TemplateResponse(
        request,
        "page_form.html",
        {
            "page": page,
            "content_json": json.dumps(content, ensure_ascii=False),
            "media_items": await media_context(session),
            "csrf_token": request.session["csrf_token"],
            "error": None,
        },
    )


@router.post("/pages/save", response_class=HTMLResponse, response_model=None)
async def save_page(
    request: Request,
    session: Session,
    csrf_token: Annotated[str, Form()],
    slug: Annotated[str, Form()],
    title: Annotated[str, Form()],
    seo_title: Annotated[str, Form()],
    seo_description: Annotated[str, Form()],
    content_json: Annotated[str, Form()],
    content_status: Annotated[ContentStatus, Form()],
    page_id: Annotated[UUID | None, Form()] = None,
    _: str = Depends(require_admin),
) -> HTMLResponse | RedirectResponse:
    ensure_csrf(request, csrf_token)
    try:
        payload = PagePayload(
            slug=slug,
            title=title,
            seo_title=seo_title,
            seo_description=seo_description,
            content=json.loads(content_json),
            status=content_status,
        )
    except (json.JSONDecodeError, ValidationError) as exc:
        return templates.TemplateResponse(
            request,
            "page_form.html",
            {
                "page": None,
                "content_json": content_json,
                "media_items": await media_context(session),
                "csrf_token": csrf_token,
                "error": str(exc),
            },
            status_code=422,
        )

    page = await session.get(Page, page_id) if page_id else Page()
    if page is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono strony.")
    apply_payload(page, payload)
    session.add(page)
    await commit_or_conflict(session)
    return redirect("/admin")


@router.get("/projects/new", response_class=HTMLResponse)
@router.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def project_form(
    request: Request,
    session: Session,
    project_id: UUID | None = None,
    _: str = Depends(require_admin),
) -> HTMLResponse:
    project = await session.get(Project, project_id) if project_id else None
    if project_id and project is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono realizacji.")
    content = project.content if project else {"blocks": []}
    if "blocks" not in content:
        content = {"blocks": []}
    return templates.TemplateResponse(
        request,
        "project_form.html",
        {
            "project": project,
            "content_json": json.dumps(content, ensure_ascii=False),
            "gallery_json": json.dumps(
                project.gallery if project else [], ensure_ascii=False
            ),
            "media_items": await media_context(session),
            "csrf_token": request.session["csrf_token"],
            "error": None,
        },
    )


@router.post("/projects/save", response_class=HTMLResponse, response_model=None)
async def save_project(
    request: Request,
    session: Session,
    csrf_token: Annotated[str, Form()],
    slug: Annotated[str, Form()],
    title: Annotated[str, Form()],
    excerpt: Annotated[str, Form()],
    category: Annotated[str, Form()],
    location: Annotated[str, Form()],
    seo_title: Annotated[str, Form()],
    seo_description: Annotated[str, Form()],
    content_json: Annotated[str, Form()],
    gallery_json: Annotated[str, Form()],
    content_status: Annotated[ContentStatus, Form()],
    area_m2: Annotated[str, Form()] = "",
    duration: Annotated[str, Form()] = "",
    completion_date: Annotated[str, Form()] = "",
    cover_image_id: Annotated[str, Form()] = "",
    featured: Annotated[str | None, Form()] = None,
    project_id: Annotated[UUID | None, Form()] = None,
    _: str = Depends(require_admin),
) -> HTMLResponse | RedirectResponse:
    ensure_csrf(request, csrf_token)
    form_error_context = {
        "project": None,
        "content_json": content_json,
        "gallery_json": gallery_json,
        "media_items": await media_context(session),
        "csrf_token": csrf_token,
    }
    try:
        existing = await session.get(Project, project_id) if project_id else None
        sort_order = existing.sort_order if existing else 0
        if existing is None:
            max_order = await session.scalar(select(func.max(Project.sort_order)))
            sort_order = int(max_order or -1) + 1

        payload = ProjectPayload(
            slug=slug,
            title=title,
            excerpt=excerpt,
            category=category,
            location=location or None,
            area_m2=parse_optional_decimal(area_m2),
            duration=duration.strip() or None,
            completion_date=parse_optional_date(completion_date),
            featured=featured in {"on", "true", "1"},
            sort_order=sort_order,
            cover_image_id=parse_optional_uuid(cover_image_id),
            seo_title=seo_title,
            seo_description=seo_description,
            content=json.loads(content_json),
            gallery=json.loads(gallery_json),
            status=content_status,
        )
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return templates.TemplateResponse(
            request,
            "project_form.html",
            {**form_error_context, "error": str(exc)},
            status_code=422,
        )

    project = await session.get(Project, project_id) if project_id else Project()
    if project is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono realizacji.")
    apply_payload(project, payload)
    session.add(project)
    await commit_or_conflict(session)
    return redirect("/admin")


@router.post("/projects/reorder")
async def reorder_projects(
    request: Request,
    session: Session,
    _: str = Depends(require_admin),
) -> dict[str, bool]:
    body = await request.json()
    ensure_csrf(request, str(body.get("csrf_token", "")))
    order = body.get("order") or []
    if not isinstance(order, list):
        raise HTTPException(status_code=422, detail="Nieprawidłowa kolejność.")

    for index, raw_id in enumerate(order):
        try:
            project_id = UUID(str(raw_id))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Nieprawidłowy identyfikator.") from exc
        project = await session.get(Project, project_id)
        if project is None:
            continue
        project.sort_order = index
        session.add(project)
    await session.commit()
    return {"ok": True}


@router.post("/publish")
async def publish(
    request: Request,
    csrf_token: Annotated[str, Form()],
    _: str = Depends(require_admin),
) -> RedirectResponse:
    ensure_csrf(request, csrf_token)
    hook = get_settings().vercel_deploy_hook
    if not hook:
        raise HTTPException(status_code=503, detail="Brak VERCEL_DEPLOY_HOOK.")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(hook, json={"published_at": datetime.now(UTC).isoformat()})
        response.raise_for_status()
    return redirect("/admin?published=1")

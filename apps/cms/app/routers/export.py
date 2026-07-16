from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import CaseStudy, ContentStatus, Media, Page, Post, Project, SiteSettings
from app.security import require_export_token

router = APIRouter(
    prefix="/api/export",
    tags=["export"],
    dependencies=[Depends(require_export_token)],
)
Session = Annotated[AsyncSession, Depends(get_session)]


def serialize_model(model: Any) -> dict[str, Any]:
    data = {column.name: getattr(model, column.name) for column in model.__table__.columns}
    return jsonable_encoder(data)


async def published(session: AsyncSession, model: Any) -> list[Any]:
    result = await session.scalars(
        select(model)
        .where(model.status == ContentStatus.PUBLISHED)
        .order_by(model.published_at.desc())
    )
    return list(result.all())


@router.get("/site")
async def export_site(session: Session) -> dict[str, Any]:
    settings = await session.get(SiteSettings, "default")
    media = list((await session.scalars(select(Media).order_by(Media.created_at))).all())
    pages = await published(session, Page)
    projects = await published(session, Project)
    posts = await published(session, Post)
    case_studies = await published(session, CaseStudy)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC),
        "settings": serialize_model(settings) if settings else None,
        "media": [serialize_model(item) for item in media],
        "pages": [serialize_model(item) for item in pages],
        "projects": [serialize_model(item) for item in projects],
        "posts": [serialize_model(item) for item in posts],
        "case_studies": [serialize_model(item) for item in case_studies],
    }

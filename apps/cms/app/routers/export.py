from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

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


async def published(session: AsyncSession, model: Any, *order_by: Any) -> list[Any]:
    query = select(model).where(model.status == ContentStatus.PUBLISHED)
    if order_by:
        query = query.order_by(*order_by)
    else:
        query = query.order_by(model.published_at.desc())
    result = await session.scalars(query)
    return list(result.all())


def enrich_cover(item: dict[str, Any], media_by_id: dict[UUID, Media]) -> dict[str, Any]:
    cover_id = item.get("cover_image_id")
    if cover_id:
        media = media_by_id.get(UUID(str(cover_id)) if not isinstance(cover_id, UUID) else cover_id)
        item["cover_image"] = media.public_url if media else None
    else:
        item["cover_image"] = None
    return item


@router.get("/site")
async def export_site(session: Session) -> dict[str, Any]:
    settings = await session.get(SiteSettings, "default")
    media_rows = list((await session.scalars(select(Media).order_by(Media.created_at))).all())
    media_by_id = {item.id: item for item in media_rows}
    pages = await published(session, Page)
    projects = await published(session, Project, Project.sort_order.asc(), Project.published_at.desc())
    posts = await published(session, Post)
    case_studies = await published(session, CaseStudy)

    serialized_projects = [
        enrich_cover(serialize_model(item), media_by_id) for item in projects
    ]
    serialized_posts = [enrich_cover(serialize_model(item), media_by_id) for item in posts]
    serialized_case_studies = [
        enrich_cover(serialize_model(item), media_by_id) for item in case_studies
    ]

    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC),
        "settings": serialize_model(settings) if settings else None,
        "media": [serialize_model(item) for item in media_rows],
        "pages": [serialize_model(item) for item in pages],
        "projects": serialized_projects,
        "posts": serialized_posts,
        "case_studies": serialized_case_studies,
    }

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import CaseStudy, ContentStatus, Page, Project
from app.schemas import (
    CaseStudyPayload,
    CaseStudyResponse,
    PagePayload,
    PageResponse,
    ProjectPayload,
    ProjectResponse,
)
from app.security import require_admin

router = APIRouter(
    prefix="/api/admin",
    tags=["content"],
    dependencies=[Depends(require_admin)],
)
Session = Annotated[AsyncSession, Depends(get_session)]


from typing import TypeVar

ModelT = TypeVar("ModelT", Page, Project, CaseStudy)


def apply_payload(
    model: ModelT, payload: PagePayload | ProjectPayload | CaseStudyPayload
) -> ModelT:
    values = payload.model_dump()
    for field, value in values.items():
        setattr(model, field, value)
    if payload.status == ContentStatus.PUBLISHED and model.published_at is None:
        model.published_at = datetime.now(UTC)
    elif payload.status != ContentStatus.PUBLISHED:
        model.published_at = None
    return model


async def commit_or_conflict(session: AsyncSession) -> None:
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slug jest już używany albo dane naruszają reguły CMS.",
        ) from exc


@router.get("/pages", response_model=list[PageResponse])
async def list_pages(session: Session) -> list[Page]:
    return list((await session.scalars(select(Page).order_by(Page.updated_at.desc()))).all())


@router.post("/pages", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_page(payload: PagePayload, session: Session) -> Page:
    page = apply_payload(Page(), payload)
    session.add(page)
    await commit_or_conflict(session)
    await session.refresh(page)
    return page


@router.put("/pages/{page_id}", response_model=PageResponse)
async def update_page(page_id: UUID, payload: PagePayload, session: Session) -> Page:
    page = await session.get(Page, page_id)
    if page is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono strony.")
    apply_payload(page, payload)
    await commit_or_conflict(session)
    await session.refresh(page)
    return page


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(page_id: UUID, session: Session) -> Response:
    page = await session.get(Page, page_id)
    if page is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono strony.")
    await session.delete(page)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(session: Session) -> list[Project]:
    return list(
        (
            await session.scalars(
                select(Project).order_by(Project.sort_order.asc(), Project.updated_at.desc())
            )
        ).all()
    )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectPayload, session: Session) -> Project:
    project = apply_payload(Project(), payload)
    session.add(project)
    await commit_or_conflict(session)
    await session.refresh(project)
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, payload: ProjectPayload, session: Session) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono realizacji.")
    apply_payload(project, payload)
    await commit_or_conflict(session)
    await session.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, session: Session) -> Response:
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono realizacji.")
    await session.delete(project)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/case-studies", response_model=list[CaseStudyResponse])
async def list_case_studies(session: Session) -> list[CaseStudy]:
    return list(
        (await session.scalars(select(CaseStudy).order_by(CaseStudy.updated_at.desc()))).all()
    )


@router.post("/case-studies", response_model=CaseStudyResponse, status_code=status.HTTP_201_CREATED)
async def create_case_study(payload: CaseStudyPayload, session: Session) -> CaseStudy:
    case_study = apply_payload(CaseStudy(), payload)
    session.add(case_study)
    await commit_or_conflict(session)
    await session.refresh(case_study)
    return case_study


@router.put("/case-studies/{case_study_id}", response_model=CaseStudyResponse)
async def update_case_study(
    case_study_id: UUID, payload: CaseStudyPayload, session: Session
) -> CaseStudy:
    case_study = await session.get(CaseStudy, case_study_id)
    if case_study is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono case study.")
    apply_payload(case_study, payload)
    await commit_or_conflict(session)
    await session.refresh(case_study)
    return case_study


@router.delete("/case-studies/{case_study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case_study(case_study_id: UUID, session: Session) -> Response:
    case_study = await session.get(CaseStudy, case_study_id)
    if case_study is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono case study.")
    await session.delete(case_study)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

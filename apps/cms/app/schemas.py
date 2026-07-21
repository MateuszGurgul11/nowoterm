from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ContentStatus

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class PagePayload(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN, max_length=120)
    title: str = Field(min_length=1, max_length=180)
    seo_title: str = Field(min_length=1, max_length=70)
    seo_description: str = Field(min_length=1, max_length=180)
    content: dict[str, Any] = Field(default_factory=dict)
    og_image_id: UUID | None = None
    status: ContentStatus = ContentStatus.DRAFT


class PageResponse(PagePayload):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ProjectPayload(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN, max_length=120)
    title: str = Field(min_length=1, max_length=180)
    excerpt: str = Field(default="", max_length=500)
    category: str = Field(min_length=1, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    area_m2: Decimal | None = Field(default=None, gt=0)
    duration: str | None = Field(default=None, max_length=80)
    completion_date: date | None = None
    featured: bool = False
    sort_order: int = 0
    cover_image_id: UUID | None = None
    gallery: list[dict[str, Any]] = Field(default_factory=list)
    content: dict[str, Any] = Field(default_factory=dict)
    seo_title: str = Field(min_length=1, max_length=70)
    seo_description: str = Field(min_length=1, max_length=180)
    status: ContentStatus = ContentStatus.DRAFT

    @field_validator("area_m2")
    @classmethod
    def normalize_area(cls, value: Decimal | None) -> Decimal | None:
        return value.quantize(Decimal("0.01")) if value is not None else None


class ProjectResponse(ProjectPayload):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CaseStudyPayload(BaseModel):
    project_id: UUID | None = None
    slug: str = Field(pattern=SLUG_PATTERN, max_length=120)
    title: str = Field(min_length=1, max_length=180)
    challenge: str = Field(default="", max_length=2000)
    solution: dict[str, Any] = Field(default_factory=dict)
    results: list[dict[str, Any]] = Field(default_factory=list)
    cover_image_id: UUID | None = None
    seo_title: str = Field(min_length=1, max_length=70)
    seo_description: str = Field(min_length=1, max_length=180)
    status: ContentStatus = ContentStatus.DRAFT


class CaseStudyResponse(CaseStudyPayload):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PublishResponse(BaseModel):
    accepted: bool
    message: str
    deployment_response_status: int | None = None

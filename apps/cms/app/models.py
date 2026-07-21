import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON

JSON_TYPE = JSON().with_variant(JSONB(), "postgresql")
TEXT_ARRAY = JSON().with_variant(ARRAY(Text()), "postgresql")


class Base(DeclarativeBase):
    pass


class ContentStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


CONTENT_STATUS = Enum(
    ContentStatus,
    name="content_status",
    schema="public",
    values_callable=lambda values: [value.value for value in values],
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class PublishableMixin(TimestampMixin):
    status: Mapped[ContentStatus] = mapped_column(
        CONTENT_STATUS, default=ContentStatus.DRAFT, server_default="draft"
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Media(TimestampMixin, Base):
    __tablename__ = "media"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storage_path: Mapped[str] = mapped_column(Text, unique=True)
    public_url: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(Text)
    mime_type: Mapped[str] = mapped_column(Text)
    alt_text: Mapped[str] = mapped_column(Text, default="")
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    size_bytes: Mapped[int | None] = mapped_column()


class SiteSettings(TimestampMixin, Base):
    __tablename__ = "site_settings"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(Text, primary_key=True, default="default")
    company_name: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    street: Mapped[str] = mapped_column(Text)
    postal_code: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(Text)
    region: Mapped[str] = mapped_column(Text)
    social_links: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    default_seo_title: Mapped[str] = mapped_column(Text)
    default_seo_description: Mapped[str] = mapped_column(Text)
    default_og_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.media.id", ondelete="SET NULL")
    )
    organization_schema: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)


class Page(PublishableMixin, Base):
    __tablename__ = "pages"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(Text)
    seo_title: Mapped[str] = mapped_column(String(70))
    seo_description: Mapped[str] = mapped_column(String(180))
    og_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.media.id", ondelete="SET NULL")
    )
    content: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)


class Project(PublishableMixin, Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(Text)
    excerpt: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    area_m2: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    duration: Mapped[str | None] = mapped_column(Text)
    completion_date: Mapped[date | None] = mapped_column(Date)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    cover_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.media.id", ondelete="SET NULL")
    )
    gallery: Mapped[list[dict[str, Any]]] = mapped_column(JSON_TYPE, default=list)
    content: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    seo_title: Mapped[str] = mapped_column(String(70))
    seo_description: Mapped[str] = mapped_column(String(180))


class Post(PublishableMixin, Base):
    __tablename__ = "posts"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(Text)
    excerpt: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    tags: Mapped[list[str]] = mapped_column(TEXT_ARRAY, default=list)
    author_name: Mapped[str] = mapped_column(Text, default="Novoterm Budownictwo")
    cover_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.media.id", ondelete="SET NULL")
    )
    seo_title: Mapped[str] = mapped_column(String(70))
    seo_description: Mapped[str] = mapped_column(String(180))


class CaseStudy(PublishableMixin, Base):
    __tablename__ = "case_studies"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.projects.id", ondelete="SET NULL")
    )
    slug: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(Text)
    challenge: Mapped[str] = mapped_column(Text, default="")
    solution: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    results: Mapped[list[dict[str, Any]]] = mapped_column(JSON_TYPE, default=list)
    cover_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("public.media.id", ondelete="SET NULL")
    )
    seo_title: Mapped[str] = mapped_column(String(70))
    seo_description: Mapped[str] = mapped_column(String(180))

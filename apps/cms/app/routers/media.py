import uuid
from pathlib import Path
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.models import Media
from app.security import require_admin

router = APIRouter(
    prefix="/api/admin/media",
    tags=["media"],
    dependencies=[Depends(require_admin)],
)
Session = Annotated[AsyncSession, Depends(get_session)]
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/avif",
    "image/svg+xml",
}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.get("")
async def list_media(session: Session) -> list[dict[str, object]]:
    media = list((await session.scalars(select(Media).order_by(Media.created_at.desc()))).all())
    return [
        {
            "id": item.id,
            "url": item.public_url,
            "file_name": item.file_name,
            "alt_text": item.alt_text,
            "mime_type": item.mime_type,
        }
        for item in media
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_media(
    session: Session,
    file: Annotated[UploadFile, File()],
    alt_text: Annotated[str, Form(min_length=1, max_length=240)],
) -> dict[str, object]:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(status_code=503, detail="Brak konfiguracji Supabase Storage.")
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Nieobsługiwany format obrazu.")

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Plik przekracza limit 10 MB.")

    suffix = Path(file.filename or "").suffix.lower()
    storage_path = f"uploads/{uuid.uuid4().hex}{suffix}"
    bucket = settings.supabase_media_bucket
    upload_url = f"{settings.supabase_url}/storage/v1/object/{bucket}/{storage_path}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
        "Content-Type": file.content_type,
        "x-upsert": "false",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(upload_url, headers=headers, content=content)
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Supabase odrzucił przesłanie pliku.")

    public_url = f"{settings.supabase_url}/storage/v1/object/public/{bucket}/{storage_path}"
    media = Media(
        storage_path=storage_path,
        public_url=public_url,
        file_name=file.filename or storage_path,
        mime_type=file.content_type,
        alt_text=alt_text,
        size_bytes=len(content),
    )
    session.add(media)
    await session.commit()
    await session.refresh(media)
    return {"id": media.id, "url": media.public_url, "alt_text": media.alt_text}


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(media_id: UUID, session: Session) -> Response:
    media = await session.get(Media, media_id)
    if media is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono pliku.")

    settings = get_settings()
    if settings.supabase_url and settings.supabase_service_role_key:
        bucket = settings.supabase_media_bucket
        delete_url = f"{settings.supabase_url}/storage/v1/object/{bucket}/{media.storage_path}"
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "apikey": settings.supabase_service_role_key,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(delete_url, headers=headers)
        if response.status_code >= 400 and response.status_code != 404:
            raise HTTPException(status_code=502, detail="Nie udało się usunąć pliku z Supabase Storage.")

    await session.delete(media)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

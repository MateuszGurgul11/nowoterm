from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

router = APIRouter(prefix="/health", tags=["health"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(session: Session) -> dict[str, str]:
    try:
        await session.execute(text("select 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Baza danych jest niedostępna.") from exc
    return {"status": "ready"}

from fastapi import APIRouter

from app.config import settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.app_version,
    }

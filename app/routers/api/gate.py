from fastapi import APIRouter, Depends

from app.auth import verify_api_key

router = APIRouter(
    prefix="/gate",
    tags=["Gate"])


@router.get("/gate")
async def gate(
    _: None = Depends(verify_api_key),
):
    return {
        "gate": "closed",
    }

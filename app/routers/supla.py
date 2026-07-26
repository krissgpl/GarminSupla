from fastapi import APIRouter

from app.services.supla_service import SuplaService

router = APIRouter(
    prefix="/api",
    tags=["SUPLA"],
)

supla_service = SuplaService()


@router.get("/test/iodevices")
def test_iodevices():
    return supla_service.get_iodevices()


@router.get("/test/channels")
def test_channels():
    return supla_service.get_channels()

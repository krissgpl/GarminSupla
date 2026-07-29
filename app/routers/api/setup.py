from fastapi import APIRouter

from app.models.api import SetupStatus, GateSummary, SelectGateRequest
from app.models.settings import SelectedGate
from app.services.setup_service import SetupService

router = APIRouter(
    prefix="/setup",
    tags=["Setup"],
)

setup_service = SetupService()

@router.get(
    "",
    response_model=SetupStatus,
)

def get_status() -> SetupStatus:
    """Return the current setup status."""

    return setup_service.get_status()

@router.get(
    "/gates",
    response_model=list[GateSummary],
)

def get_available_gates() -> list[GateSummary]:
    """Return available gate channels."""

    return setup_service.get_available_gates()

@router.get(
    "/gates",
    response_model=list[GateSummary],
    responses={
        401: {
            "description": "OAuth authorization expired",
            "content": {
                "application/json": {
                    "example": {
                        "error": "oauth_expired",
                        "message": "Authorization has expired. Please authorize GarminSupla again.",
                    }
                }
            },
        },
        502: {
            "description": "SUPLA API error",
        },
    },
)

def get_available_gates() -> list[GateSummary]:
    """Return available gate channels."""

    return setup_service.get_available_gates()

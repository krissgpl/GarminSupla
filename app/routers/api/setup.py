from fastapi import APIRouter

from app.models.api import SetupStatus, GateSummary, SelectGateRequest, WatchStatus
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

@router.post(
    "/gate",
    response_model=SelectedGate,
)

def select_gate(
    request: SelectGateRequest,
) -> SelectedGate:
    """Save the selected gate."""

    return setup_service.save_selected_gate(
        request.channel_id,
    )

@router.get(
    "/watch",
    response_model=WatchStatus,
)
def get_watch_status() -> WatchStatus:
    """Return Garmin watch setup status."""

    return setup_service.get_watch_status()

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.api import SetupStatus, GateSummary, SelectGateRequest, WatchStatus
from app.models.settings import SelectedGate
from app.services.setup_service import SetupService

from app.api.admin_auth import require_admin_csrf
from app.models.admin import AdminAccount

from app.models.api.pairing import PairingApproveRequest
from app.services.pairing_service import PairingService

router = APIRouter(
    prefix="/setup",
    tags=["Setup"],
)

setup_service = SetupService()
pairing_service = PairingService()

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
    admin: AdminAccount = Depends(require_admin_csrf),
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

@router.post(
    "/watch/pair",
    status_code=status.HTTP_204_NO_CONTENT,
)
def approve_watch_pairing(
    request: PairingApproveRequest,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> None:
    """Approve Garmin watch pairing using its six-digit code."""

    session = pairing_service.approve_pairing(
        request.code
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pairing code not found or expired.",
        )

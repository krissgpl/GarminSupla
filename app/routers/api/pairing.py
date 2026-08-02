from fastapi import APIRouter, HTTPException, status

from app.models.api.pairing import (
    PairingConsumeResponse,
    PairingStartResponse,
    PairingStatusResponse,
)
from app.services.pairing_service import (
    PAIRING_TTL_SECONDS,
    PairingService,
)


router = APIRouter(
    prefix="/watch/pair",
    tags=["Watch Pairing"],
)

pairing_service = PairingService()


@router.post(
    "",
    response_model=PairingStartResponse,
)
def start_pairing() -> PairingStartResponse:
    """Start Garmin watch pairing."""

    session = pairing_service.create_pairing()

    return PairingStartResponse(
        pairing_id=session.pairing_id,
        code=session.code,
        expires_in=PAIRING_TTL_SECONDS,
    )


@router.get(
    "/{pairing_id}",
    response_model=PairingStatusResponse,
)
def get_pairing_status(
    pairing_id: str,
) -> PairingStatusResponse:
    """Return the current pairing status."""

    session = pairing_service.get_pairing(
        pairing_id
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pairing session not found.",
        )

    return PairingStatusResponse(
        status=(
            "approved"
            if session.approved
            else "pending"
        ),
    )


@router.post(
    "/{pairing_id}/consume",
    response_model=PairingConsumeResponse,
)
def consume_pairing(
    pairing_id: str,
) -> PairingConsumeResponse:
    """Consume an approved pairing session."""

    result = pairing_service.consume_pairing(
        pairing_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved pairing session not found.",
        )

    return PairingConsumeResponse(
        watch_id=result.watch_id,
        token=result.watch_token,
    )

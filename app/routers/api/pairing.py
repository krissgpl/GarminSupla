from collections import deque
from math import ceil
from threading import Lock
from time import monotonic

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
from app.stores.pairing_store import PairingCapacityExceeded


router = APIRouter(
    prefix="/watch/pair",
    tags=["Watch Pairing"],
)

pairing_service = PairingService()

PAIRING_CREATE_LIMIT = 12
PAIRING_CREATE_WINDOW_SECONDS = 60

PAIRING_STATUS_LIMIT = 1500
PAIRING_CONSUME_LIMIT = 120
PAIRING_REQUEST_WINDOW_SECONDS = 60

_pairing_create_times = deque()
_pairing_create_lock = Lock()

_pairing_status_times = deque()
_pairing_status_lock = Lock()

_pairing_consume_times = deque()
_pairing_consume_lock = Lock()


def _check_pairing_create_limit() -> None:
    """Limit new pairing sessions per process."""

    now = monotonic()

    with _pairing_create_lock:
        cutoff = now - PAIRING_CREATE_WINDOW_SECONDS

        while (
            _pairing_create_times
            and _pairing_create_times[0] <= cutoff
        ):
            _pairing_create_times.popleft()

        if len(_pairing_create_times) >= PAIRING_CREATE_LIMIT:
            retry_after = max(
                1,
                ceil(
                    PAIRING_CREATE_WINDOW_SECONDS
                    - (now - _pairing_create_times[0])
                ),
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many pairing requests.",
                headers={
                    "Retry-After": str(retry_after),
                },
            )

        _pairing_create_times.append(now)


def _check_pairing_request_limit(
    times,
    lock,
    limit: int,
) -> None:
    """Bound pairing endpoint traffic per process."""

    now = monotonic()

    with lock:
        cutoff = now - PAIRING_REQUEST_WINDOW_SECONDS

        while times and times[0] <= cutoff:
            times.popleft()

        if len(times) >= limit:
            retry_after = max(
                1,
                ceil(
                    PAIRING_REQUEST_WINDOW_SECONDS
                    - (now - times[0])
                ),
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many pairing requests.",
                headers={
                    "Retry-After": str(retry_after),
                },
            )

        times.append(now)


@router.post(
    "",
    response_model=PairingStartResponse,
)
def start_pairing() -> PairingStartResponse:
    """Start Garmin watch pairing."""

    _check_pairing_create_limit()

    try:
        session = pairing_service.create_pairing()

    except PairingCapacityExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many active pairing sessions.",
            headers={"Retry-After": "60"},
        ) from None

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
    """Return Garmin watch pairing status."""

    _check_pairing_request_limit(
        times=_pairing_status_times,
        lock=_pairing_status_lock,
        limit=PAIRING_STATUS_LIMIT,
    )

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

    _check_pairing_request_limit(
        times=_pairing_consume_times,
        lock=_pairing_consume_lock,
        limit=PAIRING_CONSUME_LIMIT,
    )

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

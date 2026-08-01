from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.settings import WatchDevice
from app.services.watch_service import WatchService


bearer_scheme = HTTPBearer(
    auto_error=False,
)

watch_service = WatchService()


def authenticate_watch(
    credentials: HTTPAuthorizationCredentials | None = Security(
        bearer_scheme
    ),
) -> WatchDevice:
    """Authenticate a Garmin watch using a Bearer token."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing watch token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    watch = watch_service.authenticate(
        credentials.credentials
    )

    if watch is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid watch token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return watch

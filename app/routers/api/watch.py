from fastapi import APIRouter, Depends

from app.api.watch_auth import authenticate_watch
from app.models.settings import WatchDevice

from app.models.api.watch import (
    WatchActionRequest,
    WatchActionResponse,
    WatchConfig,
    WatchItemConfig,
)

from app.services.watch_config_service import (
    WatchConfigService,
)

from app.services.watch_action_service import (
    WatchActionService,
)

router = APIRouter(
    prefix="/watch",
    tags=["Watch"],
)

watch_config_service = WatchConfigService()
watch_action_service = WatchActionService()

@router.get("/me")
def get_watch(
    watch: WatchDevice = Depends(
        authenticate_watch
    ),
):
    """Return authenticated watch information."""

    return {
        "id": watch.id,
        "name": watch.name,
        "enabled": watch.enabled,
    }


@router.get(
    "/config",
    response_model=WatchConfig,
)
def get_watch_config(
    watch: WatchDevice = Depends(
        authenticate_watch
    ),
) -> WatchConfig:
    """Return configuration for the authenticated Garmin watch."""

    settings = watch_config_service.get_settings()

    items = [
        WatchItemConfig(
            id=item.id,
            type=item.type,
            name=item.name,
            status_enabled=item.status_enabled,
            confirmation_required=(
                item.confirmation_required
            ),
        )
        for item in sorted(
            settings.watch_settings.items,
            key=lambda item: item.order,
        )
        if item.enabled
    ]

    return WatchConfig(
        configured=bool(items),
        items=items,
    )


@router.post(
    "/action",
    response_model=WatchActionResponse,
)
def execute_watch_action(
    request: WatchActionRequest,
    watch: WatchDevice = Depends(
        authenticate_watch
    ),
) -> WatchActionResponse:
    """Execute an action requested by the authenticated Garmin watch."""

    return watch_action_service.execute(
        item_id=request.item_id,
        action=request.action,
    )

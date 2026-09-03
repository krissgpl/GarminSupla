from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.api.watch_auth import authenticate_watch
from app.models.settings import WatchDevice

from app.models.api.watch import (
    WatchActionRequest,
    WatchActionResponse,
    WatchConfig,
    WatchItemConfig,
    WatchMetadataUpdate,
)

from app.services.watch_config_service import (
    WatchConfigService,
)

from app.services.watch_action_service import (
    WatchActionService,
)

from app.services.watch_service import (
    WatchService,
)

router = APIRouter(
    prefix="/watch",
    tags=["Watch"],
)

watch_config_service = WatchConfigService()
watch_action_service = WatchActionService()
watch_service = WatchService()


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


@router.put(
    "/metadata",
    response_model=WatchMetadataUpdate,
)
def update_watch_metadata(
    request: WatchMetadataUpdate,
    watch: WatchDevice = Depends(
        authenticate_watch
    ),
) -> WatchMetadataUpdate:
    """Update metadata for the authenticated Garmin watch."""

    updated = watch_service.update_metadata(
        watch_id=watch.id,
        metadata=request.model_dump(
            exclude_unset=True
        ),
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watch no longer registered.",
        )

    return WatchMetadataUpdate(
        device_model=updated.device_model,
        device_id=updated.device_id,
        part_number=updated.part_number,
        firmware_version=updated.firmware_version,
        connect_iq_version=updated.connect_iq_version,
        system_language=updated.system_language,
        app_version=updated.app_version,
    )


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

    enabled_items = [
        item
        for item in sorted(
            settings.watch_settings.items,
            key=lambda item: item.order,
        )
        if item.enabled
    ]

    statuses = watch_config_service.get_item_statuses(
        enabled_items
    )

    items = []

    for item in enabled_items:
        connected, state = statuses.get(
            item.id,
            (False, "unknown"),
        )

        items.append(
            WatchItemConfig(
                id=item.id,
                type=item.type,
                name=item.name,
                icon=item.icon,
                status_enabled=item.status_enabled,
                confirmation_required=(
                    item.confirmation_required
                ),
                connected=connected,
                state=state,
            )
        )

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

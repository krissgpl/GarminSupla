from fastapi import APIRouter, Depends

from app.api.watch_auth import authenticate_watch
from app.models.settings import WatchDevice

from app.models.api.watch import (
    WatchConfig,
    WatchGateConfig,
)
from app.stores.settings_store import SettingsStore

router = APIRouter(
    prefix="/watch",
    tags=["Watch"],
)

settings_store = SettingsStore()

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

    settings = settings_store.load()

    gate = settings.supla.selected_gate

    if gate is None:
        return WatchConfig(
            configured=False,
            gate=None,
            confirmation_required=True,
        )

    return WatchConfig(
        configured=True,
        gate=WatchGateConfig(
            name=gate.caption,
            status_enabled=gate.sensor_channel_id is not None,
        ),
        confirmation_required=True,
    )

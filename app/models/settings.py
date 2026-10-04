from pydantic import (
    BaseModel,
    Field,
)
from typing import Literal


class UISettings(BaseModel):
    theme: Literal[
        "auto",
        "light",
        "dark",
    ] = "auto"

    language: Literal[
        "auto",
        "pl",
        "en",
    ] = "auto"


class WatchItem(BaseModel):
    id: str
    type: Literal[
        "gate",
        "scene",
        "light",
        "switch",
        "roller_shutter",
        "awning",
    ]
    name: str
    icon: str = "default"
    supla_id: int
    order: int = 0
    confirmation_required: bool = True
    status_enabled: bool = False
    sensor_channel_id: int | None = None
    enabled: bool = True


class SuplaSettings(BaseModel):
    server: str = "https://supla.krissg.ovh"
    access_token: str | None = None
    refresh_token: str | None = None


class WatchDevice(BaseModel):
    id: str
    name: str = "Garmin Watch"

    device_model: str | None = None
    device_id: str | None = None
    part_number: str | None = None
    firmware_version: str | None = None
    connect_iq_version: str | None = None
    system_language: str | None = None

    application_language: Literal[
        "auto",
        "pl",
        "en",
    ] = "auto"

    app_version: str | None = None

    token_hash: str
    credential_revision: int = 1
    created_at: str
    last_seen_at: str | None = None
    enabled: bool = True

    items: list[WatchItem] = Field(
        default_factory=list
    )


class Settings(BaseModel):
    ui: UISettings = Field(
        default_factory=UISettings
    )

    supla: SuplaSettings = Field(
        default_factory=SuplaSettings
    )

    watches: list[WatchDevice] = Field(
        default_factory=list
    )

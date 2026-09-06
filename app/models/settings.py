from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
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

    @field_validator(
        "theme",
        mode="before",
    )
    @classmethod
    def migrate_legacy_theme(
        cls,
        value: object,
    ) -> object:
        if value == "system":
            return "auto"

        return value


class SelectedGate(BaseModel):
    id: int
    caption: str
    sensor_channel_id: int | None = None


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


class WatchSettings(BaseModel):
    items: list[WatchItem] = Field(default_factory=list)


class SuplaSettings(BaseModel):
    server: str = "https://supla.krissg.ovh"
    access_token: str | None = None
    refresh_token: str | None = None
    selected_gate: SelectedGate | None = None


class WatchDevice(BaseModel):
    id: str
    name: str = "Garmin Watch"

    device_model: str | None = None
    device_id: str | None = None
    part_number: str | None = None
    firmware_version: str | None = None
    connect_iq_version: str | None = None
    system_language: str | None = None
    app_version: str | None = None

    token_hash: str
    created_at: str
    last_seen_at: str | None = None
    enabled: bool = True


class Settings(BaseModel):
    version: int = 1
    configured: bool = False

    ui: UISettings = Field(
        default_factory=UISettings
    )

    supla: SuplaSettings = Field(
        default_factory=SuplaSettings
    )

    # Legacy single-watch field.
    # Kept temporarily during the multi-watch migration.
    watch: WatchDevice | None = None

    # New multi-watch collection.
    watches: list[WatchDevice] = Field(
        default_factory=list
    )

    watch_settings: WatchSettings = Field(
        default_factory=WatchSettings
    )

    @model_validator(mode="after")
    def migrate_watch_collection(
        self,
    ) -> "Settings":
        """Populate the compatibility watch representation."""

        if (
            self.watch is not None
            and not self.watches
        ):
            self.watches = [
                self.watch
            ]

        elif (
            self.watch is None
            and len(self.watches) == 1
        ):
            self.watch = self.watches[0]

        return self

    def sync_single_watch_compatibility(
        self,
    ) -> None:
        """Keep legacy and collection fields synchronized."""

        if self.watch is None:
            self.watches = []
            return

        self.watches = [
            self.watch
        ]

from typing import Literal

from pydantic import BaseModel, model_validator

from app.models.settings import SelectedGate


class GateSummary(BaseModel):
    id: int
    caption: str
    sensor_channel_id: int | None


class SelectGateRequest(BaseModel):
    channel_id: int


class UILanguageSettings(BaseModel):
    language: Literal[
        "auto",
        "pl",
        "en",
    ]


class UIThemeSettings(BaseModel):
    theme: Literal[
        "auto",
        "light",
        "dark",
    ]


class SetupStatus(BaseModel):
    server: str
    authorized: bool
    selected_gate: SelectedGate | None
    setup_completed: bool


class WatchStatus(BaseModel):
    configured: bool
    id: str | None = None
    name: str | None = None
    enabled: bool = False

    device_model: str | None = None
    device_id: str | None = None
    part_number: str | None = None
    firmware_version: str | None = None
    connect_iq_version: str | None = None
    system_language: str | None = None
    app_version: str | None = None

    created_at: str | None = None
    last_seen_at: str | None = None


class WatchItemUpdate(BaseModel):
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
    icon: Literal[
        "garage_gate",
        "sliding_gate",
        "double_swing_gate",
        "light",
        "switch",
        "roller_shutter",
        "awning",
        "scene",
    ]
    supla_id: int
    order: int = 0
    confirmation_required: bool = True
    status_enabled: bool = False
    sensor_channel_id: int | None = None
    enabled: bool = True

    @model_validator(mode="after")
    def validate_icon_for_type(self):
        allowed_icons = {
            "gate": {
                "garage_gate",
                "sliding_gate",
                "double_swing_gate",
            },
            "light": {
                "light",
            },
            "switch": {
                "switch",
            },
            "scene": {
                "scene",
            },
            "roller_shutter": {
                "roller_shutter",
            },
            "awning": {
                "awning",
            },
        }

        if self.icon not in allowed_icons[self.type]:
            raise ValueError(
                f'Icon "{self.icon}" is not allowed '
                f'for item type "{self.type}".'
            )

        return self

class WatchItemsUpdateRequest(BaseModel):
    items: list[WatchItemUpdate]

    @model_validator(mode="after")
    def validate_items(self):
        ids = [
            item.id
            for item in self.items
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "Watch item IDs must be unique."
            )

        return self

class SuplaAvailableItem(BaseModel):
    supla_id: int
    type: Literal[
        "gate",
        "scene",
        "light",
        "switch",
        "roller_shutter",
        "awning",
    ]
    name: str
    function: str
    sensor_channel_id: int | None = None

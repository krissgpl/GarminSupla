from typing import Literal

from pydantic import BaseModel, model_validator

from app.models.settings import SelectedGate


class GateSummary(BaseModel):
    id: int
    caption: str
    sensor_channel_id: int | None


class SelectGateRequest(BaseModel):
    channel_id: int


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
        "default",
        "garage_gate",
        "sliding_gate",
        "double_swing_gate",
    ] = "default"
    supla_id: int
    order: int = 0
    confirmation_required: bool = True
    status_enabled: bool = False
    sensor_channel_id: int | None = None
    enabled: bool = True


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
        "light",
        "switch",
        "roller_shutter",
        "awning",
    ]
    name: str
    function: str
    sensor_channel_id: int | None = None

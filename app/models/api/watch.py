from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class WatchItemType(str, Enum):
    GATE = "gate"
    SCENE = "scene"
    LIGHT = "light"
    SWITCH = "switch"
    ROLLER_SHUTTER = "roller_shutter"
    AWNING = "awning"

class WatchItemConfig(BaseModel):
    id: str
    type: WatchItemType
    name: str
    icon: str = "default"
    status_enabled: bool = False
    confirmation_required: bool = True
    connected: bool = False
    state: str = "unknown"


class WatchConfig(BaseModel):
    configured: bool
    items: list[WatchItemConfig] = Field(
        default_factory=list
    )


class WatchMetadataUpdate(BaseModel):
    device_model: str | None = None
    device_id: str | None = None
    part_number: str | None = None
    firmware_version: str | None = None
    connect_iq_version: str | None = None
    system_language: str | None = None
    app_version: str | None = None


class WatchAction(str, Enum):
    TOGGLE = "toggle"
    OPEN = "open"
    CLOSE = "close"
    STOP = "stop"
    COLLAPSE = "collapse"
    EXPAND = "expand"


class WatchActionRequest(BaseModel):
    item_id: str
    action: WatchAction


class WatchActionResponse(BaseModel):
    success: bool
    message: str
    refresh_required: bool = False

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class WatchItemType(str, Enum):
    GATE = "gate"
    SCENE = "scene"


class WatchItemConfig(BaseModel):
    id: str
    type: WatchItemType
    name: str
    icon: str = "default"
    status_enabled: bool = False
    confirmation_required: bool = True
    connected: bool = False
    state: Literal["opened", "closed", "unknown"] = "unknown"


class WatchConfig(BaseModel):
    configured: bool
    items: list[WatchItemConfig] = Field(
        default_factory=list
    )


class WatchAction(str, Enum):
    TOGGLE = "toggle"


class WatchActionRequest(BaseModel):
    item_id: str
    action: WatchAction


class WatchActionResponse(BaseModel):
    success: bool
    message: str
    refresh_required: bool = False

from enum import Enum

from pydantic import BaseModel, Field


class WatchItemType(str, Enum):
    GATE = "gate"
    SCENE = "scene"


class WatchItemConfig(BaseModel):
    id: str
    type: WatchItemType
    name: str
    status_enabled: bool = False
    confirmation_required: bool = True


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

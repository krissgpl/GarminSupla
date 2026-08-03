from typing import Literal

from pydantic import BaseModel, Field


class WatchItemConfig(BaseModel):
    id: str
    type: Literal["gate", "scene"]
    name: str
    status_enabled: bool = False
    confirmation_required: bool = True


class WatchConfig(BaseModel):
    configured: bool
    items: list[WatchItemConfig] = Field(
        default_factory=list
    )

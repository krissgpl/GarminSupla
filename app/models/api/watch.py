from pydantic import BaseModel


class WatchGateConfig(BaseModel):
    name: str
    status_enabled: bool = True


class WatchConfig(BaseModel):
    configured: bool
    gate: WatchGateConfig | None = None
    confirmation_required: bool = True

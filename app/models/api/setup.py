from pydantic import BaseModel

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

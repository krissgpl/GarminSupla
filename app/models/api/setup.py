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

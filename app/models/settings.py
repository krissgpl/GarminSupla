from pydantic import BaseModel, Field


class UISettings(BaseModel):
    theme: str = "system"


class SelectedGate(BaseModel):
    id: int
    caption: str
    sensor_channel_id: int | None = None


class SuplaSettings(BaseModel):
    server: str = "https://supla.krissg.ovh"
    access_token: str | None = None
    refresh_token: str | None = None
    selected_gate: SelectedGate | None = None

class WatchDevice(BaseModel):
    id: str
    name: str = "Garmin Watch"
    token_hash: str
    created_at: str
    last_seen_at: str | None = None
    enabled: bool = True

class Settings(BaseModel):
    version: int = 1
    configured: bool = False
    ui: UISettings = Field(default_factory=UISettings)
    supla: SuplaSettings = Field(default_factory=SuplaSettings)
    watch: WatchDevice | None = None


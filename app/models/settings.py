from pydantic import BaseModel, Field


class UISettings(BaseModel):
    theme: str = "system"


class SuplaSettings(BaseModel):
    server: str = "https://supla.krissg.ovh"
    access_token: str | None = None
    refresh_token: str | None = None
    selected_gate: int | None = None


class Settings(BaseModel):
    version: int = 1
    configured: bool = False
    ui: UISettings = Field(default_factory=UISettings)
    supla: SuplaSettings = Field(default_factory=SuplaSettings)

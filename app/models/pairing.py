from datetime import datetime

from pydantic import BaseModel


class PairingSession(BaseModel):
    """Temporary Garmin watch pairing session."""

    pairing_id: str
    code: str
    created_at: datetime
    expires_at: datetime
    approved: bool = False

class PairingResult(BaseModel):
    """Credentials issued after successful pairing."""

    watch_id: str
    watch_token: str

from typing import Literal

from pydantic import BaseModel, Field


class PairingStartResponse(BaseModel):
    pairing_id: str
    code: str
    expires_in: int


class PairingStatusResponse(BaseModel):
    status: Literal[
        "pending",
        "approved",
    ]


class PairingConsumeResponse(BaseModel):
    watch_id: str
    token: str


class PairingApproveRequest(BaseModel):
    code: str = Field(
        pattern=r"^\d{6}$",
    )

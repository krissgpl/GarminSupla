from pydantic import BaseModel, Field


class AdminAccount(BaseModel):
    username: str
    password_hash: str
    created_at: str
    enabled: bool = True

    # Two-factor authentication
    totp_enabled: bool = False
    totp_secret_encrypted: str | None = None

    recovery_code_hashes: list[str] = Field(
        default_factory=list
    )

    # Last successfully used TOTP time counter.
    totp_last_used_counter: int | None = Field(
        default=None,
        ge=0,
    )

    # Used to invalidate administrator sessions
    # after security-sensitive account changes.
    session_version: int = Field(
        default=0,
        ge=0,
    )

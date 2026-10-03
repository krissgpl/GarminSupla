from cryptography.fernet import Fernet
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_name: str = "GarminSupla"
    app_version: str = "0.5.1"

    api_key: str
    api_port: int = 8008

    admin_session_secret: str

    # Optional until administrator 2FA is configured.
    totp_encryption_key: str | None = None

    supla_client_id: str
    supla_client_secret: str
    supla_redirect_uri: str
    supla_scope: str

    @field_validator("totp_encryption_key")
    @classmethod
    def validate_totp_encryption_key(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        try:
            Fernet(value.encode("ascii"))
        except (ValueError, UnicodeError):
            raise ValueError(
                "Invalid TOTP encryption key."
            ) from None

        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )


settings = AppSettings()

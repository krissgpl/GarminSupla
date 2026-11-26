from ipaddress import ip_address

from cryptography.fernet import Fernet
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_name: str = "GarminSupla"
    app_version: str = "0.6.0-beta.1"

    admin_session_secret: str

    # Enabled only after trusted proxy validation.
    admin_login_rate_limit_enabled: bool = False
    admin_login_trusted_proxy_ips: str = ""

    # Optional until administrator 2FA is configured.
    totp_encryption_key: str | None = None

    # Optional: configured through the setup wizard.
    # Existing installations can still use .env.
    supla_client_id: str | None = None
    supla_client_secret: str | None = None
    # Optional: configured through the setup wizard.
    # Legacy installations can still use .env.
    supla_redirect_uri: str | None = None
    # Minimum permissions required by GarminSupla.
    # Can be overridden by SUPLA_SCOPE in .env.
    supla_scope: str = (
        "iodevices_r channels_r channels_ea "
        "scenes_r scenes_ea offline_access"
    )

    @model_validator(mode="after")
    def validate_admin_login_proxy_ips(self) -> "AppSettings":
        """Validate proxy IPs before enabling login rate limiting."""

        raw = self.admin_login_trusted_proxy_ips

        if not raw.strip():
            if self.admin_login_rate_limit_enabled:
                raise ValueError(
                    "Login rate limiting requires trusted proxy IPs."
                )

            self.admin_login_trusted_proxy_ips = ""
            return self

        entries = raw.split(",")

        if len(entries) > 16:
            raise ValueError(
                "Too many trusted proxy IPs."
            )

        normalized = []
        seen = set()

        for entry in entries:
            value = entry.strip()

            if not value:
                raise ValueError(
                    "Trusted proxy IP list contains an empty entry."
                )

            try:
                address = ip_address(value)
            except ValueError:
                raise ValueError(
                    "Trusted proxy entries must be IP addresses."
                ) from None

            if address.is_unspecified or address.is_multicast:
                raise ValueError(
                    "Unspecified and multicast proxy IPs "
                    "are not allowed."
                )

            canonical = str(address)

            if canonical in seen:
                raise ValueError(
                    "Duplicate trusted proxy IP."
                )

            seen.add(canonical)
            normalized.append(canonical)

        self.admin_login_trusted_proxy_ips = ",".join(
            normalized
        )

        return self

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

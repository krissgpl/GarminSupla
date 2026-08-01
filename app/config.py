from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_name: str = "GarminSupla"
    app_version: str = "0.1.0"

    api_key: str
    api_port: int = 8008

    admin_session_secret: str

    supla_client_id: str
    supla_client_secret: str
    supla_redirect_uri: str
    supla_scope: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = AppSettings()

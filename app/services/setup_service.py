from app.models.setup import SetupForm
from app.models.settings import Settings
from app.stores.settings_store import SettingsStore


class SetupService:
    """Business logic for the setup wizard."""

    def __init__(self, store: SettingsStore | None = None):
        self._store = store if store is not None else SettingsStore()

    def save_server(self, form: SetupForm) -> Settings:
        """Save the SUPLA server address."""

        settings = self._store.load()

        settings.supla.server = str(form.server).rstrip("/")

        self._store.save(settings)

        return settings

    def load_settings(self) -> Settings:
        """Load current application settings."""

        return self._store.load()

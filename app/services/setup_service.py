from app.services.supla_service import SuplaService
from app.models.api import SetupStatus, GateSummary
from app.models.setup import SetupForm
from app.models.settings import Settings, SelectedGate
from app.stores.settings_store import SettingsStore


class SetupService:
    """Business logic for the setup wizard."""

    def __init__(
        self,
        store: SettingsStore | None = None,
        supla_service: SuplaService | None = None,
    ) -> None:
        self._store = (
            store if store is not None else SettingsStore()
        )

        self._supla_service = (
            supla_service
            if supla_service is not None
            else SuplaService()
        )

    def save_server(self, form: SetupForm) -> Settings:
        """Save the SUPLA server address."""

        settings = self._store.load()

        settings.supla.server = str(form.server).rstrip("/")

        self._store.save(settings)

        return settings

    def load_settings(self) -> Settings:
        """Load current application settings."""

        return self._store.load()

    def get_status(self) -> SetupStatus:
        """Return the current setup status."""

        settings = self._store.load()

        authorized = bool(
            settings.supla.access_token
        )

        setup_completed = bool(
            settings.supla.server
            and authorized
            and settings.supla.selected_gate
        )

        return SetupStatus(
            server=settings.supla.server,
            authorized=authorized,
        selected_gate=settings.supla.selected_gate,
        setup_completed=setup_completed,
        )

    def save_selected_gate(
        self,
        channel_id: int,
    ) -> SelectedGate:
        """Save the selected gate."""

        return self._supla_service.select_gate(
            channel_id,
        )

    def get_available_gates(self) -> list[GateSummary]:
        """Return available gate channels."""

        return self._supla_service.get_available_gates()

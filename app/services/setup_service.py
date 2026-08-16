from app.services.supla_service import SuplaService
from app.models.api import SetupStatus, GateSummary, WatchStatus
from app.models.setup import SetupForm
from app.models.api.setup import SuplaAvailableItem

from app.models.settings import (
    Settings,
    SelectedGate,
    WatchItem,
)

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

        new_server = str(form.server).rstrip("/")

        if settings.supla.server != new_server:
            settings.supla.server = new_server
            settings.supla.access_token = None
            settings.supla.refresh_token = None
            settings.supla.selected_gate = None
        else:
            settings.supla.server = new_server

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
        )

        return SetupStatus(
            server=settings.supla.server,
            authorized=authorized,
        selected_gate=settings.supla.selected_gate,
        setup_completed=setup_completed,
        )

    def get_watch_status(self) -> WatchStatus:
        """Return safe Garmin watch status information."""

        settings = self._store.load()

        watch = settings.watch

        if watch is None:
            return WatchStatus(
               configured=False,
           )

        return WatchStatus(
            configured=True,
            id=watch.id,
            name=watch.name,
            enabled=watch.enabled,
            created_at=watch.created_at,
            last_seen_at=watch.last_seen_at,
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

    def get_watch_items(self) -> list[WatchItem]:
        """Return configured Garmin watch items."""

        settings = self._store.load()

        return sorted(
            settings.watch_settings.items,
            key=lambda item: item.order,
        )

    def save_watch_items(
        self,
        items: list[WatchItem],
    ) -> list[WatchItem]:
        """Replace Garmin watch item configuration."""

        settings = self._store.load()

        sorted_items = sorted(
            items,
            key=lambda item: item.order,
        )

        settings.watch_settings.items = sorted_items

        self._store.save(settings)

        return sorted_items

    def get_available_supla_items(
        self,
    ) -> list[SuplaAvailableItem]:
        """Return currently available SUPLA watch items."""

        return self._supla_service.get_available_watch_items()

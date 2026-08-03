from uuid import uuid4

from app.models.settings import (
    Settings,
    WatchItem,
)
from app.stores.settings_store import SettingsStore


class WatchConfigService:
    def __init__(self) -> None:
        self._settings_store = SettingsStore()

    def get_settings(self) -> Settings:
        settings = self._settings_store.load()

        if self._migrate_selected_gate(settings):
            self._settings_store.save(settings)

        return settings

    def _migrate_selected_gate(
        self,
        settings: Settings,
    ) -> bool:
        """
        Migrate the legacy selected_gate configuration
        to the generic watch item model.
        """

        if settings.watch_settings.items:
            return False

        gate = settings.supla.selected_gate

        if gate is None:
            return False

        item = WatchItem(
            id=str(uuid4()),
            type="gate",
            name=gate.caption,
            supla_id=gate.id,
            order=0,
            confirmation_required=True,
            status_enabled=gate.sensor_channel_id is not None,
            sensor_channel_id=gate.sensor_channel_id,
            enabled=True,
        )

        settings.watch_settings.items.append(item)

        return True

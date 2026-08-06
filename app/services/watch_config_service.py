from uuid import uuid4

from app.models.settings import (
    Settings,
    WatchItem,
)
from app.stores.settings_store import SettingsStore
from app.services.supla_service import SuplaService


class WatchConfigService:
    def __init__(self) -> None:
        self._settings_store = SettingsStore()
        self._supla_service = SuplaService()

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

    def get_item_statuses(
        self,
        items: list[WatchItem],
    ) -> dict[str, tuple[bool, str]]:
        channels = self._supla_service.get_channels_with_state()

        channels_by_id = {
            channel.get("id"): channel
            for channel in channels
        }

        statuses: dict[str, tuple[bool, str]] = {}

        for item in items:
            statuses[item.id] = self._get_item_status(
                item,
                channels_by_id,
            )

        return statuses

    def _get_item_status(
        self,
        item: WatchItem,
        channels_by_id: dict,
    ) -> tuple[bool, str]:
        if (
            item.type != "gate"
            or not item.status_enabled
            or item.sensor_channel_id is None
        ):
            return False, "unknown"

        sensor = channels_by_id.get(
            item.sensor_channel_id
        )

        if sensor is None:
            return False, "unknown"

        connected = sensor.get("connected") is True

        if not connected:
            return False, "unknown"

        state = sensor.get("state")

        if not isinstance(state, dict):
            return True, "unknown"

        hi = state.get("hi")

        if hi is True:
            return True, "closed"

        if hi is False:
            return True, "opened"

        return True, "unknown"

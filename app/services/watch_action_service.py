from app.models.api.watch import (
    WatchAction,
    WatchActionResponse,
)
from app.models.settings import WatchItem
from app.services.supla_service import SuplaService
from app.stores.settings_store import SettingsStore


class WatchActionService:

    def __init__(self) -> None:
        self._settings_store = SettingsStore()
        self._supla_service = SuplaService()

    def execute(
        self,
        item_id: str,
        action: WatchAction,
    ) -> WatchActionResponse:

        settings = self._settings_store.load()

        item = next(
            (
                item
                for item in settings.watch_settings.items
                if item.id == item_id
            ),
            None,
        )

        if item is None:
            return WatchActionResponse(
                success=False,
                message="Item not found.",
            )

        if not item.enabled:
            return WatchActionResponse(
                success=False,
                message="Item disabled.",
            )

        if item.type == "gate":
            return self._execute_gate(
                item,
                action,
            )

        return WatchActionResponse(
            success=False,
            message="Unsupported item type.",
        )

    def _execute_gate(
        self,
        item: WatchItem,
        action: WatchAction,
    ) -> WatchActionResponse:

        if action != WatchAction.TOGGLE:
            return WatchActionResponse(
                success=False,
                message="Unsupported action.",
            )

        self._supla_service.toggle_gate(
            item.supla_id,
        )

        return WatchActionResponse(
            success=True,
            message="Action accepted.",
            refresh_required=True,
        )

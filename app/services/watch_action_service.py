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

        if item.type in ("light", "switch"):
            return self._execute_toggle_channel(
                item,
                action,
            )

        if item.type == "roller_shutter":
            return self._execute_roller_shutter(
                item,
                action,
            )

        if item.type == "awning":
            return self._execute_awning(
                item,
                action,
            )

        if item.type == "scene":
            return self._execute_scene(
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

        if item.sensor_channel_id is None:
            return WatchActionResponse(
                success=False,
                message="Gate sensor not configured.",
            )

        executed_action = self._supla_service.execute_gate_action(
            item.supla_id,
            item.sensor_channel_id,
        )

        return WatchActionResponse(
            success=True,
            message=f"Gate action executed: {executed_action}.",
            refresh_required=True,
        )

    def _execute_toggle_channel(
        self,
        item: WatchItem,
        action: WatchAction,
    ) -> WatchActionResponse:

        if action != WatchAction.TOGGLE:
            return WatchActionResponse(
                success=False,
                message="Unsupported action.",
            )

        self._supla_service.toggle_channel(
            item.supla_id,
        )

        return WatchActionResponse(
            success=True,
            message="Channel toggled.",
            refresh_required=True,
        )

    def _execute_roller_shutter(
        self,
        item: WatchItem,
        action: WatchAction,
    ) -> WatchActionResponse:

        if action not in (
            WatchAction.OPEN,
            WatchAction.CLOSE,
            WatchAction.STOP,
        ):
            return WatchActionResponse(
                success=False,
                message="Unsupported action.",
            )

        self._supla_service.execute_roller_shutter_action(
            item.supla_id,
            action.value,
        )

        return WatchActionResponse(
            success=True,
            message=(
                "Roller shutter action executed: "
                f"{action.value}."
            ),
            refresh_required=True,
        )

    def _execute_awning(
        self,
        item: WatchItem,
        action: WatchAction,
    ) -> WatchActionResponse:

        if action not in (
            WatchAction.COLLAPSE,
            WatchAction.EXPAND,
            WatchAction.STOP,
        ):
            return WatchActionResponse(
                success=False,
                message="Unsupported action.",
            )

        self._supla_service.execute_awning_action(
            item.supla_id,
            action.value,
        )

        return WatchActionResponse(
            success=True,
            message=(
                "Awning action executed: "
                f"{action.value}."
            ),
            refresh_required=True,
        )

    def _execute_scene(
        self,
        item: WatchItem,
        action: WatchAction,
    ) -> WatchActionResponse:

        if action != WatchAction.TOGGLE:
            return WatchActionResponse(
                success=False,
                message="Unsupported action.",
            )

        self._supla_service.execute_scene(
            item.supla_id,
        )

        return WatchActionResponse(
            success=True,
            message="Scene executed.",
            refresh_required=True,
        )

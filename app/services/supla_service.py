from app.clients.supla_client import SuplaClient
from app.exceptions import GateStateUnavailableError
from app.models.supla import GateChannel
from app.models.settings import SelectedGate
from app.models.api import GateSummary
from app.models.api.setup import SuplaAvailableItem
from app.services.oauth_service import OAuthService
from app.stores.settings_store import SettingsStore


class SuplaService:
    def __init__(self) -> None:
        self._settings_store = SettingsStore()
        self._oauth_service = OAuthService()

    def _client(self) -> SuplaClient:
        settings = self._settings_store.load()

        return SuplaClient(
            server=settings.supla.server,
        )

    def get_iodevices(self):
        return self._oauth_service.execute_with_token_refresh(
            self._client().get_iodevices,
        )

    def get_channels(self):
        return self._oauth_service.execute_with_token_refresh(
            self._client().get_channels,
        )

    def get_channels_with_state(self):
        return self._oauth_service.execute_with_token_refresh(
            self._client().get_channels,
            "state,connected",
        )

    def get_gate_channels(self) -> list[GateChannel]:
        channels = self.get_channels()

        gates = [
            GateChannel.model_validate(channel)
            for channel in channels
        ]

        return [
            gate
            for gate in gates
            if gate.function.name == "CONTROLLINGTHEGATE"
        ]

    def select_gate(self, channel_id: int) -> SelectedGate:
        settings = self._settings_store.load()

        gates = self.get_gate_channels()

        gate = next(
            (gate for gate in gates if gate.id == channel_id),
            None,
        )

        if gate is None:
            raise ValueError(f"Gate channel {channel_id} not found.")

        selected_gate = SelectedGate(
            id=gate.id,
            caption=gate.caption or f"Gate {gate.id}",
            sensor_channel_id=gate.sensor_channel_id,
        )

        settings.supla.selected_gate = selected_gate

        self._settings_store.save(settings)

        return selected_gate

    def get_available_gates(self) -> list[GateSummary]:
        return [
            GateSummary(
                id=gate.id,
                caption=gate.caption or f"Gate {gate.id}",
                sensor_channel_id=gate.sensor_channel_id,
            )
            for gate in self.get_gate_channels()
        ]

    def get_available_watch_items(
        self,
    ) -> list[SuplaAvailableItem]:
        """
        Return currently available executable SUPLA channels.

        Data is fetched live from SUPLA on every call.
        """

        channels = self.get_channels()
        iodevices = self.get_iodevices()

        enabled_iodevice_ids = {
            device.get("id")
            for device in iodevices
            if device.get("enabled") is True
        }

        type_by_function = {
            "CONTROLLINGTHEGATE": "gate",
            "LIGHTSWITCH": "light",
            "POWERSWITCH": "switch",
            "CONTROLLINGTHEROLLERSHUTTER": "roller_shutter",
            "TERRACE_AWNING": "awning",
        }

        items: list[SuplaAvailableItem] = []

        for channel in channels:
            iodevice_id = channel.get("iodeviceId")

            if iodevice_id not in enabled_iodevice_ids:
                continue

            function = channel.get("function")

            if not isinstance(function, dict):
                continue

            function_name = function.get("name")

            item_type = type_by_function.get(
                function_name
            )

            if item_type is None:
                continue

            possible_actions = (
                channel.get("possibleActions")
                or []
            )

            if not possible_actions:
                continue

            channel_id = channel.get("id")

            if not isinstance(channel_id, int):
                continue

            caption = channel.get("caption")

            if not caption:
                caption = (
                    function.get("caption")
                    or f"SUPLA {channel_id}"
                )

            sensor_channel_id = None

            if item_type == "gate":
                config = channel.get("config")

                if isinstance(config, dict):
                    sensor_channel_id = (
                        config.get(
                            "openingSensorChannelId"
                        )
                    )

            items.append(
                SuplaAvailableItem(
                    supla_id=channel_id,
                    type=item_type,
                    name=str(caption),
                    function=str(function_name),
                    sensor_channel_id=(
                        sensor_channel_id
                    ),
                )
            )

        return items

    def execute_gate_action(
        self,
        channel_id: int,
        sensor_channel_id: int,
    ) -> str:
        channels = self.get_channels_with_state()

        sensor = next(
            (
                channel
                for channel in channels
                if channel.get("id") == sensor_channel_id
            ),
            None,
        )

        if sensor is None:
            raise GateStateUnavailableError(
                f"Gate sensor channel {sensor_channel_id} not found."
            )

        if sensor.get("connected") is not True:
            raise GateStateUnavailableError(
                "Gate sensor is not connected."
            )

        state = sensor.get("state")

        if not isinstance(state, dict):
            raise GateStateUnavailableError(
                "Gate state is unavailable."
            )

        hi = state.get("hi")

        if hi is True:
            action = "open"
        elif hi is False:
            action = "close"
        else:
            raise GateStateUnavailableError(
                "Gate state is unavailable."
            )

        self._oauth_service.execute_with_token_refresh(
            self._client().execute_channel_action,
            channel_id,
            action,
        )

        return action

    def toggle_channel(
        self,
        channel_id: int,
    ) -> None:
        self._oauth_service.execute_with_token_refresh(
            self._client().execute_channel_action,
            channel_id,
            "toggle",
        )

    def execute_roller_shutter_action(
        self,
        channel_id: int,
        action: str,
    ) -> None:
        action_map = {
            "open": "reveal",
            "close": "shut",
            "stop": "stop",
        }

        supla_action = action_map.get(action)

        if supla_action is None:
            raise ValueError(
                f"Unsupported roller shutter action: {action}"
            )

        self._oauth_service.execute_with_token_refresh(
            self._client().execute_channel_action,
            channel_id,
            supla_action,
        )

    def execute_awning_action(
        self,
        channel_id: int,
        action: str,
    ) -> None:
        action_map = {
            "collapse": "reveal",
            "expand": "shut",
            "stop": "stop",
        }

        supla_action = action_map.get(action)

        if supla_action is None:
            raise ValueError(
                f"Unsupported awning action: {action}"
            )

        self._oauth_service.execute_with_token_refresh(
            self._client().execute_channel_action,
            channel_id,
            supla_action,
        )

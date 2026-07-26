from app.clients.supla_client import SuplaClient
from app.stores.settings_store import SettingsStore
from app.models.supla import GateChannel
from app.models.settings import SelectedGate
from app.services.oauth_service import OAuthService


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

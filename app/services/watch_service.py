import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from app.models.settings import WatchDevice
from app.services.watch_device_resolver import (
    resolve_watch_model,
)
from app.stores.settings_store import SettingsStore


class WatchService:
    """Manage Garmin watch registration and authentication."""

    def __init__(
        self,
        store: SettingsStore | None = None,
    ):
        self._store = (
            store
            if store is not None
            else SettingsStore()
        )

    @staticmethod
    def _hash_token(token: str) -> str:
        """Return SHA-256 hash of a watch token."""

        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    def authenticate(
        self,
        token: str,
    ) -> WatchDevice | None:
        """Authenticate a Garmin watch using its bearer token."""

        settings = self._store.load()

        watch = settings.watch

        if watch is None:
            return None

        if not watch.enabled:
            return None

        token_hash = self._hash_token(token)

        if not secrets.compare_digest(
            token_hash,
            watch.token_hash,
        ):
            return None

        return watch

    def update_metadata(
        self,
        watch_id: str,
        metadata: dict[str, str | None],
    ) -> WatchDevice | None:
        """Update metadata for the registered Garmin watch."""

        settings = self._store.load()

        watch = settings.watch

        if watch is None:
            return None

        if watch.id != watch_id:
            return None

        allowed_fields = {
            "device_id",
            "part_number",
            "firmware_version",
            "connect_iq_version",
            "system_language",
            "app_version",
        }

        for field, value in metadata.items():
            if field not in allowed_fields:
                continue

            setattr(
                watch,
                field,
                value,
            )

        if "part_number" in metadata:
            watch.device_model = (
                resolve_watch_model(
                    watch.part_number
                )
            )

        self._store.save(settings)

        return watch

    def register_watch(
        self,
        name: str = "Garmin Watch",
    ) -> tuple[WatchDevice, str]:
        """Register a watch and return its one-time plaintext token."""

        settings = self._store.load()

        token = secrets.token_urlsafe(32)

        watch = WatchDevice(
            id=str(uuid.uuid4()),
            name=name,
            token_hash=self._hash_token(token),
            created_at=datetime.now(timezone.utc).isoformat(),
            last_seen_at=None,
            enabled=True,
        )

        settings.watch = watch

        self._store.save(settings)

        return watch, token

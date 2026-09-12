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

        token_hash = self._hash_token(token)

        for watch in settings.watches:
            if not watch.enabled:
                continue

            if secrets.compare_digest(
                token_hash,
                watch.token_hash,
            ):
                return watch

        return None

    def reissue_token(
        self,
        watch_id: str,
    ) -> tuple[WatchDevice, str] | None:
        """Issue a new token for an existing Garmin watch."""

        settings = self._store.load()

        watch = next(
            (
                candidate
                for candidate in settings.watches
                if candidate.id == watch_id
            ),
            None,
        )

        if watch is None:
            return None

        token = secrets.token_urlsafe(32)

        watch.token_hash = self._hash_token(
            token
        )

        watch.credential_revision += 1

        if (
            settings.watch is not None
            and settings.watch.id == watch.id
        ):
            settings.watch = watch

        self._store.save(settings)

        return watch, token

    def update_metadata(
        self,
        watch_id: str,
        metadata: dict[str, str | None],
    ) -> WatchDevice | None:
        """Update metadata for a registered Garmin watch."""

        settings = self._store.load()

        watch = None

        for candidate in settings.watches:
            if candidate.id == watch_id:
                watch = candidate
                break

        if watch is None:
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

        watch.last_seen_at = (
            datetime.now(timezone.utc).isoformat()
        )

        if (
            settings.watch is not None
            and settings.watch.id == watch.id
        ):
            settings.watch = watch

        self._store.save(settings)

        return watch

    def register_watch(
        self,
        name: str = "Garmin Watch",
        copy_from_watch_id: str | None = None,
    ) -> tuple[WatchDevice, str] | None:
        """Register a watch and return its one-time plaintext token."""

        settings = self._store.load()

        source = None

        if copy_from_watch_id is not None:
            source = next(
                (
                    candidate
                    for candidate in settings.watches
                    if (
                        candidate.id
                        == copy_from_watch_id
                    )
                ),
                None,
            )

            if source is None:
                return None

        token = secrets.token_urlsafe(32)

        watch = WatchDevice(
            id=str(uuid.uuid4()),
            name=name,
            token_hash=self._hash_token(
                token
            ),
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
            last_seen_at=None,
            enabled=True,
            items=(
                [
                    item.model_copy(
                        deep=True
                    )
                    for item in source.items
                ]
                if source is not None
                else []
            ),
        )

        settings.watches.append(
            watch
        )

        settings.watch = watch

        # Keep the legacy current-watch
        # configuration synchronized.
        settings.watch_settings.items = [
            item.model_copy(
                deep=True
            )
            for item in watch.items
        ]

        self._store.save(settings)

        return watch, token

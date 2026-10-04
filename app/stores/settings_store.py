from contextlib import contextmanager
from json import JSONDecodeError
from pathlib import Path
from threading import Lock
from typing import Iterator

import fcntl
import json
import logging
import os

from pydantic import ValidationError

from app.models.settings import Settings


logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "data/config.json"


class SettingsStore:
    """Persistent application configuration storage."""

    def __init__(
        self,
        path: str = DEFAULT_CONFIG_PATH,
    ):
        self.path = Path(path)
        self._lock = Lock()

    def exists(self) -> bool:
        """Return True if the configuration file exists."""

        return self.path.exists()

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        """Lock configuration storage across threads and processes."""

        with self._lock:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            lock_path = Path(
                str(self.path) + ".lock"
            )

            fd = os.open(
                lock_path,
                os.O_CREAT | os.O_RDWR,
                0o600,
            )

            os.fchmod(
                fd,
                0o600,
            )

            with os.fdopen(
                fd,
                "r+",
            ) as lock_file:
                fcntl.flock(
                    lock_file.fileno(),
                    fcntl.LOCK_EX,
                )

                try:
                    yield

                finally:
                    fcntl.flock(
                        lock_file.fileno(),
                        fcntl.LOCK_UN,
                    )

    def save(
        self,
        settings: Settings,
    ) -> None:
        """Persist application configuration securely."""

        with self._exclusive_lock():
            current = (
                self._load_existing_unlocked()
            )

            if current is not None:
                self._protect_watch_credentials(
                    settings,
                    current,
                )

            self._write_unlocked(
                settings
            )

    def load(self) -> Settings:
        """Load application configuration from disk."""

        with self._exclusive_lock():
            if not self.path.exists():
                logger.info(
                    "Configuration file not found. "
                    "Creating default configuration."
                )

                settings = Settings()

                self._write_unlocked(
                    settings
                )

                return settings

            try:
                return self._read_unlocked()

            except (
                JSONDecodeError,
                ValidationError,
            ):
                logger.warning(
                    "Configuration file is invalid."
                )

                self._backup_corrupted_unlocked()

                logger.info(
                    "Creating default configuration."
                )

                settings = Settings()

                self._write_unlocked(
                    settings
                )

                return settings

    def _read_unlocked(
        self,
    ) -> Settings:
        """Read configuration while storage is locked."""

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

        return Settings.model_validate(
            data
        )

    def _load_existing_unlocked(
        self,
    ) -> Settings | None:
        """Load existing valid configuration without creating defaults."""

        if not self.path.exists():
            return None

        try:
            return self._read_unlocked()

        except (
            OSError,
            JSONDecodeError,
            ValidationError,
        ):
            return None

    @staticmethod
    def _protect_watch_credentials(
        incoming: Settings,
        current: Settings,
    ) -> None:
        """
        Prevent stale configuration writes from restoring
        superseded Garmin watch credentials.
        """

        current_by_id = {
            watch.id: watch
            for watch in current.watches
        }

        incoming_by_id = {
            watch.id: watch
            for watch in incoming.watches
        }

        for watch_id, incoming_watch in (
            incoming_by_id.items()
        ):
            current_watch = (
                current_by_id.get(
                    watch_id
                )
            )

            if current_watch is None:
                continue

            if (
                incoming_watch.credential_revision
                < current_watch.credential_revision
            ):
                incoming_watch.token_hash = (
                    current_watch.token_hash
                )

                incoming_watch.credential_revision = (
                    current_watch.credential_revision
                )

                continue

            if (
                incoming_watch.credential_revision
                == current_watch.credential_revision
                and incoming_watch.token_hash
                != current_watch.token_hash
            ):
                raise ValueError(
                    "Conflicting Garmin watch credentials."
                )

    def _write_unlocked(
        self,
        settings: Settings,
    ) -> None:
        """Atomically write configuration while storage is locked."""

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp_path = self.path.with_suffix(
            ".tmp"
        )

        fd = os.open(
            tmp_path,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_TRUNC,
            0o600,
        )

        os.fchmod(
            fd,
            0o600,
        )

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                settings.model_dump(
                    mode="json"
                ),
                file,
                indent=4,
                ensure_ascii=False,
            )

            file.flush()

            os.fsync(
                file.fileno()
            )

        tmp_path.replace(
            self.path
        )

    def _backup_corrupted_unlocked(
        self,
    ) -> None:
        """Backup corrupted configuration while storage is locked."""

        backup_path = self.path.with_suffix(
            ".broken.json"
        )

        try:
            self.path.replace(
                backup_path
            )

            logger.warning(
                "Corrupted configuration backed up to %s",
                backup_path,
            )

        except OSError:
            logger.exception(
                "Unable to backup corrupted configuration."
            )

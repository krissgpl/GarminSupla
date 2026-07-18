from pathlib import Path
from threading import Lock
import json
import logging
from json import JSONDecodeError

from pydantic import ValidationError

from app.models.settings import Settings

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "data/config.json"


class SettingsStore:
    """Persistent application configuration storage."""

    def __init__(self, path: str = DEFAULT_CONFIG_PATH):
        self.path = Path(path)
        self._lock = Lock()

    def exists(self) -> bool:
        """Return True if the configuration file exists."""
        return self.path.exists()

    def save(self, settings: Settings) -> None:
        """Persist application configuration to disk."""

        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            tmp_path = self.path.with_suffix(".tmp")

            with tmp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    settings.model_dump(mode="json"),
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            tmp_path.replace(self.path)

    def load(self) -> Settings:
        """Load application configuration from disk."""

        if not self.exists():
            logger.info(
                "Configuration file not found. Creating default configuration."
            )
            return self._create_default()

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return Settings.model_validate(data)

        except (JSONDecodeError, ValidationError):
            logger.warning("Configuration file is invalid.")

            self._backup_corrupted()

            logger.info("Creating default configuration.")

            return self._create_default()

    def _create_default(self) -> Settings:
        """Create and persist default configuration."""

        settings = Settings()
        self.save(settings)

        return settings

    def _backup_corrupted(self) -> None:
        """Backup corrupted configuration file."""

        backup_path = self.path.with_suffix(".broken.json")

        try:
            self.path.replace(backup_path)

            logger.warning(
                "Corrupted configuration backed up to %s",
                backup_path,
            )

        except OSError:
            logger.exception("Unable to backup corrupted configuration.")

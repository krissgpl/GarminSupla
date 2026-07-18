from pathlib import Path
from threading import Lock
import json

from app.models.settings import Settings


class SettingsStore:
    """Persistent application configuration storage."""

    def __init__(self, path: str = "data/config.json"):
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
        raise NotImplementedError

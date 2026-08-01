from json import JSONDecodeError
import json
import logging
from pathlib import Path
from threading import Lock

from pydantic import ValidationError

from app.models.admin import AdminAccount


logger = logging.getLogger(__name__)

DEFAULT_ADMIN_PATH = "data/admin.json"


class AdminStore:
    """Persistent administrator account storage."""

    def __init__(self, path: str = DEFAULT_ADMIN_PATH):
        self.path = Path(path)
        self._lock = Lock()

    def exists(self) -> bool:
        """Return True if an administrator account exists."""

        return self.path.exists()

    def save(self, admin: AdminAccount) -> None:
        """Persist administrator account to disk."""

        with self._lock:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            tmp_path = self.path.with_suffix(".tmp")

            with tmp_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    admin.model_dump(mode="json"),
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            tmp_path.replace(self.path)

    def load(self) -> AdminAccount | None:
        """Load administrator account."""

        if not self.exists():
            return None

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return AdminAccount.model_validate(data)

        except (JSONDecodeError, ValidationError):
            logger.exception(
                "Administrator configuration is invalid."
            )

            return None

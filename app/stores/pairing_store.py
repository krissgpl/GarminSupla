import json
from datetime import datetime, timezone
from pathlib import Path

from app.models.pairing import PairingSession


class PairingStore:
    """Store the temporary Garmin watch pairing session."""

    def __init__(
        self,
        path: str = "data/pairing.json",
    ) -> None:
        self._path = Path(path)

    def load(self) -> PairingSession | None:
        """Load the active pairing session."""

        if not self._path.exists():
            return None

        try:
            data = json.loads(
                self._path.read_text(
                    encoding="utf-8",
                )
            )

            session = PairingSession.model_validate(
                data
            )

        except (
            OSError,
            json.JSONDecodeError,
            ValueError,
        ):
            return None

        now = datetime.now(timezone.utc)

        if session.expires_at <= now:
            self.delete()
            return None

        return session

    def save(
        self,
        session: PairingSession,
    ) -> None:
        """Save a pairing session."""

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._path.write_text(
            session.model_dump_json(
                indent=2,
            ),
            encoding="utf-8",
        )

    def delete(self) -> None:
        """Delete the pairing session."""

        try:
            self._path.unlink()
        except FileNotFoundError:
            pass

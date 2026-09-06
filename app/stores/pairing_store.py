import json
from datetime import datetime, timezone
from pathlib import Path

from app.models.pairing import PairingSession


class PairingStore:
    """Store temporary Garmin watch pairing sessions."""

    def __init__(
        self,
        path: str = "data/pairing.json",
    ) -> None:
        self._path = Path(path)

    def load(self) -> PairingSession | None:
        """Load the first active pairing session."""

        sessions = self.load_all()

        if not sessions:
            return None

        return sessions[0]

    def load_all(self) -> list[PairingSession]:
        """Load all active pairing sessions."""

        if not self._path.exists():
            return []

        try:
            data = json.loads(
                self._path.read_text(
                    encoding="utf-8",
                )
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return []

        if (
            isinstance(data, dict)
            and "sessions" in data
        ):
            raw_sessions = data["sessions"]

            if not isinstance(
                raw_sessions,
                list,
            ):
                return []

        else:
            # Legacy single-session format.
            raw_sessions = [
                data
            ]

        now = datetime.now(timezone.utc)
        sessions = []

        for raw_session in raw_sessions:
            try:
                session = (
                    PairingSession.model_validate(
                        raw_session
                    )
                )

            except ValueError:
                continue

            if session.expires_at <= now:
                continue

            sessions.append(
                session
            )

        return sessions

    def save(
        self,
        session: PairingSession,
    ) -> None:
        """Save or update a pairing session."""

        sessions = self.load_all()

        replaced = False

        for index, existing in enumerate(
            sessions
        ):
            if (
                existing.pairing_id
                == session.pairing_id
            ):
                sessions[index] = session
                replaced = True
                break

        if not replaced:
            sessions.append(
                session
            )

        self._write_sessions(
            sessions
        )

    def delete(
        self,
        pairing_id: str | None = None,
    ) -> None:
        """Delete one pairing session or all sessions."""

        if pairing_id is None:
            try:
                self._path.unlink()
            except FileNotFoundError:
                pass

            return

        sessions = [
            session
            for session in self.load_all()
            if session.pairing_id != pairing_id
        ]

        if not sessions:
            try:
                self._path.unlink()
            except FileNotFoundError:
                pass

            return

        self._write_sessions(
            sessions
        )

    def _write_sessions(
        self,
        sessions: list[PairingSession],
    ) -> None:
        """Persist pairing sessions."""

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "sessions": [
                session.model_dump(
                    mode="json",
                )
                for session in sessions
            ]
        }

        self._path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

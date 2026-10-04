from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Iterator

import fcntl
import json
import os
import secrets

from app.models.pairing import PairingSession


class PairingStore:
    """Store temporary Garmin watch pairing sessions."""

    def __init__(
        self,
        path: str = "data/pairing.json",
    ) -> None:
        self._path = Path(path)
        self._lock = Lock()

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        """Lock pairing storage across threads and Linux processes."""

        with self._lock:
            self._path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            lock_path = Path(
                str(self._path) + ".lock"
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

    def load_all(self) -> list[PairingSession]:
        """Load all active pairing sessions."""

        with self._exclusive_lock():
            return self._load_all_unlocked()

    def _load_all_unlocked(
        self,
    ) -> list[PairingSession]:
        """Load active pairing sessions while storage is locked."""

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
            not isinstance(data, dict)
            or "sessions" not in data
        ):
            return []

        raw_sessions = data["sessions"]

        if not isinstance(
            raw_sessions,
            list,
        ):
            return []

        now = datetime.now(
            timezone.utc
        )

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
        """Save or update a pairing session atomically."""

        with self._exclusive_lock():
            sessions = (
                self._load_all_unlocked()
            )

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

            self._write_sessions_unlocked(
                sessions
            )

    def claim_approved(
        self,
        pairing_id: str,
    ) -> PairingSession | None:
        """
        Atomically claim one approved pairing session.

        A successfully claimed session is removed from persistent
        storage before it is returned, so concurrent consumers
        cannot receive the same pairing session.
        """

        with self._exclusive_lock():
            sessions = (
                self._load_all_unlocked()
            )

            claimed = None
            remaining = []

            for session in sessions:
                if (
                    claimed is None
                    and session.approved
                    and secrets.compare_digest(
                        session.pairing_id,
                        pairing_id,
                    )
                ):
                    claimed = session
                    continue

                remaining.append(
                    session
                )

            if claimed is None:
                return None

            if remaining:
                self._write_sessions_unlocked(
                    remaining
                )
            else:
                self._delete_file_unlocked()

            return claimed

    def _delete_file_unlocked(
        self,
    ) -> None:
        """Delete pairing storage while it is locked."""

        try:
            self._path.unlink()

        except FileNotFoundError:
            pass

    def _write_sessions_unlocked(
        self,
        sessions: list[PairingSession],
    ) -> None:
        """Persist pairing sessions while storage is locked."""

        data = {
            "sessions": [
                session.model_dump(
                    mode="json",
                )
                for session in sessions
            ]
        }

        tmp_path = Path(
            str(self._path) + ".tmp"
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
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

            file.flush()

            os.fsync(
                file.fileno()
            )

        tmp_path.replace(
            self._path
        )

import secrets
from datetime import datetime, timedelta, timezone

from app.models.pairing import PairingResult, PairingSession
from app.services.watch_service import WatchService
from app.stores.pairing_store import PairingStore


PAIRING_TTL_SECONDS = 5 * 60


class PairingService:
    """Manage Garmin watch pairing."""

    def __init__(
        self,
        store: PairingStore | None = None,
        watch_service: WatchService | None = None,
    ) -> None:
        self._store = (
            store if store is not None else PairingStore()
        )

        self._watch_service = (
            watch_service
            if watch_service is not None
            else WatchService()
        )

    def create_pairing(self) -> PairingSession:
        """Create a new temporary pairing session."""

        existing = self._store.load()

        if existing is not None:
            return existing

        now = datetime.now(timezone.utc)

        session = PairingSession(
            pairing_id=secrets.token_urlsafe(32),
            code=f"{secrets.randbelow(1_000_000):06d}",
            created_at=now,
            expires_at=now + timedelta(
                seconds=PAIRING_TTL_SECONDS,
            ),
        )

        self._store.save(session)

        return session

    def approve_pairing(
        self,
        code: str,
    ) -> PairingSession | None:
        """Approve a pairing using its six-digit code."""

        session = self._store.load()

        if session is None:
            return None

        if not secrets.compare_digest(
            session.code,
            code,
        ):
            return None

        if session.approved:
            return session

        session.approved = True

        self._store.save(session)

        return session

    def get_pairing(
        self,
        pairing_id: str,
    ) -> PairingSession | None:
        """Return a pairing session by its secret identifier."""

        session = self._store.load()

        if session is None:
            return None

        if not secrets.compare_digest(
            session.pairing_id,
            pairing_id,
        ):
            return None

        return session

    def consume_pairing(
        self,
        pairing_id: str,
        name: str = "Garmin Watch",
    ) -> PairingResult | None:
        """Complete an approved pairing and issue watch credentials."""

        session = self.get_pairing(
            pairing_id
        )

        if session is None:
            return None

        if not session.approved:
            return None

        watch, token = self._watch_service.register_watch(
            name=name,
        )

        self._store.delete()

        return PairingResult(
            watch_id=watch.id,
            watch_token=token,
        )

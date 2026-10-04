import tempfile
import unittest

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models.pairing import PairingSession
from app.services.pairing_service import (
    PAIRING_TTL_SECONDS,
    PairingService,
)
from app.services.watch_service import WatchService
from app.stores.pairing_store import PairingStore
from app.stores.settings_store import SettingsStore


class PairingServiceTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        pairing_path = (
            Path(self.temp_dir.name)
            / "pairing.json"
        )

        settings_path = (
            Path(self.temp_dir.name)
            / "config.json"
        )

        self.pairing_store = PairingStore(
            path=str(pairing_path)
        )

        self.settings_store = SettingsStore(
            path=str(settings_path)
        )

        self.watch_service = WatchService(
            store=self.settings_store
        )

        self.service = PairingService(
            store=self.pairing_store,
            watch_service=self.watch_service,
        )

    def test_create_pairing_creates_valid_temporary_session(
        self,
    ):
        session = self.service.create_pairing()

        self.assertEqual(
            len(session.code),
            6,
        )

        self.assertTrue(
            session.code.isdigit()
        )

        self.assertFalse(
            session.approved
        )

        lifetime = (
            session.expires_at
            - session.created_at
        ).total_seconds()

        self.assertEqual(
            lifetime,
            PAIRING_TTL_SECONDS,
        )

        self.assertIsNotNone(
            self.service.get_pairing(
                session.pairing_id
            )
        )

    def test_unapproved_pairing_cannot_be_consumed(
        self,
    ):
        session = self.service.create_pairing()

        result = self.service.consume_pairing(
            session.pairing_id
        )

        self.assertIsNone(
            result
        )

        self.assertIsNotNone(
            self.service.get_pairing(
                session.pairing_id
            )
        )

    def test_expired_pairing_cannot_be_approved_or_consumed(
        self,
    ):
        now = datetime.now(
            timezone.utc
        )

        session = PairingSession(
            pairing_id="expired-pairing-id",
            code="123456",
            created_at=now - timedelta(
                minutes=10
            ),
            expires_at=now - timedelta(
                minutes=5
            ),
        )

        self.pairing_store.save(
            session
        )

        approved = self.service.approve_pairing(
            session.code
        )

        consumed = self.service.consume_pairing(
            session.pairing_id
        )

        self.assertIsNone(
            approved
        )

        self.assertIsNone(
            consumed
        )

        self.assertIsNone(
            self.service.get_pairing(
                session.pairing_id
            )
        )

    def test_approved_pairing_can_be_consumed_only_once(
        self,
    ):
        session = self.service.create_pairing()

        approved = self.service.approve_pairing(
            session.code
        )

        self.assertIsNotNone(
            approved
        )

        first_result = self.service.consume_pairing(
            session.pairing_id
        )

        self.assertIsNotNone(
            first_result
        )

        authenticated_watch = (
            self.watch_service.authenticate(
                first_result.watch_token
            )
        )

        self.assertIsNotNone(
            authenticated_watch
        )

        self.assertEqual(
            authenticated_watch.id,
            first_result.watch_id,
        )

        second_result = self.service.consume_pairing(
            session.pairing_id
        )

        self.assertIsNone(
            second_result
        )

        self.assertIsNone(
            self.service.get_pairing(
                session.pairing_id
            )
        )


if __name__ == "__main__":
    unittest.main()

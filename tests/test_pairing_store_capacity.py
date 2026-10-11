import tempfile
import unittest

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.pairing import PairingSession
from app.routers.api import pairing
from app.stores.pairing_store import (
    MAX_ACTIVE_PAIRINGS,
    PairingCapacityExceeded,
    PairingStore,
)
from app.watch_app import watch_app


class PairingStoreCapacityTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.store = PairingStore(
            path=str(
                Path(self.temp_dir.name)
                / "pairing.json"
            )
        )

    def make_session(self, index):
        now = datetime.now(timezone.utc)

        return PairingSession(
            pairing_id=f"pairing-{index}",
            code=f"{index:06d}",
            created_at=now,
            expires_at=now + timedelta(minutes=5),
        )

    def test_capacity_and_existing_session_update(self):
        for index in range(MAX_ACTIVE_PAIRINGS):
            self.store.save(
                self.make_session(index)
            )

        self.assertEqual(
            len(self.store.load_all()),
            MAX_ACTIVE_PAIRINGS,
        )

        with self.assertRaises(PairingCapacityExceeded):
            self.store.save(
                self.make_session(MAX_ACTIVE_PAIRINGS)
            )

        self.assertEqual(
            len(self.store.load_all()),
            MAX_ACTIVE_PAIRINGS,
        )

        existing = self.store.load_all()[0]
        existing.approved = True
        self.store.save(existing)

        self.assertTrue(
            self.store.load_all()[0].approved
        )

        existing.expires_at = (
            datetime.now(timezone.utc)
            - timedelta(seconds=1)
        )
        self.store.save(existing)

        self.store.save(
            self.make_session(MAX_ACTIVE_PAIRINGS)
        )

        self.assertEqual(
            len(self.store.load_all()),
            MAX_ACTIVE_PAIRINGS,
        )

    def test_api_returns_429_when_capacity_reached(self):
        client = TestClient(
            watch_app,
            base_url="https://testserver",
        )

        with pairing._pairing_create_lock:
            pairing._pairing_create_times.clear()

        try:
            with patch.object(
                pairing.pairing_service,
                "create_pairing",
                side_effect=PairingCapacityExceeded(),
            ):
                response = client.post(
                    "/api/v1/watch/pair"
                )

            self.assertEqual(response.status_code, 429)
            self.assertEqual(
                response.headers.get("retry-after"),
                "60",
            )

        finally:
            with pairing._pairing_create_lock:
                pairing._pairing_create_times.clear()


if __name__ == "__main__":
    unittest.main()

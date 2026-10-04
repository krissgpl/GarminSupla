import tempfile
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models.pairing import PairingSession
from app.stores.pairing_store import PairingStore


class PairingStoreAtomicityTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        self.path = (
            Path(self.temp_dir.name)
            / "pairing.json"
        )

    def test_approved_pairing_can_be_claimed_only_once_concurrently(
        self,
    ):
        first_store = PairingStore(
            path=str(self.path)
        )

        second_store = PairingStore(
            path=str(self.path)
        )

        now = datetime.now(
            timezone.utc
        )

        session = PairingSession(
            pairing_id="concurrent-pairing-id",
            code="123456",
            created_at=now,
            expires_at=now + timedelta(
                minutes=5
            ),
            approved=True,
        )

        first_store.save(
            session
        )

        barrier = threading.Barrier(
            3
        )

        def claim(
            store: PairingStore,
        ) -> PairingSession | None:
            barrier.wait()

            return store.claim_approved(
                session.pairing_id
            )

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:
            first_future = executor.submit(
                claim,
                first_store,
            )

            second_future = executor.submit(
                claim,
                second_store,
            )

            barrier.wait()

            results = [
                first_future.result(
                    timeout=5
                ),
                second_future.result(
                    timeout=5
                ),
            ]

        claimed = [
            result
            for result in results
            if result is not None
        ]

        self.assertEqual(
            len(claimed),
            1,
        )

        self.assertEqual(
            claimed[0].pairing_id,
            session.pairing_id,
        )

        self.assertEqual(
            first_store.load_all(),
            [],
        )

        self.assertEqual(
            second_store.load_all(),
            [],
        )


if __name__ == "__main__":
    unittest.main()

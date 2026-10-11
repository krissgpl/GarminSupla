import unittest

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.pairing import (
    PairingResult,
    PairingSession,
)
from app.routers.api import pairing
from app.watch_app import watch_app


class WatchPairingEndpointLimitTests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(
            watch_app,
            base_url="https://testserver",
        )

        self._clear_limits()

    def tearDown(self):
        self._clear_limits()

    def _clear_limits(self):
        for times, lock in (
            (
                pairing._pairing_status_times,
                pairing._pairing_status_lock,
            ),
            (
                pairing._pairing_consume_times,
                pairing._pairing_consume_lock,
            ),
        ):
            with lock:
                times.clear()

    def test_status_endpoint_limit(self):
        now = datetime.now(timezone.utc)

        session = PairingSession(
            pairing_id="test-pairing-id",
            code="123456",
            created_at=now,
            expires_at=now + timedelta(minutes=5),
        )

        url = "/api/v1/watch/pair/test-pairing-id"

        with (
            patch.object(
                pairing,
                "PAIRING_STATUS_LIMIT",
                2,
            ),
            patch.object(
                pairing,
                "monotonic",
                return_value=1000.0,
            ),
            patch.object(
                pairing.pairing_service,
                "get_pairing",
                return_value=session,
            ) as get_pairing,
        ):
            self.assertEqual(
                self.client.get(url).status_code,
                200,
            )

            self.assertEqual(
                self.client.get(url).status_code,
                200,
            )

            blocked = self.client.get(url)

            self.assertEqual(blocked.status_code, 429)
            self.assertEqual(
                blocked.headers.get("retry-after"),
                "60",
            )
            self.assertEqual(
                get_pairing.call_count,
                2,
            )

        with (
            patch.object(
                pairing,
                "PAIRING_STATUS_LIMIT",
                2,
            ),
            patch.object(
                pairing,
                "monotonic",
                return_value=1061.0,
            ),
            patch.object(
                pairing.pairing_service,
                "get_pairing",
                return_value=session,
            ),
        ):
            self.assertEqual(
                self.client.get(url).status_code,
                200,
            )

    def test_consume_endpoint_limit(self):
        result = PairingResult(
            watch_id="test-watch-id",
            watch_token="test-watch-token",
        )

        url = (
            "/api/v1/watch/pair/"
            "test-pairing-id/consume"
        )

        with (
            patch.object(
                pairing,
                "PAIRING_CONSUME_LIMIT",
                2,
            ),
            patch.object(
                pairing,
                "monotonic",
                return_value=2000.0,
            ),
            patch.object(
                pairing.pairing_service,
                "consume_pairing",
                return_value=result,
            ) as consume_pairing,
        ):
            self.assertEqual(
                self.client.post(url).status_code,
                200,
            )

            self.assertEqual(
                self.client.post(url).status_code,
                200,
            )

            blocked = self.client.post(url)

            self.assertEqual(blocked.status_code, 429)
            self.assertEqual(
                blocked.headers.get("retry-after"),
                "60",
            )
            self.assertEqual(
                consume_pairing.call_count,
                2,
            )

        with (
            patch.object(
                pairing,
                "PAIRING_CONSUME_LIMIT",
                2,
            ),
            patch.object(
                pairing,
                "monotonic",
                return_value=2061.0,
            ),
            patch.object(
                pairing.pairing_service,
                "consume_pairing",
                return_value=result,
            ),
        ):
            self.assertEqual(
                self.client.post(url).status_code,
                200,
            )


if __name__ == "__main__":
    unittest.main()

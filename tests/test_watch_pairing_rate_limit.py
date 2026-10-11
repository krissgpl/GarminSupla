import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.pairing import PairingSession
from app.routers.api import pairing
from app.watch_app import watch_app


class WatchPairingRateLimitTests(unittest.TestCase):

    def test_pairing_creation_is_rate_limited(self):
        now = datetime.now(timezone.utc)

        session = PairingSession(
            pairing_id="test-pairing-id",
            code="123456",
            created_at=now,
            expires_at=now + timedelta(minutes=5),
        )

        client = TestClient(
            watch_app,
            base_url="https://testserver",
        )

        try:
            with pairing._pairing_create_lock:
                pairing._pairing_create_times.clear()

            with (
                patch.object(
                    pairing.pairing_service,
                    "create_pairing",
                    return_value=session,
                ),
                patch.object(
                    pairing,
                    "monotonic",
                    return_value=1000.0,
                ),
            ):
                for _ in range(pairing.PAIRING_CREATE_LIMIT):
                    response = client.post(
                        "/api/v1/watch/pair"
                    )
                    self.assertEqual(
                        response.status_code,
                        200,
                    )

                blocked = client.post(
                    "/api/v1/watch/pair"
                )

                self.assertEqual(
                    blocked.status_code,
                    429,
                )
                self.assertEqual(
                    blocked.headers.get("retry-after"),
                    "60",
                )

            with (
                patch.object(
                    pairing.pairing_service,
                    "create_pairing",
                    return_value=session,
                ),
                patch.object(
                    pairing,
                    "monotonic",
                    return_value=1061.0,
                ),
            ):
                allowed = client.post(
                    "/api/v1/watch/pair"
                )
                self.assertEqual(
                    allowed.status_code,
                    200,
                )

        finally:
            with pairing._pairing_create_lock:
                pairing._pairing_create_times.clear()


if __name__ == "__main__":
    unittest.main()

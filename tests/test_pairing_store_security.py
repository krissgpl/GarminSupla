import stat
import tempfile
import unittest

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models.pairing import PairingSession
from app.stores.pairing_store import PairingStore


class PairingStoreSecurityTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        self.path = (
            Path(self.temp_dir.name)
            / "pairing.json"
        )

        self.store = PairingStore(
            path=str(self.path)
        )

        now = datetime.now(
            timezone.utc
        )

        self.session = PairingSession(
            pairing_id="test-pairing-id",
            code="123456",
            created_at=now,
            expires_at=now + timedelta(
                minutes=5
            ),
        )

    def test_pairing_file_is_owner_only(self):
        self.store.save(
            self.session
        )

        mode = stat.S_IMODE(
            self.path.stat().st_mode
        )

        self.assertEqual(
            mode,
            0o600,
        )

    def test_rewrite_repairs_permissions(self):
        self.store.save(
            self.session
        )

        self.path.chmod(
            0o644
        )

        self.session.approved = True

        self.store.save(
            self.session
        )

        mode = stat.S_IMODE(
            self.path.stat().st_mode
        )

        self.assertEqual(
            mode,
            0o600,
        )


if __name__ == "__main__":
    unittest.main()

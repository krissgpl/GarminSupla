import os
import stat
import subprocess
import sys
import tempfile
import unittest

from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.x509.oid import NameOID


ROOT_DIR = Path(__file__).resolve().parent.parent
HOSTNAME = "watch.example.test"


class InstallationFlowTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.root = Path(temporary.name)
        self.env = self.root / ".env"
        self.compose = self.root / "docker-compose.yml"
        self.caddy = self.root / "deploy/caddy/Caddyfile"
        self.cert_dir = self.root / "certs"

    def run_module(self, module, *arguments):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                module,
                *map(str, arguments),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr or result.stdout,
        )

        return result

    def create_test_certificate(self):
        self.cert_dir.mkdir()

        key = ed25519.Ed25519PrivateKey.generate()
        now = datetime.now(timezone.utc)

        subject = x509.Name([
            x509.NameAttribute(
                NameOID.COMMON_NAME,
                HOSTNAME,
            ),
        ])

        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(key.public_key())
            .serial_number(
                x509.random_serial_number()
            )
            .not_valid_before(
                now - timedelta(days=1)
            )
            .not_valid_after(
                now + timedelta(days=30)
            )
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(HOSTNAME),
                ]),
                critical=False,
            )
            .sign(key, algorithm=None)
        )

        (
            self.cert_dir / "fullchain.pem"
        ).write_bytes(
            certificate.public_bytes(
                serialization.Encoding.PEM
            )
        )

        private_key = self.cert_dir / "private.key"

        private_key.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

        private_key.chmod(0o600)

    def test_complete_fresh_installation(self):
        # 1. Initialize an isolated environment.
        runtime_ids = (
            ("--run-uid", "1000", "--run-gid", "1000")
            if os.getuid() == 0 or os.getgid() == 0
            else ()
        )

        self.run_module(
            "scripts.init_env",
            "--output",
            self.env,
            *runtime_ids,
        )

        self.assertTrue(self.env.is_file())

        mode = stat.S_IMODE(
            self.env.stat().st_mode
        )

        self.assertEqual(mode, 0o600)

        initial_lines = self.env.read_text(
            encoding="utf-8"
        ).splitlines()

        secret_lines = [
            line
            for line in initial_lines
            if line.startswith(
                "ADMIN_SESSION_SECRET="
            )
        ]

        self.assertEqual(len(secret_lines), 1)

        secret = secret_lines[0].split("=", 1)[1]
        self.assertGreaterEqual(len(secret), 60)

        # 2. Initialize deployment configuration.
        self.run_module(
            "scripts.init_deploy",
            "--target-dir",
            self.root,
        )

        self.assertEqual(
            self.compose.read_bytes(),
            (
                ROOT_DIR / "docker-compose.example.yml"
            ).read_bytes(),
        )

        self.assertEqual(
            self.caddy.read_bytes(),
            (
                ROOT_DIR / "deploy/caddy/Caddyfile.example"
            ).read_bytes(),
        )

        # 3. Create a disposable certificate.
        self.create_test_certificate()

        with self.env.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                f"GARMIN_SUPLA_WATCH_DOMAIN={HOSTNAME}\n"
                f"GARMIN_SUPLA_CERT_DIR={self.cert_dir}\n"
            )

        # 4. Validate the generated configuration.
        result = self.run_module(
            "scripts.check_deploy",
            "--env-file",
            self.env,
        )

        self.assertIn(
            "preflight passed",
            result.stdout,
        )

        self.assertNotIn(
            secret,
            result.stdout + result.stderr,
        )

        # 5. Re-run both initializers.
        # All existing files must remain unchanged.
        files = (
            self.env,
            self.compose,
            self.caddy,
        )

        before = {
            path: path.read_bytes()
            for path in files
        }

        self.run_module(
            "scripts.init_env",
            "--output",
            self.env,
        )

        self.run_module(
            "scripts.init_deploy",
            "--target-dir",
            self.root,
        )

        for path in files:
            with self.subTest(path=path.name):
                self.assertEqual(
                    path.read_bytes(),
                    before[path],
                )

        # 6. Preflight still passes after re-initialization.
        self.run_module(
            "scripts.check_deploy",
            "--env-file",
            self.env,
        )


if __name__ == "__main__":
    unittest.main()

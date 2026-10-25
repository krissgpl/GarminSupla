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

HOST = "watch.example.test"


class CheckDeployTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.root = Path(temporary.name)
        self.env = self.root / ".env"
        self.certs = self.root / "certs"

        self.certs.mkdir()

        self.write_env()
        self.write_certificate()

    def write_env(
        self,
        *,
        host=HOST,
        secret="test-private-secret",
        cert_dir=None,
    ):
        if cert_dir is None:
            cert_dir = str(self.certs)

        self.env.write_text(
            f"ADMIN_SESSION_SECRET={secret}\n"
            f"GARMIN_SUPLA_WATCH_DOMAIN={host}\n"
            f"GARMIN_SUPLA_CERT_DIR={cert_dir}\n",
            encoding="utf-8",
        )

    def write_certificate(
        self,
        *,
        names=(HOST,),
        expired=False,
    ):
        key = ed25519.Ed25519PrivateKey.generate()
        now = datetime.now(timezone.utc)

        subject = x509.Name([
            x509.NameAttribute(
                NameOID.COMMON_NAME,
                HOST,
            )
        ])

        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(key.public_key())
            .serial_number(
                x509.random_serial_number()
            )
            .not_valid_before(
                now - timedelta(days=10)
            )
            .not_valid_after(
                now + timedelta(
                    days=-1 if expired else 30
                )
            )
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(name)
                    for name in names
                ]),
                critical=False,
            )
        )

        cert = builder.sign(
            key,
            algorithm=None,
        )

        (
            self.certs / "fullchain.pem"
        ).write_bytes(
            cert.public_bytes(
                serialization.Encoding.PEM
            )
        )

        (
            self.certs / "private.key"
        ).write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

    def run_check(self):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.check_deploy",
                "--env-file",
                str(self.env),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def test_valid_configuration_passes(self):
        result = self.run_check()

        self.assertEqual(
            result.returncode,
            0,
            result.stderr,
        )

        self.assertIn(
            "preflight passed",
            result.stdout,
        )

        self.assertNotIn(
            "test-private-secret",
            result.stdout + result.stderr,
        )

    def test_wildcard_certificate_passes(self):
        self.write_certificate(
            names=("*.example.test",)
        )

        self.assertEqual(
            self.run_check().returncode,
            0,
        )

    def test_missing_env_fails(self):
        self.env.unlink()

        self.assertNotEqual(
            self.run_check().returncode,
            0,
        )

    def test_missing_admin_secret_fails(self):
        self.write_env(secret="")

        result = self.run_check()

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "ADMIN_SESSION_SECRET",
            result.stderr,
        )

    def test_invalid_domain_fails(self):
        self.write_env(
            host="https://watch.example.test:8008"
        )

        result = self.run_check()

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "GARMIN_SUPLA_WATCH_DOMAIN",
            result.stderr,
        )

    def test_missing_certificate_fails(self):
        (
            self.certs / "fullchain.pem"
        ).unlink()

        self.assertNotEqual(
            self.run_check().returncode,
            0,
        )

    def test_missing_private_key_fails(self):
        (
            self.certs / "private.key"
        ).unlink()

        self.assertNotEqual(
            self.run_check().returncode,
            0,
        )

    def test_wrong_hostname_fails(self):
        self.write_certificate(
            names=("other.example.test",)
        )

        self.assertNotEqual(
            self.run_check().returncode,
            0,
        )

    def test_expired_certificate_fails(self):
        self.write_certificate(expired=True)

        self.assertNotEqual(
            self.run_check().returncode,
            0,
        )

    def test_mismatched_key_fails(self):
        key = ed25519.Ed25519PrivateKey.generate()

        (
            self.certs / "private.key"
        ).write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

        result = self.run_check()

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "does not match",
            result.stderr,
        )

    def test_relative_certificate_directory_fails(self):
        self.write_env(
            cert_dir="relative/certs"
        )

        self.assertNotEqual(
            self.run_check().returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()

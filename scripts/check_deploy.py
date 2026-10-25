"""Read-only preflight checks for Watch API HTTPS."""

import argparse
import re
import sys

from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from dotenv import dotenv_values


ROOT_DIR = Path(__file__).resolve().parent.parent


def _required(config: dict, name: str) -> str:
    value = config.get(name)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Missing required setting: {name}."
        )

    return value.strip()


def _valid_hostname(hostname: str) -> bool:
    if len(hostname) > 253 or "." not in hostname:
        return False

    for label in hostname.split("."):
        if (
            len(label) not in range(1, 64)
            or label.startswith("-")
            or label.endswith("-")
            or re.fullmatch(
                r"[A-Za-z0-9-]+",
                label,
            ) is None
        ):
            return False

    return True


def _dns_name_matches(
    pattern: str,
    hostname: str,
) -> bool:
    pattern = pattern.lower()
    hostname = hostname.lower()

    if "*" not in pattern:
        return pattern == hostname

    if (
        not pattern.startswith("*.")
        or pattern.count("*") != 1
    ):
        return False

    suffix = pattern[2:]

    return (
        hostname.endswith("." + suffix)
        and hostname.count(".")
        == suffix.count(".") + 1
    )


def validate(env_file: Path) -> None:
    if not env_file.is_file():
        raise ValueError(
            "Configuration .env file was not found."
        )

    try:
        config = dotenv_values(
            env_file,
            interpolate=False,
        )

    except (OSError, UnicodeError) as exc:
        raise ValueError(
            "Cannot read the .env configuration."
        ) from exc

    _required(
        config,
        "ADMIN_SESSION_SECRET",
    )

    hostname = _required(
        config,
        "GARMIN_SUPLA_WATCH_DOMAIN",
    )

    if not _valid_hostname(hostname):
        raise ValueError(
            "GARMIN_SUPLA_WATCH_DOMAIN "
            "must be a DNS hostname."
        )

    cert_directory = Path(
        _required(
            config,
            "GARMIN_SUPLA_CERT_DIR",
        )
    )

    if (
        not cert_directory.is_absolute()
        or not cert_directory.is_dir()
    ):
        raise ValueError(
            "GARMIN_SUPLA_CERT_DIR must be "
            "an existing absolute directory."
        )

    cert_file = cert_directory / "fullchain.pem"
    key_file = cert_directory / "private.key"

    if not cert_file.is_file():
        raise ValueError(
            "Missing TLS certificate: fullchain.pem."
        )

    if not key_file.is_file():
        raise ValueError(
            "Missing TLS private key: private.key."
        )

    try:
        cert = x509.load_pem_x509_certificate(
            cert_file.read_bytes()
        )

    except (OSError, ValueError) as exc:
        raise ValueError(
            "Cannot parse TLS certificate fullchain.pem."
        ) from exc

    now = datetime.now(timezone.utc)

    if not (
        cert.not_valid_before_utc
        <= now
        < cert.not_valid_after_utc
    ):
        raise ValueError(
            "TLS certificate is not currently valid (dates)."
        )

    try:
        san = cert.extensions.get_extension_for_class(
            x509.SubjectAlternativeName
        ).value

    except x509.ExtensionNotFound as exc:
        raise ValueError(
            "TLS certificate has no DNS subjectAltName."
        ) from exc

    if not any(
        _dns_name_matches(name, hostname)
        for name in san.get_values_for_type(
            x509.DNSName
        )
    ):
        raise ValueError(
            "TLS certificate does not cover "
            "GARMIN_SUPLA_WATCH_DOMAIN."
        )

    try:
        private_key = (
            serialization.load_pem_private_key(
                key_file.read_bytes(),
                password=None,
            )
        )

        public_format = (
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        cert_public = (
            cert.public_key().public_bytes(
                *public_format
            )
        )

        key_public = (
            private_key.public_key().public_bytes(
                *public_format
            )
        )

    except (
        OSError,
        ValueError,
        TypeError,
        UnsupportedAlgorithm,
    ) as exc:
        raise ValueError(
            "Cannot read an unencrypted TLS private key."
        ) from exc

    if cert_public != key_public:
        raise ValueError(
            "TLS private key does not match fullchain.pem."
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check local HTTPS settings "
            "without changing files."
        )
    )

    parser.add_argument(
        "--env-file",
        type=Path,
        default=ROOT_DIR / ".env",
    )

    args = parser.parse_args()

    try:
        validate(args.env_file)

    except ValueError as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        "OK: Watch API HTTPS preflight passed "
        "(local checks only)."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

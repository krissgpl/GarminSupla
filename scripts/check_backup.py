"""Read-only preflight for a future offline GarminSupla backup.

Checks file metadata and access only. Does not copy or read secret values.
"""

import argparse
import os
import stat
from pathlib import Path


REQUIRED_FILES = (
    (".env", True),
    ("docker-compose.yml", False),
    ("deploy/caddy/Caddyfile", False),
    ("data/config.json", True),
    ("data/admin.json", True),
)


def _directory(
    path: Path,
    label: str,
    errors: list[str],
) -> bool:
    try:
        info = path.lstat()
    except OSError:
        errors.append(
            f"{label}: missing or inaccessible directory"
        )
        return False

    if not stat.S_ISDIR(info.st_mode):
        errors.append(
            f"{label}: expected a real directory, not a link"
        )
        return False

    if not os.access(path, os.R_OK | os.X_OK):
        errors.append(
            f"{label}: directory is not accessible"
        )
        return False

    return True


def _file(
    path: Path,
    label: str,
    private: bool,
    errors: list[str],
) -> None:
    try:
        info = path.lstat()
    except OSError:
        errors.append(
            f"{label}: missing or inaccessible file"
        )
        return

    if not stat.S_ISREG(info.st_mode):
        errors.append(
            f"{label}: expected a regular file, not a link"
        )
        return

    mode = stat.S_IMODE(info.st_mode)

    if private and mode & 0o077:
        errors.append(
            f"{label}: insecure permissions {mode:04o} "
            "(require owner-only)"
        )

    if not os.access(path, os.R_OK):
        errors.append(
            f"{label}: cannot be read by the current user"
        )


def validate(
    root: Path,
    cert_dir: Path,
) -> list[str]:
    errors: list[str] = []

    if not cert_dir.is_absolute():
        return [
            "--cert-dir must be an absolute directory"
        ]

    if not _directory(
        root,
        "installation root",
        errors,
    ):
        return errors

    if not _directory(
        root / "data",
        "data/",
        errors,
    ):
        return errors

    if not _directory(
        cert_dir,
        "TLS directory",
        errors,
    ):
        return errors

    for relative, private in REQUIRED_FILES:
        _file(
            root / relative,
            relative,
            private,
            errors,
        )

    _file(
        cert_dir / "fullchain.pem",
        "TLS fullchain.pem",
        False,
        errors,
    )

    _file(
        cert_dir / "private.key",
        "TLS private.key",
        True,
        errors,
    )

    pairing = root / "data/pairing.json"

    if pairing.is_symlink() or pairing.exists():
        _file(
            pairing,
            "data/pairing.json",
            True,
            errors,
        )

    # Historyczne kopie mogą zawierać dane SUPLA.
    # Sprawdzamy tylko metadane.

    try:
        entries = list(
            (root / "data").iterdir()
        )
    except OSError:
        errors.append(
            "data/: unable to list directory"
        )
        return errors

    for entry in entries:
        name = entry.name

        if name in {
            "config.json",
            "admin.json",
            "pairing.json",
        }:
            continue

        if name.endswith(".lock"):
            continue

        if name.startswith(
            ("config.", "admin.")
        ):
            _file(
                entry,
                f"data/{name}",
                True,
                errors,
            )

    secrets_dir = (
        root / "deploy/caddy/secrets"
    )

    if (
        secrets_dir.is_symlink()
        or secrets_dir.exists()
    ):
        if _directory(
            secrets_dir,
            "deploy/caddy/secrets/",
            errors,
        ):
            mode = stat.S_IMODE(
                secrets_dir.stat().st_mode
            )

            if mode & 0o077:
                errors.append(
                    "deploy/caddy/secrets/: "
                    "directory must be owner-only"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--root",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--cert-dir",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    errors = validate(
        args.root,
        args.cert_dir,
    )

    for problem in errors:
        print(f"ERROR: {problem}")

    print(
        "INFO: This is a read-only preflight, "
        "not a backup. It does not check "
        "live-write consistency or back up "
        "Caddy named Docker volumes."
    )

    if errors:
        print(
            "ERROR: backup preflight found "
            f"{len(errors)} problem(s)"
        )
        return 1

    print(
        "OK: backup file preflight passed "
        "(no backup created)"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Read-only verification of a GarminSupla file backup archive.

Validates manifest, files, TAR metadata and SHA-256 checksums.
Never extracts files or contacts Docker.
"""

import argparse
import hashlib
import json
import re
import stat
import sys
import tarfile

from pathlib import Path

from scripts.create_backup import FILES


CHUNK = 1024 * 1024
MAX_MANIFEST = 1024 * 1024
MAX_ENTRIES = 4096

REQUIRED = set(FILES) | {
    "certs/fullchain.pem",
    "certs/private.key",
}

OPTIONAL = {
    "data/pairing.json",
}

SECRETS_PREFIX = "deploy/caddy/secrets/"

EXPECTED_EXCLUDES = [
    "caddy_docker_volumes",
    "historical_data_copies",
    "lock_files",
]


def allowed_name(name: str) -> bool:
    """Accept only known file paths and private Caddy secrets."""

    if not isinstance(name, str):
        return False

    if name in REQUIRED | OPTIONAL:
        return True

    if not name.startswith(SECRETS_PREFIX):
        return False

    relative = name[len(SECRETS_PREFIX):]
    parts = relative.split("/")

    return (
        bool(relative)
        and "\\" not in relative
        and all(
            part not in ("", ".", "..")
            for part in parts
        )
        and all(
            character.isprintable()
            for character in relative
        )
    )


def file_checksum(source):
    digest = hashlib.sha256()
    size = 0

    while True:
        chunk = source.read(CHUNK)

        if not chunk:
            break

        size += len(chunk)
        digest.update(chunk)

    return size, digest.hexdigest()


def verify_archive(path: Path) -> int:
    """Verify file archive without extracting its contents."""

    path = Path(path)
    info = path.lstat()

    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError(
            "Backup must be a regular owner-only file"
        )

    found = set()
    actual = {}
    manifest = None

    try:
        with tarfile.open(
            path,
            mode="r:gz",
        ) as archive:

            for member in archive:
                name = member.name

                if len(found) >= MAX_ENTRIES:
                    raise ValueError(
                        "Too many backup archive entries"
                    )

                if name in found:
                    raise ValueError(
                        "Duplicate backup archive entry"
                    )

                if (
                    name != "manifest.json"
                    and not allowed_name(name)
                ):
                    raise ValueError(
                        "Unexpected backup archive path"
                    )

                if (
                    not member.isfile()
                    or member.mode != 0o600
                    or member.uid != 0
                    or member.gid != 0
                    or member.size < 0
                ):
                    raise ValueError(
                        "Unsafe backup archive entry metadata"
                    )

                found.add(name)

                source = archive.extractfile(member)

                if source is None:
                    raise ValueError(
                        "Unreadable backup archive entry"
                    )

                if name == "manifest.json":
                    if member.size > MAX_MANIFEST:
                        raise ValueError(
                            "Oversized backup manifest"
                        )

                    content = source.read(
                        MAX_MANIFEST + 1
                    )

                    if len(content) != member.size:
                        raise ValueError(
                            "Incomplete backup manifest"
                        )

                    manifest = json.loads(content)

                else:
                    size, digest = file_checksum(
                        source
                    )

                    if size != member.size:
                        raise ValueError(
                            "Incomplete backup file entry"
                        )

                    actual[name] = (
                        size,
                        digest,
                    )

    except (
        tarfile.TarError,
        EOFError,
        json.JSONDecodeError,
        UnicodeError,
    ) as exc:
        raise ValueError(
            "Invalid GarminSupla file backup archive"
        ) from exc

    if not isinstance(manifest, dict):
        raise ValueError(
            "Missing or invalid backup manifest"
        )

    records = manifest.get("files")

    if (
        manifest.get("format")
        != "garminsupla-files/v1"
        or manifest.get(
            "complete_system_backup"
        ) is not False
        or manifest.get("excludes")
        != EXPECTED_EXCLUDES
        or not isinstance(records, list)
        or len(records) != len(actual)
    ):
        raise ValueError(
            "Invalid file backup manifest"
        )

    if not REQUIRED.issubset(actual):
        raise ValueError(
            "Required backup files are missing"
        )

    declared = set()

    for record in records:
        if not isinstance(record, dict):
            raise ValueError(
                "Invalid backup file record"
            )

        name = record.get("path")
        size = record.get("size")
        digest = record.get("sha256")

        if (
            not allowed_name(name)
            or name in declared
            or type(size) is not int
            or size < 0
            or not isinstance(digest, str)
            or re.fullmatch(
                r"[0-9a-f]{64}",
                digest,
            ) is None
        ):
            raise ValueError(
                "Invalid backup file manifest record"
            )

        declared.add(name)

        if actual.get(name) != (size, digest):
            raise ValueError(
                "Backup file SHA-256 or size mismatch"
            )

    if declared != set(actual):
        raise ValueError(
            "Backup manifest file list mismatch"
        )

    # No file may also be an ancestor directory of another.
    for name in actual:
        parts = name.split("/")

        for position in range(1, len(parts)):
            parent = "/".join(
                parts[:position]
            )

            if parent in actual:
                raise ValueError(
                    "File conflicts with backup directory"
                )

    return len(actual)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--archive",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    try:
        count = verify_archive(
            args.archive
        )

    except (
        OSError,
        ValueError,
    ) as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: verified {count} GarminSupla backup files "
        "and SHA-256 hashes"
    )
    print(
        "INFO: read-only verification; "
        "no files restored and Docker not accessed"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

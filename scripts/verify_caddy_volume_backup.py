"""Read-only verification of an offline GarminSupla Caddy volume archive.

Checks the outer manifest, embedded TAR entries, and SHA-256 checksums.
Does not contact Docker or extract files.
"""

import argparse
import hashlib
import json
import re
import stat
import sys
import tarfile
from pathlib import Path

from scripts.check_caddy_volumes import VOLUMES


CHUNK = 1024 * 1024
MAX_MANIFEST = 1024 * 1024


class HashingReader:
    def __init__(self, source):
        self.source = source
        self.digest = hashlib.sha256()
        self.size = 0

    def read(self, size=-1):
        data = self.source.read(size)
        self.digest.update(data)
        self.size += len(data)
        return data


def check_inner_archive(source):
    """Validate every TAR entry without extracting anything."""

    reader = HashingReader(source)
    seen = {}

    try:
        with tarfile.open(
            fileobj=reader,
            mode="r|",
        ) as inner:

            for entry in inner:
                name = entry.name.rstrip("/")
                parts = name.split("/")

                if (
                    not name
                    or name.startswith("/")
                    or "\\" in name
                    or any(
                        part in ("", ".", "..")
                        for part in parts
                    )
                    or name in seen
                    or not (
                        entry.isdir()
                        or entry.isfile()
                    )
                ):
                    raise ValueError(
                        "Unsafe embedded volume TAR entry"
                    )

                for n in range(1, len(parts)):
                    parent = "/".join(parts[:n])

                    if (
                        parent in seen
                        and not seen[parent]
                    ):
                        raise ValueError(
                            "File is used as directory in volume TAR"
                        )

                if (
                    entry.isfile()
                    and any(
                        previous.startswith(name + "/")
                        for previous in seen
                    )
                ):
                    raise ValueError(
                        "File replaces directory in volume TAR"
                    )

                seen[name] = entry.isdir()

                if entry.isfile():
                    content = inner.extractfile(entry)

                    if content is None:
                        raise ValueError(
                            "Unreadable embedded volume TAR entry"
                        )

                    while content.read(CHUNK):
                        pass

        # Include TAR padding in the checksum.
        while reader.read(CHUNK):
            pass

    except (
        tarfile.TarError,
        EOFError,
        OSError,
    ) as exc:
        raise ValueError(
            "Invalid embedded volume TAR"
        ) from exc

    return (
        reader.size,
        reader.digest.hexdigest(),
    )


def verify_archive(
    path: Path,
    project: str,
) -> int:
    if re.fullmatch(
        r"[a-z][a-z0-9_-]*",
        project,
    ) is None:
        raise ValueError(
            "Invalid Docker Compose project name"
        )

    info = path.lstat()

    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError(
            "Backup must be a regular owner-only file"
        )

    expected_names = {
        "manifest.json",
        *(
            f"volumes/{name}.tar"
            for name in VOLUMES
        ),
    }

    try:
        with tarfile.open(
            path,
            mode="r:gz",
        ) as outer:

            members = outer.getmembers()
            names = [
                entry.name
                for entry in members
            ]

            if (
                len(members) != len(expected_names)
                or set(names) != expected_names
                or any(
                    not entry.isfile()
                    for entry in members
                )
            ):
                raise ValueError(
                    "Unexpected outer backup TAR entries"
                )

            manifest_member = outer.getmember(
                "manifest.json"
            )

            if manifest_member.size > MAX_MANIFEST:
                raise ValueError(
                    "Oversized backup manifest"
                )

            manifest_file = outer.extractfile(
                manifest_member
            )

            if manifest_file is None:
                raise ValueError(
                    "Missing backup manifest"
                )

            manifest = json.loads(
                manifest_file.read(
                    MAX_MANIFEST + 1
                )
            )

            if (
                not isinstance(manifest, dict)
                or manifest.get("format")
                != "garminsupla-caddy-volumes/v1"
                or manifest.get(
                    "complete_system_backup"
                ) is not False
                or not isinstance(
                    manifest.get("volumes"),
                    list,
                )
                or len(manifest["volumes"])
                != len(VOLUMES)
            ):
                raise ValueError(
                    "Invalid backup manifest"
                )

            for short_name, entry in zip(
                VOLUMES,
                manifest["volumes"],
            ):
                member_name = (
                    f"volumes/{short_name}.tar"
                )

                if (
                    not isinstance(entry, dict)
                    or entry.get("volume")
                    != f"{project}_{short_name}"
                    or entry.get("member")
                    != member_name
                    or type(entry.get("size")) is not int
                    or entry["size"] < 0
                    or not isinstance(
                        entry.get("sha256"),
                        str,
                    )
                    or re.fullmatch(
                        r"[0-9a-f]{64}",
                        entry["sha256"],
                    ) is None
                ):
                    raise ValueError(
                        "Invalid volume manifest record"
                    )

                member = outer.getmember(
                    member_name
                )

                if member.size != entry["size"]:
                    raise ValueError(
                        "Volume TAR size does not match manifest"
                    )

                payload = outer.extractfile(
                    member
                )

                if payload is None:
                    raise ValueError(
                        "Missing volume TAR data"
                    )

                size, digest = check_inner_archive(
                    payload
                )

                if (
                    size != entry["size"]
                    or digest != entry["sha256"]
                ):
                    raise ValueError(
                        "Volume TAR SHA-256 or size mismatch"
                    )

    except (
        tarfile.TarError,
        EOFError,
        json.JSONDecodeError,
        UnicodeError,
    ) as exc:
        raise ValueError(
            "Invalid Caddy volume backup archive"
        ) from exc

    return len(VOLUMES)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--archive",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--project",
        required=True,
    )

    args = parser.parse_args()

    try:
        count = verify_archive(
            args.archive,
            args.project,
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
        f"OK: verified {count} Caddy volume "
        "TAR archives and SHA-256 hashes"
    )
    print(
        "INFO: read-only verification; "
        "no files or Docker volumes restored"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

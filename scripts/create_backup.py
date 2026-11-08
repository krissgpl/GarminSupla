"""Create a private, offline-only GarminSupla file archive.

Caddy Docker named volumes are NOT included.
This is not a complete disaster-recovery backup.
"""

import argparse
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tarfile
import tempfile

from datetime import datetime, timezone
from pathlib import Path

from scripts.check_backup import validate


FILES = (
    ".env",
    "docker-compose.yml",
    "deploy/caddy/Caddyfile",
    "data/config.json",
    "data/admin.json",
)


class HashingReader:
    def __init__(self, file, digest):
        self.file = file
        self.digest = digest

    def read(self, size=-1):
        chunk = self.file.read(size)
        self.digest.update(chunk)
        return chunk


def source_files(root, cert_dir):
    files = [
        (root / name, name)
        for name in FILES
    ]

    files.extend([
        (
            cert_dir / "fullchain.pem",
            "certs/fullchain.pem",
        ),
        (
            cert_dir / "private.key",
            "certs/private.key",
        ),
    ])

    pairing = root / "data/pairing.json"

    if pairing.exists() or pairing.is_symlink():
        files.append((
            pairing,
            "data/pairing.json",
        ))

    secrets = root / "deploy/caddy/secrets"

    if secrets.exists() or secrets.is_symlink():
        for directory, names, filenames in os.walk(
            secrets,
            followlinks=False,
        ):
            current = Path(directory)
            info = current.lstat()

            if (
                not stat.S_ISDIR(info.st_mode)
                or stat.S_IMODE(info.st_mode) & 0o077
            ):
                raise ValueError(
                    "Caddy secrets directory is not private"
                )

            for name in names:
                nested = (current / name).lstat()

                if (
                    not stat.S_ISDIR(nested.st_mode)
                    or stat.S_IMODE(nested.st_mode) & 0o077
                ):
                    raise ValueError(
                        "Caddy secrets directory entry is unsafe"
                    )

            for name in filenames:
                path = current / name
                info = path.lstat()

                if (
                    not stat.S_ISREG(info.st_mode)
                    or stat.S_IMODE(info.st_mode) & 0o077
                ):
                    raise ValueError(
                        "Caddy secrets file entry is unsafe"
                    )

                archive_name = (
                    Path("deploy/caddy/secrets")
                    / path.relative_to(secrets)
                ).as_posix()

                files.append((path, archive_name))

    return sorted(
        files,
        key=lambda item: item[1],
    )


def check_destination(root, cert_dir, output):
    if not output.is_absolute():
        raise ValueError(
            "Backup output must be an absolute path"
        )

    parent = output.parent
    info = parent.lstat()

    if (
        not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.geteuid()
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError(
            "Backup output directory must be "
            "owner-only (0700) and owned by current user"
        )

    if output.exists() or output.is_symlink():
        raise FileExistsError(
            "Backup destination already exists"
        )

    target_parent = parent.resolve(strict=True)

    for forbidden in (
        root.resolve(strict=True),
        cert_dir.resolve(strict=True),
    ):
        if (
            target_parent == forbidden
            or target_parent.is_relative_to(forbidden)
        ):
            raise ValueError(
                "Backup output directory must be "
                "outside installation and TLS directories"
            )


def check_services_stopped(root):
    command = [
        "docker",
        "compose",
        "--project-directory",
        str(root),
        "--env-file",
        str(root / ".env"),
        "-f",
        str(root / "docker-compose.yml"),
        "ps",
        "-q",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (
        OSError,
        subprocess.TimeoutExpired,
    ) as exc:
        raise RuntimeError(
            "Docker Compose availability could "
            "not be verified"
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "Docker Compose service status "
            "could not be verified"
        )

    if result.stdout.strip():
        raise RuntimeError(
            "Docker Compose reports running services; "
            "offline backup refused"
        )


def create_backup(
    root,
    cert_dir,
    output,
    *,
    check_offline=True,
):
    root = Path(root)
    cert_dir = Path(cert_dir)
    output = Path(output)

    problems = validate(root, cert_dir)

    if problems:
        raise ValueError(
            "Backup preflight failed: "
            + "; ".join(problems)
        )

    check_destination(
        root,
        cert_dir,
        output,
    )

    if check_offline:
        check_services_stopped(root)

    files = source_files(root, cert_dir)

    fd, temporary = tempfile.mkstemp(
        prefix=".garminsupla-backup-",
        suffix=".partial",
        dir=output.parent,
    )

    try:
        with os.fdopen(fd, "wb") as destination:
            with tarfile.open(
                fileobj=destination,
                mode="w:gz",
            ) as archive:
                entries = []

                for source, name in files:
                    flags = (
                        os.O_RDONLY
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_NONBLOCK", 0)
                    )

                    source_fd = os.open(
                        source,
                        flags,
                    )

                    with os.fdopen(
                        source_fd,
                        "rb",
                    ) as infile:
                        before = os.fstat(
                            infile.fileno()
                        )

                        if not stat.S_ISREG(
                            before.st_mode
                        ):
                            raise ValueError(
                                "Source is not a regular file: "
                                + name
                            )

                        private = (
                            name in {
                                ".env",
                                "data/config.json",
                                "data/admin.json",
                                "data/pairing.json",
                                "certs/private.key",
                            }
                            or name.startswith(
                                "deploy/caddy/secrets/"
                            )
                        )

                        if (
                            private
                            and stat.S_IMODE(
                                before.st_mode
                            ) & 0o077
                        ):
                            raise ValueError(
                                "Source has unsafe permissions: "
                                + name
                            )

                        item = tarfile.TarInfo(name)
                        item.size = before.st_size
                        item.mode = 0o600
                        item.mtime = 0
                        item.uid = 0
                        item.gid = 0

                        digest = hashlib.sha256()

                        archive.addfile(
                            item,
                            HashingReader(
                                infile,
                                digest,
                            ),
                        )

                        after = os.fstat(
                            infile.fileno()
                        )

                        before_signature = (
                            before.st_size,
                            before.st_mtime_ns,
                            before.st_ctime_ns,
                        )

                        after_signature = (
                            after.st_size,
                            after.st_mtime_ns,
                            after.st_ctime_ns,
                        )

                        if (
                            before_signature
                            != after_signature
                        ):
                            raise RuntimeError(
                                "Source changed during archive: "
                                + name
                            )

                        entries.append({
                            "path": name,
                            "size": before.st_size,
                            "sha256": digest.hexdigest(),
                        })

                manifest = {
                    "format": "garminsupla-files/v1",
                    "created_utc": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "complete_system_backup": False,
                    "excludes": [
                        "caddy_docker_volumes",
                        "historical_data_copies",
                        "lock_files",
                    ],
                    "files": entries,
                }

                encoded = json.dumps(
                    manifest,
                    indent=2,
                ).encode("utf-8")

                item = tarfile.TarInfo(
                    "manifest.json"
                )

                item.size = len(encoded)
                item.mode = 0o600
                item.mtime = 0

                archive.addfile(
                    item,
                    io.BytesIO(encoded),
                )

            destination.flush()
            os.fsync(
                destination.fileno()
            )

        # Atomic publication, without overwriting
        # an existing destination.
        os.link(
            temporary,
            output,
        )

        directory_fd = os.open(
            output.parent,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0),
        )

        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    finally:
        os.unlink(temporary)

def main():
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

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--confirm-stopped",
        action="store_true",
        help=(
            "Confirm a maintenance window "
            "with services stopped"
        ),
    )

    args = parser.parse_args()

    if not args.confirm_stopped:
        print(
            "ERROR: --confirm-stopped is required; "
            "the backup must run offline",
            file=sys.stderr,
        )
        return 1

    try:
        create_backup(
            args.root,
            args.cert_dir,
            args.output,
        )
    except (
        OSError,
        ValueError,
        RuntimeError,
    ) as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        "OK: private offline file backup created "
        "(Docker volumes excluded)"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

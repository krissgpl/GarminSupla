"""Create and verify a paired, private GarminSupla backup set offline.

The backup is deliberately not claimed to be a complete system backup.
A manifest pairs archives but cannot independently prove offline consistency.
On failure, a newly created private output directory is retained for inspection;
no existing directory or archive is overwritten or removed.
"""

import argparse
import hashlib
import json
import os
import secrets
import stat
import subprocess
import sys

from datetime import datetime, timezone
from pathlib import Path

from scripts.create_backup import create_backup, check_services_stopped
from scripts.create_caddy_volume_backup import create_caddy_volume_backup
from scripts.check_caddy_volumes import validate as validate_volumes
from scripts.verify_backup_set import verify_set


CHUNK = 1024 * 1024
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)


def _signature(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_uid,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _check_new_directory(root: Path, cert_dir: Path, output: Path) -> None:
    if not output.is_absolute() or not output.name or output.name in (".", ".."):
        raise ValueError("Backup set output must be an absolute directory")

    parent = output.parent
    info = parent.lstat()

    if (
        not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.geteuid()
        or stat.S_IMODE(info.st_mode) != 0o700
        or parent.resolve(strict=True) != parent
    ):
        raise ValueError("Backup set parent must be a real owner-only 0700 directory")

    if output.exists() or output.is_symlink():
        raise FileExistsError("Backup set output already exists")

    for source in (root.resolve(strict=True), cert_dir.resolve(strict=True)):
        if parent == source or parent.is_relative_to(source):
            raise ValueError("Backup set must be outside installation and TLS directories")


def _directory_signature(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_mode)


def _check_identity(path: Path, expected) -> None:
    actual = path.lstat()
    if (
        _directory_signature(actual) != _directory_signature(expected)
        or not stat.S_ISDIR(actual.st_mode)
        or actual.st_uid != os.geteuid()
        or stat.S_IMODE(actual.st_mode) != 0o700
        or path.resolve(strict=True) != path
    ):
        raise RuntimeError("Backup set directory changed")


def _check_compose_project(root: Path, project: str) -> None:
    """Prevent pairing files from one Compose project with others' volumes."""
    command = [
        "docker",
        "compose",
        "--project-directory",
        str(root),
        "--env-file",
        str(root / ".env"),
        "-f",
        str(root / "docker-compose.yml"),
        "config",
        "--format",
        "json",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("Docker Compose project could not be verified") from exc

    if result.returncode != 0:
        raise RuntimeError("Docker Compose project query failed")

    try:
        config = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid Docker Compose project metadata") from exc

    if not isinstance(config, dict) or config.get("name") != project:
        raise ValueError("Backup project does not match Docker Compose project")


def _archive_record(path: Path) -> dict:
    fd = os.open(path, FILE_FLAGS)
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(source.fileno())
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or stat.S_IMODE(before.st_mode) != 0o600
        ):
            raise ValueError("Backup set archive must be a private owner-only file")

        digest = hashlib.sha256()
        size = 0
        while chunk := source.read(CHUNK):
            digest.update(chunk)
            size += len(chunk)

        if (
            size != before.st_size
            or _signature(os.fstat(source.fileno())) != _signature(before)
            or _signature(path.lstat()) != _signature(before)
        ):
            raise RuntimeError("Backup archive changed during manifest hashing")

        return {"name": path.name, "size": size, "sha256": digest.hexdigest()}


def create_backup_set(
    root: Path,
    cert_dir: Path,
    project: str,
    image: str,
    output_dir: Path,
) -> tuple[int, int]:
    """Create separate file/volume archives then verify and publish their manifest."""
    root, cert_dir, output_dir = map(Path, (root, cert_dir, output_dir))
    if not root.is_absolute() or not cert_dir.is_absolute():
        raise ValueError("Installation and TLS paths must be absolute")

    _check_new_directory(root, cert_dir, output_dir)

    if not image or image.startswith("-"):
        raise ValueError("A locally cached Docker image is required")

    # All checks must pass before creating even an empty backup directory.
    _check_compose_project(root, project)
    check_services_stopped(root)
    validate_volumes(project)

    output_dir.mkdir(mode=0o700)
    directory_info = output_dir.lstat()
    _check_identity(output_dir, directory_info)

    files = output_dir / "files.tar.gz"
    volumes = output_dir / "volumes.tar.gz"
    manifest = output_dir / "backup-set.json"
    temporary = output_dir / ".backup-set.json.partial"

    try:
        create_backup(root, cert_dir, files)
        _check_identity(output_dir, directory_info)
        create_caddy_volume_backup(project, image, root, cert_dir, volumes)
        _check_identity(output_dir, directory_info)

        # A postflight checks Compose identity, status and volume identities.
        _check_compose_project(root, project)
        check_services_stopped(root)
        validate_volumes(project)

        record = {
            "format": "garminsupla-backup-set/v1",
            "set_id": secrets.token_hex(16),
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "source_project": project,
            "complete_system_backup": False,
            "offline_consistency_proven": False,
            "archives": {
                "files": _archive_record(files),
                "caddy_volumes": _archive_record(volumes),
            },
        }
        encoded = json.dumps(record, indent=2).encode("utf-8")
        _check_identity(output_dir, directory_info)

        fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
        )
        with os.fdopen(fd, "wb") as destination:
            destination.write(encoded)
            destination.flush()
            os.fsync(destination.fileno())

        # Only publish after full read-only verification of both archives.
        verified = verify_set(temporary)
        _check_identity(output_dir, directory_info)
        _check_compose_project(root, project)
        check_services_stopped(root)
        validate_volumes(project)

        os.link(temporary, manifest)
        temporary.unlink()
        directory_fd = os.open(output_dir, DIR_FLAGS)
        try:
            if _directory_signature(os.fstat(directory_fd)) != _directory_signature(directory_info):
                raise RuntimeError("Backup set directory changed during publication")
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return verified
    finally:
        # Archives are deliberately preserved on failure for manual inspection.
        # A failed set will have no published manifest unless publication itself failed.
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--cert-dir", required=True, type=Path)
    parser.add_argument("--project", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--confirm-stopped", action="store_true")
    args = parser.parse_args()

    if not args.confirm_stopped:
        print("ERROR: --confirm-stopped is required", file=sys.stderr)
        return 1

    try:
        count_files, count_volumes = create_backup_set(
            args.root, args.cert_dir, args.project, args.image, args.output_dir
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("INFO: inspect any new private output directory before retrying", file=sys.stderr)
        return 1

    print(f"OK: verified backup set: {count_files} files, {count_volumes} Caddy volumes")
    print("INFO: backup set is not a complete system backup; offline consistency unproven")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

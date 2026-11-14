"""Read-only preflight for isolated GarminSupla file restoration.

Checks a verified file backup and an unused, private restore target.
Does not create directories, extract files or contact Docker.
"""

import argparse
import os
import re
import stat
import sys

from pathlib import Path

from scripts.verify_file_backup import verify_archive


TARGET_PATTERN = r"gsrestore[a-z0-9]{8,32}"


def check_target(target: Path) -> Path:
    """Require a new target below a real owner-only directory."""

    target = Path(target)

    if not target.is_absolute():
        raise ValueError(
            "Restore target must be an absolute path"
        )

    if re.fullmatch(
        TARGET_PATTERN,
        target.name,
    ) is None:
        raise ValueError(
            "Restore target name must be gsrestore "
            "followed by 8-32 lowercase letters or digits"
        )

    parent = target.parent

    try:
        info = parent.lstat()
        resolved = parent.resolve(
            strict=True
        )

    except (
        OSError,
        RuntimeError,
    ) as exc:
        raise ValueError(
            "Restore parent directory is unavailable"
        ) from exc

    if (
        not stat.S_ISDIR(info.st_mode)
        or resolved != parent
    ):
        raise ValueError(
            "Restore parent must be a real directory "
            "without symlinks or path traversal"
        )

    if (
        info.st_uid != os.geteuid()
        or stat.S_IMODE(info.st_mode) != 0o700
    ):
        raise ValueError(
            "Restore parent must be owned by current user "
            "with permissions 0700"
        )

    try:
        target.lstat()

    except FileNotFoundError:
        return target

    raise FileExistsError(
        "Restore target already exists"
    )


def validate_restore_target(
    archive: Path,
    target: Path,
) -> tuple[Path, int]:
    """Verify archive first, then inspect target metadata."""

    count = verify_archive(
        Path(archive)
    )

    destination = check_target(
        Path(target)
    )

    return destination, count


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--archive",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--target",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    try:
        target, count = validate_restore_target(
            args.archive,
            args.target,
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
        f"OK: verified {count} backup files"
    )
    print(
        "OK: isolated restore destination available"
    )
    print(
        f"INFO: target name {target.name}"
    )
    print(
        "INFO: read-only preflight; no files restored "
        "and no directories created"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

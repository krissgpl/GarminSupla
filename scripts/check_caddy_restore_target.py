"""Read-only preflight for an isolated Caddy volume restore target."""

import argparse
import re
import sys
from pathlib import Path

from scripts.check_caddy_volumes import VOLUMES, _docker
from scripts.verify_caddy_volume_backup import verify_archive


TARGET_PATTERN = r"gsrestore[a-z0-9]{8,32}"


def check_target(source_project: str, target_project: str):
    if re.fullmatch(TARGET_PATTERN, target_project) is None:
        raise ValueError(
            "Restore target must be a new gsrestore project "
            "with an 8-32 character lowercase suffix"
        )

    if source_project == target_project:
        raise ValueError(
            "Restore target must differ from source project"
        )

    expected = tuple(
        f"{target_project}_{short_name}"
        for short_name in VOLUMES
    )

    all_volumes = set(
        _docker(
            "volume",
            "ls",
            "--format",
            "{{.Name}}",
        ).splitlines()
    )

    if any(name in all_volumes for name in expected):
        raise RuntimeError(
            "Restore target volume already exists"
        )

    project_volumes = _docker(
        "volume",
        "ls",
        "--format",
        "{{.Name}}",
        "--filter",
        f"label=com.docker.compose.project={target_project}",
    )

    if project_volumes:
        raise RuntimeError(
            "Restore target project already owns Docker volumes"
        )

    containers = _docker(
        "ps",
        "-a",
        "-q",
        "--filter",
        f"label=com.docker.compose.project={target_project}",
    )

    if containers:
        raise RuntimeError(
            "Restore target project already has containers"
        )

    networks = _docker(
        "network",
        "ls",
        "--format",
        "{{.Name}}",
        "--filter",
        f"label=com.docker.compose.project={target_project}",
    )

    if networks:
        raise RuntimeError(
            "Restore target project already has networks"
        )

    return expected


def validate_restore_target(
    archive: Path,
    source_project: str,
    target_project: str,
):
    # Verify all archive contents before querying Docker.
    verify_archive(archive, source_project)

    return check_target(
        source_project,
        target_project,
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--archive",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--source-project",
        required=True,
    )
    parser.add_argument(
        "--target-project",
        required=True,
    )

    args = parser.parse_args()

    try:
        names = validate_restore_target(
            args.archive,
            args.source_project,
            args.target_project,
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

    print("OK: archive verified")
    print("OK: restore target project is unused")
    print(
        f"OK: {len(names)} destination volume names available"
    )
    print(
        "INFO: read-only restore preflight; "
        "no Docker resources created"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

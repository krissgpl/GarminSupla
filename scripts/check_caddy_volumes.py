"""Read-only preflight for offline Caddy Docker volume backup.

Inspect Docker metadata only; never read volume contents.
"""

import argparse
import json
import re
import subprocess
import sys


VOLUMES = (
    "garminsupla_caddy_data",
    "garminsupla_caddy_config",
)


def _docker(*args: str) -> str:
    try:
        result = subprocess.run(
            ["docker", *args],
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
            "Docker metadata query unavailable"
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "Docker metadata query failed"
        )

    return result.stdout.strip()


def validate(project: str) -> tuple[str, ...]:
    """Fail closed unless both expected volumes are offline."""

    if re.fullmatch(
        r"[a-z][a-z0-9_-]*",
        project,
    ) is None:
        raise ValueError(
            "Invalid Docker Compose project name"
        )

    names = []

    for volume in VOLUMES:
        name = f"{project}_{volume}"

        try:
            inspected = json.loads(
                _docker(
                    "volume",
                    "inspect",
                    name,
                )
            )
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Invalid Docker volume metadata"
            ) from exc

        if (
            not isinstance(inspected, list)
            or len(inspected) != 1
            or not isinstance(inspected[0], dict)
        ):
            raise RuntimeError(
                "Unexpected Docker volume metadata"
            )

        info = inspected[0]
        labels = info.get("Labels") or {}

        if not isinstance(labels, dict):
            raise RuntimeError(
                "Invalid Docker volume labels"
            )

        if info.get("Name") != name:
            raise RuntimeError(
                "Docker volume name mismatch"
            )

        if (
            labels.get(
                "com.docker.compose.project"
            )
            != project
        ):
            raise RuntimeError(
                "Docker volume project label mismatch"
            )

        if (
            labels.get(
                "com.docker.compose.volume"
            )
            != volume
        ):
            raise RuntimeError(
                "Docker volume service label mismatch"
            )

        if (
            info.get("Driver") != "local"
            or info.get("Scope") != "local"
            or info.get("Options") not in (None, {})
        ):
            raise RuntimeError(
                "Unexpected Docker volume driver or options"
            )

        names.append(name)

    # Check the entire Compose project, not only Caddy.
    # A running service means this is not an offline window.

    running = _docker(
        "ps",
        "-q",
        "--filter",
        f"label=com.docker.compose.project={project}",
    )

    if running:
        raise RuntimeError(
            "Compose project has running containers; "
            "offline backup refused"
        )

    # Also reject unrelated containers using these volumes.

    for name in names:
        users = _docker(
            "ps",
            "-q",
            "--filter",
            f"volume={name}",
        )

        if users:
            raise RuntimeError(
                "Caddy volume is used by a running container; "
                "offline backup refused"
            )

    return tuple(names)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--project",
        required=True,
        help="Docker Compose project name",
    )

    args = parser.parse_args()

    try:
        names = validate(args.project)
    except (ValueError, RuntimeError) as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        "OK: Caddy volume metadata verified"
    )
    print(
        f"OK: {len(names)} expected local volumes found"
    )
    print(
        "OK: no running containers use the volumes"
    )
    print(
        "INFO: read-only preflight only; "
        "no backup created"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

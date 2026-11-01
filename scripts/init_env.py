import argparse
import os
import secrets
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT_DIR / ".env",
    )

    parser.add_argument(
        "--run-uid",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--run-gid",
        type=int,
        default=None,
    )

    args = parser.parse_args()
    target = args.output

    if target.exists() or target.is_symlink():
        print(f"Existing configuration preserved: {target}")
        return

    if (args.run_uid is None) != (args.run_gid is None):
        parser.error(
            "--run-uid and --run-gid must be provided together."
        )

    if args.run_uid is None:
        run_uid = os.getuid()
        run_gid = os.getgid()
    else:
        run_uid = args.run_uid
        run_gid = args.run_gid

    if run_uid <= 0 or run_gid <= 0:
        parser.error(
            "Non-root UID and GID must be positive. "
            "Run setup as a non-root user or explicitly "
            "provide --run-uid and --run-gid."
        )

    template = ROOT_DIR / ".env.example"

    excluded = (
        "ADMIN_SESSION_SECRET=",
        "GARMIN_SUPLA_RUN_UID=",
        "GARMIN_SUPLA_RUN_GID=",
    )

    lines = [
        line
        for line in template.read_text(
            encoding="utf-8"
        ).splitlines()
        if not line.startswith(excluded)
    ]

    lines.extend([
        f"GARMIN_SUPLA_RUN_UID={run_uid}",
        f"GARMIN_SUPLA_RUN_GID={run_gid}",
        "ADMIN_SESSION_SECRET=" + secrets.token_urlsafe(48),
    ])

    content = "\n".join(lines) + "\n"

    try:
        fd = os.open(
            target,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError:
        print(f"Existing configuration preserved: {target}")
        return

    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Configuration created: {target}")


if __name__ == "__main__":
    main()

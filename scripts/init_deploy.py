import argparse
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def create_from_template(
    source: Path,
    target: Path,
) -> None:
    """Create a deployment file without overwriting it."""

    content = source.read_bytes()

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        fd = os.open(
            target,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )

    except FileExistsError:
        print(f"Existing file preserved: {target}")
        return

    try:
        with os.fdopen(fd, "wb") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())

    except BaseException:
        target.unlink(missing_ok=True)
        raise

    print(f"Deployment file created: {target}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Initialize GarminSupla Docker deployment "
            "without overwriting existing files."
        )
    )

    parser.add_argument(
        "--target-dir",
        type=Path,
        default=ROOT_DIR,
    )

    args = parser.parse_args()

    target_dir = args.target_dir

    files = (
        (
            ROOT_DIR / "docker-compose.example.yml",
            target_dir / "docker-compose.yml",
        ),
        (
            ROOT_DIR / "deploy/caddy/Caddyfile.example",
            target_dir / "deploy/caddy/Caddyfile",
        ),
    )

    for source, target in files:
        create_from_template(
            source,
            target,
        )


if __name__ == "__main__":
    main()

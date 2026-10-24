
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
    args = parser.parse_args()

    target = args.output

    if target.exists():
        print(f"Existing configuration preserved: {target}")
        return

    template = ROOT_DIR / ".env.example"

    lines = [
        line
        for line in template.read_text(
            encoding="utf-8"
        ).splitlines()
        if not line.startswith("ADMIN_SESSION_SECRET=")
    ]

    lines.append(
        "ADMIN_SESSION_SECRET="
        + secrets.token_urlsafe(48)
    )

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

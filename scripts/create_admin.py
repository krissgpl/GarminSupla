from datetime import datetime, timezone
from getpass import getpass

from pwdlib import PasswordHash

from app.models.admin import AdminAccount
from app.stores.admin_store import AdminStore


def main() -> None:
    store = AdminStore()

    if store.exists():
        print("Administrator account already exists.")
        raise SystemExit(1)

    username = input("Admin username: ").strip()

    if not username:
        print("Username cannot be empty.")
        raise SystemExit(1)

    password = getpass("Admin password: ")
    password_confirm = getpass("Confirm password: ")

    if password != password_confirm:
        print("Passwords do not match.")
        raise SystemExit(1)

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        raise SystemExit(1)

    password_hash = PasswordHash.recommended()

    admin = AdminAccount(
        username=username,
        password_hash=password_hash.hash(password),
        created_at=datetime.now(timezone.utc).isoformat(),
        enabled=True,
    )

    store.save(admin)

    print()
    print("Administrator account created successfully.")
    print("Username:", admin.username)


if __name__ == "__main__":
    main()

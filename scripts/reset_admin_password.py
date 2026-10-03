from getpass import getpass

from pwdlib import PasswordHash

from app.models.admin import AdminAccount
from app.stores.admin_store import AdminStore


CONFIRMATION_TEXT = "RESET"


def reset_admin_password(
    store: AdminStore,
    admin: AdminAccount,
    new_password_hash: str,
) -> AdminAccount:
    """
    Atomically reset the administrator password.

    The supplied administrator snapshot binds the operation
    to the security state confirmed by the operator.
    """

    if not admin.enabled:
        raise ValueError(
            "Administrator account is disabled."
        )

    updated = store.reset_password(
        username=admin.username,
        expected_session_version=(
            admin.session_version
        ),
        expected_password_hash=(
            admin.password_hash
        ),
        new_password_hash=(
            new_password_hash
        ),
    )

    if updated is None:
        raise ValueError(
            "Administrator authentication state changed."
        )

    return updated


def main(
    store: AdminStore | None = None,
) -> None:
    """Run the local emergency administrator password reset."""

    if store is None:
        store = AdminStore()

    admin = store.load()

    if admin is None:
        print(
            "Administrator account does not exist."
        )
        raise SystemExit(1)

    if not admin.enabled:
        print(
            "Administrator account is disabled."
        )
        raise SystemExit(1)

    print()
    print("EMERGENCY ADMINISTRATOR PASSWORD RESET")
    print()
    print("Username:", admin.username)
    print()
    print(
        "This operation will:"
    )
    print(
        "- replace the administrator password,"
    )
    print(
        "- invalidate all existing administrator sessions."
    )
    print()
    print(
        "Two-factor authentication configuration "
        "will not be changed."
    )
    print()

    confirmation = input(
        f"Type {CONFIRMATION_TEXT} to continue: "
    ).strip()

    if confirmation != CONFIRMATION_TEXT:
        print()
        print("Password reset cancelled.")
        raise SystemExit(1)

    password = getpass(
        "New admin password: "
    )

    password_confirm = getpass(
        "Confirm new password: "
    )

    if password != password_confirm:
        print()
        print("Passwords do not match.")
        raise SystemExit(1)

    if len(password) < 12:
        print()
        print(
            "Password must contain at least 12 characters."
        )
        raise SystemExit(1)

    password_hash = PasswordHash.recommended()

    new_password_hash = password_hash.hash(
        password
    )

    try:
        reset_admin_password(
            store,
            admin,
            new_password_hash,
        )

    except ValueError:
        print()
        print(
            "Unable to reset the password because the "
            "administrator security state changed."
        )
        print(
            "Run the command again and verify "
            "the current state."
        )
        raise SystemExit(1) from None

    print()
    print(
        "Administrator password reset successfully."
    )
    print(
        "All previous administrator sessions "
        "have been invalidated."
    )
    print(
        "Sign in with the new administrator password."
    )
    print(
        "If two-factor authentication is enabled, "
        "it is still required."
    )


if __name__ == "__main__":
    main()

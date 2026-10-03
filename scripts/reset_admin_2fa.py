from app.models.admin import AdminAccount
from app.stores.admin_store import AdminStore


CONFIRMATION_TEXT = "RESET"


def reset_admin_2fa(
    store: AdminStore,
    admin: AdminAccount,
) -> AdminAccount:
    """
    Atomically reset administrator two-factor authentication.

    The supplied administrator snapshot binds the operation
    to the security state confirmed by the operator.
    """

    if (
        not admin.enabled
        or not admin.totp_enabled
        or not admin.totp_secret_encrypted
    ):
        raise ValueError(
            "Two-factor authentication is not enabled."
        )

    updated = store.disable_totp(
        username=admin.username,
        expected_session_version=(
            admin.session_version
        ),
        expected_encrypted_secret=(
            admin.totp_secret_encrypted
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
    """Run the local emergency administrator 2FA reset."""

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

    if (
        not admin.totp_enabled
        or not admin.totp_secret_encrypted
    ):
        print(
            "Two-factor authentication is not enabled."
        )
        raise SystemExit(1)

    print()
    print("EMERGENCY ADMINISTRATOR 2FA RESET")
    print()
    print("Username:", admin.username)
    print()
    print(
        "This operation will:"
    )
    print(
        "- disable administrator two-factor authentication,"
    )
    print(
        "- remove the TOTP secret,"
    )
    print(
        "- remove all remaining recovery codes,"
    )
    print(
        "- invalidate all existing administrator sessions."
    )
    print()
    print(
        "The administrator password will not be changed."
    )
    print()

    confirmation = input(
        f"Type {CONFIRMATION_TEXT} to continue: "
    ).strip()

    if confirmation != CONFIRMATION_TEXT:
        print()
        print("2FA reset cancelled.")
        raise SystemExit(1)

    try:
        reset_admin_2fa(
            store,
            admin,
        )

    except ValueError:
        print()
        print(
            "Unable to reset 2FA because the "
            "administrator security state changed."
        )
        print(
            "Run the command again and verify "
            "the current state."
        )
        raise SystemExit(1) from None

    print()
    print(
        "Administrator 2FA reset successfully."
    )
    print(
        "All previous administrator sessions "
        "have been invalidated."
    )
    print(
        "Sign in with the administrator password "
        "and configure 2FA again."
    )


if __name__ == "__main__":
    main()

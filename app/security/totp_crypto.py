from cryptography.fernet import Fernet, InvalidToken


class TotpSecretCipher:
    """Encrypt and decrypt administrator TOTP secrets."""

    def __init__(self, key: str):
        if not isinstance(key, str) or not key:
            raise ValueError(
                "Invalid TOTP encryption key."
            )

        try:
            self._fernet = Fernet(
                key.encode("ascii")
            )
        except (ValueError, UnicodeError):
            raise ValueError(
                "Invalid TOTP encryption key."
            ) from None

    def encrypt(self, secret: str) -> str:
        """Encrypt a TOTP secret before storing it."""

        if not isinstance(secret, str) or not secret:
            raise ValueError(
                "TOTP secret must not be empty."
            )

        return self._fernet.encrypt(
            secret.encode("utf-8")
        ).decode("ascii")

    def decrypt(self, encrypted_secret: str) -> str:
        """Decrypt a previously encrypted TOTP secret."""

        try:
            return self._fernet.decrypt(
                encrypted_secret.encode("ascii")
            ).decode("utf-8")

        except (
            InvalidToken,
            ValueError,
            UnicodeError,
        ):
            raise ValueError(
                "Unable to decrypt TOTP secret."
            ) from None

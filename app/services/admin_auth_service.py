import binascii
import hashlib
import hmac

import pyotp

from pwdlib import PasswordHash
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)

from app.config import settings
from app.models.admin import AdminAccount
from app.security.recovery_codes import (
    generate_recovery_codes,
    hash_recovery_code,
)
from app.security.totp_crypto import TotpSecretCipher
from app.security.totp_service import (
    generate_totp_secret,
    match_totp_counter,
)
from app.stores.admin_store import AdminStore


CSRF_CONTEXT = b"garminsupla-admin-csrf"

SESSION_SALT = "garminsupla-admin-session"
SESSION_MAX_AGE = 8 * 60 * 60

TOTP_CHALLENGE_SALT = "garminsupla-admin-totp-challenge"
TOTP_CHALLENGE_MAX_AGE = 5 * 60

TOTP_ENROLLMENT_SALT = "garminsupla-admin-totp-enrollment"
TOTP_ENROLLMENT_MAX_AGE = 10 * 60

TOTP_ISSUER = "GarminSupla"


class AdminAuthService:
    """Authenticate administrators and manage signed sessions."""

    def __init__(self):
        self._store = AdminStore()
        self._password_hash = PasswordHash.recommended()

        self._serializer = URLSafeTimedSerializer(
            settings.admin_session_secret,
            salt=SESSION_SALT,
        )

        self._totp_challenge_serializer = URLSafeTimedSerializer(
            settings.admin_session_secret,
            salt=TOTP_CHALLENGE_SALT,
        )

        self._totp_enrollment_serializer = URLSafeTimedSerializer(
            settings.admin_session_secret,
            salt=TOTP_ENROLLMENT_SALT,
        )

    def administrator_exists(self) -> bool:
        """Return True if administrator storage exists."""

        return self._store.exists()

    def verify_credentials(
        self,
        username: str,
        password: str,
    ) -> AdminAccount | None:
        """Verify administrator username and password."""

        admin = self._store.load()

        if admin is None:
            return None

        if not admin.enabled:
            return None

        if username != admin.username:
            return None

        if not self._password_hash.verify(
            password,
            admin.password_hash,
        ):
            return None

        return admin

    def create_totp_enrollment(
        self,
        admin: AdminAccount,
        password: str,
    ) -> tuple[str, str]:
        """
        Start administrator TOTP enrollment.

        Require password confirmation, generate a new
        TOTP secret, encrypt it, and return:

        - a short-lived signed enrollment token,
        - an otpauth provisioning URI.

        The pending secret is not persisted yet.
        """

        current = self._load_matching_admin(
            admin
        )

        if current is None:
            raise ValueError(
                "Administrator authentication state changed."
            )

        if (
            current.totp_enabled
            or current.totp_secret_encrypted is not None
        ):
            raise ValueError(
                "Two-factor authentication is already configured."
            )

        if (
            not isinstance(password, str)
            or not password
            or not self._password_hash.verify(
                password,
                current.password_hash,
            )
        ):
            raise ValueError(
                "Password confirmation failed."
            )

        encryption_key = settings.totp_encryption_key

        if not encryption_key:
            raise ValueError(
                "TOTP encryption key is unavailable."
            )

        secret = generate_totp_secret()

        try:
            cipher = TotpSecretCipher(
                encryption_key
            )

            encrypted_secret = cipher.encrypt(
                secret
            )

        except (
            ValueError,
            TypeError,
            binascii.Error,
        ):
            raise ValueError(
                "Unable to prepare TOTP enrollment."
            ) from None

        enrollment_token = (
            self._totp_enrollment_serializer.dumps(
                {
                    "username": current.username,
                    "session_version": (
                        current.session_version
                    ),
                    "encrypted_secret": (
                        encrypted_secret
                    ),
                }
            )
        )

        provisioning_uri = (
            pyotp.TOTP(
                secret
            ).provisioning_uri(
                name=current.username,
                issuer_name=TOTP_ISSUER,
            )
        )

        return (
            enrollment_token,
            provisioning_uri,
        )

    def confirm_totp_enrollment(
        self,
        enrollment_token: str,
        code: str,
    ) -> tuple[AdminAccount, list[str]]:
        """
        Confirm TOTP enrollment using the first authenticator code.

        Persist the encrypted secret and recovery-code hashes
        only after successful verification. Plaintext recovery
        codes are returned once and are never persisted.
        """

        if (
            not isinstance(enrollment_token, str)
            or not enrollment_token
        ):
            raise ValueError(
                "Invalid or expired TOTP enrollment."
            )

        try:
            payload = (
                self._totp_enrollment_serializer.loads(
                    enrollment_token,
                    max_age=TOTP_ENROLLMENT_MAX_AGE,
                )
            )

        except (
            BadSignature,
            SignatureExpired,
        ):
            raise ValueError(
                "Invalid or expired TOTP enrollment."
            ) from None

        if not isinstance(payload, dict):
            raise ValueError(
                "Invalid or expired TOTP enrollment."
            )

        username = payload.get(
            "username"
        )

        session_version = payload.get(
            "session_version"
        )

        encrypted_secret = payload.get(
            "encrypted_secret"
        )

        if (
            not isinstance(username, str)
            or not username
            or type(session_version) is not int
            or session_version < 0
            or not isinstance(encrypted_secret, str)
            or not encrypted_secret
        ):
            raise ValueError(
                "Invalid or expired TOTP enrollment."
            )

        current = self._store.load()

        if (
            current is None
            or not current.enabled
            or current.username != username
            or current.session_version != session_version
            or current.totp_enabled
            or current.totp_secret_encrypted is not None
        ):
            raise ValueError(
                "Administrator authentication state changed."
            )

        encryption_key = settings.totp_encryption_key

        if not encryption_key:
            raise ValueError(
                "TOTP encryption key is unavailable."
            )

        try:
            cipher = TotpSecretCipher(
                encryption_key
            )

            secret = cipher.decrypt(
                encrypted_secret
            )

            counter = match_totp_counter(
                secret,
                code,
            )

        except (
            ValueError,
            TypeError,
            binascii.Error,
        ):
            raise ValueError(
                "Invalid TOTP enrollment code."
            ) from None

        if counter is None:
            raise ValueError(
                "Invalid TOTP enrollment code."
            )

        (
            recovery_codes,
            recovery_code_hashes,
        ) = generate_recovery_codes()

        updated = self._store.enable_totp(
            username=username,
            expected_session_version=session_version,
            encrypted_secret=encrypted_secret,
            first_counter=counter,
            recovery_code_hashes=recovery_code_hashes,
        )

        if updated is None:
            raise ValueError(
                "Administrator authentication state changed."
            )

        return (
            updated,
            recovery_codes,
        )

    def disable_totp(
        self,
        admin: AdminAccount,
        password: str,
    ) -> AdminAccount:
        """
        Disable administrator TOTP after password confirmation.

        Successful disable removes all TOTP and recovery
        authentication material and invalidates existing sessions.
        """

        current = self._load_matching_admin(
            admin
        )

        if (
            current is None
            or not current.totp_enabled
            or not current.totp_secret_encrypted
        ):
            raise ValueError(
                "Two-factor authentication is not configured."
            )

        if (
            not isinstance(password, str)
            or not password
            or not self._password_hash.verify(
                password,
                current.password_hash,
            )
        ):
            raise ValueError(
                "Password confirmation failed."
            )

        updated = self._store.disable_totp(
            username=current.username,
            expected_session_version=(
                current.session_version
            ),
            expected_encrypted_secret=(
                current.totp_secret_encrypted
            ),
        )

        if updated is None:
            raise ValueError(
                "Administrator authentication state changed."
            )

        return updated

    def verify_totp_code(
        self,
        admin: AdminAccount,
        code: str,
    ) -> bool:
        """Verify and atomically consume a TOTP code."""

        current = self._store.load()

        if (
            current is None
            or not current.enabled
            or not current.totp_enabled
            or not admin.enabled
            or not admin.totp_enabled
            or not current.totp_secret_encrypted
            or not admin.totp_secret_encrypted
            or current.username != admin.username
            or current.session_version != admin.session_version
        ):
            return False

        if not hmac.compare_digest(
            current.password_hash,
            admin.password_hash,
        ):
            return False

        if not hmac.compare_digest(
            current.totp_secret_encrypted,
            admin.totp_secret_encrypted,
        ):
            return False

        encryption_key = settings.totp_encryption_key

        if not encryption_key:
            return False

        try:
            cipher = TotpSecretCipher(
                encryption_key
            )

            secret = cipher.decrypt(
                current.totp_secret_encrypted
            )

            counter = match_totp_counter(
                secret,
                code,
                last_used_counter=(
                    current.totp_last_used_counter
                ),
            )

        except (
            ValueError,
            TypeError,
            binascii.Error,
        ):
            return False

        if counter is None:
            return False

        return self._store.consume_totp_counter(
            username=current.username,
            expected_encrypted_secret=(
                current.totp_secret_encrypted
            ),
            counter=counter,
        )

    def _load_matching_admin(
        self,
        admin: AdminAccount,
    ) -> AdminAccount | None:
        """
        Reload the administrator and reject stale
        authentication/security state.
        """

        current = self._store.load()

        if (
            current is None
            or not current.enabled
            or not admin.enabled
            or current.username != admin.username
            or current.session_version != admin.session_version
            or current.totp_enabled != admin.totp_enabled
        ):
            return None

        if not hmac.compare_digest(
            current.password_hash,
            admin.password_hash,
        ):
            return None

        if current.totp_enabled:
            if (
                not current.totp_secret_encrypted
                or not admin.totp_secret_encrypted
            ):
                return None

            if not hmac.compare_digest(
                current.totp_secret_encrypted,
                admin.totp_secret_encrypted,
            ):
                return None

        return current

    def create_totp_challenge(
        self,
        admin: AdminAccount,
    ) -> str:
        """
        Create a short-lived signed challenge after
        successful password authentication.

        The challenge is not an authenticated session.
        """

        current = self._load_matching_admin(
            admin
        )

        if (
            current is None
            or not current.totp_enabled
            or not current.totp_secret_encrypted
        ):
            raise ValueError(
                "Two-factor authentication challenge unavailable."
            )

        return self._totp_challenge_serializer.dumps(
            {
                "username": current.username,
                "session_version": current.session_version,
            }
        )

    def verify_totp_challenge(
        self,
        token: str,
    ) -> AdminAccount | None:
        """
        Verify a short-lived TOTP challenge and return
        the current administrator account.
        """

        if not isinstance(token, str) or not token:
            return None

        try:
            payload = self._totp_challenge_serializer.loads(
                token,
                max_age=TOTP_CHALLENGE_MAX_AGE,
            )

        except (
            BadSignature,
            SignatureExpired,
        ):
            return None

        if not isinstance(payload, dict):
            return None

        username = payload.get(
            "username"
        )

        session_version = payload.get(
            "session_version"
        )

        if not isinstance(
            username,
            str,
        ):
            return None

        if type(session_version) is not int:
            return None

        admin = self._store.load()

        if (
            admin is None
            or not admin.enabled
            or not admin.totp_enabled
            or not admin.totp_secret_encrypted
            or admin.username != username
            or admin.session_version != session_version
        ):
            return None

        return admin

    def create_session(
        self,
        admin: AdminAccount,
        *,
        totp_code: str | None = None,
        recovery_code: str | None = None,
    ) -> str:
        """
        Create a signed administrator session.

        When two-factor authentication is enabled, require
        exactly one valid additional authentication factor:
        either TOTP or a one-time recovery code.
        """

        current = self._load_matching_admin(
            admin
        )

        if current is None:
            raise ValueError(
                "Administrator authentication state changed."
            )

        totp_verified = False

        if current.totp_enabled:
            supplied_factor_count = (
                int(totp_code is not None)
                + int(recovery_code is not None)
            )

            if supplied_factor_count != 1:
                raise ValueError(
                    "Additional authentication required."
                )

            if recovery_code is not None:
                try:
                    recovery_code_hash = (
                        hash_recovery_code(
                            recovery_code
                        )
                    )

                except ValueError:
                    raise ValueError(
                        "Additional authentication required."
                    ) from None

                updated = (
                    self._store.consume_recovery_code(
                        username=current.username,
                        expected_session_version=(
                            current.session_version
                        ),
                        expected_encrypted_secret=(
                            current.totp_secret_encrypted
                        ),
                        recovery_code_hash=(
                            recovery_code_hash
                        ),
                    )
                )

                if updated is None:
                    raise ValueError(
                        "Additional authentication required."
                    )

                current = updated
                totp_verified = True

            else:
                if not self.verify_totp_code(
                    admin,
                    totp_code,
                ):
                    raise ValueError(
                        "Additional authentication required."
                    )

                current = self._load_matching_admin(
                    admin
                )

                if (
                    current is None
                    or not current.totp_enabled
                ):
                    raise ValueError(
                        "Administrator authentication state changed."
                    )

                totp_verified = True

        elif (
            totp_code is not None
            or recovery_code is not None
        ):
            raise ValueError(
                "Unexpected additional authentication."
            )

        return self._serializer.dumps(
            {
                "username": current.username,
                "session_version":
                    current.session_version,
                "totp_verified": totp_verified,
            }
        )

    def verify_session(
        self,
        token: str,
    ) -> AdminAccount | None:
        """Verify a signed administrator session."""

        try:
            payload = self._serializer.loads(
                token,
                max_age=SESSION_MAX_AGE,
            )

        except (
            BadSignature,
            SignatureExpired,
        ):
            return None

        if not isinstance(payload, dict):
            return None

        username = payload.get(
            "username"
        )

        session_version = payload.get(
            "session_version"
        )

        if not isinstance(
            username,
            str,
        ):
            return None

        if type(session_version) is not int:
            return None

        admin = self._store.load()

        if (
            admin is None
            or not admin.enabled
            or admin.username != username
            or admin.session_version != session_version
        ):
            return None

        if (
            admin.totp_enabled
            and payload.get("totp_verified") is not True
        ):
            return None

        return admin

    def create_csrf_token(
        self,
        session_token: str,
    ) -> str:
        """Create a CSRF token bound to an administrator session."""

        return hmac.new(
            key=settings.admin_session_secret.encode(
                "utf-8"
            ),
            msg=(
                CSRF_CONTEXT
                + session_token.encode("utf-8")
            ),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def verify_csrf_token(
        self,
        session_token: str,
        csrf_token: str,
    ) -> bool:
        """Verify a CSRF token bound to an administrator session."""

        expected = self.create_csrf_token(
            session_token
        )

        return hmac.compare_digest(
            expected,
            csrf_token,
        )

from pwdlib import PasswordHash
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)

from app.config import settings
from app.models.admin import AdminAccount
from app.stores.admin_store import AdminStore


SESSION_SALT = "garminsupla-admin-session"
SESSION_MAX_AGE = 8 * 60 * 60


class AdminAuthService:
    """Authenticate administrators and manage signed sessions."""

    def __init__(self):
        self._store = AdminStore()
        self._password_hash = PasswordHash.recommended()

        self._serializer = URLSafeTimedSerializer(
            settings.admin_session_secret,
            salt=SESSION_SALT,
        )

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

    def create_session(
        self,
        admin: AdminAccount,
    ) -> str:
        """Create a signed administrator session."""

        return self._serializer.dumps(
            {
                "username": admin.username,
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

        except (BadSignature, SignatureExpired):
            return None

        username = payload.get("username")

        if not isinstance(username, str):
            return None

        admin = self._store.load()

        if admin is None:
            return None

        if not admin.enabled:
            return None

        if admin.username != username:
            return None

        return admin

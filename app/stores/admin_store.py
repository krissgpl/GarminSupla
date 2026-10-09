from contextlib import contextmanager
from json import JSONDecodeError
from pathlib import Path
from threading import Lock
from typing import Iterator

import fcntl
import hmac
import json
import logging
import os

from pydantic import ValidationError

from app.models.admin import AdminAccount


logger = logging.getLogger(__name__)

DEFAULT_ADMIN_PATH = "data/admin.json"


class AdminStore:
    """Persistent administrator account storage."""

    def __init__(
        self,
        path: str = DEFAULT_ADMIN_PATH,
    ):
        self.path = Path(path)
        self._lock = Lock()

    def exists(self) -> bool:
        """Return True if an administrator exists."""

        return self.path.exists()

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        """Lock storage across threads and Linux processes."""

        with self._lock:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            lock_path = Path(
                str(self.path) + ".lock"
            )

            fd = os.open(
                lock_path,
                os.O_CREAT | os.O_RDWR,
                0o600,
            )

            with os.fdopen(fd, "r+") as lock_file:
                fcntl.flock(
                    lock_file.fileno(),
                    fcntl.LOCK_EX,
                )

                try:
                    yield

                finally:
                    fcntl.flock(
                        lock_file.fileno(),
                        fcntl.LOCK_UN,
                    )

    def _write_unlocked(
        self,
        admin: AdminAccount,
    ) -> None:
        """Atomically replace administrator data."""

        tmp_path = self.path.with_suffix(
            ".tmp"
        )

        fd = os.open(
            tmp_path,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_TRUNC,
            0o600,
        )

        os.fchmod(
            fd,
            0o600,
        )

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                admin.model_dump(mode="json"),
                file,
                indent=4,
                ensure_ascii=False,
            )

            file.flush()
            os.fsync(
                file.fileno()
            )

        tmp_path.replace(
            self.path
        )

    def save(
        self,
        admin: AdminAccount,
    ) -> None:
        """Persist administrator account to disk."""

        with self._exclusive_lock():
            current = self.load()

            # A stale update must never reduce the session
            # version. Otherwise previously invalidated
            # administrator sessions could become valid again.

            if (
                current is not None
                and admin.session_version
                < current.session_version
            ):
                raise ValueError(
                    "Outdated administrator security settings."
                )

            # Preserve an already consumed TOTP counter
            # when an unrelated update uses older data.
            #
            # Resetting the counter is permitted when
            # TOTP is disabled or its secret changes.

            if (
                current is not None
                and current.username == admin.username
                and current.totp_enabled
                and admin.totp_enabled
                and current.totp_secret_encrypted
                and (
                    current.totp_secret_encrypted
                    == admin.totp_secret_encrypted
                )
                and (
                    current.totp_last_used_counter
                    is not None
                )
            ):
                proposed_counter = (
                    admin.totp_last_used_counter
                )

                if (
                    proposed_counter is None
                    or proposed_counter
                    < current.totp_last_used_counter
                ):
                    admin = admin.model_copy(
                        update={
                            "totp_last_used_counter":
                                current.totp_last_used_counter
                        }
                    )

            self._write_unlocked(
                admin
            )

    def enable_totp(
        self,
        username: str,
        expected_session_version: int,
        encrypted_secret: str,
        first_counter: int,
        recovery_code_hashes: list[str],
    ) -> AdminAccount | None:
        """
        Atomically enable administrator TOTP.

        Persist only recovery-code hashes. The first verified
        TOTP counter is consumed as part of activation.
        """

        if (
            not isinstance(username, str)
            or not username
            or type(expected_session_version) is not int
            or expected_session_version < 0
            or not isinstance(encrypted_secret, str)
            or not encrypted_secret
            or type(first_counter) is not int
            or first_counter < 0
            or not isinstance(
                recovery_code_hashes,
                list,
            )
            or not recovery_code_hashes
            or any(
                not isinstance(value, str)
                or not value
                for value
                in recovery_code_hashes
            )
            or (
                len(set(recovery_code_hashes))
                != len(recovery_code_hashes)
            )
        ):
            return None

        with self._exclusive_lock():
            admin = self.load()

            if (
                admin is None
                or not admin.enabled
                or admin.username != username
                or (
                    admin.session_version
                    != expected_session_version
                )
                or admin.totp_enabled
                or admin.totp_secret_encrypted is not None
            ):
                return None

            updated = admin.model_copy(
                update={
                    "totp_enabled": True,
                    "totp_secret_encrypted":
                        encrypted_secret,
                    "recovery_code_hashes":
                        list(recovery_code_hashes),
                    "totp_last_used_counter":
                        first_counter,
                    "session_version":
                        admin.session_version + 1,
                }
            )

            self._write_unlocked(
                updated
            )

            return updated

    def disable_totp(
        self,
        username: str,
        expected_session_version: int,
        expected_encrypted_secret: str,
    ) -> AdminAccount | None:
        """
        Atomically disable administrator TOTP.

        Remove all TOTP and recovery authentication material
        and rotate session_version.
        """

        if (
            not isinstance(username, str)
            or not username
            or type(expected_session_version) is not int
            or expected_session_version < 0
            or not isinstance(
                expected_encrypted_secret,
                str,
            )
            or not expected_encrypted_secret
        ):
            return None

        with self._exclusive_lock():
            admin = self.load()

            if (
                admin is None
                or not admin.enabled
                or not admin.totp_enabled
                or admin.username != username
                or (
                    admin.session_version
                    != expected_session_version
                )
                or not admin.totp_secret_encrypted
            ):
                return None

            if not hmac.compare_digest(
                admin.totp_secret_encrypted,
                expected_encrypted_secret,
            ):
                return None

            updated = admin.model_copy(
                update={
                    "totp_enabled": False,
                    "totp_secret_encrypted": None,
                    "recovery_code_hashes": [],
                    "totp_last_used_counter": None,
                    "session_version":
                        admin.session_version + 1,
                }
            )

            self._write_unlocked(
                updated
            )

            return updated

    def reset_password(
        self,
        username: str,
        expected_session_version: int,
        expected_password_hash: str,
        new_password_hash: str,
    ) -> AdminAccount | None:
        """
        Atomically reset administrator password.

        Preserve two-factor authentication material and rotate
        session_version to invalidate existing sessions.
        """

        if (
            not isinstance(username, str)
            or not username
            or type(expected_session_version) is not int
            or expected_session_version < 0
            or not isinstance(
                expected_password_hash,
                str,
            )
            or not expected_password_hash
            or not isinstance(
                new_password_hash,
                str,
            )
            or not new_password_hash
        ):
            return None

        with self._exclusive_lock():
            admin = self.load()

            if (
                admin is None
                or not admin.enabled
                or admin.username != username
                or (
                    admin.session_version
                    != expected_session_version
                )
            ):
                return None

            if not hmac.compare_digest(
                admin.password_hash,
                expected_password_hash,
            ):
                return None

            updated = admin.model_copy(
                update={
                    "password_hash":
                        new_password_hash,
                    "session_version":
                        admin.session_version + 1,
                }
            )

            self._write_unlocked(
                updated
            )

            return updated

    def consume_totp_counter(
        self,
        username: str,
        expected_encrypted_secret: str,
        counter: int,
    ) -> bool:
        """Atomically consume a verified TOTP counter."""

        if (
            not isinstance(counter, int)
            or isinstance(counter, bool)
            or counter < 0
            or not expected_encrypted_secret
        ):
            return False

        with self._exclusive_lock():
            admin = self.load()

            if (
                admin is None
                or not admin.enabled
                or not admin.totp_enabled
                or admin.username != username
                or not admin.totp_secret_encrypted
            ):
                return False

            if not hmac.compare_digest(
                admin.totp_secret_encrypted,
                expected_encrypted_secret,
            ):
                return False

            last_used = (
                admin.totp_last_used_counter
            )

            if (
                last_used is not None
                and counter <= last_used
            ):
                return False

            updated = admin.model_copy(
                update={
                    "totp_last_used_counter": counter,
                }
            )

            self._write_unlocked(
                updated
            )

            return True

    def consume_recovery_code(
        self,
        username: str,
        expected_session_version: int,
        expected_encrypted_secret: str,
        recovery_code_hash: str,
    ) -> AdminAccount | None:
        """
        Atomically consume one administrator recovery code.

        Successful recovery authentication removes exactly
        one stored hash and rotates session_version.
        """

        if (
            not isinstance(username, str)
            or not username
            or type(expected_session_version) is not int
            or expected_session_version < 0
            or not isinstance(
                expected_encrypted_secret,
                str,
            )
            or not expected_encrypted_secret
            or not isinstance(
                recovery_code_hash,
                str,
            )
            or not recovery_code_hash
        ):
            return None

        with self._exclusive_lock():
            admin = self.load()

            if (
                admin is None
                or not admin.enabled
                or not admin.totp_enabled
                or admin.username != username
                or (
                    admin.session_version
                    != expected_session_version
                )
                or not admin.totp_secret_encrypted
            ):
                return None

            if not hmac.compare_digest(
                admin.totp_secret_encrypted,
                expected_encrypted_secret,
            ):
                return None

            matched_index = None

            for index, stored_hash in enumerate(
                admin.recovery_code_hashes
            ):
                if hmac.compare_digest(
                    stored_hash,
                    recovery_code_hash,
                ):
                    matched_index = index
                    break

            if matched_index is None:
                return None

            remaining_hashes = list(
                admin.recovery_code_hashes
            )

            del remaining_hashes[
                matched_index
            ]

            updated = admin.model_copy(
                update={
                    "recovery_code_hashes":
                        remaining_hashes,
                    "session_version":
                        admin.session_version + 1,
                }
            )

            self._write_unlocked(
                updated
            )

            return updated

    def load(self) -> AdminAccount | None:
        """Load administrator account."""

        if not self.exists():
            return None

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(
                    file
                )

            if not isinstance(
                data,
                dict,
            ):
                logger.error(
                    "Administrator configuration is invalid."
                )

                return None

            missing_fields = (
                set(AdminAccount.model_fields)
                - set(data)
            )

            if missing_fields:
                logger.error(
                    "Administrator configuration is incomplete. "
                    "Missing fields: %s",
                    ", ".join(
                        sorted(missing_fields)
                    ),
                )

                return None

            return AdminAccount.model_validate(
                data
            )

        except (
            JSONDecodeError,
            ValidationError,
        ):
            logger.error(
                "Administrator configuration is invalid."
            )

            return None

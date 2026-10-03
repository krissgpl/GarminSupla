import base64
import hashlib
import hmac
import secrets

from app.config import settings


RECOVERY_CODE_COUNT = 10
RECOVERY_CODE_BYTES = 15
RECOVERY_CODE_RAW_LENGTH = 24

RECOVERY_CODE_CONTEXT = (
    b"garminsupla-admin-recovery-code-v1\x00"
)


def _normalize_recovery_code(
    code: str,
) -> str:
    """Normalize and validate a recovery code."""

    if not isinstance(code, str):
        raise ValueError(
            "Invalid recovery code."
        )

    normalized = (
        code.strip()
        .replace("-", "")
        .replace(" ", "")
        .upper()
    )

    if (
        len(normalized) != RECOVERY_CODE_RAW_LENGTH
        or not normalized.isascii()
        or any(
            character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
            for character in normalized
        )
    ):
        raise ValueError(
            "Invalid recovery code."
        )

    return normalized


def hash_recovery_code(
    code: str,
) -> str:
    """
    Hash a high-entropy recovery code with a keyed digest.

    Only this digest is persisted.
    """

    normalized = _normalize_recovery_code(
        code
    )

    digest = hmac.new(
        key=settings.admin_session_secret.encode(
            "utf-8"
        ),
        msg=(
            RECOVERY_CODE_CONTEXT
            + normalized.encode("ascii")
        ),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return f"v1${digest}"


def generate_recovery_codes(
) -> tuple[list[str], list[str]]:
    """
    Generate one-time administrator recovery codes.

    Return plaintext codes for one-time display together
    with hashes suitable for persistent storage.
    """

    codes: list[str] = []
    seen: set[str] = set()

    while len(codes) < RECOVERY_CODE_COUNT:
        raw = base64.b32encode(
            secrets.token_bytes(
                RECOVERY_CODE_BYTES
            )
        ).decode("ascii").rstrip("=")

        code = "-".join(
            raw[index:index + 4]
            for index in range(
                0,
                len(raw),
                4,
            )
        )

        if code in seen:
            continue

        seen.add(code)
        codes.append(code)

    hashes = [
        hash_recovery_code(code)
        for code in codes
    ]

    return codes, hashes

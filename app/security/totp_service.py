import hmac
import time

import pyotp


TOTP_INTERVAL_SECONDS = 30
TOTP_DIGITS = 6


def generate_totp_secret() -> str:
    """Generate a random 160-bit TOTP secret."""

    return pyotp.random_base32()


def match_totp_counter(
    secret: str,
    code: str,
    *,
    for_time: int | None = None,
    last_used_counter: int | None = None,
) -> int | None:
    """
    Verify a TOTP code and return its matching time counter.

    Accept the current 30-second interval and one interval
    before or after it.

    If last_used_counter is provided, reject codes from
    that interval or any earlier interval.

    The caller must atomically persist the accepted counter
    to provide replay protection across requests.
    """

    if (
        not isinstance(code, str)
        or len(code) != TOTP_DIGITS
        or not code.isascii()
        or not code.isdecimal()
    ):
        return None

    timestamp = (
        int(time.time())
        if for_time is None
        else for_time
    )

    if timestamp < 0:
        return None

    current_counter = (
        timestamp // TOTP_INTERVAL_SECONDS
    )

    totp = pyotp.TOTP(
        secret,
        digits=TOTP_DIGITS,
        interval=TOTP_INTERVAL_SECONDS,
    )

    for counter in (
        current_counter,
        current_counter - 1,
        current_counter + 1,
    ):
        if counter < 0:
            continue

        if (
            last_used_counter is not None
            and counter <= last_used_counter
        ):
            continue

        expected_code = totp.at(
            counter * TOTP_INTERVAL_SECONDS
        )

        if hmac.compare_digest(
            code,
            expected_code,
        ):
            return counter

    return None

import base64
import unittest

from app.security.totp_service import (
    generate_totp_secret,
    match_totp_counter,
)


RFC_SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"


class TotpServiceTests(unittest.TestCase):

    def test_generates_160_bit_secret(self):
        secret = generate_totp_secret()

        decoded = base64.b32decode(secret)

        self.assertEqual(
            len(secret),
            32,
        )

        self.assertEqual(
            len(decoded),
            20,
        )

    def test_verifies_rfc_test_vector(self):
        # RFC 6238, SHA-1, timestamp 59.
        # Eight-digit result: 94287082.
        # Six-digit result: 287082.

        counter = match_totp_counter(
            RFC_SECRET,
            "287082",
            for_time=59,
        )

        self.assertEqual(
            counter,
            1,
        )

    def test_allows_one_interval_clock_drift(self):
        # Code from interval 1.

        for timestamp in (29, 59, 60):
            with self.subTest(
                timestamp=timestamp
            ):
                self.assertEqual(
                    match_totp_counter(
                        RFC_SECRET,
                        "287082",
                        for_time=timestamp,
                    ),
                    1,
                )

    def test_rejects_code_outside_time_window(self):
        self.assertIsNone(
            match_totp_counter(
                RFC_SECRET,
                "287082",
                for_time=90,
            )
        )

    def test_accepts_code_with_leading_zero(self):
        # RFC 6238, timestamp 1111111109.
        # Eight-digit result: 07081804.
        # Six-digit result: 081804.

        counter = match_totp_counter(
            RFC_SECRET,
            "081804",
            for_time=1111111109,
        )

        self.assertEqual(
            counter,
            1111111109 // 30,
        )

    def test_rejects_incorrect_code(self):
        self.assertIsNone(
            match_totp_counter(
                RFC_SECRET,
                "000000",
                for_time=59,
            )
        )

    def test_rejects_invalid_code_format(self):
        invalid_codes = (
            "28708",
            "287082 ",
            "abcdef",
            "２８７０８２",
            287082,
            None,
        )

        for code in invalid_codes:
            with self.subTest(code=code):
                self.assertIsNone(
                    match_totp_counter(
                        RFC_SECRET,
                        code,
                        for_time=59,
                    )
                )

    def test_rejects_reused_totp_counter(self):
        # Counter 1 has already been used.

        result = match_totp_counter(
            RFC_SECRET,
            "287082",
            for_time=59,
            last_used_counter=1,
        )

        self.assertIsNone(result)

    def test_accepts_counter_newer_than_last_used(self):
        # Counter 0 was used previously.
        # The code from counter 1 is still valid.

        result = match_totp_counter(
            RFC_SECRET,
            "287082",
            for_time=59,
            last_used_counter=0,
        )

        self.assertEqual(
            result,
            1,
        )

    def test_rejects_previous_code_after_new_login(self):
        # Counter 1 has already been used.
        # Its code must be rejected even while the
        # clock-drift window still includes counter 1.

        self.assertIsNone(
            match_totp_counter(
                RFC_SECRET,
                "287082",
                for_time=60,
                last_used_counter=1,
            )
        )

        # A new code from counter 2 must be accepted.

        import pyotp

        new_code = pyotp.TOTP(
            RFC_SECRET
        ).at(60)

        self.assertEqual(
            match_totp_counter(
                RFC_SECRET,
                new_code,
                for_time=60,
                last_used_counter=1,
            ),
            2,
        )


if __name__ == "__main__":
    unittest.main()

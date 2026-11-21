import unittest

from app.security.admin_login_rate_limit import (
    AdminLoginRateLimiter,
    resolve_client_key,
)


class ClientIdentityTests(unittest.TestCase):

    def test_trusted_proxy_forwards_real_ip(self):
        key = resolve_client_key(
            "192.0.2.10",
            "198.51.100.123",
            frozenset({"192.0.2.10"}),
        )
        self.assertEqual(key, "198.51.100.123")

    def test_untrusted_peer_cannot_spoof_ip(self):
        key = resolve_client_key(
            "192.0.2.11",
            "198.51.100.123",
            frozenset({"192.0.2.10"}),
        )
        self.assertEqual(key, "192.0.2.11")

    def test_missing_forwarded_ip_uses_peer(self):
        key = resolve_client_key(
            "192.0.2.10",
            None,
            frozenset({"192.0.2.10"}),
        )
        self.assertEqual(key, "192.0.2.10")

    def test_invalid_forwarded_ip_uses_peer(self):
        key = resolve_client_key(
            "192.0.2.10",
            "198.51.100.123, 203.0.113.4",
            frozenset({"192.0.2.10"}),
        )
        self.assertEqual(key, "192.0.2.10")

    def test_unknown_peer_does_not_trust_header(self):
        key = resolve_client_key(
            None,
            "198.51.100.123",
            frozenset({"192.0.2.10"}),
        )
        self.assertEqual(key, "peer:unknown")

    def test_ipv6_is_normalized(self):
        key = resolve_client_key(
            "2001:db8::1",
            "2001:0db8:0000::2",
            frozenset({"2001:db8::1"}),
        )
        self.assertEqual(key, "2001:db8::2")


class AdminLoginRateLimiterTests(unittest.TestCase):

    def setUp(self):
        self.now = 1000.0
        self.limiter = AdminLoginRateLimiter(
            failure_limit=3,
            window_seconds=60,
            max_clients=4,
            clock=lambda: self.now,
        )

    def test_allows_attempts_before_limit(self):
        self.assertEqual(self.limiter.retry_after("ip-a"), 0)

        for _ in range(2):
            self.limiter.record_failure("ip-a")

        self.assertEqual(self.limiter.retry_after("ip-a"), 0)

    def test_blocks_after_failure_limit(self):
        for _ in range(3):
            self.limiter.record_failure("ip-a")

        self.assertEqual(
            self.limiter.retry_after("ip-a"),
            60,
        )

    def test_retry_after_counts_down(self):
        for _ in range(3):
            self.limiter.record_failure("ip-a")

        self.now += 59

        self.assertEqual(
            self.limiter.retry_after("ip-a"),
            1,
        )

    def test_window_expiration_restores_access(self):
        for _ in range(3):
            self.limiter.record_failure("ip-a")

        self.now += 60

        self.assertEqual(
            self.limiter.retry_after("ip-a"),
            0,
        )

    def test_other_client_is_not_blocked(self):
        for _ in range(3):
            self.limiter.record_failure("ip-a")

        self.assertGreater(
            self.limiter.retry_after("ip-a"),
            0,
        )
        self.assertEqual(
            self.limiter.retry_after("ip-b"),
            0,
        )

    def test_failure_counter_is_shared_by_stages(self):
        # The same client key will be used by password,
        # TOTP and recovery-code endpoint integrations.
        for stage in ("password", "totp", "recovery"):
            self.limiter.record_failure("same-client")

        self.assertEqual(
            self.limiter.retry_after("same-client"),
            60,
        )

    def test_memory_is_bounded(self):
        for index in range(10):
            self.limiter.record_failure(f"ip-{index}")

        self.assertLessEqual(
            len(self.limiter._failures),
            4,
        )

    def test_invalid_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            AdminLoginRateLimiter(failure_limit=0)

        with self.assertRaises(ValueError):
            AdminLoginRateLimiter(window_seconds=0)

        with self.assertRaises(ValueError):
            AdminLoginRateLimiter(max_clients=0)


if __name__ == "__main__":
    unittest.main()

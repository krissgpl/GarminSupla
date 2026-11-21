import unittest

from pydantic import ValidationError

from app.config import AppSettings


class AdminLoginProxySettingsTests(unittest.TestCase):

    def settings(self, **kwargs):
        return AppSettings(
            _env_file=None,
            admin_session_secret="unit-test-placeholder",
            **kwargs,
        )

    def test_disabled_limiter_allows_empty_proxy_list(self):
        settings = self.settings(
            admin_login_rate_limit_enabled=False,
            admin_login_trusted_proxy_ips="",
        )
        self.assertFalse(
            settings.admin_login_rate_limit_enabled
        )
        self.assertEqual(
            settings.admin_login_trusted_proxy_ips,
            "",
        )

    def test_enabled_limiter_requires_proxy(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips="",
            )

    def test_whitespace_only_proxy_is_rejected_when_enabled(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips="   ",
            )

    def test_valid_ipv4_proxy(self):
        settings = self.settings(
            admin_login_rate_limit_enabled=True,
            admin_login_trusted_proxy_ips="192.0.2.10",
        )
        self.assertEqual(
            settings.admin_login_trusted_proxy_ips,
            "192.0.2.10",
        )

    def test_ipv4_and_ipv6_are_normalized(self):
        settings = self.settings(
            admin_login_rate_limit_enabled=True,
            admin_login_trusted_proxy_ips=(
                " 192.0.2.10, 2001:0db8::1 "
            ),
        )
        self.assertEqual(
            settings.admin_login_trusted_proxy_ips,
            "192.0.2.10,2001:db8::1",
        )

    def test_invalid_ip_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips="not-an-ip",
            )

    def test_cidr_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips="192.0.2.0/24",
            )

    def test_empty_list_element_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips="192.0.2.10,",
            )

    def test_duplicate_ips_are_rejected(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips=(
                    "192.0.2.10,192.0.2.10"
                ),
            )

    def test_unspecified_address_is_rejected(self):
        for address in ("0.0.0.0", "::"):
            with self.subTest(address=address):
                with self.assertRaises(ValidationError):
                    self.settings(
                        admin_login_rate_limit_enabled=True,
                        admin_login_trusted_proxy_ips=address,
                    )

    def test_multicast_address_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips="224.0.0.1",
            )

    def test_more_than_sixteen_proxies_is_rejected(self):
        addresses = ",".join(
            f"192.0.2.{index}"
            for index in range(1, 18)
        )

        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=True,
                admin_login_trusted_proxy_ips=addresses,
            )

    def test_invalid_proxy_is_rejected_even_when_disabled(self):
        with self.assertRaises(ValidationError):
            self.settings(
                admin_login_rate_limit_enabled=False,
                admin_login_trusted_proxy_ips="invalid",
            )


if __name__ == "__main__":
    unittest.main()

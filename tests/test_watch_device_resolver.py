import unittest

from app.services.watch_device_resolver import (
    resolve_watch_model,
)


class WatchDeviceResolverTests(unittest.TestCase):

    def test_resolves_known_part_number(self):
        self.assertEqual(
            resolve_watch_model(
                "006-B4631-00"
            ),
            "fēnix 8 Pro",
        )

    def test_normalizes_part_number(self):
        self.assertEqual(
            resolve_watch_model(
                "  006-b4631-00  "
            ),
            "fēnix 8 Pro",
        )

    def test_returns_none_for_unknown_part_number(self):
        self.assertIsNone(
            resolve_watch_model(
                "006-B0000-00"
            )
        )

    def test_returns_none_for_none(self):
        self.assertIsNone(
            resolve_watch_model(
                None
            )
        )

    def test_returns_none_for_empty_part_number(self):
        self.assertIsNone(
            resolve_watch_model(
                ""
            )
        )

    def test_returns_none_for_whitespace_part_number(self):
        self.assertIsNone(
            resolve_watch_model(
                "   "
            )
        )


if __name__ == "__main__":
    unittest.main()

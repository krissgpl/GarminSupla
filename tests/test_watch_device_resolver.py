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

    def test_resolves_supported_current_generation_models(self):
        cases = {
            "006-B4315-00": "Forerunner 965",
            "006-B4426-00": "vívoactive 5",
            "006-B4532-00": "fēnix 8 Solar (47mm)",
            "006-B4533-00": "fēnix 8 Solar (51mm)",
            "006-B4534-00": "fēnix 8 AMOLED (43mm)",
            "006-B4536-00": "fēnix 8 AMOLED (47mm/51mm)",
            "006-B4565-00": "Forerunner 970",
            "006-B4625-00": "vívoactive 6",
            "006-B4631-00": "fēnix 8 Pro",
            "006-B4666-00": "fēnix E",
        }

        for part_number, expected_model in cases.items():
            with self.subTest(
                part_number=part_number
            ):
                self.assertEqual(
                    resolve_watch_model(
                        part_number
                    ),
                    expected_model,
                )

    def test_resolves_fenix_5_family(self):
        cases = {
            "006-B2544-00": "fēnix 5S",
            "006-B2797-00": "fēnix 5S",
            "006-B2900-00": "fēnix 5S Plus",
            "006-B3134-00": "fēnix 5S Plus",
            "006-B2604-00": "fēnix 5X",
            "006-B2798-00": "fēnix 5X",
            "006-B3111-00": "fēnix 5X Plus",
            "006-B3135-00": "fēnix 5X Plus",
        }

        for part_number, expected_model in cases.items():
            with self.subTest(
                part_number=part_number
            ):
                self.assertEqual(
                    resolve_watch_model(
                        part_number
                    ),
                    expected_model,
                )

    def test_resolves_fenix_6_family(self):
        cases = {
            "006-B3287-00": "fēnix 6S",
            "006-B3512-00": "fēnix 6S",
            "006-B3764-00": "fēnix 6S Solar",
            "006-B3768-00": "fēnix 6S Dual Power",

            "006-B3288-00": "fēnix 6S Pro",
            "006-B3513-00": "fēnix 6S Pro",
            "006-B3765-00": "fēnix 6S Pro Solar",
            "006-B3769-00": "fēnix 6S Pro Dual Power",

            "006-B3289-00": "fēnix 6",
            "006-B3514-00": "fēnix 6",
            "006-B3766-00": "fēnix 6 Solar",
            "006-B3770-00": "fēnix 6 Dual Power",

            "006-B3290-00": "fēnix 6 Pro",
            "006-B3515-00": "fēnix 6 Pro",
            "006-B3767-00": "fēnix 6 Pro Solar",
            "006-B3771-00": "fēnix 6 Pro Dual Power",

            "006-B3291-00": "fēnix 6X Pro",
            "006-B3516-00": "fēnix 6X Pro",
        }

        for part_number, expected_model in cases.items():
            with self.subTest(
                part_number=part_number
            ):
                self.assertEqual(
                    resolve_watch_model(
                        part_number
                    ),
                    expected_model,
                )

if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_caddy_restore_target import (
    check_target,
    validate_restore_target,
)


SOURCE = "gsarchive"
TARGET = "gsrestoreabc12345"


class RestoreTargetTests(unittest.TestCase):

    def setUp(self):
        self.existing_volumes = ""
        self.project_volumes = ""
        self.containers = ""
        self.networks = ""

    def docker(self, *args):
        if args[:2] == ("volume", "ls"):
            if "--filter" in args:
                return self.project_volumes
            return self.existing_volumes

        if args[:2] == ("ps", "-a"):
            return self.containers

        if args[:2] == ("network", "ls"):
            return self.networks

        raise AssertionError(
            f"Unexpected Docker query: {args}"
        )

    def check(self):
        with patch(
            "scripts.check_caddy_restore_target._docker",
            side_effect=self.docker,
        ):
            return check_target(SOURCE, TARGET)

    def test_unused_target_accepted(self):
        result = self.check()

        self.assertEqual(
            result,
            (
                TARGET + "_garminsupla_caddy_data",
                TARGET + "_garminsupla_caddy_config",
            ),
        )

    def test_invalid_target_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "gsrestore",
        ):
            check_target(
                SOURCE,
                "garminsupla",
            )

    def test_same_source_and_target_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "must differ",
        ):
            check_target(
                TARGET,
                TARGET,
            )

    def test_existing_destination_volume_rejected(self):
        self.existing_volumes = (
            TARGET + "_garminsupla_caddy_data"
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "volume already exists",
        ):
            self.check()

    def test_project_volume_rejected(self):
        self.project_volumes = (
            TARGET + "_unrelated_volume"
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "already owns Docker volumes",
        ):
            self.check()

    def test_stopped_container_rejected(self):
        self.containers = "stopped-container-id"

        with self.assertRaisesRegex(
            RuntimeError,
            "already has containers",
        ):
            self.check()

    def test_existing_network_rejected(self):
        self.networks = TARGET + "_default"

        with self.assertRaisesRegex(
            RuntimeError,
            "already has networks",
        ):
            self.check()

    def test_docker_failure_fails_closed(self):
        with patch(
            "scripts.check_caddy_restore_target._docker",
            side_effect=RuntimeError(
                "Docker metadata query failed"
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "query failed",
            ):
                check_target(
                    SOURCE,
                    TARGET,
                )

    def test_archive_verification_precedes_docker(self):
        with (
            patch(
                "scripts.check_caddy_restore_target.verify_archive",
                side_effect=ValueError(
                    "Invalid backup"
                ),
            ),
            patch(
                "scripts.check_caddy_restore_target._docker",
                side_effect=AssertionError(
                    "Docker should not be queried"
                ),
            ),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Invalid backup",
            ):
                validate_restore_target(
                    Path("/synthetic/archive.tar.gz"),
                    SOURCE,
                    TARGET,
                )

    def test_verified_archive_allows_target_check(self):
        with (
            patch(
                "scripts.check_caddy_restore_target.verify_archive",
                return_value=2,
            ) as verifier,
            patch(
                "scripts.check_caddy_restore_target._docker",
                side_effect=self.docker,
            ),
        ):
            result = validate_restore_target(
                Path("/synthetic/archive.tar.gz"),
                SOURCE,
                TARGET,
            )

            self.assertEqual(len(result), 2)
            verifier.assert_called_once()


if __name__ == "__main__":
    unittest.main()

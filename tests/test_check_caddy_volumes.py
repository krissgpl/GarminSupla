import json
import subprocess
import sys
import unittest

from pathlib import Path
from unittest.mock import patch

from scripts.check_caddy_volumes import (
    VOLUMES,
    validate,
)


ROOT_DIR = Path(__file__).resolve().parent.parent


class CheckCaddyVolumesTests(unittest.TestCase):

    def setUp(self):
        self.project = "gstest"
        self.running_project = False
        self.running_volume = None
        self.bad_label = False
        self.bad_driver = False
        self.bad_options = False

    def fake_docker(self, *args):
        if args[:2] == ("volume", "inspect"):
            name = args[2]
            volume = name.removeprefix(
                self.project + "_"
            )

            info = {
                "Name": name,
                "Driver": (
                    "other"
                    if self.bad_driver
                    else "local"
                ),
                "Scope": "local",
                "Options": (
                    {"device": "external"}
                    if self.bad_options
                    else None
                ),
                "Labels": {
                    "com.docker.compose.project": (
                        "wrong"
                        if self.bad_label
                        else self.project
                    ),
                    "com.docker.compose.volume":
                        volume,
                },
            }

            return json.dumps([info])

        if args[:2] == ("ps", "-q"):
            value = args[-1]

            if value.startswith(
                "label=com.docker.compose.project="
            ):
                return (
                    "running-project-container"
                    if self.running_project
                    else ""
                )

            if value.startswith("volume="):
                if (
                    self.running_volume
                    == value.removeprefix("volume=")
                ):
                    return "running-volume-container"

                return ""

        raise AssertionError(
            "Unexpected Docker query"
        )

    def check(self):
        with patch(
            "scripts.check_caddy_volumes._docker",
            side_effect=self.fake_docker,
        ):
            return validate(self.project)

    def test_correct_offline_volumes_pass(self):
        names = self.check()

        self.assertEqual(
            names,
            tuple(
                f"{self.project}_{name}"
                for name in VOLUMES
            ),
        )

    def test_running_project_is_rejected(self):
        self.running_project = True

        with self.assertRaisesRegex(
            RuntimeError,
            "offline backup refused",
        ):
            self.check()

    def test_running_volume_consumer_is_rejected(self):
        self.running_volume = (
            self.project + "_" + VOLUMES[0]
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "offline backup refused",
        ):
            self.check()

    def test_wrong_project_label_is_rejected(self):
        self.bad_label = True

        with self.assertRaisesRegex(
            RuntimeError,
            "project label mismatch",
        ):
            self.check()

    def test_unexpected_driver_is_rejected(self):
        self.bad_driver = True

        with self.assertRaisesRegex(
            RuntimeError,
            "driver or options",
        ):
            self.check()

    def test_external_volume_options_are_rejected(self):
        self.bad_options = True

        with self.assertRaisesRegex(
            RuntimeError,
            "driver or options",
        ):
            self.check()

    def test_docker_query_failure_fails_closed(self):
        with patch(
            "scripts.check_caddy_volumes._docker",
            side_effect=RuntimeError(
                "Docker metadata query failed"
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "query failed",
            ):
                validate(self.project)

    def test_invalid_project_name_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid Docker Compose project",
        ):
            validate("../other-project")

    def test_cli_requires_project_name(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.check_caddy_volumes",
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(
            result.returncode,
            0,
        )
        self.assertIn(
            "--project",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()

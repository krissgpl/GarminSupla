import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


class DockerignoreTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = ROOT_DIR / ".dockerignore"

        cls.rules = {
            line.strip()
            for line in path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
            and not line.lstrip().startswith("#")
        }

    def test_sensitive_files_are_excluded(self):
        required = {
            ".env",
            ".env.*",
            "data/",
            "docker-compose.yml",
            "deploy/caddy/Caddyfile",
            "deploy/caddy/secrets/",
            "**/*.pem",
            "**/*.key",
            "**/*.p12",
            "**/*.pfx",
        }

        self.assertTrue(
            required.issubset(self.rules),
            required - self.rules,
        )

    def test_environment_template_is_preserved(self):
        self.assertIn(
            "!.env.example",
            self.rules,
        )

        self.assertTrue(
            (ROOT_DIR / ".env.example").is_file()
        )

    def test_local_artifacts_are_excluded(self):
        required = {
            ".git/",
            "**/__pycache__/",
            "*.py[cod]",
            ".venv/",
            "venv/",
        }

        self.assertTrue(
            required.issubset(self.rules),
            required - self.rules,
        )


if __name__ == "__main__":
    unittest.main()

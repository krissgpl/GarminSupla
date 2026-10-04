import importlib
import unittest


class AppImportTests(unittest.TestCase):
    def test_application_imports(self):
        module = importlib.import_module(
            "app.main"
        )

        self.assertIsNotNone(
            module.app
        )


if __name__ == "__main__":
    unittest.main()

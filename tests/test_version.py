"""Version discovery must work in installed packages and source checkouts."""

from importlib.metadata import PackageNotFoundError
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch


VERSION_MODULE = Path(__file__).resolve().parents[1] / "psyflow" / "_version.py"


class TestVersion(unittest.TestCase):
    def test_installed_metadata_does_not_read_source_files(self):
        with patch("importlib.metadata.version", return_value="1.2.3") as metadata:
            with patch.object(Path, "read_text", side_effect=AssertionError("source read")):
                result = runpy.run_path(str(VERSION_MODULE))
        metadata.assert_called_once_with("psyflow")
        self.assertEqual(result["__version__"], "1.2.3")

    def test_source_checkout_fallback(self):
        with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
            with patch.object(Path, "read_text", return_value='version = "0.1.12"\n') as read:
                result = runpy.run_path(str(VERSION_MODULE))
        read.assert_called_once_with(encoding="utf-8")
        self.assertEqual(result["__version__"], "0.1.12")

    def test_missing_or_unreadable_source_does_not_break_import(self):
        for error in (FileNotFoundError(), PermissionError(), UnicodeError()):
            with self.subTest(error=type(error).__name__):
                with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
                    with patch.object(Path, "read_text", side_effect=error):
                        result = runpy.run_path(str(VERSION_MODULE))
                self.assertEqual(result["__version__"], "0+unknown")

    def test_missing_source_version_does_not_break_import(self):
        with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
            with patch.object(Path, "read_text", return_value="[project]\n"):
                result = runpy.run_path(str(VERSION_MODULE))
        self.assertEqual(result["__version__"], "0+unknown")


if __name__ == "__main__":
    unittest.main()

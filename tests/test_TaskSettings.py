"""Tests for psyflow.TaskSettings - add_subinfo edge cases."""

import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from psyflow.TaskSettings import TaskSettings


class TestAddSubinfoSavePath(unittest.TestCase):
    """add_subinfo() should fall back to the default output directory."""

    def _assert_default_output_dir(self, save_path):
        with tempfile.TemporaryDirectory() as td:
            fallback_dir = os.path.join(td, "outputs", "human")

            with patch("psyflow.TaskSettings.DEFAULT_SAVE_PATH", fallback_dir):
                settings = TaskSettings(save_path=save_path)

                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    settings.add_subinfo({"subject_id": "001"})

            self.assertEqual(settings.save_path, fallback_dir)
            self.assertTrue(os.path.isdir(fallback_dir))
            self.assertIn("Created", mock_out.getvalue())
            self.assertTrue(settings.log_file.startswith(fallback_dir))
            self.assertTrue(settings.res_file.startswith(fallback_dir))
            self.assertTrue(settings.json_file.startswith(fallback_dir))

    def test_none_save_path_uses_default_output_dir(self):
        self._assert_default_output_dir(None)

    def test_empty_save_path_uses_default_output_dir(self):
        self._assert_default_output_dir("")

    def test_existing_dir_prints_exists(self):
        with tempfile.TemporaryDirectory() as td:
            settings = TaskSettings(save_path=td)

            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                settings.add_subinfo({"subject_id": "001"})

            self.assertIn("already exists", mock_out.getvalue())

    def test_new_dir_is_created(self):
        with tempfile.TemporaryDirectory() as td:
            new_dir = os.path.join(td, "outputs", "human")
            settings = TaskSettings(save_path=new_dir)

            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                settings.add_subinfo({"subject_id": "001"})

            self.assertTrue(os.path.isdir(new_dir))
            self.assertIn("Created", mock_out.getvalue())


if __name__ == "__main__":
    unittest.main()

"""Tests for psyflow.TaskSettings — add_subinfo edge cases."""

import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from psyflow.TaskSettings import TaskSettings


class TestAddSubinfoSavePath(unittest.TestCase):
    """add_subinfo() should not claim a directory exists when save_path is None."""

    def test_none_save_path_does_not_print_exists(self):
        settings = TaskSettings(save_path=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            settings.add_subinfo({"subject_id": "001"})

        output = mock_out.getvalue()
        self.assertNotIn("already exists", output)

    def test_empty_save_path_does_not_print_exists(self):
        settings = TaskSettings(save_path="")

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            settings.add_subinfo({"subject_id": "001"})

        output = mock_out.getvalue()
        self.assertNotIn("already exists", output)

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

import sys
import unittest


class TestImport(unittest.TestCase):
    def test_import_psyflow_does_not_import_psychopy(self):
        # The package should be importable without pulling in PsychoPy by default.
        sys.modules.pop("psyflow", None)
        sys.modules.pop("psychopy", None)

        import psyflow  # noqa: F401

        self.assertNotIn("psychopy", sys.modules)


class TestTaskSettings(unittest.TestCase):
    def test_from_dict_sets_derived_fields(self):
        from psyflow.TaskSettings import TaskSettings

        s = TaskSettings.from_dict(
            {
                "total_blocks": 2,
                "total_trials": 5,
                "fullscreen": False,
            }
        )
        self.assertEqual(s.total_blocks, 2)
        self.assertEqual(s.total_trials, 5)
        # ceil(5/2) == 3
        self.assertEqual(s.trials_per_block, 3)


if __name__ == "__main__":
    unittest.main()


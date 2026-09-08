import sys
import subprocess
from pathlib import Path
import textwrap
import unittest


class TestImport(unittest.TestCase):
    def _assert_clean_import(self, code: str) -> None:
        # Do not evict modules used by other tests in the shared pytest process.
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(code)],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_import_psyflow_does_not_import_psychopy(self):
        # The package should be importable without pulling in PsychoPy by default.
        self._assert_clean_import("""
            import sys
            import psyflow
            assert "psychopy" not in sys.modules
        """)

    def test_import_psyflow_utils_does_not_import_psychopy(self):
        self._assert_clean_import("""
            import sys
            from psyflow.utils import resolve_deadline
            assert resolve_deadline([0.25, 0.5]) == 0.5
            assert "psychopy" not in sys.modules
            assert "psyflow.utils.display" not in sys.modules
            assert "psyflow.utils.experiment" not in sys.modules
        """)


class TestSimContextHelpers(unittest.TestCase):
    def test_set_trial_context_resolves_deadline_sequences(self):
        from psyflow.sim.context_helpers import set_trial_context

        class DummyUnit:
            def __init__(self) -> None:
                self.state: dict[str, object] | None = None

            def set_state(self, **kwargs):
                self.state = kwargs
                return kwargs

        unit = DummyUnit()
        result = set_trial_context(
            unit,
            trial_id=1,
            phase="target",
            deadline_s=[0.2, 0.5],
            valid_keys=["space"],
        )

        self.assertEqual(result["deadline_s"], 0.5)
        self.assertEqual(unit.state["deadline_s"], 0.5)


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


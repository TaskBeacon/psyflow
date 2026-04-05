import sys
import unittest


class TestImport(unittest.TestCase):
    def _clear_psyflow_and_psychopy_modules(self) -> None:
        for name in [
            module_name
            for module_name in list(sys.modules)
            if module_name == "psyflow"
            or module_name.startswith("psyflow.")
            or module_name == "psychopy"
            or module_name.startswith("psychopy.")
        ]:
            sys.modules.pop(name, None)

    def test_import_psyflow_does_not_import_psychopy(self):
        # The package should be importable without pulling in PsychoPy by default.
        self._clear_psyflow_and_psychopy_modules()

        import psyflow  # noqa: F401

        self.assertNotIn("psychopy", sys.modules)

    def test_import_psyflow_utils_does_not_import_psychopy(self):
        self._clear_psyflow_and_psychopy_modules()

        from psyflow.utils import resolve_deadline

        self.assertEqual(resolve_deadline([0.25, 0.5]), 0.5)
        self.assertNotIn("psychopy", sys.modules)
        self.assertNotIn("psyflow.utils.display", sys.modules)
        self.assertNotIn("psyflow.utils.experiment", sys.modules)


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


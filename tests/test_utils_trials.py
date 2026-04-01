"""Tests for psyflow.utils.trials — trial ID and deadline helpers."""

import importlib.util
import unittest

# Load the module directly from its file path to avoid the psyflow.utils
# __init__.py which eagerly imports psychopy-dependent modules.
_spec = importlib.util.spec_from_file_location(
    "psyflow.utils.trials",
    "psyflow/utils/trials.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

next_trial_id = _mod.next_trial_id
reset_trial_counter = _mod.reset_trial_counter
resolve_deadline = _mod.resolve_deadline
resolve_trial_id = _mod.resolve_trial_id


class TestTrialCounter(unittest.TestCase):
    """Global trial counter increment and reset."""

    def setUp(self):
        reset_trial_counter(0)

    def test_increments(self):
        self.assertEqual(next_trial_id(), 1)
        self.assertEqual(next_trial_id(), 2)
        self.assertEqual(next_trial_id(), 3)

    def test_reset_to_custom_start(self):
        reset_trial_counter(100)
        self.assertEqual(next_trial_id(), 101)


class TestResolveDeadline(unittest.TestCase):
    """resolve_deadline() scalar/list/tuple → float | None."""

    def test_int(self):
        self.assertEqual(resolve_deadline(5), 5.0)

    def test_float(self):
        self.assertEqual(resolve_deadline(1.5), 1.5)

    def test_list_returns_max(self):
        self.assertEqual(resolve_deadline([0.2, 0.5, 0.3]), 0.5)

    def test_tuple_returns_max(self):
        self.assertEqual(resolve_deadline((1, 3, 2)), 3.0)

    def test_empty_list_returns_none(self):
        self.assertIsNone(resolve_deadline([]))

    def test_none_returns_none(self):
        self.assertIsNone(resolve_deadline(None))

    def test_string_returns_none(self):
        self.assertIsNone(resolve_deadline("fast"))


class TestResolveTrialId(unittest.TestCase):
    """resolve_trial_id() from various input types."""

    def test_none_passthrough(self):
        self.assertIsNone(resolve_trial_id(None))

    def test_int_passthrough(self):
        self.assertEqual(resolve_trial_id(42), 42)

    def test_str_passthrough(self):
        self.assertEqual(resolve_trial_id("trial_1"), "trial_1")

    def test_callable(self):
        self.assertEqual(resolve_trial_id(lambda: 7), 7)

    def test_callable_returning_non_int_str_coerced(self):
        result = resolve_trial_id(lambda: 3.14)
        self.assertEqual(result, "3.14")

    def test_callable_exception_returns_none(self):
        def bad():
            raise ValueError("boom")
        self.assertIsNone(resolve_trial_id(bad))

    def test_object_with_histories(self):
        class FakeController:
            histories = {"A": [1, 2], "B": [3]}
        self.assertEqual(resolve_trial_id(FakeController()), 4)

    def test_unknown_type_coerced_to_str(self):
        self.assertEqual(resolve_trial_id(42.0), "42.0")


if __name__ == "__main__":
    unittest.main()

import unittest

from psyflow.TaskSettings import TaskSettings


class TestConditionWeights(unittest.TestCase):
    def test_resolve_from_mapping(self) -> None:
        settings = TaskSettings.from_dict(
            {
                "total_blocks": 1,
                "total_trials": 4,
                "conditions": ["AX", "AY", "BX", "BY"],
                "condition_weights": {"AX": 0.4, "AY": 0.1, "BX": 0.1, "BY": 0.4},
            }
        )
        weights = settings.resolve_condition_weights()
        self.assertEqual(weights, [0.4, 0.1, 0.1, 0.4])

    def test_resolve_from_list(self) -> None:
        settings = TaskSettings.from_dict(
            {
                "total_blocks": 1,
                "total_trials": 3,
                "conditions": ["A", "B", "C"],
                "condition_weights": [1, 2, 3],
            }
        )
        weights = settings.resolve_condition_weights()
        self.assertEqual(weights, [1.0, 2.0, 3.0])

    def test_none_returns_none(self) -> None:
        settings = TaskSettings.from_dict(
            {
                "total_blocks": 1,
                "total_trials": 2,
                "conditions": ["A", "B"],
            }
        )
        self.assertIsNone(settings.resolve_condition_weights())

    def test_invalid_missing_key_raises(self) -> None:
        settings = TaskSettings.from_dict(
            {
                "total_blocks": 1,
                "total_trials": 2,
                "conditions": ["A", "B"],
                "condition_weights": {"A": 1.0},
            }
        )
        with self.assertRaises(ValueError):
            settings.resolve_condition_weights()

    def test_invalid_non_positive_raises(self) -> None:
        settings = TaskSettings.from_dict(
            {
                "total_blocks": 1,
                "total_trials": 2,
                "conditions": ["A", "B"],
                "condition_weights": [1.0, 0.0],
            }
        )
        with self.assertRaises(ValueError):
            settings.resolve_condition_weights()


if __name__ == "__main__":
    unittest.main()

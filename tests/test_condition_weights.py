import unittest

from psyflow.utils.trials import resolve_condition_weights


class TestConditionWeights(unittest.TestCase):
    def test_resolve_from_mapping(self) -> None:
        conditions = ["AX", "AY", "BX", "BY"]
        raw = {"AX": 0.4, "AY": 0.1, "BX": 0.1, "BY": 0.4}
        weights = resolve_condition_weights(raw, conditions)
        self.assertEqual(weights, [0.4, 0.1, 0.1, 0.4])

    def test_resolve_from_list(self) -> None:
        weights = resolve_condition_weights([1, 2, 3], ["A", "B", "C"])
        self.assertEqual(weights, [1.0, 2.0, 3.0])

    def test_none_returns_none(self) -> None:
        self.assertIsNone(resolve_condition_weights(None, ["A", "B"]))

    def test_invalid_missing_key_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_condition_weights({"A": 1.0}, ["A", "B"])

    def test_invalid_non_positive_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_condition_weights([1.0, 0.0], ["A", "B"])


if __name__ == "__main__":
    unittest.main()

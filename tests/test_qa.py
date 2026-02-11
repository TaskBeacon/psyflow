import json
import tempfile
import unittest
from pathlib import Path


class TestQAStatic(unittest.TestCase):
    def test_contract_lint_requires_required_columns(self):
        from psyflow.qa.static import ContractInvalidError, contract_lint

        with self.assertRaises(ContractInvalidError):
            contract_lint({})

        with self.assertRaises(ContractInvalidError):
            contract_lint({"required_columns": []})

        # Minimal OK
        contract_lint({"required_columns": ["condition"]})


class TestQATrace(unittest.TestCase):
    def test_validate_trace_csv_required_columns_and_rt_invariants(self):
        from psyflow.qa.trace import validate_trace_csv

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "qa_trace.csv"
            p.write_text(
                "condition,target_rt,target_duration,target_key_press,target_response\n"
                "win,0.2,0.5,True,space\n"
                "lose,,0.5,False,\n",
                encoding="utf-8",
            )

            res = validate_trace_csv(p, required_columns=["condition"])
            self.assertEqual(res["errors"], [])

    def test_validate_events_planned_executed_mismatch(self):
        from psyflow.qa.trace import validate_events

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "qa_events.jsonl"
            p.write_text(
                json.dumps({"type": "trigger_planned", "code": 1}) + "\n"
                + json.dumps({"type": "trigger_executed", "code": 1}) + "\n"
                + json.dumps({"type": "trigger_planned", "code": 2}) + "\n",
                encoding="utf-8",
            )
            res = validate_events(p)
            self.assertTrue(res["errors"])


if __name__ == "__main__":
    unittest.main()

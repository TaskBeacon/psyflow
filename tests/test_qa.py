import json
import tempfile
import unittest
from pathlib import Path

try:
    import yaml as _yaml  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    _HAS_YAML = False
else:
    _HAS_YAML = True


class TestQAStatic(unittest.TestCase):
    def test_contract_lint_requires_required_columns(self):
        from psyflow.qa.static import ContractInvalidError, contract_lint

        with self.assertRaises(ContractInvalidError):
            contract_lint({})

        with self.assertRaises(ContractInvalidError):
            contract_lint({"required_columns": []})

        # Minimal OK
        contract_lint({"required_columns": ["condition"]})

    @unittest.skipUnless(_HAS_YAML, "pyyaml is not installed")
    def test_static_qa_reads_acceptance_from_config_qa(self):
        from psyflow.qa.static import static_qa

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg_dir = root / "config"
            cfg_dir.mkdir(parents=True, exist_ok=True)
            (cfg_dir / "config_qa.yaml").write_text(
                "\n".join(
                    [
                        "task:",
                        "  key_list: [space]",
                        "triggers:",
                        "  map:",
                        "    exp_onset: 1",
                        "qa:",
                        "  acceptance_criteria:",
                        "    required_columns: [condition]",
                        "    allowed_keys: [space]",
                        "    triggers_required: true",
                    ]
                ),
                encoding="utf-8",
            )

            out = static_qa(root)
            self.assertEqual(out["acceptance_source"], "config:qa.acceptance_criteria")
            self.assertEqual(Path(out["config_path"]), cfg_dir / "config_qa.yaml")


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

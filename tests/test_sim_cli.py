import json
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner


class TestSimCLI(unittest.TestCase):
    def test_sim_cli_success_writes_report(self):
        from psyflow.sim_cli import main as sim_main

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as td:
            result = runner.invoke(
                sim_main,
                [
                    td,
                    "--runtime-cmd",
                    'python -c "pass"',
                    "--output-dir",
                    "outputs/sim-test",
                    "--seed",
                    "7",
                    "--participant-id",
                    "sim007",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            report_path = Path(td) / "outputs" / "sim-test" / "sim_report.json"
            self.assertTrue(report_path.exists())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report.get("status"), "pass")
            self.assertEqual(report.get("mode"), "sim")
            self.assertEqual(report.get("session", {}).get("seed"), 7)

    def test_sim_cli_failure_writes_report(self):
        from psyflow.sim_cli import main as sim_main

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as td:
            result = runner.invoke(
                sim_main,
                [
                    td,
                    "--runtime-cmd",
                    'python -c "import sys;sys.exit(3)"',
                    "--output-dir",
                    "outputs/sim-test",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            report_path = Path(td) / "outputs" / "sim-test" / "sim_report.json"
            self.assertTrue(report_path.exists())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report.get("status"), "fail")
            self.assertEqual(report.get("mode"), "sim")


if __name__ == "__main__":
    unittest.main()

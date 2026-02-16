import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json

try:
    import yaml as _yaml  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    _HAS_YAML = False
else:
    _HAS_YAML = True


class TestTaskLauncher(unittest.TestCase):
    def test_run_task_shortcut_directory_with_config_and_passthrough(self):
        from psyflow.task_launcher import run_task_shortcut

        with tempfile.TemporaryDirectory() as td:
            task_dir = Path(td)
            main_py = task_dir / "main.py"
            main_py.write_text("print('ok')\n", encoding="utf-8")
            cfg = task_dir / "config" / "config_qa.yaml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text("qa: {}\n", encoding="utf-8")

            with patch("psyflow.task_launcher.subprocess.run") as run_mock:
                run_mock.return_value = SimpleNamespace(returncode=0)
                code = run_task_shortcut(
                    "qa",
                    [str(task_dir), "--config", "config/config_qa.yaml", "--seed", "7"],
                )

                self.assertEqual(code, 0)
                run_mock.assert_called_once()
                args, kwargs = run_mock.call_args
                cmd = args[0]
                self.assertEqual(cmd[2], "qa")
                self.assertIn("--config", cmd)
                self.assertIn(str(cfg.resolve()), cmd)
                self.assertTrue(str(main_py.resolve()) in cmd)
                self.assertEqual(kwargs.get("cwd"), str(task_dir.resolve()))

    def test_run_task_shortcut_accepts_main_py_path(self):
        from psyflow.task_launcher import run_task_shortcut

        with tempfile.TemporaryDirectory() as td:
            task_dir = Path(td)
            main_py = task_dir / "main.py"
            main_py.write_text("print('ok')\n", encoding="utf-8")

            with patch("psyflow.task_launcher.subprocess.run") as run_mock:
                run_mock.return_value = SimpleNamespace(returncode=0)
                code = run_task_shortcut("sim", [str(main_py)])

                self.assertEqual(code, 0)
                args, kwargs = run_mock.call_args
                cmd = args[0]
                self.assertEqual(cmd[2], "sim")
                self.assertTrue(str(main_py.resolve()) in cmd)
                self.assertEqual(kwargs.get("cwd"), str(task_dir.resolve()))

    def test_run_task_shortcut_errors_without_main_py(self):
        from psyflow.task_launcher import run_task_shortcut

        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(SystemExit):
                run_task_shortcut("human", [td])

    def test_maturity_update_promotes_without_downgrade(self):
        from psyflow.task_launcher import _update_taskbeacon_maturity

        with tempfile.TemporaryDirectory() as td:
            task_dir = Path(td)
            tb = task_dir / "taskbeacon.yaml"
            tb.write_text("id: T000000\nmaturity: piloted\n", encoding="utf-8")

            res1 = _update_taskbeacon_maturity(task_dir, target="smoke_tested")
            self.assertFalse(res1["updated"])
            self.assertEqual(res1["maturity"], "piloted")

            res2 = _update_taskbeacon_maturity(task_dir, target="validated")
            self.assertTrue(res2["updated"])
            self.assertEqual(res2["maturity"], "validated")
            self.assertIn("maturity: validated", tb.read_text(encoding="utf-8"))

    def test_readme_maturity_badge_is_replaced(self):
        from psyflow.task_launcher import _update_readme_maturity_badge

        with tempfile.TemporaryDirectory() as td:
            task_dir = Path(td)
            readme = task_dir / "README.md"
            readme.write_text(
                "# Demo Task\n\n"
                "![Maturity: draft](https://img.shields.io/badge/Maturity-draft-64748b?style=for-the-badge)\n",
                encoding="utf-8",
            )

            first = _update_readme_maturity_badge(task_dir, maturity="smoke_tested")
            self.assertTrue(first["updated"])
            text = readme.read_text(encoding="utf-8")
            self.assertIn("Maturity: smoke_tested", text)
            self.assertIn("style=flat-square", text)

            second = _update_readme_maturity_badge(task_dir, maturity="smoke_tested")
            self.assertFalse(second["updated"])

    def test_readme_maturity_badge_handles_non_utf8_readme(self):
        from psyflow.task_launcher import _update_readme_maturity_badge

        with tempfile.TemporaryDirectory() as td:
            task_dir = Path(td)
            readme = task_dir / "README.md"
            payload = "# Demo Task\n\nLegacy byte – line\n"
            readme.write_bytes(payload.encode("cp1252"))

            result = _update_readme_maturity_badge(task_dir, maturity="piloted")
            self.assertTrue(result["updated"])
            out = readme.read_text(encoding="cp1252")
            self.assertIn("Maturity: piloted", out)

    @unittest.skipUnless(_HAS_YAML, "pyyaml is not installed")
    def test_run_qa_shortcut_requires_acceptance_criteria(self):
        from psyflow.task_launcher import run_qa_shortcut

        with tempfile.TemporaryDirectory() as td:
            task_dir = Path(td)
            (task_dir / "main.py").write_text("print('ok')\n", encoding="utf-8")
            cfg = task_dir / "config" / "config_qa.yaml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text("qa:\n  output_dir: outputs/qa\n", encoding="utf-8")

            code = run_qa_shortcut([str(task_dir), "--config", "config/config_qa.yaml", "--no-maturity-update"])
            self.assertEqual(code, 1)

            report = task_dir / "outputs" / "qa" / "qa_report.json"
            self.assertTrue(report.exists())
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("failure_code"), "CONTRACT_INVALID")


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

try:
    import yaml as _yaml  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    _HAS_YAML = False
else:
    _HAS_YAML = True


@unittest.skipUnless(_HAS_YAML, "pyyaml is not installed")
class TestValidateCommand(unittest.TestCase):
    def _make_min_task(self, root: Path, *, contract_version: str = "v0.1.0") -> None:
        (root / "assets").mkdir(parents=True, exist_ok=True)
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "config").mkdir(parents=True, exist_ok=True)

        (root / "assets" / "README.md").write_text("# assets\n", encoding="utf-8")
        (root / ".gitignore").write_text("outputs/\n", encoding="utf-8")
        (root / "README.md").write_text(
            "\n".join(
                [
                    "# Demo Task",
                    "",
                    "| Field | Value |",
                    "|---|---|",
                    "| Name | Demo Task |",
                    "| Version | main (0.1.0) |",
                    "| Date Updated | 2026/02/16 |",
                    "| PsyFlow Version | 0.1.8 |",
                    "",
                    "## 1. Task Overview",
                    "demo",
                    "",
                    "## 2. Task Flow",
                    "### Block-Level Flow",
                    "| Step | Description |",
                    "|---|---|",
                    "| 1 | demo |",
                    "",
                    "### Trial-Level Flow",
                    "| Phase | Description |",
                    "|---|---|",
                    "| choice | demo |",
                    "",
                    "### Controller Logic",
                    "| Component | Logic |",
                    "|---|---|",
                    "| controller | demo |",
                    "",
                    "## 3. Configuration Summary",
                    "### a. Subject Info",
                    "| Field | Meaning |",
                    "|---|---|",
                    "| subject_id | demo |",
                    "",
                    "### b. Window Settings",
                    "| Parameter | Value |",
                    "|---|---|",
                    "| size | [1280, 720] |",
                    "",
                    "### c. Stimuli",
                    "| Name | Type | Description |",
                    "|---|---|---|",
                    "| fixation | text | demo |",
                    "",
                    "### d. Timing",
                    "| Phase | Duration |",
                    "|---|---|",
                    "| cue | 0.3 |",
                    "",
                    "## 4. Methods (for academic publication)",
                    "demo",
                ]
            ),
            encoding="utf-8",
        )
        (root / "CHANGELOG.md").write_text(
            "\n".join(
                [
                    "# CHANGELOG",
                    "",
                    "## [0.1.0] - 2026-02-16",
                    "",
                    "### Added",
                    "- init",
                ]
            ),
            encoding="utf-8",
        )
        (root / "taskbeacon.yaml").write_text(
            "\n".join(
                [
                    "id: T000000",
                    "slug: demo",
                    "title: Demo Task",
                    "acquisition: behavior",
                    "variant: baseline",
                    "maturity: draft",
                    "version:",
                    "  release_tag: ''",
                    "contracts:",
                    f"  psyflow_taps: {contract_version}",
                ]
            ),
            encoding="utf-8",
        )
        (root / "main.py").write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    "from psyflow import parse_task_run_options, context_from_config, runtime_context",
                    "MODES = ('human', 'qa', 'sim')",
                    "DEFAULT_CONFIG_BY_MODE = {'human': 'config/config.yaml', 'qa': 'config/config_qa.yaml', 'sim': 'config/config_scripted_sim.yaml'}",
                    "def run(options):",
                    "    return options",
                    "def main():",
                    "    task_root = Path('.')",
                    "    options = parse_task_run_options(task_root=task_root, description='x', default_config_by_mode=DEFAULT_CONFIG_BY_MODE, modes=MODES)",
                    "    run(options)",
                    "if __name__ == '__main__':",
                    "    main()",
                ]
            ),
            encoding="utf-8",
        )
        (root / "src" / "run_trial.py").write_text(
            "\n".join(
                [
                    "from psyflow import set_trial_context",
                    "def run_trial(win, kb, settings, condition):",
                    "    # cue",
                    "    x='cue'",
                    "    # anticipation",
                    "    set_trial_context(None, trial_id=1, phase='anticipation', deadline_s=0.2, valid_keys=['space'], condition_id='win', block_id='block_0', task_factors={})",
                    "    capture_response = True",
                    "    # target",
                    "    set_trial_context(None, trial_id=1, phase='target', deadline_s=0.2, valid_keys=['space'], condition_id='win', block_id='block_0', task_factors={})",
                    "    # feedback",
                    "    y='feedback'",
                ]
            ),
            encoding="utf-8",
        )
        (root / "config" / "config.yaml").write_text(
            "\n".join(
                [
                    "window:",
                    "  size: [1280, 720]",
                    "  units: deg",
                    "  screen: 0",
                    "  bg_color: gray",
                    "  fullscreen: false",
                    "task:",
                    "  task_name: demo",
                    "  total_blocks: 1",
                    "  total_trials: 10",
                    "  conditions: [win]",
                    "  key_list: [space]",
                    "  seed_mode: same_across_sub",
                    "timing:",
                    "  cue_duration: 0.3",
                    "stimuli:",
                    "  fixation: {type: text, text: '+'}",
                    "triggers:",
                    "  map: {exp_onset: 1}",
                    "  driver:",
                    "    type: serial_url",
                ]
            ),
            encoding="utf-8",
        )
        (root / "config" / "config_qa.yaml").write_text(
            "\n".join(
                [
                    "window:",
                    "  size: [1280, 720]",
                    "  units: deg",
                    "  screen: 0",
                    "  bg_color: gray",
                    "  fullscreen: false",
                    "task:",
                    "  task_name: demo",
                    "  total_blocks: 1",
                    "  total_trials: 2",
                    "  trial_per_block: 2",
                    "  conditions: [win]",
                    "  key_list: [space]",
                    "  seed_mode: same_across_sub",
                    "timing:",
                    "  cue_duration: 0.3",
                    "stimuli:",
                    "  fixation: {type: text, text: '+'}",
                    "triggers:",
                    "  map: {exp_onset: 1}",
                    "  driver:",
                    "    type: serial_url",
                    "qa:",
                    "  output_dir: outputs/qa",
                    "  acceptance_criteria:",
                    "    required_columns: [condition]",
                    "    expected_trial_count: 2",
                ]
            ),
            encoding="utf-8",
        )
        (root / "config" / "config_scripted_sim.yaml").write_text(
            "\n".join(
                [
                    "window:",
                    "  size: [1280, 720]",
                    "  units: deg",
                    "  screen: 0",
                    "  bg_color: gray",
                    "  fullscreen: false",
                    "task:",
                    "  task_name: demo",
                    "  total_blocks: 1",
                    "  total_trials: 2",
                    "  trial_per_block: 2",
                    "  conditions: [win]",
                    "  key_list: [space]",
                    "  seed_mode: same_across_sub",
                    "timing:",
                    "  cue_duration: 0.3",
                    "stimuli:",
                    "  fixation: {type: text, text: '+'}",
                    "triggers:",
                    "  map: {exp_onset: 1}",
                    "  driver:",
                    "    type: serial_url",
                    "sim:",
                    "  output_dir: outputs/sim",
                    "  seed: 1",
                    "  policy: warn",
                    "  responder:",
                    "    type: scripted",
                ]
            ),
            encoding="utf-8",
        )
        (root / "responders").mkdir(parents=True, exist_ok=True)
        (root / "responders" / "__init__.py").write_text("", encoding="utf-8")
        (root / "responders" / "task_sampler.py").write_text(
            "\n".join(
                [
                    "class TaskSamplerResponder:",
                    "    def start_session(self, session, rng):",
                    "        self.rng = rng",
                    "    def act(self, obs):",
                    "        return {'key': 'space', 'rt_s': 0.2}",
                ]
            ),
            encoding="utf-8",
        )
        (root / "config" / "config_sampler_sim.yaml").write_text(
            "\n".join(
                [
                    "window:",
                    "  size: [1280, 720]",
                    "  units: deg",
                    "  screen: 0",
                    "  bg_color: gray",
                    "  fullscreen: false",
                    "task:",
                    "  task_name: demo",
                    "  total_blocks: 1",
                    "  total_trials: 2",
                    "  trial_per_block: 2",
                    "  conditions: [win]",
                    "  key_list: [space]",
                    "  seed_mode: same_across_sub",
                    "timing:",
                    "  cue_duration: 0.3",
                    "stimuli:",
                    "  fixation: {type: text, text: '+'}",
                    "triggers:",
                    "  map: {exp_onset: 1}",
                    "  driver:",
                    "    type: serial_url",
                    "sim:",
                    "  output_dir: outputs/sim",
                    "  seed: 1",
                    "  policy: warn",
                    "  responder:",
                    "    type: responders.task_sampler:TaskSamplerResponder",
                ]
            ),
            encoding="utf-8",
        )

    def test_run_validator_no_fail_for_minimal_task(self):
        from psyflow.validate import run_validator

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_min_task(root, contract_version="v0.1.0")
            report = run_validator(root, contracts_version="v0.1.0")
            self.assertEqual(report["summary"]["fail"], 0)
            self.assertEqual(report["exit_code"], 0)

    def test_run_validator_fails_on_contract_version_mismatch(self):
        from psyflow.validate import run_validator

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_min_task(root, contract_version="v0.0.1")
            report = run_validator(root, contracts_version="v0.1.0")
            self.assertGreater(report["summary"]["fail"], 0)
            names = [r["name"] for r in report["results"] if r["status"] == "FAIL"]
            self.assertIn("taskbeacon", names)

    def test_warns_for_asset_backed_stimulus_without_path(self):
        from psyflow.validate import run_validator

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_min_task(root, contract_version="v0.1.0")
            (root / "config" / "config.yaml").write_text(
                "\n".join(
                    [
                        "window:",
                        "  size: [1280, 720]",
                        "  units: deg",
                        "  screen: 0",
                        "  bg_color: gray",
                        "  fullscreen: false",
                        "task:",
                        "  task_name: demo",
                        "  total_blocks: 1",
                        "  total_trials: 10",
                        "  trial_per_block: 1",
                        "  conditions: [win]",
                        "  key_list: [space]",
                        "  seed_mode: same_across_sub",
                        "timing:",
                        "  cue_duration: 0.3",
                        "stimuli:",
                        "  fixation: {type: text, text: '+'}",
                        "  cue_image:",
                        "    type: image",
                        "triggers:",
                        "  map: {exp_onset: 1}",
                        "  driver:",
                        "    type: serial_url",
                    ]
                ),
                encoding="utf-8",
            )
            report = run_validator(root, contracts_version="v0.1.0")
            cfg_rows = [r for r in report["results"] if r["name"] == "config_base"]
            self.assertEqual(len(cfg_rows), 1)
            self.assertEqual(cfg_rows[0]["status"], "WARN")
            joined = "\n".join(cfg_rows[0]["messages"])
            self.assertIn("asset-backed type", joined)

    def test_fails_when_custom_responder_missing_act(self):
        from psyflow.validate import run_validator

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_min_task(root, contract_version="v0.1.0")
            (root / "responders").mkdir(parents=True, exist_ok=True)
            (root / "responders" / "__init__.py").write_text("", encoding="utf-8")
            (root / "responders" / "bad.py").write_text(
                "\n".join(
                    [
                        "class BadResponder:",
                        "    def __init__(self):",
                        "        pass",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "config" / "config_sampler_sim.yaml").write_text(
                "\n".join(
                    [
                        "window:",
                        "  size: [1280, 720]",
                        "  units: deg",
                        "  screen: 0",
                        "  bg_color: gray",
                        "  fullscreen: false",
                        "task:",
                        "  task_name: demo",
                        "  total_blocks: 1",
                        "  total_trials: 2",
                        "  trial_per_block: 2",
                        "  conditions: [win]",
                        "  key_list: [space]",
                        "  seed_mode: same_across_sub",
                        "timing:",
                        "  cue_duration: 0.3",
                        "stimuli:",
                        "  fixation: {type: text, text: '+'}",
                        "triggers:",
                        "  map: {exp_onset: 1}",
                        "  driver:",
                        "    type: serial_url",
                        "sim:",
                        "  output_dir: outputs/sim",
                        "  seed: 1",
                        "  policy: warn",
                        "  responder:",
                        "    type: responders.bad:BadResponder",
                    ]
                ),
                encoding="utf-8",
            )
            report = run_validator(root, contracts_version="v0.1.0")
            rp_rows = [r for r in report["results"] if r["name"] == "responder_plugin"]
            self.assertEqual(len(rp_rows), 1)
            self.assertEqual(rp_rows[0]["status"], "FAIL")
            joined = "\n".join(rp_rows[0]["messages"])
            self.assertIn("missing required method: act()", joined)

    def test_gitignore_fails_without_outputs_or_data_rule(self):
        from psyflow.validate import run_validator

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_min_task(root, contract_version="v0.1.0")
            (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
            report = run_validator(root, contracts_version="v0.1.0")
            rows = [r for r in report["results"] if r["name"] == "gitignore"]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "FAIL")
            joined = "\n".join(rows[0]["messages"])
            self.assertIn("task_output_data", joined)


if __name__ == "__main__":
    unittest.main()

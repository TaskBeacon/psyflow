from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import click

from psyflow.qa import qa_artifact_paths
from psyflow.qa.report import FailureCode, QAReport
from psyflow.qa.static import StaticQAError, contract_lint, load_yaml, static_qa
from psyflow.qa.trace import validate_events, validate_trace_csv


@click.command()
@click.argument("task_dir", required=False, default=".")
@click.option("--output-dir", default="outputs/qa", show_default=True, help="QA output directory (relative to task_dir).")
@click.option("--config", "config_path", default=None, help="Path to config YAML (defaults to task_dir/config/config.yaml if present).")
@click.option("--acceptance", "acceptance_path", default=None, help="Path to acceptance_criteria.yaml (defaults to task_dir/acceptance_criteria.yaml if present).")
@click.option("--runtime-cmd", default=None, help="Optional command to run the task, e.g. \"python main.py\".")
@click.option("--enable-scaling", is_flag=True, help="Enable QA timing scaling for the runtime subprocess.")
@click.option("--timing-scale", default=1.0, type=float, show_default=True, help="Scale factor when --enable-scaling is set.")
@click.option("--min-frames", default=2, type=int, show_default=True, help="Minimum frames per stage in QA mode.")
@click.option("--strict", is_flag=True, help="Fail on invariant violations (instead of reporting them).")
@click.option(
    "--responder",
    type=click.Choice(["scripted", "null"], case_sensitive=False),
    default="scripted",
    show_default=True,
)
@click.option("--responder-key", default=None, help="Scripted responder key (default: first valid key).")
@click.option("--responder-rt", default=0.2, type=float, show_default=True, help="Scripted responder RT (seconds).")
@click.option("--responder-class", default=None, help="Import path for external responder class/factory.")
@click.option("--responder-kwargs", default=None, help="JSON kwargs for --responder-class.")
def main(
    task_dir: str,
    output_dir: str,
    config_path: str | None,
    acceptance_path: str | None,
    runtime_cmd: str | None,
    enable_scaling: bool,
    timing_scale: float,
    min_frames: int,
    strict: bool,
    responder: str,
    responder_key: str | None,
    responder_rt: float,
    responder_class: str | None,
    responder_kwargs: str | None,
):
    """Run static QA and (optionally) a runtime QA command for a task directory."""
    tdir = Path(task_dir).resolve()
    paths = qa_artifact_paths(tdir, output_dir=output_dir)
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(path: Path, obj: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, ensure_ascii=True, indent=2), encoding="utf-8")

    report = QAReport(
        status="pass",
        task_dir=str(tdir),
        mode="qa",
        artifacts={
            "output_dir": str(paths.output_dir),
            "qa_report": str(paths.report_json),
            "static_report": str(paths.static_report_json),
            "contract_report": str(paths.contract_report_json),
            "qa_trace": str(paths.trace_csv),
            "qa_events": str(paths.events_jsonl),
        },
    )

    # Contract report (C2): purely declarative checks based on acceptance_criteria.yaml.
    acc_path = acceptance_path or (tdir / "acceptance_criteria.yaml")
    if acc_path and Path(acc_path).exists():
        try:
            acc = load_yaml(acc_path)
            contract_lint(acc if isinstance(acc, dict) else {})
            contract = {
                "status": "pass",
                "task_dir": str(tdir),
                "acceptance_path": str(Path(acc_path)),
                "required_columns": acc.get("required_columns") if isinstance(acc, dict) else None,
                "expected_trial_count": acc.get("expected_trial_count") if isinstance(acc, dict) else None,
            }
        except StaticQAError as e:
            contract = {
                "status": "fail",
                "task_dir": str(tdir),
                "failure_code": getattr(e, "code", FailureCode.CONTRACT_INVALID),
                "message": str(e),
            }
            report.status = "fail"
            report.failure_code = FailureCode.CONTRACT_INVALID
            report.message = str(e)
        except Exception as e:
            contract = {
                "status": "fail",
                "task_dir": str(tdir),
                "failure_code": FailureCode.CONTRACT_INVALID,
                "message": str(e),
            }
            report.status = "fail"
            report.failure_code = FailureCode.CONTRACT_INVALID
            report.message = str(e)
    else:
        contract = {
            "status": "skip",
            "task_dir": str(tdir),
            "message": "acceptance_criteria.yaml not found",
        }
    _write_json(paths.contract_report_json, contract)
    if report.status == "fail":
        report.write(paths.report_json)
        click.echo(f"[qa] fail: {report.message}")
        click.echo(f"[qa] report: {paths.report_json}")
        raise SystemExit(1)

    try:
        static = static_qa(tdir, config_path=config_path, acceptance_path=acceptance_path)
        report.details["static"] = static
        _write_json(
            paths.static_report_json,
            {"status": "pass", "task_dir": str(tdir), "details": static},
        )
    except StaticQAError as e:
        report.status = "fail"
        report.failure_code = getattr(e, "code", FailureCode.CONFIG_INVALID)
        report.message = str(e)
        _write_json(
            paths.static_report_json,
            {
                "status": "fail",
                "task_dir": str(tdir),
                "failure_code": report.failure_code,
                "message": report.message,
            },
        )
        report.write(paths.report_json)
        click.echo(f"[qa] fail: {report.message}")
        click.echo(f"[qa] report: {paths.report_json}")
        raise SystemExit(1)
    except Exception as e:
        report.status = "fail"
        report.failure_code = FailureCode.CONFIG_INVALID
        report.message = str(e)
        _write_json(
            paths.static_report_json,
            {
                "status": "fail",
                "task_dir": str(tdir),
                "failure_code": report.failure_code,
                "message": report.message,
            },
        )
        report.write(paths.report_json)
        click.echo(f"[qa] fail: {report.message}")
        click.echo(f"[qa] report: {paths.report_json}")
        raise SystemExit(1)

    # If no runtime command is provided, we stop after static QA.
    if not runtime_cmd:
        report.write(paths.report_json)
        click.echo("[qa] pass (static only)")
        click.echo(f"[qa] report: {paths.report_json}")
        click.echo(f"[qa] output: {paths.output_dir}")
        return

    # Prepare subprocess environment for QA mode.
    env = dict(os.environ)
    env["PSYFLOW_MODE"] = "qa"
    env["PSYFLOW_QA_OUTPUT_DIR"] = str(Path(output_dir))
    env["PSYFLOW_QA_ENABLE_SCALING"] = "1" if enable_scaling else "0"
    env["PSYFLOW_QA_TIMING_SCALE"] = str(timing_scale)
    env["PSYFLOW_QA_MIN_FRAMES"] = str(min_frames)
    env["PSYFLOW_QA_STRICT"] = "1" if strict else "0"

    env["PSYFLOW_QA_RESPONDER"] = responder
    if responder_key:
        env["PSYFLOW_QA_RESPONDER_KEY"] = responder_key
    env["PSYFLOW_QA_RESPONDER_RT"] = str(responder_rt)
    if responder_class:
        env["PSYFLOW_RESPONDER_CLASS"] = str(responder_class)
    if responder_kwargs:
        env["PSYFLOW_RESPONDER_KWARGS"] = str(responder_kwargs)
    if config_path:
        env["PSYFLOW_CONFIG"] = str(config_path)

    # Run the task command in the task directory.
    try:
        proc = subprocess.run(
            runtime_cmd,
            cwd=str(tdir),
            env=env,
            shell=True,
            check=False,
        )
    except Exception as e:
        report.status = "fail"
        report.failure_code = FailureCode.RUNTIME_EXCEPTION
        report.message = f"Failed to run runtime command: {e}"
        report.write(paths.report_json)
        click.echo(f"[qa] fail: {report.message}")
        click.echo(f"[qa] report: {paths.report_json}")
        raise SystemExit(1)

    report.details["runtime"] = {"cmd": runtime_cmd, "returncode": proc.returncode}
    if proc.returncode != 0:
        report.status = "fail"
        report.failure_code = FailureCode.RUNTIME_EXCEPTION
        report.message = f"Runtime command failed (exit {proc.returncode})."
        report.write(paths.report_json)
        click.echo(f"[qa] fail: {report.message}")
        click.echo(f"[qa] report: {paths.report_json}")
        raise SystemExit(1)

    # Runtime trace validation (A').
    required_columns: list[str] = []
    expected_trial_count = None
    expected_condition_counts = None
    allowed_keys = None
    if acc_path and Path(acc_path).exists():
        try:
            acc = load_yaml(acc_path)
            if isinstance(acc, dict):
                if isinstance(acc.get("required_columns"), list):
                    required_columns = [c for c in acc["required_columns"] if isinstance(c, str)]
                if isinstance(acc.get("expected_trial_count"), int):
                    expected_trial_count = acc.get("expected_trial_count")
                if isinstance(acc.get("expected_condition_counts"), dict):
                    expected_condition_counts = acc.get("expected_condition_counts")
                if isinstance(acc.get("allowed_keys"), list):
                    allowed_keys = [k for k in acc.get("allowed_keys") if isinstance(k, str)]
        except Exception:
            pass

    try:
        trace_res = validate_trace_csv(
            paths.trace_csv,
            required_columns=required_columns,
            expected_trial_count=expected_trial_count,
            expected_condition_counts=expected_condition_counts,
            allowed_keys=allowed_keys,
            strict=strict,
        )
        report.details["trace_validation"] = trace_res
        if trace_res.get("errors"):
            report.status = "fail"
            report.failure_code = FailureCode.INVARIANT_VIOLATION
            report.message = "Trace invariants violated."
    except Exception as e:
        report.status = "fail"
        report.failure_code = FailureCode.LOG_SCHEMA_MISMATCH
        report.message = str(e)

    ev_res = validate_events(paths.events_jsonl)
    report.details["event_validation"] = ev_res
    if ev_res.get("errors") and report.status != "fail":
        report.status = "fail"
        report.failure_code = FailureCode.TRIGGER_MISSING
        report.message = ev_res["errors"][0]

    report.write(paths.report_json)
    click.echo(f"[qa] {report.status}")
    click.echo(f"[qa] report: {paths.report_json}")
    click.echo(f"[qa] trace: {paths.trace_csv}")
    click.echo(f"[qa] events: {paths.events_jsonl}")
    raise SystemExit(0 if report.status == "pass" else 1)


if __name__ == "__main__":
    main()

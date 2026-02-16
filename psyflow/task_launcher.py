from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


def _read_text_with_fallback(path: Path, *, encodings: Sequence[str] = ("utf-8", "utf-8-sig", "cp1252", "latin-1")) -> tuple[str, str]:
    last_err: Exception | None = None
    for enc in encodings:
        try:
            return path.read_text(encoding=enc), enc
        except UnicodeDecodeError as exc:
            last_err = exc
    if last_err is not None:
        raise last_err
    return path.read_text(encoding="utf-8"), "utf-8"


def _resolve_task_entry(task: str) -> tuple[Path, Path]:
    p = Path(task).expanduser().resolve()

    if p.is_file():
        if p.suffix.lower() != ".py":
            raise FileNotFoundError(f"Task entry must be a Python file, got: {p}")
        return p.parent, p

    if p.is_dir():
        main_py = p / "main.py"
        if not main_py.exists():
            raise FileNotFoundError(f"Task directory has no main.py: {p}")
        return p, main_py

    raise FileNotFoundError(f"Task path not found: {p}")


def _resolve_config_path(task_dir: Path, config_arg: str | None, *, defaults: list[str]) -> Path:
    if config_arg:
        cfg = Path(config_arg)
        if not cfg.is_absolute():
            cfg = task_dir / cfg
        cfg = cfg.resolve()
        if not cfg.exists():
            raise FileNotFoundError(f"Config file not found: {cfg}")
        return cfg

    for rel in defaults:
        p = (task_dir / rel).resolve()
        if p.exists():
            return p
    raise FileNotFoundError(
        "Config file not found. Checked defaults: " + ", ".join(str(task_dir / rel) for rel in defaults)
    )


def _build_parser(mode: str, *, description: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"psyflow-{mode if mode != 'human' else 'run'}",
        description=description or f"Run a psyflow task in {mode} mode via its task-local main.py.",
    )
    parser.add_argument(
        "task",
        help="Task directory (containing main.py) or a direct path to main.py",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional config path forwarded to task main.py.",
    )
    parser.add_argument(
        "--python",
        dest="python_exe",
        default=sys.executable,
        help="Python executable used to launch the task (default: current interpreter).",
    )
    return parser


def _run_mode(
    *,
    task_dir: Path,
    main_py: Path,
    python_exe: str,
    mode: str,
    config_path: Path | None,
    passthrough: Sequence[str],
) -> int:
    cmd: list[str] = [str(python_exe), str(main_py), mode]
    if config_path is not None:
        cmd.extend(["--config", str(config_path)])
    cmd.extend(passthrough)
    proc = subprocess.run(cmd, cwd=str(task_dir))
    return int(proc.returncode)


def run_task_shortcut(mode: str, argv: Sequence[str] | None = None, *, defaults: list[str] | None = None) -> int:
    mode = str(mode).strip().lower()
    if mode not in ("human", "qa", "sim"):
        raise ValueError(f"Unsupported mode: {mode!r}")

    parser = _build_parser(mode)
    ns, passthrough = parser.parse_known_args(argv)

    try:
        task_dir, main_py = _resolve_task_entry(ns.task)
    except FileNotFoundError as exc:
        parser.error(str(exc))

    cfg: Path | None = None
    if ns.config:
        try:
            cfg = _resolve_config_path(task_dir, ns.config, defaults=[])
        except FileNotFoundError as exc:
            parser.error(str(exc))
    elif defaults:
        try:
            cfg = _resolve_config_path(task_dir, None, defaults=defaults)
        except FileNotFoundError:
            cfg = None

    return _run_mode(
        task_dir=task_dir,
        main_py=main_py,
        python_exe=str(ns.python_exe),
        mode=mode,
        config_path=cfg,
        passthrough=passthrough,
    )


def _maturity_rank(value: str) -> int:
    order = {
        "draft": 0,
        "smoke_tested": 1,
        "piloted": 2,
        "validated": 3,
    }
    return order.get(value, -1)


def _normalize_maturity(value: str | None) -> str | None:
    if value is None:
        return None
    raw = str(value).strip().lower().replace(" ", "_")
    return raw or None


def _promote_maturity(current: str | None, target: str) -> str:
    cur = _normalize_maturity(current)
    tgt = _normalize_maturity(target) or "smoke_tested"
    if cur is None:
        return tgt
    if _maturity_rank(cur) >= _maturity_rank(tgt):
        return cur
    return tgt


def _update_taskbeacon_maturity(task_dir: Path, *, target: str) -> dict[str, Any]:
    path = task_dir / "taskbeacon.yaml"
    if not path.exists():
        return {"updated": False, "path": str(path), "reason": "taskbeacon.yaml not found", "maturity": None}

    text = path.read_text(encoding="utf-8")
    m = re.search(r"(?m)^maturity:\s*([^\n#]+)", text)
    current = m.group(1).strip() if m else None
    final = _promote_maturity(current, target)

    if m is not None:
        new_text = re.sub(r"(?m)^maturity:\s*[^\n#]+", f"maturity: {final}", text, count=1)
    else:
        suffix = "" if text.endswith("\n") else "\n"
        new_text = f"{text}{suffix}maturity: {final}\n"

    changed = new_text != text
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return {"updated": changed, "path": str(path), "from": current, "to": final, "maturity": final}


def _maturity_badge_line(maturity: str) -> str:
    value = _normalize_maturity(maturity) or "smoke_tested"
    colors = {
        "draft": "64748b",
        "smoke_tested": "d97706",
        "piloted": "16a34a",
        "validated": "2563eb",
    }
    color = colors.get(value, "0ea5e9")
    return (
        f"![Maturity: {value}]"
        f"(https://img.shields.io/badge/Maturity-{value}-{color}"
        "?style=flat-square&labelColor=111827)"
    )


def _update_readme_maturity_badge(task_dir: Path, *, maturity: str | None) -> dict[str, Any]:
    if not maturity:
        return {"updated": False, "path": str(task_dir / "README.md"), "reason": "maturity not set"}

    path = task_dir / "README.md"
    if not path.exists():
        return {"updated": False, "path": str(path), "reason": "README.md not found"}

    text, encoding = _read_text_with_fallback(path)
    badge = _maturity_badge_line(maturity)

    if re.search(r"(?m)^!\[Maturity:.*\]\(.*\)\s*$", text):
        new_text = re.sub(r"(?m)^!\[Maturity:.*\]\(.*\)\s*$", badge, text, count=1)
    else:
        lines = text.splitlines()
        if lines and lines[0].startswith("# "):
            lines.insert(1, "")
            lines.insert(2, badge)
            new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
        else:
            prefix = "" if text.startswith("#") else ""
            new_text = f"{badge}\n\n{text}" if text else f"{badge}\n"

    changed = new_text != text
    if changed:
        path.write_text(new_text, encoding=encoding)
    return {"updated": changed, "path": str(path), "maturity": maturity}


def run_qa_shortcut(argv: Sequence[str] | None = None) -> int:
    from psyflow.qa import QAReport, contract_lint, qa_artifact_paths, static_qa, validate_events, validate_trace_csv
    from psyflow.qa.report import FailureCode
    from psyflow.qa.static import (
        AssetMissingError,
        ConfigInvalidError,
        ContractInvalidError,
        KeysInvalidError,
        TriggerInvalidError,
        load_yaml,
    )

    parser = _build_parser(
        "qa",
        description=(
            "Run a task in QA mode, validate QA artifacts, and optionally update "
            "task maturity metadata and README maturity badge on pass."
        ),
    )
    parser.add_argument(
        "--set-maturity",
        default="smoke_tested",
        help="Maturity value to set/promote in taskbeacon.yaml when QA passes (default: smoke_tested).",
    )
    parser.add_argument(
        "--no-maturity-update",
        action="store_true",
        help="Disable taskbeacon.yaml/README maturity updates on QA pass.",
    )
    ns, passthrough = parser.parse_known_args(argv)

    try:
        task_dir, main_py = _resolve_task_entry(ns.task)
    except FileNotFoundError as exc:
        parser.error(str(exc))

    try:
        cfg_path = _resolve_config_path(
            task_dir,
            ns.config,
            defaults=["config/config_qa.yaml", "config/config.yaml"],
        )
    except FileNotFoundError as exc:
        parser.error(str(exc))

    cfg = load_yaml(cfg_path)
    qa_cfg = cfg.get("qa", {}) if isinstance(cfg, dict) else {}
    if not isinstance(qa_cfg, dict):
        qa_cfg = {}
    output_dir = qa_cfg.get("output_dir", "outputs/qa")
    artifacts = qa_artifact_paths(task_dir, output_dir=output_dir)
    artifacts.output_dir.mkdir(parents=True, exist_ok=True)

    def _report_fail(code: str, message: str, details: dict[str, Any] | None = None) -> int:
        report = QAReport(
            status="fail",
            failure_code=code,
            message=message,
            task_dir=str(task_dir),
            mode="qa",
            artifacts={
                "report_json": str(artifacts.report_json),
                "static_report_json": str(artifacts.static_report_json),
                "contract_report_json": str(artifacts.contract_report_json),
                "trace_csv": str(artifacts.trace_csv),
                "events_jsonl": str(artifacts.events_jsonl),
            },
            details=details or {},
        )
        report.write(artifacts.report_json)
        print(f"[psyflow-qa] FAIL {code}: {message}")
        print(f"[psyflow-qa] Report: {artifacts.report_json}")
        return 1

    try:
        static_result = static_qa(task_dir, config_path=cfg_path)
    except ConfigInvalidError as exc:
        return _report_fail(FailureCode.CONFIG_INVALID, str(exc))
    except AssetMissingError as exc:
        return _report_fail(FailureCode.ASSET_MISSING, str(exc))
    except ContractInvalidError as exc:
        return _report_fail(FailureCode.CONTRACT_INVALID, str(exc))
    except TriggerInvalidError as exc:
        return _report_fail(FailureCode.TRIGGER_INVALID, str(exc))
    except KeysInvalidError as exc:
        return _report_fail(FailureCode.KEYS_INVALID, str(exc))
    except Exception as exc:  # pragma: no cover
        return _report_fail(FailureCode.CONFIG_INVALID, f"Unexpected static QA error: {exc}")

    artifacts.static_report_json.write_text(
        json.dumps(static_result, ensure_ascii=True, indent=2), encoding="utf-8"
    )

    acceptance = qa_cfg.get("acceptance_criteria")
    if not isinstance(acceptance, dict):
        return _report_fail(
            FailureCode.CONTRACT_INVALID,
            "qa.acceptance_criteria is required in config_qa.yaml for psyflow-qa validation.",
        )
    try:
        contract_lint(acceptance)
    except ContractInvalidError as exc:
        return _report_fail(FailureCode.CONTRACT_INVALID, str(exc))

    contract_report = {
        "acceptance_source": static_result.get("acceptance_source"),
        "acceptance_path": static_result.get("acceptance_path"),
        "acceptance_criteria": acceptance,
    }
    artifacts.contract_report_json.write_text(
        json.dumps(contract_report, ensure_ascii=True, indent=2), encoding="utf-8"
    )

    rc = _run_mode(
        task_dir=task_dir,
        main_py=main_py,
        python_exe=str(ns.python_exe),
        mode="qa",
        config_path=cfg_path,
        passthrough=passthrough,
    )
    if rc != 0:
        return _report_fail(
            FailureCode.RUNTIME_EXCEPTION,
            f"Task QA runtime exited with non-zero code: {rc}",
            details={"returncode": rc, "config_path": str(cfg_path)},
        )

    try:
        trace_result = validate_trace_csv(
            artifacts.trace_csv,
            required_columns=acceptance.get("required_columns"),
            expected_trial_count=acceptance.get("expected_trial_count"),
            allowed_keys=acceptance.get("allowed_keys"),
        )
    except Exception as exc:
        return _report_fail(
            FailureCode.LOG_SCHEMA_MISMATCH,
            f"Failed validating trace CSV: {exc}",
            details={"trace_csv": str(artifacts.trace_csv)},
        )

    events_result = validate_events(artifacts.events_jsonl)
    trace_errors = list(trace_result.get("errors", []))
    event_errors = list(events_result.get("errors", []))
    all_errors = trace_errors + event_errors

    if all_errors:
        code = FailureCode.TRIGGER_MISSING if event_errors and not trace_errors else FailureCode.INVARIANT_VIOLATION
        return _report_fail(
            code,
            "; ".join(all_errors[:3]),
            details={
                "trace_errors": trace_errors,
                "event_errors": event_errors,
                "trace_csv": str(artifacts.trace_csv),
                "events_jsonl": str(artifacts.events_jsonl),
            },
        )

    maturity_result: dict[str, Any] = {}
    badge_result: dict[str, Any] = {}
    final_maturity: str | None = None
    if not ns.no_maturity_update:
        maturity_result = _update_taskbeacon_maturity(task_dir, target=ns.set_maturity)
        final_maturity = maturity_result.get("maturity")
        badge_result = _update_readme_maturity_badge(task_dir, maturity=final_maturity)

    report = QAReport(
        status="pass",
        task_dir=str(task_dir),
        mode="qa",
        artifacts={
            "report_json": str(artifacts.report_json),
            "static_report_json": str(artifacts.static_report_json),
            "contract_report_json": str(artifacts.contract_report_json),
            "trace_csv": str(artifacts.trace_csv),
            "events_jsonl": str(artifacts.events_jsonl),
        },
        details={
            "config_path": str(cfg_path),
            "static": static_result,
            "trace": trace_result,
            "events": events_result,
            "maturity_update": maturity_result,
            "readme_badge_update": badge_result,
        },
    )
    report.write(artifacts.report_json)
    print("[psyflow-qa] PASS")
    print(f"[psyflow-qa] Report: {artifacts.report_json}")
    return 0


def run_main() -> None:
    raise SystemExit(run_task_shortcut("human", defaults=["config/config.yaml"]))


def qa_main() -> None:
    raise SystemExit(run_qa_shortcut())


def sim_main() -> None:
    raise SystemExit(run_task_shortcut("sim", defaults=["config/config_scripted_sim.yaml"]))

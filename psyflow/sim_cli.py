from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import click


def _resolve_output_dir(task_dir: Path, output_dir: str) -> Path:
    out = Path(output_dir)
    if out.is_absolute():
        return out
    return task_dir / out


def _default_session_id(participant_id: str, seed: int) -> str:
    return f"sim-{participant_id}-seed{seed}"


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2), encoding="utf-8")


@click.command()
@click.argument("task_dir", required=False, default=".")
@click.option("--output-dir", default="outputs/sim", show_default=True, help="Simulation output directory (relative to task_dir).")
@click.option("--runtime-cmd", default="python main.py", show_default=True, help="Task command to execute.")
@click.option("--config", "config_path", default=None, help="Optional config path exposed as PSYFLOW_CONFIG for runtime.")
@click.option("--seed", default=0, type=int, show_default=True, help="Simulation seed.")
@click.option("--participant-id", default="sim001", show_default=True, help="Participant id for session context.")
@click.option("--session-id", default=None, help="Session id (default: sim-<participant>-seed<seed>).")
@click.option("--policy", type=click.Choice(["strict", "warn", "coerce"], case_sensitive=False), default="warn", show_default=True)
@click.option("--default-rt-s", default=0.2, type=float, show_default=True, help="Fallback RT in coerce mode.")
@click.option("--clamp-rt", is_flag=True, help="Clamp out-of-bounds RT instead of rejecting (coerce policy only).")
@click.option("--responder", type=click.Choice(["scripted", "null"], case_sensitive=False), default="scripted", show_default=True)
@click.option("--responder-key", default=None, help="Scripted responder key (default: first valid key).")
@click.option("--responder-rt", default=0.25, type=float, show_default=True, help="Scripted responder RT (seconds).")
@click.option("--responder-class", default=None, help="Import path for external responder class/factory.")
@click.option("--responder-kwargs", default=None, help="JSON kwargs for --responder-class.")
@click.option("--sim-log-path", default=None, help="Path for sim JSONL log (defaults to <output-dir>/sim_events.jsonl).")
def main(
    task_dir: str,
    output_dir: str,
    runtime_cmd: str,
    config_path: str | None,
    seed: int,
    participant_id: str,
    session_id: str | None,
    policy: str,
    default_rt_s: float,
    clamp_rt: bool,
    responder: str,
    responder_key: str | None,
    responder_rt: float,
    responder_class: str | None,
    responder_kwargs: str | None,
    sim_log_path: str | None,
):
    """Run a psyflow task in simulation mode with responder plugins."""
    tdir = Path(task_dir).resolve()
    out = _resolve_output_dir(tdir, output_dir)
    out.mkdir(parents=True, exist_ok=True)

    sid = session_id or _default_session_id(participant_id=participant_id, seed=seed)
    log_path = sim_log_path or str(Path(output_dir) / "sim_events.jsonl")

    env = dict(os.environ)
    env["PSYFLOW_MODE"] = "sim"
    env["PSYFLOW_QA_OUTPUT_DIR"] = str(Path(output_dir))
    env["PSYFLOW_SIM_SEED"] = str(int(seed))
    env["PSYFLOW_PARTICIPANT_ID"] = str(participant_id)
    env["PSYFLOW_SESSION_ID"] = str(sid)
    env["PSYFLOW_SIM_POLICY"] = str(policy).strip().lower()
    env["PSYFLOW_SIM_DEFAULT_RT_S"] = str(float(default_rt_s))
    env["PSYFLOW_SIM_CLAMP_RT"] = "1" if clamp_rt else "0"
    env["PSYFLOW_QA_RESPONDER"] = str(responder).strip().lower()
    env["PSYFLOW_QA_RESPONDER_RT"] = str(float(responder_rt))
    env["PSYFLOW_SIM_LOG_PATH"] = str(log_path)

    if responder_key:
        env["PSYFLOW_QA_RESPONDER_KEY"] = str(responder_key)
    if responder_class:
        env["PSYFLOW_RESPONDER_CLASS"] = str(responder_class)
    if responder_kwargs:
        env["PSYFLOW_RESPONDER_KWARGS"] = str(responder_kwargs)
    if config_path:
        env["PSYFLOW_CONFIG"] = str(config_path)

    try:
        proc = subprocess.run(
            runtime_cmd,
            cwd=str(tdir),
            env=env,
            shell=True,
            check=False,
        )
        status = "pass" if proc.returncode == 0 else "fail"
        report = {
            "status": status,
            "task_dir": str(tdir),
            "mode": "sim",
            "runtime": {"cmd": runtime_cmd, "returncode": proc.returncode},
            "session": {
                "participant_id": participant_id,
                "session_id": sid,
                "seed": int(seed),
                "policy": env["PSYFLOW_SIM_POLICY"],
            },
            "responder": {
                "kind": env["PSYFLOW_QA_RESPONDER"],
                "class": env.get("PSYFLOW_RESPONDER_CLASS"),
                "kwargs": env.get("PSYFLOW_RESPONDER_KWARGS"),
            },
            "artifacts": {
                "output_dir": str(out),
                "trace_csv": str(out / "qa_trace.csv"),
                "sim_events": str(_resolve_output_dir(tdir, log_path)),
                "sim_report": str(out / "sim_report.json"),
            },
        }
        _write_json(out / "sim_report.json", report)
        click.echo(f"[sim] {status}")
        click.echo(f"[sim] report: {out / 'sim_report.json'}")
        click.echo(f"[sim] output: {out}")
        click.echo(f"[sim] trace: {out / 'qa_trace.csv'}")
        click.echo(f"[sim] events: {_resolve_output_dir(tdir, log_path)}")
        raise SystemExit(0 if status == "pass" else 1)
    except Exception as e:
        report = {
            "status": "fail",
            "task_dir": str(tdir),
            "mode": "sim",
            "runtime": {"cmd": runtime_cmd},
            "error": str(e),
            "artifacts": {"sim_report": str(out / "sim_report.json")},
        }
        _write_json(out / "sim_report.json", report)
        click.echo(f"[sim] fail: {e}")
        click.echo(f"[sim] report: {out / 'sim_report.json'}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

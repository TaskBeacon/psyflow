from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QAArtifactPaths:
    output_dir: Path
    report_json: Path
    static_report_json: Path
    contract_report_json: Path
    trace_csv: Path
    events_jsonl: Path


def qa_artifact_paths(task_dir: str | Path, *, output_dir: str | Path = "outputs/qa") -> QAArtifactPaths:
    task_dir = Path(task_dir)
    out = Path(output_dir)
    if not out.is_absolute():
        out = task_dir / out
    return QAArtifactPaths(
        output_dir=out,
        report_json=out / "qa_report.json",
        static_report_json=out / "static_report.json",
        contract_report_json=out / "contract_report.json",
        trace_csv=out / "qa_trace.csv",
        events_jsonl=out / "qa_events.jsonl",
    )

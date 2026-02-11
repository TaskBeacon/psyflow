from __future__ import annotations

import contextlib
import contextvars
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class QAConfig:
    """QA knobs used by the responder injection layer.

    Defaults are intentionally conservative: scaling is OFF.
    """

    enable_scaling: bool = False
    timing_scale: float = 1.0
    min_frames: int = 2
    strict: bool = False
    max_wait_s: float = 10.0  # used for indefinite waits in QA mode


@dataclass
class QAContext:
    mode: str = "human"  # human | qa | sim
    responder: Any = None
    config: QAConfig = field(default_factory=QAConfig)
    event_logger: Optional[Callable[[dict[str, Any]], None]] = None
    task_dir: Optional[Path] = None
    output_dir: Optional[Path] = None


_CTX: contextvars.ContextVar[Optional[QAContext]] = contextvars.ContextVar("psyflow_qa_ctx", default=None)


def get_context() -> Optional[QAContext]:
    return _CTX.get()


def log_event(event: dict[str, Any]) -> None:
    """Best-effort QA event logging (never raise)."""
    ctx = get_context()
    if ctx is None or ctx.event_logger is None:
        return
    try:
        ctx.event_logger(event)
    except Exception:
        # QA logging should never break the runtime.
        return


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_jsonl_logger(path: Path) -> Callable[[dict[str, Any]], None]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def _log(ev: dict[str, Any]) -> None:
        rec = dict(ev)
        rec.setdefault("t_utc", _utc_now_iso())
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=True) + "\n")

    return _log


@contextlib.contextmanager
def qa_context(ctx: QAContext):
    """Activate QA context for the current execution context."""
    token = _CTX.set(ctx)
    try:
        yield ctx
    finally:
        _CTX.reset(token)


def context_from_env(*, task_dir: str | os.PathLike | None = None) -> QAContext:
    """Build a QAContext from environment variables.

    This is intentionally minimal and intended for task scripts.
    """
    mode = os.getenv("PSYFLOW_MODE", "human").strip().lower() or "human"

    output_dir = os.getenv("PSYFLOW_QA_OUTPUT_DIR", "outputs/qa")
    enable_scaling = os.getenv("PSYFLOW_QA_ENABLE_SCALING", "0").strip() in ("1", "true", "yes", "on")
    timing_scale = float(os.getenv("PSYFLOW_QA_TIMING_SCALE", "1.0"))
    min_frames = int(os.getenv("PSYFLOW_QA_MIN_FRAMES", "2"))
    strict = os.getenv("PSYFLOW_QA_STRICT", "0").strip() in ("1", "true", "yes", "on")

    cfg = QAConfig(
        enable_scaling=enable_scaling,
        timing_scale=timing_scale,
        min_frames=min_frames,
        strict=strict,
    )

    responder = None
    if mode in ("qa", "sim"):
        responder_kind = os.getenv("PSYFLOW_QA_RESPONDER", "scripted").strip().lower() or "scripted"
        if responder_kind == "scripted":
            from .responder import ScriptedResponder

            key = os.getenv("PSYFLOW_QA_RESPONDER_KEY", None)
            rt_s = float(os.getenv("PSYFLOW_QA_RESPONDER_RT", "0.2"))
            responder = ScriptedResponder(key=key, rt_s=rt_s)

    tdir = Path(task_dir) if task_dir is not None else None
    out = (tdir / output_dir) if (tdir is not None and not Path(output_dir).is_absolute()) else Path(output_dir)

    events_path = out / "qa_events.jsonl"
    event_logger = make_jsonl_logger(events_path) if mode in ("qa", "sim") else None

    return QAContext(
        mode=mode,
        responder=responder,
        config=cfg,
        event_logger=event_logger,
        task_dir=tdir,
        output_dir=out,
    )

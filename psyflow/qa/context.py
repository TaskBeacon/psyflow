from __future__ import annotations

import contextlib
import contextvars
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from psyflow.sim.contracts import SessionInfo
from psyflow.sim.loader import load_responder
from psyflow.sim.logging import make_sim_jsonl_logger
from psyflow.sim.rng import make_rng


def _cfg_get(mapping: dict[str, Any] | None, path: tuple[str, ...], default: Any = None) -> Any:
    cur: Any = mapping or {}
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(int(value))
    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("1", "true", "yes", "on"):
            return True
        if s in ("0", "false", "no", "off"):
            return False
    return bool(default)


@dataclass(frozen=True)
class QAConfig:
    """QA/sim knobs used by the responder injection layer."""

    enable_scaling: bool = False
    timing_scale: float = 1.0
    min_frames: int = 2
    strict: bool = False
    max_wait_s: float = 10.0
    sim_policy: str = "warn"  # strict | warn | coerce
    default_rt_s: float = 0.2
    clamp_rt: bool = False


@dataclass
class QAContext:
    mode: str = "human"  # human | qa | sim
    responder: Any = None
    responder_meta: dict[str, Any] = field(default_factory=dict)
    config: QAConfig = field(default_factory=QAConfig)
    event_logger: Optional[Callable[[dict[str, Any]], None]] = None
    sim_logger: Optional[Callable[[dict[str, Any]], None]] = None
    task_dir: Optional[Path] = None
    output_dir: Optional[Path] = None
    session: Optional[SessionInfo] = None
    rng: Any = None


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
        return


def log_sim_event(event: dict[str, Any]) -> None:
    """Best-effort simulation event logging (never raise)."""
    ctx = get_context()
    if ctx is None or ctx.sim_logger is None:
        return
    try:
        ctx.sim_logger(event)
    except Exception:
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
        try:
            responder = getattr(ctx, "responder", None)
            if responder is not None and hasattr(responder, "end_session"):
                responder.end_session()
        except Exception:
            pass
        _CTX.reset(token)


def context_from_env(
    *,
    task_dir: str | os.PathLike | None = None,
    config: dict[str, Any] | None = None,
) -> QAContext:
    """Build QA/sim context from environment variables (+ optional config mapping)."""
    raw_cfg = config
    if isinstance(config, dict) and isinstance(config.get("raw"), dict):
        raw_cfg = config.get("raw")

    mode_cfg = str(_cfg_get(raw_cfg, ("sim", "mode"), "human") or "human").strip().lower()
    mode = os.getenv("PSYFLOW_MODE", mode_cfg).strip().lower() or "human"

    default_output_dir = "outputs/sim" if mode == "sim" else "outputs/qa"
    output_dir_cfg = _cfg_get(raw_cfg, ("sim", "output_dir"), None) or _cfg_get(raw_cfg, ("qa", "output_dir"), None)
    output_dir = os.getenv("PSYFLOW_QA_OUTPUT_DIR", str(output_dir_cfg or default_output_dir))

    enable_scaling = _as_bool(
        os.getenv(
            "PSYFLOW_QA_ENABLE_SCALING",
            str(int(_as_bool(_cfg_get(raw_cfg, ("qa", "enable_scaling"), False)))),
        ),
        False,
    )
    timing_scale = float(os.getenv("PSYFLOW_QA_TIMING_SCALE", str(_cfg_get(raw_cfg, ("qa", "timing_scale"), 1.0))))
    min_frames = int(os.getenv("PSYFLOW_QA_MIN_FRAMES", str(_cfg_get(raw_cfg, ("qa", "min_frames"), 2))))
    strict = _as_bool(
        os.getenv("PSYFLOW_QA_STRICT", str(int(_as_bool(_cfg_get(raw_cfg, ("qa", "strict"), False))))),
        False,
    )
    max_wait_s = float(os.getenv("PSYFLOW_QA_MAX_WAIT_S", str(_cfg_get(raw_cfg, ("qa", "max_wait_s"), 10.0))))

    sim_policy = str(
        os.getenv(
            "PSYFLOW_SIM_POLICY",
            str(_cfg_get(raw_cfg, ("sim", "policy"), "strict" if strict else "warn")),
        )
    ).strip().lower()
    if sim_policy not in ("strict", "warn", "coerce"):
        sim_policy = "strict" if strict else "warn"

    default_rt_s = float(os.getenv("PSYFLOW_SIM_DEFAULT_RT_S", str(_cfg_get(raw_cfg, ("sim", "default_rt_s"), 0.2))))
    clamp_rt = _as_bool(
        os.getenv("PSYFLOW_SIM_CLAMP_RT", str(int(_as_bool(_cfg_get(raw_cfg, ("sim", "clamp_rt"), False))))),
        False,
    )

    cfg = QAConfig(
        enable_scaling=enable_scaling,
        timing_scale=timing_scale,
        min_frames=min_frames,
        strict=strict,
        max_wait_s=max_wait_s,
        sim_policy=sim_policy,
        default_rt_s=default_rt_s,
        clamp_rt=clamp_rt,
    )

    task_name = str(
        _cfg_get(raw_cfg, ("task", "task_name"), _cfg_get(config, ("task_config", "task_name"), "unknown_task"))
        or "unknown_task"
    )
    task_version = _cfg_get(raw_cfg, ("task", "task_version"), _cfg_get(config, ("task_config", "task_version"), None))
    seed = int(os.getenv("PSYFLOW_SIM_SEED", str(_cfg_get(raw_cfg, ("sim", "seed"), 0))))
    participant_id = str(
        os.getenv(
            "PSYFLOW_PARTICIPANT_ID",
            _cfg_get(raw_cfg, ("sim", "participant_id"), _cfg_get(raw_cfg, ("task", "participant_id"), "p000")),
        )
        or "p000"
    )
    default_session_id = f"{mode}-{participant_id}-seed{seed}"
    session_id = str(os.getenv("PSYFLOW_SESSION_ID", str(_cfg_get(raw_cfg, ("sim", "session_id"), default_session_id))))
    session = SessionInfo(
        participant_id=participant_id,
        session_id=session_id,
        seed=seed,
        mode=mode if mode in ("human", "qa", "sim") else "human",
        task_name=task_name,
        task_version=task_version,
    )
    rng = make_rng(seed)

    tdir = Path(task_dir) if task_dir is not None else None
    out = (tdir / output_dir) if (tdir is not None and not Path(output_dir).is_absolute()) else Path(output_dir)

    events_path = out / "qa_events.jsonl"
    event_logger = make_jsonl_logger(events_path) if mode in ("qa", "sim") else None

    sim_log_default = "outputs/sim/sim_events.jsonl" if mode == "sim" else str(Path(output_dir) / "sim_events.jsonl")
    sim_log_cfg = _cfg_get(raw_cfg, ("sim", "log_path"), sim_log_default)
    sim_log_path = os.getenv("PSYFLOW_SIM_LOG_PATH", str(sim_log_cfg))
    sim_log = (tdir / sim_log_path) if (tdir is not None and not Path(sim_log_path).is_absolute()) else Path(sim_log_path)
    sim_logger = make_sim_jsonl_logger(sim_log) if mode in ("qa", "sim") else None

    responder = None
    responder_meta: dict[str, Any] = {}
    if mode in ("qa", "sim"):
        responder_cfg = _cfg_get(raw_cfg, ("sim", "responder"), None)
        if not isinstance(responder_cfg, dict):
            responder_cfg = _cfg_get(raw_cfg, ("responder",), {}) if isinstance(raw_cfg, dict) else {}
        if not isinstance(responder_cfg, dict):
            responder_cfg = {}
        merged_cfg = {"responder": responder_cfg}
        responder, responder_meta = load_responder(
            mode=mode,
            config=merged_cfg,
            session=session,
            rng=rng,
            allow_fallback=not strict,
        )

    return QAContext(
        mode=mode,
        responder=responder,
        responder_meta=responder_meta,
        config=cfg,
        event_logger=event_logger,
        sim_logger=sim_logger,
        task_dir=tdir,
        output_dir=out,
        session=session,
        rng=rng,
    )

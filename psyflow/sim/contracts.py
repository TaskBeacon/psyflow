from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Optional, Protocol, runtime_checkable


Mode = Literal["human", "qa", "sim"]


@dataclass(frozen=True)
class SessionInfo:
    participant_id: str
    session_id: str
    seed: int
    mode: Mode
    task_name: str = "unknown_task"
    task_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Observation:
    # Required in sim mode (warning-only in current rollout).
    trial_id: int | str | None
    phase: str
    valid_keys: list[str]
    deadline_s: float | None
    t_phase_onset: float | None = None

    # Recommended contextual fields.
    block_id: int | str | None = None
    condition_id: str | None = None
    task_factors: dict[str, Any] = field(default_factory=dict)

    # Optional fields.
    stim_id: str | None = None
    stim_features: dict[str, Any] | None = None
    history: dict[str, Any] | None = None
    t_phase_onset_global: float | None = None
    response_window_open: bool = True
    response_window_s: float | None = None
    mode: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        return self.extras.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        # Flatten extras into top-level for backward compatibility with dict-like responders.
        extras = out.pop("extras", {}) or {}
        out.update(extras)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Observation":
        known = {
            "trial_id",
            "phase",
            "valid_keys",
            "deadline_s",
            "t_phase_onset",
            "block_id",
            "condition_id",
            "task_factors",
            "stim_id",
            "stim_features",
            "history",
            "t_phase_onset_global",
            "response_window_open",
            "response_window_s",
            "mode",
        }
        payload = dict(data or {})
        extras = {k: v for k, v in payload.items() if k not in known}
        return cls(
            trial_id=payload.get("trial_id"),
            phase=str(payload.get("phase", "")),
            valid_keys=list(payload.get("valid_keys") or []),
            deadline_s=payload.get("deadline_s"),
            t_phase_onset=payload.get("t_phase_onset"),
            block_id=payload.get("block_id"),
            condition_id=payload.get("condition_id"),
            task_factors=dict(payload.get("task_factors") or {}),
            stim_id=payload.get("stim_id"),
            stim_features=payload.get("stim_features"),
            history=payload.get("history"),
            t_phase_onset_global=payload.get("t_phase_onset_global"),
            response_window_open=bool(payload.get("response_window_open", True)),
            response_window_s=payload.get("response_window_s"),
            mode=payload.get("mode"),
            extras=extras,
        )


@dataclass(frozen=True)
class Action:
    key: str | None
    rt_s: float | None
    meta: dict[str, Any] | None = None

    @property
    def rt(self) -> float | None:
        """Backward-compatible alias used by legacy qa responders."""
        return self.rt_s

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "rt_s": self.rt_s, "meta": dict(self.meta or {})}


@dataclass(frozen=True)
class Feedback:
    trial_id: int | str
    phase: str
    outcome: str | None = None
    reward: float | None = None
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class ResponderProtocol(Protocol):
    def start_session(self, session: SessionInfo, rng: Any) -> None:
        ...

    def act(self, obs: Observation) -> Action:
        ...

    def on_feedback(self, fb: Feedback) -> None:
        ...

    def end_session(self) -> None:
        ...


class NullResponder:
    """Responder that never responds (always timeout)."""

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        return None

    def act(self, obs: Observation) -> Action:
        return Action(key=None, rt_s=None, meta={"source": "null"})

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        return None


class ScriptedResponder:
    """Simple deterministic responder for QA/smoke simulation.

    Behavior:
    - fixed key if valid, else first valid key
    - fixed RT (seconds)
    """

    def __init__(self, *, key: str | None = None, rt_s: float = 0.2):
        self._key = key
        self._rt_s = float(rt_s)
        self._rng = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def act(self, obs: Observation) -> Action:
        # Backward compatibility: legacy responders may receive dict observations.
        if isinstance(obs, dict):
            valid = list(obs.get("valid_keys") or [])
            min_wait = obs.get("min_wait_s")
        else:
            valid = list(obs.valid_keys or [])
            min_wait = obs.get("min_wait_s")
        key = self._key if self._key in valid else (valid[0] if valid else None)
        rt = self._rt_s
        if min_wait is not None:
            try:
                rt = max(rt, float(min_wait))
            except Exception:
                pass
        return Action(key=key, rt_s=rt, meta={"source": "scripted"})

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        return None

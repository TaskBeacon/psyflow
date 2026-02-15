from __future__ import annotations

from typing import Any

from psyflow.sim.contracts import Action, Observation


class DemoResponder:
    """Tiny external responder plugin used by docs/tests."""

    def __init__(self, *, key: str | None = None, base_rt_s: float = 0.25, jitter_s: float = 0.05):
        self.key = key
        self.base_rt_s = float(base_rt_s)
        self.jitter_s = float(jitter_s)
        self.rng: Any = None

    def start_session(self, session, rng: Any) -> None:
        self.rng = rng

    def act(self, obs: Observation) -> Action:
        valid = list(getattr(obs, "valid_keys", []) or [])
        key = self.key if self.key in valid else (valid[0] if valid else None)
        if key is None:
            return Action(key=None, rt_s=None, meta={"source": "demo"})
        jitter = float(self.rng.uniform(-self.jitter_s, self.jitter_s)) if self.rng is not None else 0.0
        rt_s = max(0.0, self.base_rt_s + jitter)
        return Action(key=key, rt_s=rt_s, meta={"source": "demo"})

    def on_feedback(self, fb) -> None:
        return None

    def end_session(self) -> None:
        return None


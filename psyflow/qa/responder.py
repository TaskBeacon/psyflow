from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Action:
    key: Optional[str]
    rt: Optional[float]


class ScriptedResponder:
    """A minimal responder for QA runs.

    Default behavior:
    - choose a fixed key (if provided) or the first valid key
    - respond at a fixed RT (seconds)

    This is meant for smoke testing "task runs end-to-end" rather than modeling.
    """

    def __init__(self, *, key: str | None = None, rt_s: float = 0.2):
        self._key = key
        self._rt_s = float(rt_s)

    def act(self, observation: dict[str, Any]) -> Action:
        valid = observation.get("valid_keys") or []
        key = self._key if self._key in valid else (valid[0] if valid else None)

        rt = self._rt_s
        min_wait = observation.get("min_wait_s")
        if min_wait is not None:
            try:
                rt = max(rt, float(min_wait))
            except Exception:
                pass

        return Action(key=key, rt=rt)


class NullResponder:
    """Responder that never responds (always timeout)."""

    def act(self, observation: dict[str, Any]) -> Action:
        return Action(key=None, rt=None)


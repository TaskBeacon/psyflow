from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class TriggerEvent:
    """Structured trigger event (hardware-agnostic contract)."""

    name: Optional[str] = None
    code: Optional[int] = None
    payload: Optional[bytes | str] = None
    pulse_width_ms: Optional[int] = None
    reset_code: Optional[int] = None
    meta: dict[str, Any] = field(default_factory=dict)

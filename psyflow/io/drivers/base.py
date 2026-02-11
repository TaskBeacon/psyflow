from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from ..events import TriggerEvent


class TriggerDriver(Protocol):
    """Device/protocol-level trigger driver (I/O only)."""

    name: str

    def open(self) -> None: ...

    def close(self) -> None: ...

    def send(self, event: TriggerEvent, *, wait: bool = True) -> None: ...


@dataclass(frozen=True)
class DriverInfo:
    name: str
    kind: Optional[str] = None


from __future__ import annotations

from typing import Iterable

from ..events import TriggerEvent


class FanoutDriver:
    """Broadcast trigger sends to multiple drivers."""

    def __init__(self, drivers: Iterable[object], *, name: str = "fanout"):
        self.name = name
        self._drivers = list(drivers)

    def open(self) -> None:
        for d in self._drivers:
            try:
                if hasattr(d, "open"):
                    d.open()
            except Exception:
                continue

    def close(self) -> None:
        for d in self._drivers:
            try:
                if hasattr(d, "close"):
                    d.close()
            except Exception:
                continue

    def send(self, event: TriggerEvent, *, wait: bool = True) -> None:
        for d in self._drivers:
            try:
                d.send(event, wait=wait)
            except Exception:
                continue


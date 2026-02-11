from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

from ..events import TriggerEvent


@dataclass
class MockRecord:
    t_sent: float
    event: TriggerEvent


class MockDriver:
    """Mock trigger driver (no hardware).

    Records sent events and optionally prints codes to stdout.
    """

    def __init__(self, *, name: str = "mock", print_codes: bool = True):
        self.name = name
        self.print_codes = bool(print_codes)
        self.records: list[MockRecord] = []

    def open(self) -> None:
        return

    def close(self) -> None:
        return

    def send(self, event: TriggerEvent, *, wait: bool = True) -> None:
        # "wait" is ignored for mock.
        self.records.append(MockRecord(t_sent=time.time(), event=event))
        if self.print_codes and event.code is not None:
            print(f"[MockTrigger] Sent code: {event.code}")


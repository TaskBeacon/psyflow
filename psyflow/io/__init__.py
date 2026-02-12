"""I/O runtimes and drivers (triggers, later inputs).

This module is designed so that:
- tasks stay hardware-agnostic (they emit semantic events),
- drivers own protocol/hardware I/O,
- runtimes own timing semantics (now vs on-flip) and audit logging.
"""

from .events import TriggerEvent
from .runtime import TriggerRuntime, make_jsonl_logger
from .trigger import initialize_triggers
from .drivers.base import TriggerDriver
from .drivers.callable import CallableDriver
from .drivers.mock import MockDriver
from .drivers.serial import SerialDriver
from .drivers.fanout import FanoutDriver

__all__ = [
    "CallableDriver",
    "FanoutDriver",
    "MockDriver",
    "SerialDriver",
    "TriggerDriver",
    "TriggerEvent",
    "TriggerRuntime",
    "initialize_triggers",
    "make_jsonl_logger",
]

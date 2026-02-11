from __future__ import annotations

from typing import Callable, Optional, Any, Literal

from psychopy import logging

from .io import TriggerEvent, TriggerRuntime
from .io.drivers.callable import CallableDriver
from .io.drivers.mock import MockDriver


class TriggerSender:
    """Backward-compatible trigger API (compat wrapper).

    Historically, psyflow tasks used a `TriggerSender(trigger_func=...)` object
    and called `.send(code)` directly. The new architecture uses:
    - TriggerRuntime (timing semantics + logging)
    - TriggerDriver  (hardware/protocol I/O)

    This class remains as a thin wrapper for one or two releases.
    """

    def __init__(
        self,
        trigger_func: Optional[Callable[[Any], None]] = None,
        *,
        mock: bool = False,
        post_delay: float = 0.001,
        on_trigger_start: Optional[Callable[[], None]] = None,
        on_trigger_end: Optional[Callable[[], None]] = None,
        runtime: Optional[TriggerRuntime] = None,
        driver: Any = None,
    ):
        if runtime is not None:
            self.runtime = runtime
            return

        if driver is None:
            if mock or trigger_func is None:
                driver = MockDriver(print_codes=True)
            else:
                driver = CallableDriver(
                    trigger_func,
                    post_delay_s=post_delay,
                    on_trigger_start=on_trigger_start,
                    on_trigger_end=on_trigger_end,
                )

        self.runtime = TriggerRuntime(driver)

    def open(self) -> None:
        try:
            self.runtime.open()
        except Exception:
            return

    def close(self) -> None:
        try:
            self.runtime.close()
        except Exception:
            return

    def emit(
        self,
        event: TriggerEvent,
        *,
        when: Literal["now", "flip"] = "now",
        win: Any = None,
        wait: bool = True,
    ) -> None:
        self.runtime.emit(event, when=when, win=win, wait=wait)

    def send(self, code: Optional[int], wait: bool = True):
        """Compatibility API: send an integer trigger code now."""
        if code is None:
            logging.warning("[Trigger] Skipping trigger send: code is None")
            return

        try:
            code_i = int(code)
        except Exception:
            logging.warning(f"[Trigger] Skipping trigger send: non-int code {code!r}")
            return

        self.runtime.emit(TriggerEvent(code=code_i), when="now", wait=wait)


from __future__ import annotations

from typing import Any, Callable, Optional

from ..events import TriggerEvent


class CallableDriver:
    """Driver that calls a user-provided function to send a trigger.

    This is a compatibility-friendly driver: if `event.payload` is present it
    is passed to `send_fn`, otherwise `event.code` is passed.
    """

    def __init__(
        self,
        send_fn: Callable[[Any], None],
        *,
        name: str = "callable",
        post_delay_s: float = 0.001,
        on_trigger_start: Optional[Callable[[], None]] = None,
        on_trigger_end: Optional[Callable[[], None]] = None,
    ):
        self.name = name
        self._send_fn = send_fn
        self.post_delay_s = float(post_delay_s or 0.0)
        self.on_trigger_start = on_trigger_start
        self.on_trigger_end = on_trigger_end

    def open(self) -> None:
        return

    def close(self) -> None:
        return

    def send(self, event: TriggerEvent, *, wait: bool = True) -> None:
        if self.on_trigger_start:
            self.on_trigger_start()

        payload = event.payload if event.payload is not None else event.code
        self._send_fn(payload)

        if wait and self.post_delay_s:
            # Keep PsychoPy optional: fall back to time.sleep if core isn't available.
            try:
                from psychopy import core

                core.wait(self.post_delay_s)
            except Exception:
                import time

                time.sleep(self.post_delay_s)

        if wait and self.on_trigger_end:
            self.on_trigger_end()


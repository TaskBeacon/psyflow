from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional, Literal

from .events import TriggerEvent


def make_jsonl_logger(path: str | Path) -> Callable[[dict[str, Any]], None]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def _log(ev: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=True) + "\n")

    return _log


class TriggerRuntime:
    """Owns timing semantics + audit logging; delegates I/O to a driver."""

    def __init__(
        self,
        driver: Any,
        *,
        name: str | None = None,
        event_logger: Optional[Callable[[dict[str, Any]], None]] = None,
        strict: bool = False,
    ):
        self.driver = driver
        self.name = name or getattr(driver, "name", driver.__class__.__name__)
        if event_logger is None:
            path = os.getenv("PSYFLOW_TRIGGER_LOG_PATH")
            event_logger = make_jsonl_logger(path) if path else None
        self.event_logger = event_logger
        self.strict = bool(strict)
        self._emit_seq = 0

    def open(self) -> None:
        if hasattr(self.driver, "open"):
            self.driver.open()

    def close(self) -> None:
        if hasattr(self.driver, "close"):
            self.driver.close()

    def send(self, code: int | None, wait: bool = True) -> None:
        """Send a simple integer trigger code immediately."""
        if code is None:
            return
        try:
            code_i = int(code)
        except Exception:
            return
        self.emit(TriggerEvent(code=code_i), when="now", wait=wait)

    def _next_id(self) -> int:
        self._emit_seq += 1
        return self._emit_seq

    def _log(self, rec: dict[str, Any]) -> None:
        # 1) QA event sink (if active)
        try:
            from psyflow.sim.context import log_event

            log_event(rec)
        except Exception:
            pass

        # 2) Optional runtime logger (JSONL, etc.)
        if self.event_logger is not None:
            try:
                self.event_logger(rec)
            except Exception:
                pass

        # 3) PsychoPy logging (best-effort, keep optional)
        try:
            from psychopy import logging

            logging.data(f"[TriggerRuntime] {rec}")
        except Exception:
            pass

    def _effective_strict(self) -> bool:
        if self.strict:
            return True
        try:
            from psyflow.sim.context import get_context

            ctx = get_context()
            return bool(ctx is not None and getattr(getattr(ctx, "config", None), "strict", False))
        except Exception:
            return False

    def emit(
        self,
        event: TriggerEvent,
        *,
        when: Literal["now", "flip"] = "now",
        win: Any = None,
        wait: bool = True,
    ) -> None:
        """Emit a trigger event now or schedule it for the next flip."""
        if event.code is None and event.payload is None:
            # Backward compatible: None means "no trigger configured".
            self._log(
                {
                    "type": "trigger_skipped",
                    "reason": "code_and_payload_none",
                    "driver": self.name,
                    "when": when,
                    "on_flip": when == "flip",
                }
            )
            return

        # Capability checks (TTL-style pulse/reset conventions).
        effective_strict = self._effective_strict()

        if event.pulse_width_ms is not None and not hasattr(self.driver, "send_pulse"):
            msg = f"Driver {self.name!r} does not support pulse_width_ms (missing send_pulse)."
            if effective_strict:
                raise ValueError(msg)
            self._log(
                {
                    "type": "trigger_capability_missing",
                    "driver": self.name,
                    "missing": "send_pulse",
                    "message": msg,
                    "when": when,
                    "on_flip": when == "flip",
                    "event_name": event.name,
                    "code": event.code,
                    "pulse_width_ms": event.pulse_width_ms,
                    "reset_code": event.reset_code,
                }
            )

        if event.reset_code is not None and event.pulse_width_ms is None and not hasattr(self.driver, "reset"):
            msg = f"Driver {self.name!r} does not support reset_code (missing reset)."
            if effective_strict:
                raise ValueError(msg)
            self._log(
                {
                    "type": "trigger_capability_missing",
                    "driver": self.name,
                    "missing": "reset",
                    "message": msg,
                    "when": when,
                    "on_flip": when == "flip",
                    "event_name": event.name,
                    "code": event.code,
                    "pulse_width_ms": event.pulse_width_ms,
                    "reset_code": event.reset_code,
                }
            )

        emit_id = self._next_id()
        t_planned = time.time()
        planned = {
            "type": "trigger_planned",
            "emit_id": emit_id,
            "when": when,
            "on_flip": when == "flip",
            "t_planned": t_planned,
            "driver": self.name,
            "event_name": event.name,
            "code": event.code,
            "payload_len": (len(event.payload) if isinstance(event.payload, (bytes, str)) else None),
            "pulse_width_ms": event.pulse_width_ms,
            "reset_code": event.reset_code,
            "meta": dict(event.meta) if isinstance(event.meta, dict) else None,
        }
        self._log(planned)

        if when == "now":
            self._execute(event, emit_id=emit_id, t_planned=t_planned, when=when, wait=wait)
            return

        if when == "flip":
            if win is None or not hasattr(win, "callOnFlip"):
                raise ValueError("when='flip' requires a PsychoPy-like window with callOnFlip().")
            win.callOnFlip(self._execute, event, emit_id, t_planned, when, wait)
            return

        raise ValueError(f"Unsupported when={when!r}")

    def _execute(self, event: TriggerEvent, emit_id: int, t_planned: float, when: str, wait: bool) -> None:
        t_sent = time.time()
        t_flip = t_sent if when == "flip" else None
        err = None
        try:
            if event.pulse_width_ms is not None and hasattr(self.driver, "send_pulse"):
                self.driver.send_pulse(event, wait=wait)
            else:
                self.driver.send(event, wait=wait)

            if event.reset_code is not None and event.pulse_width_ms is None and hasattr(self.driver, "reset"):
                self.driver.reset(event.reset_code)
        except Exception as e:
            err = repr(e)
            if self._effective_strict():
                raise
        finally:
            self._log(
                {
                    "type": "trigger_executed",
                    "emit_id": emit_id,
                    "when": when,
                    "on_flip": when == "flip",
                    "t_planned": t_planned,
                    "t_flip": t_flip,
                    "t_sent": t_sent,
                    "driver": self.name,
                    "event_name": event.name,
                    "code": event.code,
                    "payload_len": (len(event.payload) if isinstance(event.payload, (bytes, str)) else None),
                    "pulse_width_ms": event.pulse_width_ms,
                    "reset_code": event.reset_code,
                    "meta": dict(event.meta) if isinstance(event.meta, dict) else None,
                    "error": err,
                }
            )

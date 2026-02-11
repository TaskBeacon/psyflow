from __future__ import annotations

from typing import Any, Callable, Optional

from ..events import TriggerEvent


def _default_encode(event: TriggerEvent) -> Optional[bytes]:
    if event.payload is not None:
        if isinstance(event.payload, bytes):
            return event.payload
        if isinstance(event.payload, str):
            return event.payload.encode("utf-8")
    if event.code is None:
        return None
    code = int(event.code)
    if code < 0 or code > 255:
        raise ValueError(f"Serial trigger code must be in [0,255], got {code}")
    return bytes([code])


class SerialDriver:
    """pyserial-based trigger driver."""

    def __init__(
        self,
        serial_obj: Any,
        *,
        name: str = "serial",
        encode_fn: Callable[[TriggerEvent], Optional[bytes]] = _default_encode,
    ):
        self.name = name
        self._ser = serial_obj
        self._encode = encode_fn

    def open(self) -> None:
        try:
            if hasattr(self._ser, "is_open") and not self._ser.is_open:
                self._ser.open()
        except Exception:
            return

    def close(self) -> None:
        try:
            if hasattr(self._ser, "close"):
                self._ser.close()
        except Exception:
            return

    def send(self, event: TriggerEvent, *, wait: bool = True) -> None:
        payload = self._encode(event)
        if payload is None:
            return
        self._ser.write(payload)


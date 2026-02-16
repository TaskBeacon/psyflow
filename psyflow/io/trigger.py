"""Trigger runtime/driver initialization helpers."""

from typing import Any, Callable, Dict, Optional


def initialize_triggers(
    cfg: Optional[Dict[str, Any]] = None,
    *,
    trigger_func: Optional[Callable[[Any], None]] = None,
    mock: Optional[bool] = None,
):
    """Initialize and open a TriggerRuntime from loaded config."""
    from .drivers.callable import CallableDriver
    from .drivers.mock import MockDriver
    from .drivers.serial import SerialDriver
    from .runtime import TriggerRuntime

    cfg = cfg or {}
    driver_cfg = cfg.get("trigger_driver_config", {}) or {}
    policy_cfg = cfg.get("trigger_policy_config", {}) or {}
    timing_cfg = cfg.get("trigger_timing_config", {}) or {}

    driver_type = str(driver_cfg.get("type", "")).strip().lower()
    if mock is True:
        driver_type = "mock"
    if not driver_type:
        driver_type = "callable" if trigger_func is not None else "serial_url"

    strict = bool(policy_cfg.get("strict", False))

    if driver_type == "mock":
        driver = MockDriver(print_codes=bool(driver_cfg.get("print_codes", True)))
    elif driver_type == "callable":
        if trigger_func is None:
            raise ValueError("initialize_triggers(type='callable') requires trigger_func")
        driver = CallableDriver(
            trigger_func,
            post_delay_s=float(timing_cfg.get("post_delay_s", 0.001)),
        )
    elif driver_type in ("serial_url", "serial_port"):
        import serial

        baudrate = int(driver_cfg.get("baudrate", 115200))
        timeout = float(driver_cfg.get("timeout", 1))

        if driver_type == "serial_port":
            port = str(driver_cfg.get("port", "")).strip()
            if not port:
                raise ValueError("triggers.driver.port is required when type='serial_port'")
            ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        else:
            url = str(driver_cfg.get("url", "loop://")).strip() or "loop://"
            ser = serial.serial_for_url(url, baudrate=baudrate, timeout=timeout)

        prefix_raw = driver_cfg.get("prefix", [1, 225, 1, 0])
        prefix = [int(x) for x in prefix_raw] if prefix_raw is not None else []

        def _encode(event):
            if event.payload is not None:
                if isinstance(event.payload, bytes):
                    return event.payload
                if isinstance(event.payload, str):
                    return event.payload.encode("utf-8")
            if event.code is None:
                return None
            code = int(event.code)
            if code < 0 or code > 255:
                raise ValueError(f"Trigger code must be in [0,255], got {code}")
            return bytes([*prefix, code]) if prefix else bytes([code])

        driver = SerialDriver(ser, encode_fn=_encode)
    else:
        raise ValueError(f"Unsupported triggers.driver.type: {driver_type}")

    runtime = TriggerRuntime(driver, strict=strict)
    runtime.open()
    return runtime

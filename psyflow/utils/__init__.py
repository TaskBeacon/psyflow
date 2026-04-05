"""Utility package for psyflow.

Keep this module lightweight: importing ``psyflow.utils`` should not eagerly
import PsychoPy or other optional dependencies. Public symbols are exposed via
lazy attribute access.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "count_down": ("psyflow.utils.display", "count_down"),
    "initialize_exp": ("psyflow.utils.experiment", "initialize_exp"),
    "list_supported_voices": ("psyflow.utils.voices", "list_supported_voices"),
    "load_config": ("psyflow.utils.config", "load_config"),
    "next_trial_id": ("psyflow.utils.trials", "next_trial_id"),
    "reset_trial_counter": ("psyflow.utils.trials", "reset_trial_counter"),
    "resolve_deadline": ("psyflow.utils.trials", "resolve_deadline"),
    "resolve_trial_id": ("psyflow.utils.trials", "resolve_trial_id"),
    "show_ports": ("psyflow.utils.ports", "show_ports"),
    "taps": ("psyflow.utils.templates", "taps"),
    "validate_config": ("psyflow.utils.config", "validate_config"),
}

__all__ = [
    "count_down",
    "initialize_exp",
    "list_supported_voices",
    "load_config",
    "next_trial_id",
    "reset_trial_counter",
    "resolve_deadline",
    "resolve_trial_id",
    "show_ports",
    "taps",
    "validate_config",
]


if TYPE_CHECKING:
    from .config import load_config as load_config
    from .config import validate_config as validate_config
    from .display import count_down as count_down
    from .experiment import initialize_exp as initialize_exp
    from .ports import show_ports as show_ports
    from .templates import taps as taps
    from .trials import (
        next_trial_id as next_trial_id,
        reset_trial_counter as reset_trial_counter,
        resolve_deadline as resolve_deadline,
        resolve_trial_id as resolve_trial_id,
    )
    from .voices import list_supported_voices as list_supported_voices


def __getattr__(name: str) -> Any:
    spec = _LAZY_ATTRS.get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = spec
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value  # cache for subsequent access
    return value


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(_LAZY_ATTRS.keys()))

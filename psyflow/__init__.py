"""psyflow: A utility package for modular PsychoPy experiment development.

Keep this module lightweight: importing ``psyflow`` should not immediately
import PsychoPy (or other heavy deps). Public symbols are exposed via lazy
attribute access.
"""

from __future__ import annotations

from ._version import __version__

import importlib
from typing import TYPE_CHECKING, Any


_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    # Core classes
    "BlockUnit": ("psyflow.BlockUnit", "BlockUnit"),
    "StimBank": ("psyflow.StimBank", "StimBank"),
    "StimUnit": ("psyflow.StimUnit", "StimUnit"),
    "SubInfo": ("psyflow.SubInfo", "SubInfo"),
    "TaskSettings": ("psyflow.TaskSettings", "TaskSettings"),
    # Trigger runtime/driver (recommended)
    "TriggerRuntime": ("psyflow.io.runtime", "TriggerRuntime"),
    "TriggerEvent": ("psyflow.io.events", "TriggerEvent"),
    "MockDriver": ("psyflow.io.drivers.mock", "MockDriver"),
    "SerialDriver": ("psyflow.io.drivers.serial", "SerialDriver"),
    "FanoutDriver": ("psyflow.io.drivers.fanout", "FanoutDriver"),
    "CallableDriver": ("psyflow.io.drivers.callable", "CallableDriver"),
    # CLI entry
    "cli_main": ("psyflow.cli", "main"),
    # Common utilities
    "show_ports": ("psyflow.utils", "show_ports"),
    "taps": ("psyflow.utils", "taps"),
    "count_down": ("psyflow.utils", "count_down"),
    "load_config": ("psyflow.utils", "load_config"),
    "validate_config": ("psyflow.utils", "validate_config"),
    "initialize_triggers": ("psyflow.io", "initialize_triggers"),
    "initialize_exp": ("psyflow.utils", "initialize_exp"),
    "list_supported_voices": ("psyflow.utils", "list_supported_voices"),
}

__all__ = ["__version__", *_LAZY_ATTRS.keys()]


if TYPE_CHECKING:
    from .BlockUnit import BlockUnit as BlockUnit
    from .StimBank import StimBank as StimBank
    from .StimUnit import StimUnit as StimUnit
    from .SubInfo import SubInfo as SubInfo
    from .TaskSettings import TaskSettings as TaskSettings
    from .cli import main as cli_main
    from .io import initialize_triggers as initialize_triggers
    from .utils import (
        count_down as count_down,
        initialize_exp as initialize_exp,
        list_supported_voices as list_supported_voices,
        load_config as load_config,
        show_ports as show_ports,
        taps as taps,
        validate_config as validate_config,
    )


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

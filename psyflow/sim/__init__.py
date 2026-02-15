"""Simulation responder plugin system for psyflow.

This package is pure Python and intentionally independent from PsychoPy.
"""

from .adapter import (
    HandledResponse,
    ResponderActionError,
    ResponderAdapter,
)
from .contracts import (
    Action,
    Feedback,
    NullResponder,
    Observation,
    ResponderProtocol,
    ScriptedResponder,
    SessionInfo,
)
from .context_helpers import set_trial_context
from .loader import load_responder
from .logging import iter_sim_events, make_sim_jsonl_logger
from .rng import make_rng, make_trial_seed

__all__ = [
    "Action",
    "Feedback",
    "HandledResponse",
    "NullResponder",
    "Observation",
    "ResponderActionError",
    "ResponderAdapter",
    "ResponderProtocol",
    "ScriptedResponder",
    "SessionInfo",
    "load_responder",
    "iter_sim_events",
    "make_rng",
    "make_sim_jsonl_logger",
    "make_trial_seed",
    "set_trial_context",
]

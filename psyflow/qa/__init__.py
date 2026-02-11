"""QA utilities for psyflow tasks.

This subpackage is intentionally pure-Python (no PsychoPy imports) so it can be
used in lightweight static checks and CI.
"""

from .context import QAConfig, QAContext, get_context, log_event, qa_context
from .responder import ScriptedResponder
from .static import contract_lint, load_yaml, static_qa
from .trace import validate_events, validate_trace_csv
from .artifacts import qa_artifact_paths
from .report import FailureCode, QAReport

__all__ = [
    "FailureCode",
    "QAConfig",
    "QAContext",
    "QAReport",
    "ScriptedResponder",
    "contract_lint",
    "get_context",
    "load_yaml",
    "log_event",
    "qa_artifact_paths",
    "qa_context",
    "static_qa",
    "validate_events",
    "validate_trace_csv",
]


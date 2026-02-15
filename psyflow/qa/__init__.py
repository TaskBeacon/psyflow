"""QA utilities for psyflow tasks.

This subpackage is intentionally pure-Python (no PsychoPy imports) so it can be
used in lightweight static checks and CI.
"""

from .artifacts import qa_artifact_paths
from .report import FailureCode, QAReport
from .static import contract_lint, load_yaml, static_qa
from .trace import validate_events, validate_trace_csv

__all__ = [
    "FailureCode",
    "QAReport",
    "contract_lint",
    "load_yaml",
    "qa_artifact_paths",
    "static_qa",
    "validate_events",
    "validate_trace_csv",
]


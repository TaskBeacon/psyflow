from typing import Any

_SESSION_TRIAL_COUNTER = 0

def next_trial_id() -> int:
    """Return an auto-incrementing global trial ID for the current session."""
    global _SESSION_TRIAL_COUNTER
    _SESSION_TRIAL_COUNTER += 1
    return _SESSION_TRIAL_COUNTER

def reset_trial_counter(start_at: int = 0):
    """Reset the global trial counter."""
    global _SESSION_TRIAL_COUNTER
    _SESSION_TRIAL_COUNTER = start_at

def resolve_deadline(value: Any) -> float | None:
    """Resolve a potential duration sequence into a scalar deadline (max value)."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        try:
            return float(max(value))
        except (ValueError, TypeError):
            return None
    return None

def resolve_trial_id(value: Any) -> int | str | None:
    """Resolve trial ID from a scalar, callable, or controller-like object."""
    if value is None or isinstance(value, (int, str)):
        return value
    
    if callable(value):
        try:
            res = value()
            return res if isinstance(res, (int, str)) else str(res)
        except Exception:
            return None
            
    # Support common controller patterns (e.g. AdaptiveController)
    histories = getattr(value, "histories", None)
    if isinstance(histories, dict):
        try:
            done = sum(len(items) for items in histories.values() if hasattr(items, "__len__"))
            return int(done) + 1
        except Exception:
            pass
            
    return str(value)

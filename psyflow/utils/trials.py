from typing import Any
import math

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


def resolve_condition_weights(condition_weights: Any, conditions: Any) -> list[float] | None:
    """Resolve condition weights aligned to a condition label list.

    Parameters
    ----------
    condition_weights : Any
        Either ``None`` (use even generation), a list/tuple aligned to
        ``conditions`` order, or a mapping keyed by condition labels.
    conditions : Any
        Sequence of condition labels.

    Returns
    -------
    list[float] | None
        Normalized/validated weight vector aligned to ``conditions``, or
        ``None`` when no weighted generation is requested.
    """
    if condition_weights is None:
        return None

    if not isinstance(conditions, (list, tuple)):
        raise TypeError("conditions must be a list/tuple when condition_weights is provided.")

    labels = [str(c) for c in list(conditions)]
    if not labels:
        raise ValueError("conditions must be non-empty when condition_weights is provided.")

    values: list[Any]
    if isinstance(condition_weights, dict):
        keyed = {str(k): v for k, v in condition_weights.items()}
        missing = [label for label in labels if label not in keyed]
        extra = [key for key in keyed if key not in labels]
        if missing:
            raise ValueError(f"condition_weights missing entries for condition(s): {missing}")
        if extra:
            raise ValueError(f"condition_weights contains unknown condition key(s): {extra}")
        values = [keyed[label] for label in labels]
    elif isinstance(condition_weights, (list, tuple)):
        if len(condition_weights) != len(labels):
            raise ValueError(
                "condition_weights length mismatch: expected "
                f"{len(labels)} for conditions {labels}, got {len(condition_weights)}"
            )
        values = list(condition_weights)
    else:
        raise TypeError("condition_weights must be None, list/tuple, or mapping by condition label.")

    weights: list[float] = []
    for i, raw in enumerate(values):
        try:
            w = float(raw)
        except Exception as exc:
            raise TypeError(
                f"condition_weights[{i}] could not be parsed as number: {raw!r}"
            ) from exc
        if not math.isfinite(w):
            raise ValueError(f"condition_weights[{i}] must be finite, got {w!r}")
        if w <= 0:
            raise ValueError(f"condition_weights[{i}] must be > 0, got {w!r}")
        weights.append(w)

    if sum(weights) <= 0:
        raise ValueError(f"condition_weights sum must be > 0, got {weights}")

    return weights

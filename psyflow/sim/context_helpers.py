from __future__ import annotations

from typing import Any


def _resolve_deadline(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        try:
            return float(max(value))
        except (ValueError, TypeError):
            return None
    return None


def set_trial_context(
    unit: Any,
    *,
    trial_id: Any,
    phase: str,
    deadline_s: float | list | tuple | None,
    valid_keys: list[str],
    block_id: int | str | None = None,
    condition_id: str | None = None,
    task_factors: dict[str, Any] | None = None,
    stim_id: str | None = None,
    stim_features: dict[str, Any] | None = None,
) -> Any:
    """Populate standard sim observation fields onto a StimUnit-like object.

    The object only needs to expose a ``set_state(**kwargs)`` method.
    """
    factors = dict(task_factors or {})
    return unit.set_state(
        trial_id=trial_id,
        phase=phase,
        deadline_s=_resolve_deadline(deadline_s),
        valid_keys=list(valid_keys or []),
        block_id=block_id,
        condition_id=condition_id,
        task_factors=factors,
        stim_id=stim_id,
        stim_features=stim_features,
    )

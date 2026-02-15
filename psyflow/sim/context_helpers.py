from __future__ import annotations

from typing import Any


def set_trial_context(
    unit: Any,
    *,
    trial_id: int | str | None,
    phase: str,
    deadline_s: float | None,
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
        deadline_s=deadline_s,
        valid_keys=list(valid_keys or []),
        block_id=block_id,
        condition_id=condition_id,
        task_factors=factors,
        stim_id=stim_id,
        stim_features=stim_features,
    )


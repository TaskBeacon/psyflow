from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context


def _parse_condition(condition: Any) -> dict[str, str]:
    if isinstance(condition, dict):
        cond = str(condition.get("condition", "baseline"))
        label = str(condition.get("condition_label", cond))
    elif isinstance(condition, tuple) and len(condition) >= 2:
        cond = str(condition[0])
        label = str(condition[1])
    else:
        cond = str(condition)
        label = cond

    return {
        "condition": cond,
        "condition_label": label,
    }


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run a generic template trial (fixation -> response window -> feedback -> iti)."""
    parsed = _parse_condition(condition)
    trial_id = next_trial_id()
    block_id_val = str(block_id) if block_id is not None else "block_0"
    block_idx_val = int(block_idx) if block_idx is not None else 0

    trial_data = {
        "trial_id": int(trial_id),
        "block_id": block_id_val,
        "block_idx": block_idx_val,
        "condition": parsed["condition"],
        "condition_id": f"{parsed['condition']}_{block_idx_val}_{trial_id}",
        "condition_label": parsed["condition_label"],
    }

    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    fixation_duration = float(getattr(settings, "fixation_duration", 0.5))
    fixation = make_unit(unit_label="fixation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=fixation_duration,
        valid_keys=[],
        block_id=block_id_val,
        condition_id=trial_data["condition_id"],
        task_factors={
            "stage": "fixation",
            "condition": parsed["condition"],
            "block_idx": block_idx_val,
        },
        stim_id="fixation",
    )
    fixation.show(
        duration=fixation_duration,
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    valid_keys = [str(k) for k in list(getattr(settings, "key_list", []))]
    response_window_duration = float(getattr(settings, "response_window_duration", 1.0))
    response_window = make_unit(unit_label="response_window").add_stim(
        stim_bank.get_and_format(
            "trial_prompt",
            condition_label=parsed["condition_label"],
            trial_index=trial_id,
        )
    )
    set_trial_context(
        response_window,
        trial_id=trial_id,
        phase="response_window",
        deadline_s=response_window_duration,
        valid_keys=valid_keys,
        block_id=block_id_val,
        condition_id=trial_data["condition_id"],
        task_factors={
            "stage": "response_window",
            "condition": parsed["condition"],
            "block_idx": block_idx_val,
        },
        stim_id="trial_prompt",
    )
    response_window.capture_response(
        keys=valid_keys,
        duration=response_window_duration,
        onset_trigger=settings.triggers.get("response_prompt_onset"),
        response_trigger=settings.triggers.get("response_key_press"),
        timeout_trigger=settings.triggers.get("response_timeout"),
    )
    response_window.to_dict(trial_data)

    response_key = response_window.get_state("response", None)
    response_rt = response_window.get_state("rt", None)
    responded = response_key is not None

    default_key = valid_keys[0] if valid_keys else ""
    correct_key = str(getattr(settings, "correct_key", default_key))
    response_correct = bool(responded and str(response_key) == correct_key)

    trial_data["responded"] = bool(responded)
    trial_data["response_key"] = str(response_key) if response_key is not None else ""
    trial_data["response_rt"] = float(response_rt) if isinstance(response_rt, (int, float)) else None
    trial_data["response_correct"] = bool(response_correct)
    trial_data["correct_key"] = correct_key

    feedback_duration = float(getattr(settings, "feedback_duration", 0.3))
    feedback_stim = "feedback_hit" if responded else "feedback_miss"
    if feedback_duration > 0.0 and stim_bank.has(feedback_stim):
        feedback = make_unit(unit_label="feedback").add_stim(stim_bank.get(feedback_stim))
        set_trial_context(
            feedback,
            trial_id=trial_id,
            phase="feedback",
            deadline_s=feedback_duration,
            valid_keys=[],
            block_id=block_id_val,
            condition_id=trial_data["condition_id"],
            task_factors={
                "stage": "feedback",
                "condition": parsed["condition"],
                "responded": bool(responded),
                "block_idx": block_idx_val,
            },
            stim_id=feedback_stim,
        )
        feedback.show(
            duration=feedback_duration,
            onset_trigger=settings.triggers.get(f"{feedback_stim}_onset"),
        ).to_dict(trial_data)

    iti_duration = float(getattr(settings, "iti_duration", 0.6))
    iti = make_unit(unit_label="iti").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="iti",
        deadline_s=iti_duration,
        valid_keys=[],
        block_id=block_id_val,
        condition_id=trial_data["condition_id"],
        task_factors={
            "stage": "iti",
            "condition": parsed["condition"],
            "block_idx": block_idx_val,
        },
        stim_id="fixation",
    )
    iti.show(
        duration=iti_duration,
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)

    return trial_data

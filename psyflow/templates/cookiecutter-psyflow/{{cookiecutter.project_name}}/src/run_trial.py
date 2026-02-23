from functools import partial

from psyflow import StimUnit, set_trial_context


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    controller,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """
    Run a single MID trial sequence.
    """
    trial_data = {"condition": condition}
    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    # --- Cue ---
    make_unit(unit_label="cue").add_stim(stim_bank.get(f"{condition}_cue")).show(
        duration=settings.cue_duration,
        onset_trigger=settings.triggers.get(f"{condition}_cue_onset"),
    ).to_dict(trial_data)

    # phase: pre_response_fixation
    anti = make_unit(unit_label="anticipation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        anti,
        trial_id=controller,
        phase="pre_response_fixation",
        deadline_s=settings.anticipation_duration,
        valid_keys=list(settings.key_list),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={"condition": str(condition), "stage": "pre_response_fixation", "block_idx": block_idx},
        stim_id="fixation",
    )
    anti.capture_response(
        keys=settings.key_list,
        duration=settings.anticipation_duration,
        onset_trigger=settings.triggers.get(f"{condition}_anti_onset"),
        terminate_on_response=False,
    )

    early_response = anti.get_state("response", False)
    anti.set_state(early_response=early_response)
    anti.to_dict(trial_data)

    # phase: response_window
    duration = controller.get_duration(condition)
    target = make_unit(unit_label="target").add_stim(stim_bank.get(f"{condition}_target"))
    set_trial_context(
        target,
        trial_id=controller,
        phase="response_window",
        deadline_s=duration,
        valid_keys=list(settings.key_list),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={
            "condition": str(condition),
            "stage": "response_window",
            "block_idx": block_idx,
            "target_duration_s": float(duration),
        },
        stim_id=f"{condition}_target",
    )
    target.capture_response(
        keys=settings.key_list,
        duration=duration,
        onset_trigger=settings.triggers.get(f"{condition}_target_onset"),
        response_trigger=settings.triggers.get(f"{condition}_key_press"),
        timeout_trigger=settings.triggers.get(f"{condition}_no_response"),
    )
    target.to_dict(trial_data)

    make_unit(unit_label="prefeedback_fixation").add_stim(stim_bank.get("fixation")).show(
        duration=settings.prefeedback_duration
    ).to_dict(trial_data)

    # --- Feedback ---
    if early_response:
        delta = settings.delta * -1
        hit = False
    else:
        hit = target.get_state("hit", False)
        if condition == "win":
            delta = settings.delta if hit else 0
        elif condition == "lose":
            delta = 0 if hit else settings.delta * -1
        else:
            delta = 0
    controller.update(hit, condition)

    hit_type = "hit" if hit else "miss"
    fb_stim = stim_bank.get(f"{condition}_{hit_type}_feedback")
    fb = make_unit(unit_label="feedback").add_stim(fb_stim).show(
        duration=settings.feedback_duration,
        onset_trigger=settings.triggers.get(f"{condition}_{hit_type}_fb_onset"),
    )
    fb.set_state(hit=hit, delta=delta).to_dict(trial_data)

    return trial_data

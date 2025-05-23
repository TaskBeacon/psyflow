from psyflow import StimUnit
from functools import partial
from psyflow import StimUnit
from functools import partial

def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    controller=None,
    asset_pool=None,
    trigger_sender=None,
):
    """
    General-purpose run_trial function for psyflow-based tasks.

    This function outlines a typical trial flow:
      1. Fixation
      2. Cue (optional)
      3. Target + response
      4. Feedback (optional)
      5. ITI

    You can adapt this by customizing:
      - condition naming conventions
      - stimulus types
      - response logic
      - controller updates (if applicable)
    """

    # === Trial data container ===
    trial_data = {"condition": condition}

    # === Helper for creating StimUnits ===
    make_unit = partial(StimUnit, win=win, kb=kb,  triggersender=trigger_sender)

    # === 1. Fixation (optional) ===
    if "fixation" in stim_bank.bank:
        make_unit(unit_label="fixation") \
            .add_stim(stim_bank.get("fixation")) \
            .show(duration=settings.fixation_duration,
                  onset_trigger=settings.triggers.get("fixation_onset")) \
            .to_dict(trial_data)

    # === 2. Cue presentation (optional) ===
    if f"{condition}_cue" in stim_bank.bank:
        make_unit(unit_label="cue") \
            .add_stim(stim_bank.get(f"{condition}_cue")) \
            .show(duration=settings.cue_duration,
                  onset_trigger=settings.triggers.get(f"{condition}_cue_onset")) \
            .to_dict(trial_data)

    # === 3. Target + response collection ===
    if f"{condition}_target" in stim_bank.bank:
        target_stim = stim_bank.get(f"{condition}_target")
    elif "target" in stim_bank.bank:
        target_stim = stim_bank.get("target")
    else:
        raise ValueError("Target stimulus not found.")

    correct_key = settings.left_key if "left" in condition else settings.right_key

    target_unit = make_unit(unit_label="target") \
        .add_stim(target_stim) \
        .capture_response(
            keys=settings.key_list,
            correct_keys=correct_key,
            duration=settings.target_duration,
            onset_trigger=settings.triggers.get("target_onset"),
            response_trigger=settings.triggers.get("key_press"),
            timeout_trigger=settings.triggers.get("no_response"),
            terminate_on_response=True
        )
    target_unit.to_dict(trial_data)

    # === 4. Feedback (optional) ===
    if "win_feedback" in stim_bank.bank:
        hit = target_unit.get_state("hit", False)
        feedback_stim = stim_bank.get("win_feedback" if hit else "lose_feedback")

        make_unit(unit_label="feedback") \
            .add_stim(feedback_stim) \
            .show(duration=settings.feedback_duration,
                  onset_trigger=settings.triggers.get("feedback_onset")) \
            .to_dict(trial_data)

        if controller:
            controller.update(hit)

    # === 5. ITI (optional) ===
    if "iti_stim" in stim_bank.bank:
        make_unit(unit_label="iti") \
            .add_stim(stim_bank.get("iti_stim")) \
            .show(duration=settings.iti_duration)

    return trial_data

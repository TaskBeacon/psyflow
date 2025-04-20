from psyflow import TrialUnit
from functools import partial

def run_trial(win, kb, settings, condition, stim_dict, stim_bank,  triggersender, triggerbank):
    """
    Generic trial:
      1. Fixation
      2. Cue
      3. Stimulus + response capture
      4. Feedback
    """
    trial_data = {"condition": condition}
    make_unit = partial(TrialUnit, win=win, triggersender=triggersender)

    # 1. Fixation
    make_unit(unit_label="fixation") \
        .add_stim(stim_bank["fixation"]) \
        .show(duration=settings.timing.fixation_duration, 
              onset_trigger=triggerbank.get("fixation_onset")) \
        .to_dict(trial_data)

    # 2. Cue
    make_unit(unit_label="cue") \
        .add_stim(stim_dict["cue"]) \
        .show(duration=settings.timing.cue_duration, 
              onset_trigger=triggerbank.get(f"{condition}_cue_onset")) \
        .to_dict(trial_data)

    # 3. Stimulus + response
    stim = make_unit(unit_label="stimulus") \
        .add_stim(stim_dict["stimulus"])
    stim.capture_response(
        keys=settings.task.key_list,
        duration=settings.timing.stimulus_duration,
        onset_trigger=triggerbank.get(f"{condition}_stim_onset"),
        response_trigger=triggerbank.get(f"{condition}_key_press"),
        timeout_trigger=triggerbank.get(f"{condition}_no_response"),
    )
    stim.to_dict(trial_data)

    # 4. Feedback
    # (you can adapt this section per‑task)
    fb = make_unit(unit_label="feedback") \
        .add_stim(stim_bank["feedback"]) \
        .show(duration=settings.timing.feedback_duration,
              onset_trigger=triggerbank.get(f"{condition}_fb_onset"))
    fb.to_dict(trial_data)

    # Any controller update, state logging, etc, goes here

    return trial_data

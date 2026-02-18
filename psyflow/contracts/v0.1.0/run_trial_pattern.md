# run_trial.py Pattern (v0.1.0)

A compliant `src/run_trial.py` should look like this (shape, not exact code):

```python
from psyflow import StimUnit, set_trial_context


def run_trial(win, kb, settings, condition, stim_bank, controller, trigger_runtime, block_id=None, block_idx=None):
    trial_data = {}

    # preparatory phase (task-specific naming)
    StimUnit("cue", win, kb, runtime=trigger_runtime) \
        .add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.cue_duration)

    # response window phase (name can be choice/decision/offer/probe/...)
    choice = StimUnit("choice", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("choice_screen"))
    set_trial_context(
        choice,
        trial_id=1,
        phase="choice",
        deadline_s=1.2,
        valid_keys=list(settings.key_list),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={"condition": str(condition), "block_idx": block_idx},
    )
    choice.capture_response(keys=settings.key_list, duration=1.2)

    # outcome/feedback phase
    StimUnit("feedback", win, kb, runtime=trigger_runtime) \
        .add_stim(stim_bank.get("feedback")) \
        .show(duration=1.0)

    return trial_data
```

Key requirements:
- `run_trial(...)` function present
- task flow is auditable with task-specific stage names (no MID-only naming requirement)
- at least one response window uses `set_trial_context(...)` + `capture_response(...)`
- context includes `trial_id`, `phase`, `deadline_s`, `valid_keys`
- returns serializable trial-level data

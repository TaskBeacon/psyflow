# run_trial.py Pattern (v0.1.0)

A compliant `src/run_trial.py` should look like this (shape, not exact code):

```python
from psyflow import StimUnit, set_trial_context


def run_trial(win, kb, settings, condition, stim_bank, controller, trigger_runtime, block_id=None, block_idx=None):
    trial_data = {}

    # cue
    StimUnit("cue", win, kb, runtime=trigger_runtime) \
        .add_stim(stim_bank.get(f"{condition}_cue")) \
        .show(duration=settings.cue_duration)

    # anticipation
    anti = StimUnit("anticipation", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("fixation"))
    set_trial_context(
        anti,
        trial_id=1,
        phase="anticipation",
        deadline_s=1.2,
        valid_keys=list(settings.key_list),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={"condition": str(condition), "block_idx": block_idx},
    )
    anti.capture_response(keys=settings.key_list, duration=settings.anticipation_duration)

    # target
    target = StimUnit("target", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get(f"{condition}_target"))
    set_trial_context(
        target,
        trial_id=1,
        phase="target",
        deadline_s=0.2,
        valid_keys=list(settings.key_list),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={"condition": str(condition), "block_idx": block_idx},
    )
    target.capture_response(keys=settings.key_list, duration=0.2)

    # feedback
    StimUnit("feedback", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("feedback")).show(duration=1.0)

    return trial_data
```

Key requirements:
- `run_trial(...)` function present
- stage order is auditable (`cue -> anticipation -> target -> feedback`)
- context injected for response windows (`trial_id`, `phase`, `deadline_s`, `valid_keys`)
- returns serializable trial-level data

# TaskSettings, seeds, and condition weights

`TaskSettings` is the framework-level container for runtime configuration. It gives you one object for:

- window settings
- task shape
- response keys
- seeds and block seeds
- output paths
- optional condition weights
- subject-attached metadata

It is the right place for generic runtime configuration. It is not the place to hide arbitrary task logic.

## Build settings from the flattened task config

The current pattern is:

```python
from psyflow import TaskSettings, load_config

cfg = load_config("config/config.yaml")
settings = TaskSettings.from_dict(cfg["task_config"])
```

That `task_config` bundle should already reflect the merged `window`, `task`, and timing-related sections from your config.

## Add participant info before writing outputs

After collecting participant info:

```python
subject_data = {"subject_id": "S01", "session_id": "01"}
settings.add_subinfo(subject_data)
```

This does several things:

- attaches the subject fields onto the settings object
- resolves the per-subject seed if needed
- creates the output directory when missing
- derives `log_file`, `res_file`, and `json_file`

The current default output root is:

```text
./outputs/human
```

not the older `./data` examples from the outdated docs.

## Use `from_dict()` for known fields plus extras

`from_dict()` handles two categories:

- known dataclass fields become constructor values
- extra keys become attached attributes

That makes it possible to keep nested config available on `settings` without manually extending the class every time.

## Seed behavior

The built-in seed fields are:

- `overall_seed`
- `block_seed`
- `seed_mode`

The important modes are:

- `same_across_sub`: all subjects share the same derived block seeds
- `same_within_sub`: seeds are derived from `subject_id`, so each subject gets a stable but different sequence

If `block_seed` is not supplied, PsyFlow generates per-block seeds for you.

## Condition weights moved into `TaskSettings`

This is a recent framework change.

Weighted condition generation should now use:

```python
weights = settings.resolve_condition_weights()
```

instead of the older utility-layer resolver.

`resolve_condition_weights()` accepts:

- `None`
- a list or tuple aligned to `settings.conditions`
- a mapping keyed by condition label

It validates:

- length consistency
- key coverage
- numeric parsing
- finite values
- strictly positive weights

## Minimal example

```python
from psyflow import TaskSettings

settings = TaskSettings.from_dict(
    {
        "task_name": "stroop",
        "total_blocks": 2,
        "total_trials": 48,
        "conditions": ["congruent", "incongruent"],
        "condition_weights": {"congruent": 3, "incongruent": 1},
        "key_list": ["f", "j"],
        "seed_mode": "same_within_sub",
    }
)

settings.add_subinfo({"subject_id": "S07"})
weights = settings.resolve_condition_weights()
```

## What belongs here and what does not

Good fits for `TaskSettings`:

- counts, durations, keys, seeds, output roots
- task-level conditions and condition weights
- participant metadata needed across the task

Poor fits:

- large stimulus definitions
- raw participant-facing text that should live in config/stimulus templates
- ad hoc controller state that only matters inside one custom task module

## Save a settings snapshot when useful

After `add_subinfo()`, you can archive the full resolved settings:

```python
settings.save_to_json()
```

That is useful for QA review and debugging, especially when randomized parameters or subject-attached values matter.

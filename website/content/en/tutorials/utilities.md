# Utilities for config, runtime, trial IDs, and voices

PsyFlow's utility layer is intentionally small. These helpers exist to remove generic boilerplate, not to replace task-specific reasoning.

## The current public utilities

The maintained exports from `psyflow.utils` are:

- `load_config`
- `validate_config`
- `initialize_exp`
- `count_down`
- `show_ports`
- `taps`
- `list_supported_voices`
- `next_trial_id`
- `reset_trial_counter`
- `resolve_deadline`
- `resolve_trial_id`

## Config and validation

Use the config helpers before runtime code starts mutating state:

```python
from psyflow import load_config, validate_config

cfg = load_config("config/config.yaml")
validate_config(cfg)
```

`load_config()` is the maintained entry because it prepares the normalized config structure that the rest of the framework expects.

## Experiment initialization

Use `initialize_exp()` to create the standard PsychoPy window and keyboard pair from `TaskSettings`:

```python
from psyflow import TaskSettings, initialize_exp

settings = TaskSettings.from_dict(cfg["task_config"])
win, kb = initialize_exp(settings)
```

That keeps your startup code short and consistent across tasks.

## Countdowns and ports

Two of the simplest utilities are still worth using because they keep generic setup code out of each task:

```python
from psyflow import count_down, show_ports

count_down(win, 3)
show_ports()
```

`count_down()` is useful before blocks. `show_ports()` is useful when debugging serial or hardware setup.

## TAPS template helper

Use `taps()` when you want a framework-provided starting point for a canonical package layout rather than hand-rolling directory conventions.

This matters more now because PsyFlow is being documented as one layer inside a larger auditable task package, not as an isolated runtime helper library.

## Voice inventory

If your task builds localized audio instructions, query installed voices instead of guessing:

```python
from psyflow import list_supported_voices

voices = list_supported_voices()
```

That helper is especially useful before generating task-specific instruction audio from config.

## Trial helpers

The newer trial helper set covers generic bookkeeping that used to get reimplemented inside controller objects:

```python
from psyflow import (
    next_trial_id,
    reset_trial_counter,
    resolve_deadline,
    resolve_trial_id,
)
```

### `next_trial_id()` and `reset_trial_counter()`

Use these when a global sequential trial ID is enough:

```python
trial_id = next_trial_id()
reset_trial_counter()
```

### `resolve_deadline()`

This helper reduces a scalar or sequence duration to one deadline value:

```python
deadline_s = resolve_deadline([0.6, 0.8, 1.2])
```

It returns the `max()` when the input is a sequence. That same idea now appears inside simulation context helpers too.

### `resolve_trial_id()`

This helper accepts a few common patterns:

- scalar IDs
- callables
- controller-like objects with `histories`

Use it when you want a generic trial identifier without binding the task to one controller API.

## Recommended stance

Use these utilities when:

- the problem is generic across tasks
- the public helper already exists
- using the helper makes the task more readable

Do not use them to hide paradigm-specific logic that should remain explicit in your task modules.

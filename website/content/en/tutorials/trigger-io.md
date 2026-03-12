# Trigger runtime and hardware I/O

The current trigger model is more structured than the old `TriggerSender`-centric docs.

PsyFlow now separates:

- semantic trigger events
- runtime timing semantics
- hardware drivers
- audit logging

That split makes tasks easier to keep hardware-agnostic.

## The current mental model

Your task should describe **what happened**:

- cue onset
- target onset
- feedback onset
- custom payload event

The runtime and driver layers decide **how** the signal is delivered.

## Initialize triggers

The main helper is:

```python
from psyflow import initialize_triggers

runtime = initialize_triggers(cfg)
```

`initialize_triggers()` currently reads:

- `trigger_driver_config`
- `trigger_policy_config`
- `trigger_timing_config`

from the loaded config bundle.

## Supported driver modes

The current initialization path supports:

- `mock`
- `callable`
- `serial_port`
- `serial_url`

There is also a public `FanoutDriver` for sending to multiple downstream drivers.

Use `mock` during local development and QA whenever possible.

## TriggerRuntime owns timing semantics

`TriggerRuntime` handles:

- `when="now"` vs `when="flip"`
- capability checks
- strict vs best-effort behavior
- planned and executed event logs

Example:

```python
from psyflow import TriggerEvent

runtime.emit(
    TriggerEvent(code=11, name="cue_onset"),
    when="flip",
    win=win,
)
```

If the driver lacks a requested capability, strict mode can raise immediately instead of silently continuing.

## Why this is better than older patterns

Older task code often mixed together:

- event semantics
- timing rules
- serial encoding
- reset/pulse logic

The current split lets you change hardware wiring without rewriting trial code.

## Pulse width and reset behavior

The runtime now checks whether the selected driver supports:

- `send_pulse`
- `reset`

If you request `pulse_width_ms` or `reset_code` on an incompatible driver:

- strict mode raises
- non-strict mode logs a capability-missing record

That behavior is useful in QA because it surfaces hardware assumptions earlier.

## Logging and QA

TriggerRuntime can log to:

- the QA event sink
- an optional JSONL logger
- PsychoPy logging

This preserves a reviewable record of both planned and executed trigger events.

## Recommended task-side pattern

Keep trigger usage compact and semantic:

```python
from psyflow import TriggerEvent

runtime.emit(TriggerEvent(code=21, name="target_onset"), when="flip", win=win)
```

Avoid:

- embedding serial byte formatting inside `run_trial.py`
- binding task logic to one vendor protocol
- creating custom one-off trigger wrappers unless the framework model truly cannot express the need

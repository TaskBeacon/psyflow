# QA/Sim Runtime Guide

This guide describes the current task runtime model for `human`, `qa`, and `sim`.

## Mode Model

Modes are selected by task entrypoint arguments, not by root `psyflow` subcommands:
- `human`: real keyboard input (default)
- `qa`: deterministic/scripted runtime checks
- `sim`: responder plugin simulation

Typical usage from a task directory:

```bash
python main.py
python main.py qa --config config/config_qa.yaml
python main.py sim --config config/config_sim.yaml
```

Or use shortcut launchers:

```bash
psyflow-run <task_dir>
psyflow-qa <task_dir> --config config/config_qa.yaml
psyflow-sim <task_dir> --config config/config_sim.yaml
```

## Required Task Wiring

To support QA/sim, a task `main.py` must:
1. Parse `mode` + `config` arguments.
2. Build runtime context via `psyflow.context_from_config(...)`.
3. Execute task flow inside `psyflow.runtime_context(...)` for `qa`/`sim`.
4. Keep human path unchanged when mode is `human`.

## Responder Injection Seam

Injected responses flow through:
- `StimUnit.capture_response(...)`
- `StimUnit.wait_and_continue(...)`

Validation and policy are centralized in:
- `psyflow.sim.ResponderAdapter`

Responder contract:
- `Observation`
- `Action`
- `Feedback`
- `ResponderProtocol`

Built-in responders:
- `ScriptedResponder`
- `NullResponder`

## Config Shape

Simulation settings are read from task YAML under `sim`:

```yaml
sim:
  output_dir: outputs/sim
  seed: 11
  policy: warn
  responder:
    type: src.sampler:MidSamplerResponder
    kwargs:
      key: space
```

QA settings are read from task YAML under `qa`:

```yaml
qa:
  output_dir: outputs/qa
  enable_scaling: true
  timing_scale: 0.2
  min_frames: 2
```

## Artifacts

Typical artifacts emitted by task runtime:
- QA: `outputs/qa/qa_trace.csv`, `outputs/qa/qa_events.jsonl`
- Sim: `outputs/sim/qa_trace.csv`, `outputs/sim/sim_events.jsonl`

Exact paths depend on each task config file.

## QA Pass Metadata Updates

`psyflow-qa` runs static checks + runtime execution + artifact validation.
When QA passes, it can promote task maturity and refresh README maturity badge:

```bash
psyflow-qa <task_dir> --set-maturity smoke_tested
```

Flags:
- `--set-maturity <value>`: promotion target (`smoke_tested` default).
- `--no-maturity-update`: skip `taskbeacon.yaml` / `README.md` updates.

# QA Runner + Scripted Responder (Plan)

This document turns the "static QA + runtime QA" proposal into an implementable plan with minimal churn.

Design goals:
- Minimal changes to existing task code.
- One stable seam for response injection: `StimUnit.capture_response(...)` (and `StimUnit.wait_and_continue(...)` for common instruction screens).
- Deterministic artifacts under `outputs/qa/` so a repair loop can be mechanical.

Non-goals (for now):
- Headless PsychoPy simulation (keep as future work).
- Correctness/oracle logic baked into the responder schema (avoid answer leakage).

## Modes

We standardize a simple mode switch:
- `human`: real keyboard input (default)
- `qa`: scripted responder + QA artifacts
- `sim`: reserved for future headless simulation

Tasks should read `PSYFLOW_MODE` (defaults to `human`) and behave accordingly (skip GUI forms, use mock triggers, write QA artifacts).

## Artifacts Contract

QA runner owns output paths (tasks should follow these paths in QA mode):
- `outputs/qa/qa_report.json`
- `outputs/qa/static_report.json` (static QA results)
- `outputs/qa/contract_report.json` (acceptance/contract lint results)
- `outputs/qa/qa_trace.csv`
- `outputs/qa/qa_events.jsonl` (optional, but recommended)

## Phase C: Static QA (No PsychoPy)

### C1. Config + Asset Validation
Checks:
- YAML files parse and are mappings
- Required config sections exist (if provided)
- Basic numeric sanity: timing values should be positive
- Required assets exist (if acceptance criteria lists them)

### C2. Contract Lint (Static)
This does not require a runtime trace. It validates that the *declared* contract is present:
- acceptance criteria file exists and has required fields
- required output columns list is non-empty
- optional value-range rules are well-formed

Recommended acceptance criteria file: `acceptance_criteria.yaml` at the task root.

Minimal example:
```yaml
required_columns:
  - condition
  - target_response
  - target_rt

# Optional (recommended)
# expected_trial_count: 180
# allowed_keys: ["space", "left", "right"]
# triggers_required: false
```

## Phase A': Runtime QA (Real PsychoPy Run, Scripted Input)

### Response Injection Seam
Implement scripted responses in `StimUnit.capture_response(...)` (and `StimUnit.wait_and_continue(...)`):
- Build an `Observation` dict with minimal, responder-useful fields:
  - `unit_label`, `phase_label` (if any), `deadline_s`, `valid_keys`
  - stimulus descriptor: `stim_id` and/or `stim_features` (if present in state)
  - `response_window_open` and `response_window_s`
  - neutral `condition_id` / factor-coded `task_factors` if provided (avoid response-coded leakage)
- Call `responder.act(observation)` -> `{key, rt}` (or `(key, rt)`).
- Drive the same state fields as the keyboard path uses.

### QA Timing Scaling (Optional)
Provide opt-in scaling (default OFF) to shorten runs:
- `qa.enable_scaling` (default false)
- `qa.timing_scale` (default 1.0)
- `qa.min_frames` (default 2 in QA mode)

Guardrails:
- never scale below one refresh interval when using real flips
- log both nominal and scaled durations into state in QA mode

### Triggers: Planned vs Executed (QA Mock Mode)
In QA mode:
- log `trigger_planned` when a trigger is scheduled for a flip
- log `trigger_executed` when the trigger send path runs
- record timestamps and ordering in `qa_events.jsonl`

### Runtime Trace Validation
After the run, validate the produced trace (usually `outputs/qa/qa_trace.csv`):
- required columns exist (from acceptance criteria)
- generic invariants:
  - any `*_rt` must be `None` or non-negative
  - if both `*_rt` and matching `*_duration` exist, check `rt <= duration`
  - if `*_key_press` exists, ensure consistency with `*_response` and `*_rt`
- optional trigger check: planned codes should have matching executed codes

## QA Runner CLI

`psyflow-qa` runs:
1) Static QA (C1 + C2) always
2) Optional runtime command (A') if provided
3) Trace + event validation if runtime ran

Typical usage from a task directory:
```bash
psyflow-qa . --runtime-cmd "python main.py"
```

The runner sets env vars for the subprocess:
- `PSYFLOW_MODE=qa`
- `PSYFLOW_QA_OUTPUT_DIR=outputs/qa`
- `PSYFLOW_QA_ENABLE_SCALING=0|1`
- `PSYFLOW_QA_TIMING_SCALE=...`
- `PSYFLOW_QA_MIN_FRAMES=...`
- `PSYFLOW_QA_RESPONDER=scripted`
- `PSYFLOW_QA_RESPONDER_KEY=space` (optional)
- `PSYFLOW_QA_RESPONDER_RT=0.2` (optional)

## qa_report.json Triage Taxonomy

Standard failure codes for automated repair loops:
- `CONFIG_INVALID`
- `ASSET_MISSING`
- `CONTRACT_INVALID`
- `TRIGGER_INVALID`
- `KEYS_INVALID`
- `RUNTIME_EXCEPTION`
- `LOG_SCHEMA_MISMATCH`
- `INVARIANT_VIOLATION`
- `BALANCE_OFF`
- `TRIGGER_MISSING`

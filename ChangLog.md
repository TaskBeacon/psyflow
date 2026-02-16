# psyflow change log

## 0.1.8 (2026-02-16)

### Summary
- Standardized responder configuration on `responder.type` (built-ins or import path); removed `responder.kind`/`responder.class` behavior.
- Strengthened `psyflow-qa` into a strict gate:
  - `qa.acceptance_criteria` is now required in `config/config_qa.yaml`.
  - static + runtime + trace/events validation remains bundled in one command.
- Added automatic post-QA metadata refresh on pass:
  - promotes `taskbeacon.yaml` `maturity` (no downgrade),
  - updates README maturity badge to a cleaner flat-square style.
- Hardened README badge update for non-UTF8 files via encoding fallback.
- Updated templates and MID example configs to use `type` consistently (`triggers.driver.type`, `sim.responder.type`).
- Updated docs/tests for the new QA/sim contract and launcher behavior.

### Files (high impact)
- `psyflow/task_launcher.py`
- `psyflow/sim/loader.py`
- `psyflow/sim/context.py`
- `tests/test_task_launcher.py`
- `tests/test_responder_contract.py`
- `tests/test_sim_golden.py`
- `docs/tutorials/cli_usage.md`
- `docs/tutorials/qa_runner.md`
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/config/config.yaml`
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/config/config_qa.yaml`
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/config/config_sim.yaml`
- `pyproject.toml`

## 0.1.7 (2026-02-15)

### Summary
- Removed `qa` and `sim` subcommands from root CLI (`psyflow` now exposes `init` only).
- Standardized task execution on explicit task entrypoint arguments (`python main.py [human|qa|sim] --config ...`).
- Removed framework emphasis on env-driven QA/sim wrappers from docs; documentation now points to task-level mode/config flow.

### Breaking changes
- Removed `psyflow qa ...` command.
- Removed `psyflow sim ...` command.
- QA/sim runs should now be started from the task script directly.

### Updated files
- `psyflow/cli.py`
- `tests/test_cli_root.py`
- `docs/tutorials/cli_usage.md`
- `docs/tutorials/qa_runner.md`

## 0.1.6 (2026-02-15)

### Summary
- Added a sampler-ready simulation architecture with a stable responder plugin contract (`SessionInfo`, `Observation`, `Action`, `Feedback`, lifecycle hooks).
- Added a centralized responder adapter and policy layer (`strict|warn|coerce`) used by `StimUnit.capture_response()` and `StimUnit.wait_and_continue()` so injected responses flow through one validation seam.
- Added deterministic simulation plumbing (seed/session/rng), structured JSONL simulation audit logs, and replay helpers.
- Added plugin loader/config support (built-ins + external import-path responders) and a demo external responder.
- Moved runtime context/session plumbing under `psyflow.sim.context` so responder/runtime logic stays in `sim`.
- Updated template MID task and T000006 MID task to standardize trial context fields (`trial_id`, `phase`, `deadline_s`, `valid_keys`, `condition_id`, `task_factors`) for simulation readiness.
- Added contract and determinism tests for responder plugins and sim runs.
- CLI redesign: moved to one root command `psyflow` with subcommands `init`, `qa`, `sim` for compact, terminal-friendly usage.
- Breaking packaging change: removed separate script entrypoints (`psyflow-init`, `psyflow-qa`, `psyflow-sim`) in favor of `psyflow`.
- Added clearer CLI terminal summaries for QA/sim runs (status + artifact paths).
- Neutralized runtime env names (`PSYFLOW_RESPONDER_*`, `PSYFLOW_OUTPUT_DIR`, `PSYFLOW_*` timing knobs) to remove QA-specific naming in simulation paths.
- Added shared runtime command executor helpers used by both `qa` and `sim` commands.

### Breaking changes
- CLI entrypoints changed:
  - old: `psyflow-init`, `psyflow-qa`, `psyflow-sim`
  - new: `psyflow init`, `psyflow qa`, `psyflow sim`
- `psyflow.__init__` CLI export changed from `climain` to `cli_main`.

### New modules
- `psyflow/sim/contracts.py`
- `psyflow/sim/adapter.py`
- `psyflow/sim/loader.py`
- `psyflow/sim/logging.py`
- `psyflow/sim/rng.py`
- `psyflow/sim/context_helpers.py`
- `psyflow/sim/context.py`
- `psyflow/sim/__init__.py`
- `psyflow/sim_command.py`
- `examples/sim/demo_responder.py`
- `tests/test_responder_contract.py`
- `tests/test_sim_golden.py`
- `tests/test_sim_command.py`
- `tests/test_cli_root.py`

### Core updates
- `psyflow/StimUnit.py`
- `psyflow/sim/context.py`
- `psyflow/qa/__init__.py`
- `psyflow/qa_command.py`
- `psyflow/sim_command.py`
- `psyflow/cli.py`
- `psyflow/commands/runtime.py`
- `psyflow/utils/config.py`
- `psyflow/__init__.py`
- `pyproject.toml`
- `setup.py`

### Template/docs updates
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/main.py`
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/src/run_trial.py`
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/config/config.yaml`
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/acceptance_criteria.yaml`
- `README.md`
- `docs/tutorials/cli_usage.md`
- `docs/tutorials/qa_runner.md`
- `docs/tutorials/getting_started.md`
- `docs/tutorials/getting_started_cn.md`

## 0.1.5 (2026-02-12)

### Summary
- `StimUnit.add_stim(...)` now recognizes PsychoPy runtime audio backends (via `_SoundBase` and resolved backend classes), fixing false rejections of valid sound stimuli.
- Unsupported stimulus objects in `StimUnit.add_stim(...)` now emit a warning and raise a clearer `TypeError` that lists supported classes.
- `TaskSettings.from_dict(...)` was hardened:
  - validates that input config is a dict,
  - passes only `init=True` dataclass fields into constructor,
  - validates `trial_per_block` / `trials_per_block` aliases for consistency,
  - enforces declared trials-per-block matches `ceil(total_trials / total_blocks)` when provided.
- `initialize_exp(...)` now defaults to `settings.screen` when `screen_id` is not explicitly passed.

### Files
- `psyflow/StimUnit.py`
- `psyflow/TaskSettings.py`
- `psyflow/utils/experiment.py`

## 0.1.4 (2026-02-12)

### Summary
- Breaking cleanup: removed `TriggerSender` compatibility layer; trigger flow is now `TriggerRuntime` only.
- Added `initialize_triggers(...)` bootstrap under `psyflow.io`, returning an opened `TriggerRuntime`.
- Added `TriggerRuntime.send(code, wait=True)` for simple code-based trigger sends.
- `StimUnit` now consumes `runtime=` directly and no longer supports legacy `triggersender=` fallback.
- Utility cleanup: trigger bootstrap moved out of `utils`; display helper module renamed to `utils/display.py`; serial-port alias cleanup.
- Cookiecutter template updated to the runtime-first trigger pattern (including QA mock setup).

### Trigger API Simplification (Runtime-First)

Files:
- `psyflow/TriggerSender.py` (removed)
- `psyflow/io/runtime.py`
- `psyflow/io/trigger.py`
- `psyflow/io/__init__.py`
- `psyflow/StimUnit.py`
- `psyflow/__init__.py`

#### What changed
- Removed `TriggerSender` and its exports from the public package API.
- `initialize_triggers(...)` now builds driver + `TriggerRuntime`, calls `runtime.open()`, and returns the runtime directly.
- Added `TriggerRuntime.send(...)` as a convenience for immediate integer trigger sends.
- `StimUnit` trigger path is now runtime-only:
  - constructor uses `runtime=...`
  - internal trigger emit path uses `runtime.emit(...)`
  - legacy `triggersender` fallback path was removed.

#### Migration pattern
```python
# before
from psyflow import TriggerSender
trigger_sender = TriggerSender(...)
trigger_sender.send(code)
StimUnit("trial", win, kb, triggersender=trigger_sender)

# after
from psyflow import initialize_triggers
trigger_runtime = initialize_triggers(cfg)
trigger_runtime.send(code)
StimUnit("trial", win, kb, runtime=trigger_runtime)
```

### Utility/Module Structure Cleanup

Files:
- `psyflow/utils/ports.py`
- `psyflow/utils/display.py` (renamed from `handy_display.py`)
- `psyflow/utils/__init__.py`
- `psyflow/io/trigger.py` (trigger bootstrap moved from `utils`)

#### What changed
- Removed `list_serial_ports()` alias; standardized on `show_ports()`.
- Renamed timing/display helper module to `utils/display.py` (exported API `count_down` remains available).
- Moved trigger bootstrap ownership into `psyflow.io` for clearer package boundaries.

### Template Migration (New Default Pattern)

Files:
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/main.py`
- `psyflow/templates/cookiecutter-psyflow/{{cookiecutter.project_name}}/src/run_trial.py`

#### What changed
- Template now initializes triggers via `initialize_triggers(cfg)`.
- QA mode uses `initialize_triggers(mock=True)` (no hardware dependency).
- Task code uses `trigger_runtime.send(...)` and passes `runtime=trigger_runtime` into `StimUnit`.
- Runtime is closed via `trigger_runtime.close()` during teardown.

## 0.1.3 (2026-02-11)

### Summary
- Timing/response-stage fixes in `StimUnit` (flip-synced stamps, RT consistency, close semantics, flip-locked offsets).
- Trigger sending made safer for flip callbacks (`TriggerSender.send(..., wait=False)` path).
- New trigger architecture (EEG/fMRI-ready): `TriggerRuntime` + pluggable drivers (`MockDriver`, `SerialDriver`, `FanoutDriver`), with `TriggerSender` kept as a thin compatibility wrapper.
- Added QA tooling: `psyflow-qa` CLI + `psyflow.qa` helpers for static contract checks and runtime trace/event validation with standardized artifacts under `outputs/qa/`.
- Added QA-mode scripted response injection in `StimUnit.capture_response()` and `StimUnit.wait_and_continue()` (no PsychoPy `Keyboard` emulation), plus optional QA timing scaling and trigger planned/executed event logging.
- Correctness fixes: `BlockUnit.summarize()` no longer crashes; `taps()` locates templates correctly.
- Packaging/import cleanup: Python >= 3.10 declared; LLM utilities removed (deps/docs/exports cleaned); `import psyflow` is now lazy.
- Docs hygiene: docs deployment now does a clean build; trigger/CLI tutorials updated to be copy-paste safe.
- Basic CI smoke checks added.

### QA runner + scripted responder (static QA + runtime QA)

Files:
- `psyflow/qa/*`
- `psyflow/qa_cli.py`
- `psyflow/StimUnit.py`
- `pyproject.toml`
- `setup.py`
- `docs/tutorials/qa_runner.md`
- `docs/index.rst`

#### What changed
- Added a lightweight QA runner CLI: `psyflow-qa <task_dir> [--runtime-cmd \"python main.py\"]`.
  - Always runs static checks (config/acceptance contract lint).
  - Writes machine-readable static artifacts:
    - `outputs/qa/static_report.json`
    - `outputs/qa/contract_report.json`
  - If `--runtime-cmd` is provided, runs the task in a subprocess with `PSYFLOW_MODE=qa` and validates:
    - `outputs/qa/qa_trace.csv` against `acceptance_criteria.yaml` (required columns) + generic invariants.
    - `outputs/qa/qa_events.jsonl` for trigger planned vs executed mismatches (when present).
- Introduced a pure-Python `psyflow.qa` subpackage (no PsychoPy imports) for:
  - acceptance criteria lint (`contract_lint`)
  - static checks (`static_qa`)
  - trace CSV validation (`validate_trace_csv`)
  - QA event validation (`validate_events`)
  - standardized failure taxonomy in `outputs/qa/qa_report.json`.
  - optional static validation of `task.key_list` (non-empty, subset of `allowed_keys` when provided) and trigger-code sanity (int-or-null, uniqueness when present).
- `pyyaml` is required only when loading YAML files from disk (`load_yaml()`); the QA modules remain importable in minimal environments (e.g., CI) without installing dependencies.

#### Responder injection seam (psyflow-level, minimal surface)
- `StimUnit.capture_response()` and `StimUnit.wait_and_continue()` can now inject scripted responses when a QA context is active (`mode=qa`):
  - responder acts on an `Observation` dict (stim descriptor fields are optional and pulled from `StimUnit` state when present).
  - no attempt is made to emulate PsychoPy's `Keyboard` API globally.

#### QA timing scaling (opt-in)
- QA mode supports opt-in duration scaling with guardrails:
  - default: scaling disabled
  - never below one refresh interval
  - `min_frames` default 2 in QA mode
  - logs both nominal and scaled durations into state (`*_duration_nominal`, `*_duration_scaled`) when scaling is enabled.

#### Trigger planned vs executed logging (QA mode)
- In QA mode, flip-scheduled triggers are logged as:
  - `trigger_planned` (when scheduled)
  - `trigger_executed` (when the send path runs)
  - JSONL stream: `outputs/qa/qa_events.jsonl` (when QA context is active).

#### Template updates (cookiecutter)
- The bundled task template now includes:
  - `acceptance_criteria.yaml` with required columns and basic expectations.
  - `config/config.yaml` so the scaffold runs out of the box.
  - `PSYFLOW_MODE=qa` support to skip GUI subject info and avoid hardware triggers.

### TriggerRuntime + Driver Architecture (EEG/fMRI-ready)

Files:
- `psyflow/io/*`
- `psyflow/TriggerSender.py`
- `psyflow/StimUnit.py`
- `docs/tutorials/send_trigger.md`

#### What changed
- Added `TriggerRuntime` (timing semantics + audit logging) and driver abstractions:
  - `MockDriver`: development/QA without hardware
  - `SerialDriver`: pyserial-backed byte writes (encoder lives in the driver)
  - `FanoutDriver`: broadcast to multiple drivers
  - `CallableDriver`: wrap a custom send function
- `TriggerSender` is now a thin compatibility wrapper around `TriggerRuntime`.
  Existing code calling `TriggerSender.send(code)` continues to work.
- `StimUnit.show()` and `StimUnit.capture_response()` now emit triggers through `TriggerRuntime` when available
  (automatically picked up via `TriggerSender.runtime`), preserving flip-locked semantics via the runtime.

### StimUnit.run fixed-window response stage (behavior + API)

File: `psyflow/StimUnit.py`

#### What changed
- `StimUnit.run(terminate_on_response=True)` now truly ends the stage immediately after the first valid response (or timeout) is registered.
- Previously, `run()` kept flipping until the timeout-derived window ended and only stopped drawing stimuli after a response, which could silently add blank time and made "trial end" ambiguous.
- `run()` now supports an explicit fixed-length window mode that keeps flipping for the full window duration even after a response/timeout is registered.

#### New parameters (keyword-only)
- `fixed_response_window: bool = False`: If `True`, the stage does not end early; it continues flipping until the window ends.
- `post_response_display: str = "stimuli"`: Only used when `fixed_response_window=True`. Values: `"stimuli"` (keep drawing) or `"blank"` (stop drawing) after a response/timeout is registered, until the window ends.
- `max_duration: float | None = None`: If provided, explicitly sets the stage window length (seconds) and overrides any timeout-derived duration.

#### Window duration rules
- Priority 1: `max_duration` (explicit window length).
- Priority 2: maximum registered `on_timeout()` duration.
- Priority 3: if `fixed_response_window=True` and no duration source exists, raise `ValueError`.
- Priority 4: otherwise fall back to `5.0` seconds (backward-compatible default).

#### Response/keyboard handling change
- Response hooks fire only for the first valid response; subsequent keypresses do not trigger more hooks in the same `run()` call.
- Key events are still drained every frame to reduce spillover into later stages.

#### Migration notes
- Old "keep flipping but stop drawing after response" behavior can be replicated with `fixed_response_window=True`, `post_response_display="blank"`, and a defined window length (via `max_duration` or `on_timeout()` hooks).

#### Example
```python
# End immediately on response (now matches terminate_on_response semantics)
StimUnit("trial", win, kb).add_stim(stim).run(terminate_on_response=True)

# Fixed 1.0s window; keep stimuli visible after response
StimUnit("trial", win, kb).add_stim(stim).run(
    fixed_response_window=True,
    post_response_display="stimuli",
    max_duration=1.0,
)

# Fixed 1.0s window; blank after response (closest to the old implicit behavior)
StimUnit("trial", win, kb).add_stim(stim).run(
    fixed_response_window=True,
    post_response_display="blank",
    max_duration=1.0,
)
```

### Flip-synced onset timestamps (callOnFlip argument evaluation fix)

File: `psyflow/StimUnit.py`

#### What changed
- Onset timestamps are now evaluated at flip-time by scheduling a callback that reads clocks inside the `win.flip()` callback, instead of passing pre-evaluated float values into `win.callOnFlip(...)`.
- Added internal helper `StimUnit._stamp_onset(...)` and updated these methods to use it:
  - `StimUnit.run()`
  - `StimUnit.show()`
  - `StimUnit.capture_response()`
  - `StimUnit.wait_and_continue()`

#### Related ordering change
- In response-related methods, `kb.clearEvents` and `clock.reset` are now scheduled on the flip (before stamping onset) to reduce pre-onset spillover and make "time zero" align with the onset flip more reliably.

### RT consistency + stage-close semantics + flip-locked offsets

Files:
- `psyflow/StimUnit.py`

#### What changed
- RTs are now based on PsychoPy's asynchronous keyboard timestamps (`KeyPress.rt`) rather than poll-time (`self.clock.getTime()`) where applicable.
  - `StimUnit.capture_response()` now uses `kp.rt` for `rt`/`response_time`.
  - `StimUnit.wait_and_continue()` now uses `kp.rt` for `response_time`.
- The keyboard clock is now explicitly reset on the onset flip (via `win.callOnFlip`) so that `KeyPress.rt` is unambiguously onset-relative:
  - `StimUnit.run()`
  - `StimUnit.capture_response()`
  - `StimUnit.wait_and_continue()`
- Stage-close fields are now more consistent:
  - Added internal helper `StimUnit._stamp_close(...)` and schedule it on the final flip for fixed-duration stages (flip-synced close).
  - In `capture_response()`, `close_time` is only set to the response RT when `terminate_on_response=True`; otherwise it is stamped at the end of the response window.
- `StimUnit.show()` offset triggers are now flip-locked:
  - Offset trigger + `close_time` stamping are scheduled via `win.callOnFlip(...)` on the final displayed frame.
  - Added `offset_flip_time` to record the final flip's timestamp (from `win.flip()`).

#### Timing contract (current)
- `onset_time` and `close_time` are stage-local seconds on `StimUnit.clock`, which is reset on the onset flip.
- `onset_time_global` and `close_time_global` are epoch seconds for those events.
  - `close_time_global` is computed consistently from `onset_time_global + close_time` when possible (including in `_stamp_close`).
- `flip_time` (and `offset_flip_time` in `show()`) are the return value of PsychoPy `win.flip()` (PsychoPy's monotonic timebase; not epoch).
- `rt` / `response_time` come from PsychoPy `Keyboard` RTs (asynchronous, onset-relative). `response_time_global` is derived as `onset_time_global + rt`.

### TriggerSender jitter reduction for flip callbacks

Files:
- `psyflow/TriggerSender.py`
- `psyflow/StimUnit.py`

#### What changed
- `TriggerSender.send(code, wait=True)` now accepts `wait: bool` and no longer prints on every send.
- When `wait=False`, `TriggerSender.send(...)` skips `core.wait(post_delay)` and does not call `on_trigger_end`.
  - This is intended for use inside flip callbacks (e.g., via `win.callOnFlip`) to reduce the risk of dropped frames.
- `StimUnit.send_trigger(code, wait=True)` now forwards `wait`, and all flip-scheduled trigger sends in `StimUnit.show()` / `StimUnit.capture_response()` use `wait=False`.

### StimUnit TriggerSender import (typing/runtime fix)

File: `psyflow/StimUnit.py`

- Replaced `from psyflow import TriggerSender` with a relative import (`from .TriggerSender import TriggerSender`) so that `Optional[TriggerSender]` type annotations refer to the class (not the submodule).

### BlockUnit summarize() fix + quieter condition generation

Files:
- `psyflow/BlockUnit.py`

#### What changed
- `BlockUnit.summarize()` no longer crashes (it now summarizes from `self.results` instead of mistakenly iterating the return value of `to_dict()`).
- `BlockUnit.generate_conditions()` no longer prints the full condition list to stdout; it logs via PsychoPy logging instead.

### taps() template path fix

Files:
- `psyflow/utils.py`

#### What changed
- `utils.taps()` now locates the bundled cookiecutter template via `importlib.resources.files("psyflow.templates") / template` (instead of looking under the package root).

### Minimal config validation helper

Files:
- `psyflow/utils.py`

#### What changed
- Added `validate_config(...)` for lightweight top-level section/type checks.
- `load_config(..., validate=True, required_sections=...)` can now opt into validation at load time.

### Import/Packaging Cleanup (Post-LLM Removal)

Files:
- `psyflow/__init__.py`
- `pyproject.toml`
- `setup.py`
- `docs/index.rst`
- `docs/api/psyflow.rst`
- `docs/tutorials/getting_started.md`
- `docs/tutorials/getting_started_cn.md`
- `docs/tutorials/get_subinfo.md`
- `docs/tutorials/get_subinfo_cn.md`

#### What changed
- `psyflow/__init__.py` now uses lazy exports (`__getattr__`) so `import psyflow` is lightweight and does not import PsychoPy unless needed.
- Declared Python requirement `>=3.10` (PEP 604 unions are used in the codebase).
- Removed LLM-related dependencies from packaging metadata after removing the LLM utilities.
- Removed LLM-related docs entry points from the docs tree.

### CI Smoke Checks

Files:
- `.github/workflows/ci.yml`
- `tests/test_smoke.py`

#### What changed
- Added a basic CI workflow to compile sources and run a small `unittest` smoke suite.

### ASCII Cleanup (Console/Encoding Robustness)

Files:
- `psyflow/StimBank.py`
- `psyflow/StimUnit.py`
- `psyflow/SubInfo.py`
- `psyflow/cli.py`

#### What changed
- Replaced non-essential emoji/fancy punctuation with ASCII to avoid console encoding issues on Windows setups.

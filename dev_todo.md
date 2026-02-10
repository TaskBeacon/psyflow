# psyflow dev TODO

Last updated: 2026-02-10

## Critical Issues (Must Fix)

### PsyFlow timing/response core

- [x] `StimUnit.run()` does not actually "terminate on response".
  - Fixed on 2026-02-10 by adding an explicit fixed-window mode and making `terminate_on_response=True` actually break early unless `fixed_response_window=True`.
  - See: `psyflow/log.md` and `psyflow/psyflow/StimUnit.py:323`.

- [x] Onset timestamps are not flip-synced (even though `callOnFlip` is used).
  - Fixed on 2026-02-10 by evaluating timing reads inside a flip callback (`StimUnit._stamp_onset`) rather than passing pre-evaluated float arguments into `callOnFlip(...)`.
  - See: `psyflow/log.md`, `psyflow/psyflow/StimUnit.py:202`, `psyflow/psyflow/StimUnit.py:384`, `psyflow/psyflow/StimUnit.py:578`, `psyflow/psyflow/StimUnit.py:675`, `psyflow/psyflow/StimUnit.py:821`.

- [x] RT measurement is inconsistent and can be wrong.
  - Fixed on 2026-02-10 by resetting the PsychoPy `Keyboard` clock on the onset flip and using `KeyPress.rt` (async) for RT fields where applicable.
  - See: `psyflow/log.md`, `psyflow/psyflow/StimUnit.py:187`, `psyflow/psyflow/StimUnit.py:382`, `psyflow/psyflow/StimUnit.py:673`, `psyflow/psyflow/StimUnit.py:719`, `psyflow/psyflow/StimUnit.py:819`, `psyflow/psyflow/StimUnit.py:836`.

- [x] Ambiguous meaning of `close_time`.
  - Fixed on 2026-02-10 by making `close_time` consistently mean the stage end:
    - If `terminate_on_response=True`, `close_time` is the response RT.
    - Otherwise, `close_time` is stamped on the final flip of the stage window (flip-synced via `_stamp_close`).
  - See: `psyflow/log.md`, `psyflow/psyflow/StimUnit.py:220`, `psyflow/psyflow/StimUnit.py:586`, `psyflow/psyflow/StimUnit.py:601`, `psyflow/psyflow/StimUnit.py:708`, `psyflow/psyflow/StimUnit.py:745`.

- [x] Trigger sending can inject jitter.
  - Fixed on 2026-02-10 by removing unconditional `print` in `TriggerSender.send()` and adding a `wait` flag so flip callbacks can skip `core.wait(post_delay)` and end hooks.
  - `StimUnit` now schedules flip-aligned trigger sends with `wait=False`.
  - See: `psyflow/log.md`, `psyflow/psyflow/TriggerSender.py:54`, `psyflow/psyflow/TriggerSender.py:91`, `psyflow/psyflow/StimUnit.py:166`, `psyflow/psyflow/StimUnit.py:579`, `psyflow/psyflow/StimUnit.py:676`.

- [x] Offset triggers in `StimUnit.show()` are not flip-locked.
  - Fixed on 2026-02-10 by scheduling the offset trigger via `win.callOnFlip(...)` on the final displayed frame.
  - See: `psyflow/log.md`, `psyflow/psyflow/StimUnit.py:599`, `psyflow/psyflow/StimUnit.py:601`.

- [x] `StimUnit` type annotation used the `TriggerSender` *module* instead of the class (import-time crash).
  - Fixed on 2026-02-10 by switching to a relative import: `from .TriggerSender import TriggerSender`.
  - See: `psyflow/log.md`, `psyflow/psyflow/StimUnit.py:5`.

### SST (example task) critical issues

Target task: `T000012-sst`

- [ ] Trigger name mismatches/typos mean key events aren't marked as intended.
  - `pre_top_response` is a typo (config uses `pre_stop_response`). See: `T000012-sst/src/run_trial.py:81`, `T000012-sst/config/config.yaml:207`.
  - `pre_stop_onset` / `on_stop_onset` are used but not defined in config, so onset triggers become `None`. See: `T000012-sst/src/run_trial.py:80`, `T000012-sst/src/run_trial.py:94`.

- [ ] SSD/stop-onset timing is not guaranteed.
  - Stop trials are implemented as two separate `capture_response()` calls (go-for-SSD, then stop-for-remaining), so actual stop onset includes "frame-rounded SSD" plus Python overhead plus next flip.
  - See: `T000012-sst/src/run_trial.py:73`, `T000012-sst/src/run_trial.py:87`.

- [ ] "1-up/1-down staircase" is not actually 1-up/1-down.
  - Controller updates SSD based on cumulative success rate vs target, not strictly on last-trial outcome.
  - See: `T000012-sst/src/utils.py:70`, `T000012-sst/src/utils.py:74`.

- [ ] Condition generator can loop forever on bad params.
  - `while True: shuffle until constraints satisfied` has no max-iterations fallback.
  - See: `T000012-sst/src/utils.py:140`.

## High-Impact Enhancements (Timing-Focused)

- [x] Define a strict "timing contract" for logged fields: which clock, which event, and whether it is flip-synced.
  - Fixed on 2026-02-10 by defining the contract in `psyflow/log.md` and aligning `StimUnit` fields accordingly.
  - See: `psyflow/log.md`.

- [x] Make flip-synced timestamps come from flip-synced sources.
  - Fixed on 2026-02-10 by stamping onset/close times inside flip callbacks and resetting keyboard timing on the onset flip for RT correctness.
  - See: `psyflow/log.md`.

- [ ] Add a built-in timing sanity report per block.
  - Dropped frames, measured FPS, requested vs realized durations (frame interval recording makes this straightforward in PsychoPy).

- [ ] SST-specific: treat "go onset -> stop onset" as a single timeline within one trial.
  - Log the achieved SSD (not just the requested SSD), and add strict trigger-name/config validation so typos fail fast rather than silently producing `None` triggers.

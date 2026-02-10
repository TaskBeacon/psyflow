# psyflow change log

## 2026-02-10

### StimUnit.run fixed-window response stage (behavior + API)

File: `psyflow/psyflow/StimUnit.py`

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

File: `psyflow/psyflow/StimUnit.py`

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
- `psyflow/psyflow/StimUnit.py`

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
- `psyflow/psyflow/TriggerSender.py`
- `psyflow/psyflow/StimUnit.py`

#### What changed
- `TriggerSender.send(code, wait=True)` now accepts `wait: bool` and no longer prints on every send.
- When `wait=False`, `TriggerSender.send(...)` skips `core.wait(post_delay)` and does not call `on_trigger_end`.
  - This is intended for use inside flip callbacks (e.g., via `win.callOnFlip`) to reduce the risk of dropped frames.
- `StimUnit.send_trigger(code, wait=True)` now forwards `wait`, and all flip-scheduled trigger sends in `StimUnit.show()` / `StimUnit.capture_response()` use `wait=False`.

### StimUnit TriggerSender import (typing/runtime fix)

File: `psyflow/psyflow/StimUnit.py`

- Replaced `from psyflow import TriggerSender` with a relative import (`from .TriggerSender import TriggerSender`) so that `Optional[TriggerSender]` type annotations refer to the class (not the submodule).

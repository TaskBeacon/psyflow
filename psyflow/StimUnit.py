"""Trial-level stimulus executor.

Encapsulates stimulus presentation, response capture, event triggers,
timing control, and lifecycle hooks.  Adapts automatically to simulation
mode via :class:`~psyflow.sim.adapter.ResponderAdapter`.
"""

from psychopy import core, event, visual, logging, sound
from psychopy.hardware.keyboard import Keyboard
from typing import Callable, Optional, List, Dict, Any, Sequence, TypeAlias, Union
import importlib
import random
from math import hypot
from .sim.context import get_context
from .io.events import TriggerEvent
from .sim.adapter import ResponderAdapter, ResponderActionError
from .sim.contracts import Feedback, Observation
from .pointer_trace import advance_ordered_progress, build_simulated_trace, evaluate_trace, nearest_path_position, normalize_path, transform_point
from .pointer_reach import build_simulated_reach, evaluate_reach, transform_reach_point
from psychopy.sound._base import _SoundBase


def _resolve_audio_stim_types() -> tuple[type, ...]:
    """Resolve concrete PsychoPy sound classes used at runtime."""
    types: list[type] = [_SoundBase]
    candidates = (
        ("psychopy.sound.backend_ptb", "SoundPTB"),
        ("psychopy.sound.backend_sounddevice", "SoundDeviceSound"),
        ("psychopy.sound.backend_pyo", "SoundPyo"),
        ("psychopy.sound.backend_pygame", "SoundPygame"),
    )
    for module_name, class_name in candidates:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name, None)
            if isinstance(cls, type) and cls not in types:
                types.append(cls)
        except Exception:
            continue
    return tuple(types)


AUDIO_STIM_TYPES = _resolve_audio_stim_types()
SUPPORTED_STIM_TYPES = (visual.BaseVisualStim,) + AUDIO_STIM_TYPES
SupportedStim: TypeAlias = Union[visual.BaseVisualStim, _SoundBase]

class StimUnit:
    """
    StimUnit(unit_label,win, kb,  trigger=None)

    A modular trial unit for PsychoPy-based experiments. Designed to encapsulate
    stimulus presentation, response handling, event triggers, and lifecycle hooks
    with flexible timing control.

    Features
    --------
    - Add multiple visual stimuli and manage them as a group.
    - Register event hooks for start, response, timeout, and end stages.
    - Supports both time-based and frame-based control modes.
    - Triggers aligned to visual flips (e.g., for EEG/fMRI).
    - Logs detailed trial state to PsychoPy's logging system.

    Parameters
    ----------
    win : visual.Window
        PsychoPy window where stimuli will be drawn.
    unit_label : str
        Identifier for the trial (used for logging/debugging).
    runtime : TriggerRuntime, optional
        External trigger runtime for event-aligned trigger emission.
    frame_time : float
        Duration of a single frame in seconds (default: 1/60 for 60Hz).
    """

    def __init__(
        self,
        unit_label: str,
        win: visual.Window,
        kb: Optional[Keyboard] = None,
        runtime: Any = None,
    ):
        self.win = win
        self.label = unit_label
        self.runtime = runtime
        self.stimuli: List[visual.BaseVisualStim] = []
        self.state: Dict[str, Any] = {}
        self.clock = core.Clock()
        self.kb = kb or Keyboard()
        self._hooks: Dict[str, List] = {"start": [], "response": [], "timeout": [], "end": []}
        self.frame_time = self.win.monitorFramePeriod

    def _qa_scale_duration(self, nominal_s: float) -> tuple[float, int, bool]:
        """Return (used_seconds, n_frames, scaled_flag) for QA mode.

        This keeps default behavior unchanged. In QA mode, scaling is opt-in
        via runtime context config.enable_scaling.
        """
        used = float(nominal_s)
        n_frames = max(1, int(round(used / self.frame_time)))

        ctx = get_context()
        if ctx is None or ctx.mode != "qa" or not getattr(ctx.config, "enable_scaling", False):
            return used, n_frames, False

        scale = float(getattr(ctx.config, "timing_scale", 1.0) or 1.0)
        if scale <= 0:
            scale = 1.0

        scaled = used * scale
        # Guardrail: never scale below one refresh interval when using real flips.
        scaled = max(self.frame_time, scaled)

        min_frames = int(getattr(ctx.config, "min_frames", 2) or 2)
        min_frames = max(1, min_frames)
        n_frames = max(min_frames, int(round(scaled / self.frame_time)))

        used = max(self.frame_time, n_frames * self.frame_time)
        return used, n_frames, True

    def add_stim(self, *stims: Union[SupportedStim, Sequence[SupportedStim]]) -> "StimUnit":
        """
        Add one or more visual or sound stimuli to the trial.

        Supports calling patterns:
        .add_stim(stimA)
        .add_stim(stimA, stimB, stimC)
        .add_stim([stimA, stimB, stimC])

        Parameters
        ----------
        *stims : visual.BaseVisualStim or sound.Sound or list of such
            One or more PsychoPy stimuli (visual or audio).

        Returns
        -------
        StimUnit
            Returns self for chaining.
        """
        if len(stims) == 1 and isinstance(stims[0], (list, tuple)):
            stims = stims[0]

        for stim in stims:
            if not isinstance(stim, SUPPORTED_STIM_TYPES):
                supported = ", ".join(sorted({t.__name__ for t in SUPPORTED_STIM_TYPES}))
                msg = (
                    "add_stim got unsupported object type "
                    f"{type(stim).__name__}. Supported types include: {supported}"
                )
                logging.warning(f"[StimUnit] {msg}")
                raise TypeError(msg)
            self.stimuli.append(stim)

        return self



    def clear_stimuli(self) -> "StimUnit":
        """
        Clear all previously added stimuli from the trial.

        Returns
        -------
        StimUnit
        """
        self.stimuli.clear()
        return self

    def set_state(self, prefix: Optional[str] = None, **kwargs) -> "StimUnit":
        """
        Update internal state with optional key prefixing.

        Parameters
        ----------
        prefix : str, optional
            If None, use self.label. If "", store keys as-is. Else use prefix + '_'.
        kwargs : dict
            State variables to store.
        """
        effective_prefix = prefix if prefix is not None else self.label

        for k, v in kwargs.items():
            key = f"{effective_prefix}_{k}" if effective_prefix else k
            self.state[key] = v
        return self  # Enables chaining


    def get_state(self, key: str, default: Any = None, prefix: Optional[str] = None) -> Any:
        """
        Retrieve a value from internal state.
        
        Lookup order:
        1. Try exact key.
        2. If not found, try prefixed key using:
        - provided prefix (if given)
        - otherwise self.label
        
        Parameters
        ----------
        key : str
            State variable name.
        default : Any
            Value to return if key is not found.
        prefix : str, optional
            Optional manual prefix to use (overrides self.label).
        
        Returns
        -------
        Any
            Stored value, or default if not found.
        """
        # Try raw key first
        if key in self.state:
            return self.state[key]

        # Fallback to prefixed key
        effective_prefix = prefix if prefix is not None else self.label
        full_key = f"{effective_prefix}_{key}" if effective_prefix else key
        return self.state.get(full_key, default)


    def to_dict(self, target: Optional[dict] = None) -> 'StimUnit':
        """
        Return the StimUnit

        Parameters
        ----------
        target : dict, optional
            If provided, updates this dict in-place and returns it.

        Returns
        -------
        StimUnit
            StimUnit for chaining.
        """
        if target is not None:
            target.update(self.state)
        return self
    

    def _emit_trigger(
        self,
        trigger_code: int | None,
        *,
        when: str = "now",
        wait: bool = True,
        name: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        """Internal helper to emit a trigger via TriggerRuntime."""
        code_i = None
        if trigger_code is not None:
            try:
                code_i = int(trigger_code)
            except Exception:
                logging.warning(f"[StimUnit] Skipping trigger: non-int code {trigger_code!r} (unit={self.label!r})")
                return

        if meta is None:
            meta = {}
        meta.setdefault("unit_label", self.label)
        meta.setdefault("trial_id", self.get_state("trial_id", None))
        meta.setdefault("block_id", self.get_state("block_id", None))
        meta.setdefault("condition_id", self.get_state("condition_id", None))
        meta.setdefault("task_factors", self.get_state("task_factors", None))

        if self.runtime is None:
            return

        self.runtime.emit(
            TriggerEvent(name=name, code=code_i, meta=meta),
            when="flip" if when == "flip" else "now",
            win=self.win if when == "flip" else None,
            wait=wait,
        )

    def send_trigger(self, trigger_code: int | None, wait: bool = True) -> "StimUnit":
        """Backward compatible: send a trigger code immediately (not flip-scheduled)."""
        self._emit_trigger(trigger_code, when="now", wait=wait, name="manual")
        return self

    def _reset_keyboard_clock(self) -> None:
        """Reset the PsychoPy keyboard clock if available.

        PsychoPy's `KeyPress.rt` is measured relative to the last reset of
        `kb.clock`. If we want RTs relative to stimulus onset, we need to reset
        that clock on the onset flip.
        """
        try:
            kb_clock = getattr(self.kb, "clock", None)
            if kb_clock is not None and hasattr(kb_clock, "reset"):
                kb_clock.reset()
        except Exception:
            # Never let keyboard timing helpers crash the experiment.
            pass

    def _stamp_onset(self, onset_trigger: int = None) -> None:
        """Stamp onset timing fields.

        Intended to be scheduled via ``win.callOnFlip`` so that timing values are
        evaluated at flip-time (not at scheduling time).
        """
        if onset_trigger is None:
            self.set_state(
                onset_time=self.clock.getTime(),
                onset_time_global=core.getAbsTime(),
            )
        else:
            self.set_state(
                onset_time=self.clock.getTime(),
                onset_time_global=core.getAbsTime(),
                onset_trigger=onset_trigger,
            )

    def _stamp_close(self, offset_trigger: int = None) -> None:
        """Stamp stage-close timing fields.

        Intended to be scheduled via ``win.callOnFlip`` so that timing values are
        evaluated at flip-time (not at scheduling time).
        """
        close_time = self.clock.getTime()
        onset_time_global = self.get_state("onset_time_global", None)
        close_time_global = (
            onset_time_global + close_time if onset_time_global is not None else core.getAbsTime()
        )
        if offset_trigger is None:
            self.set_state(
                close_time=close_time,
                close_time_global=close_time_global,
            )
        else:
            self.set_state(
                close_time=close_time,
                close_time_global=close_time_global,
                offset_trigger=offset_trigger,
            )

    def log_unit(self) -> None:
        """Write the current trial state to PsychoPy logs.

        All key-value pairs stored in :attr:`state` are emitted using
        ``logging.data`` which allows post-hoc reconstruction of each trial.

        Examples
        --------
        >>> unit.set_state(response="space")
        >>> unit.log_unit()
        """
        logging.data(f"[StimUnit] Data: {self.state}")


    def on_start(self, func: Optional[Callable[['StimUnit'], None]] = None):
        """
        Register or decorate a function to call at trial start.
        """
        if func is None:
            def decorator(f):
                self._hooks["start"].append(f)
                return self
            return decorator
        else:
            self._hooks["start"].append(func)
            return self

    def on_response(self, keys: List[str], func: Optional[Callable[['StimUnit', str, float], None]] = None):
        """
        Register or decorate a function to call when a valid response key is pressed.

        Parameters
        ----------
        keys : list[str]
            Keys that trigger the callback.
        func : Callable or None
            A function accepting (StimUnit, key, rt) or None to use as decorator.
        """
        if func is None:
            def decorator(f):
                self._hooks["response"].append((keys, f))
                return self
            return decorator
        else:
            self._hooks["response"].append((keys, func))
            return self

    def on_timeout(self, timeout: float, func: Optional[Callable[['StimUnit'], None]] = None):
        """
        Register or decorate a function to call on timeout.

        Parameters
        ----------
        timeout : float
            Time in seconds after which timeout is triggered.
        func : Callable or None
            A function accepting (StimUnit) or None to use as decorator.
        """
        if func is None:
            def decorator(f):
                self._hooks["timeout"].append((timeout, f))
                return self
            return decorator
        else:
            self._hooks["timeout"].append((timeout, func))
            return self

    def on_end(self, func: Optional[Callable[['StimUnit'], None]] = None):
        """
        Register or decorate a function to call at the end of the trial.
        """
        if func is None:
            def decorator(f):
                self._hooks["end"].append(f)
                return self
            return decorator
        else:
            self._hooks["end"].append(func)
            return self

    def run(
        self,
        terminate_on_response: bool = True,
        *,
        fixed_response_window: bool = False,
        post_response_display: str = "stimuli",
        max_duration: float | None = None,
    ) -> "StimUnit":
        """Execute the full trial lifecycle.

        This method draws all registered stimuli, handles response and timeout
        events, executes registered hooks and logs the final state.

        Parameters
        ----------
        terminate_on_response : bool, optional
            If ``True`` the trial ends immediately once a response is
            registered. Defaults to ``True``.
        fixed_response_window : bool, optional
            If ``True`` the stage duration is fixed and will *not* end early on
            response/timeout. The stage will continue flipping until the fixed
            window ends.
            The fixed window duration is determined by ``max_duration`` if
            provided, otherwise by the maximum registered timeout duration.
        post_response_display : {"stimuli","blank"}, optional
            Only used when ``fixed_response_window=True``.
            Controls what is shown after a response (or timeout) is registered:
            - ``"stimuli"``: keep drawing the registered stimuli until the window ends
            - ``"blank"``: stop drawing and continue flipping a blank screen
        max_duration : float or None, optional
            Explicit maximum duration (seconds) for this stage. If provided, it
            overrides any timeout-derived duration.

        Returns
        -------
        StimUnit
            The instance itself for chaining.

        Examples
        --------
        >>> StimUnit("trial1", win).run()
        """
        if post_response_display not in ("stimuli", "blank"):
            raise ValueError(
                "post_response_display must be 'stimuli' or 'blank', "
                f"got {post_response_display!r}"
            )

        self.set_state(global_time=core.getAbsTime())

        for hook in self._hooks["start"]:
            hook(self)

        # Initial flip with onset timestamp
        for stim in self.stimuli:
            stim.draw()

        # Flip-synced onset stamps: evaluate times at flip-time, not schedule-time.
        self.win.callOnFlip(self.kb.clearEvents)
        self.win.callOnFlip(self._reset_keyboard_clock)
        self.win.callOnFlip(self.clock.reset)
        self.win.callOnFlip(self._stamp_onset)
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)
        responded = False

        all_keys = list(set(k for k_list, _ in self._hooks["response"] for k in k_list))


        # Determine the maximum duration for this stage.
        timeout_durations = [t for t, _ in self._hooks["timeout"]]
        timeout_max = max(timeout_durations) if timeout_durations else None
        if max_duration is not None:
            window_duration = float(max_duration)
        elif timeout_max is not None:
            window_duration = float(timeout_max)
        else:
            if fixed_response_window:
                raise ValueError(
                    "fixed_response_window=True requires max_duration or at least one "
                    "on_timeout() hook to define the window length."
                )
            # Backward-compatible fallback: run for 5 seconds if no timeouts are set.
            window_duration = 5.0

        if window_duration <= 0:
            raise ValueError(f"max_duration/window_duration must be > 0, got {window_duration}")

        n_frames = max(1, int(round(window_duration / self.frame_time)))

        for frame_i in range(n_frames - 1):
            # End immediately once we've registered an outcome, unless the user
            # explicitly requests a fixed-length response window.
            if responded and terminate_on_response and not fixed_response_window:
                break

            should_draw = True
            if responded and fixed_response_window:
                should_draw = (post_response_display == "stimuli")

            if should_draw:
                for stim in self.stimuli:
                    stim.draw()

            if frame_i == n_frames - 2:
                # Stamp stage close on the final flip of the response window.
                self.win.callOnFlip(self._stamp_close)
            self.win.flip()

            # Drain key events every frame to avoid spillover into later stages.
            keys = self.kb.getKeys(keyList=all_keys, waitRelease=False) if all_keys else []
            if not responded:
                for key_obj in keys:
                    key_name, key_rt = key_obj.name, key_obj.rt
                    for valid_keys, hook in self._hooks["response"]:
                        if key_name in valid_keys:
                            hook(self, key_name, key_rt)
                            responded = True
                            # If the stage ends on response, record the stage close
                            # at the (asynchronously timestamped) keypress time.
                            if terminate_on_response and not fixed_response_window:
                                onset_time_global = self.get_state("onset_time_global", None)
                                close_time_global = (
                                    onset_time_global + key_rt
                                    if onset_time_global is not None
                                    else core.getAbsTime()
                                )
                                self.set_state(
                                    close_time=key_rt,
                                    close_time_global=close_time_global,
                                )
                            break
                    if responded:
                        break


            elapsed = self.clock.getTime()
            for timeout_duration, timeout_hook in self._hooks["timeout"]:
                if elapsed >= timeout_duration and not responded:
                    onset_time_global = self.get_state("onset_time_global", None)
                    timeout_time_global = (
                        onset_time_global + elapsed
                        if onset_time_global is not None
                        else core.getAbsTime()
                    )
                    self.set_state(
                        timeout_triggered=True,
                        duration=elapsed,
                        timeout_time=elapsed,
                        timeout_time_global=timeout_time_global,
                    )
                    timeout_hook(self)
                    responded = True
                    if terminate_on_response and not fixed_response_window:
                        self.set_state(
                            close_time=elapsed,
                            close_time_global=timeout_time_global,
                        )

        # Ensure close time is present. If the stage ran to the end of its window,
        # it should have been stamped on the final flip via _stamp_close().
        if self.get_state("close_time", None) is None:
            close_time = self.clock.getTime()
            onset_time_global = self.get_state("onset_time_global", None)
            close_time_global = (
                onset_time_global + close_time
                if onset_time_global is not None
                else core.getAbsTime()
            )
            self.set_state(
                close_time=close_time,
                close_time_global=close_time_global,
            )
        for hook in self._hooks["end"]:
            hook(self)

        self.log_unit()
        return self

    
    def show(
        self,
        duration: float | list | tuple | None = None,
        onset_trigger: int = None,
        offset_trigger: int = None,
        phase_drift_hz: float | None = None,
    ) -> "StimUnit":
        """
        Display the stimulus for a specified duration, using frame-based timing
        (recommended for EEG/fMRI). Audio playback is automatically started on stimulus onset.

        If duration is None, the longest duration of any sound stimulus will be used.
        If duration is set explicitly, it will be respected even if shorter than any sound duration.

        Parameters
        ----------
        duration : float | list | tuple | None
            Duration of stimulus presentation (in seconds). Can be:
            - A fixed number
            - A (min, max) range to sample from
            - None -> automatically use max sound duration (if any)
        onset_trigger : int
            Trigger code to send at stimulus onset.
        offset_trigger : int
            Trigger code to send at stimulus offset.
        phase_drift_hz : float | None
            Optional horizontal phase rate (cycles/second) for GratingStim
            objects; requires no concurrent audio/video. Preserves vertical
            and initial phases. Only this opt-in path uses an elapsed deadline
            and anticipated flip times instead of a fixed frame budget. Records
            phase samples, actual flip intervals, final phases and late-close
            evidence; the caller must evaluate presentation quality. A missed
            final refresh closes at a software decision time without submitting
            another drifting frame. The actual last phase remains available for
            a following static stage. These are software timing records, not a
            physical onset, luminance or human-perception guarantee.

        Returns
        -------
        StimUnit

        Behavior Table
        --------------
        | Condition                                | Behavior                                             |
        |------------------------------------------|------------------------------------------------------|
        | duration=None                            | Uses longest sound (or 0.0 if no sound)             |
        | duration=(1, 2)                          | Samples uniformly in [1, 2], regardless of sound    |
        | duration=1.0 + sound is 2.5 seconds      | Screen ends at 1.0s, sound may be cut off early     |
        | duration=None + sound is 2.5 seconds     | Screen and sound will both last full 2.5s           |
        """
        local_rng = random.Random()

        # auto-select duration from sound stimuli if not provided
        if duration is None:
            t_val = 0.0
            for stim in self.stimuli:
                if hasattr(stim, "getDuration") and callable(stim.getDuration):
                    try:
                        t_val = max(t_val, stim.getDuration())
                    except Exception:
                        continue
        elif isinstance(duration, (list, tuple)):
            if len(duration) == 2:
                t_val = local_rng.uniform(*duration)
            elif len(duration) == 1:
                t_val = duration[0]
            else:
                raise ValueError(f"Duration list/tuple must have 1 or 2 elements, got {len(duration)}")
        elif isinstance(duration, (int, float)):
            t_val = duration
        else:
            raise TypeError(f"Invalid duration type: {type(duration)}")

        nominal = float(t_val)
        used, n_frames, scaled = self._qa_scale_duration(nominal)
        if scaled:
            self.set_state(duration_nominal=nominal, duration_scaled=used)
        self.set_state(duration=used)

        # Opt-in grating drift; ordinary visual/audio show behavior is unchanged.
        gratings = []
        initial_phases = []
        drift_times = [0.0]
        drift_shifts = [0.0]
        drift_flips = []
        if phase_drift_hz is not None:
            from math import isfinite
            if isinstance(phase_drift_hz, bool) or not isinstance(phase_drift_hz, (int, float)) or not isfinite(phase_drift_hz):
                raise ValueError('phase_drift_hz must be a finite number')
            gratings = [s for s in self.stimuli if isinstance(s, visual.GratingStim)]
            if not gratings or any(callable(getattr(s, 'play', None)) for s in self.stimuli):
                raise ValueError('phase_drift_hz requires GratingStim and no concurrent audio/video')
            initial_phases = [s.phase.copy() for s in gratings]
            self.set_state(drift_late_close=False)

        # --- Initial Flip (trigger locked to onset) ---
        sound_stims = []
        for stim in self.stimuli:
            if hasattr(stim, "play") and callable(stim.play):
                sound_stims.append(stim)
            else:
                stim.draw()

        # Schedule flip callbacks in an order that keeps timing stamps accurate
        # even if trigger/audio callbacks are slow.
        self.win.callOnFlip(self.clock.reset)
        self.win.callOnFlip(self._stamp_onset, onset_trigger)
        self._emit_trigger(
            onset_trigger,
            when="flip",
            wait=False,
            name=f"{self.label}_onset",
            meta={"kind": "onset"},
        )
        for stim in sound_stims:
            self.win.callOnFlip(stim.play)

        # If the requested duration rounds to a single frame, onset and offset
        # occur on the same flip.
        if n_frames == 1:
            self.win.callOnFlip(self._stamp_close, offset_trigger)
            self._emit_trigger(
                offset_trigger,
                when="flip",
                wait=False,
                name=f"{self.label}_offset",
                meta={"kind": "offset"},
            )

        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)
        if gratings:
            drift_flips.append(float(flip_time))

        # --- Frame-based visual presentation ---
        visual_stims = [s for s in self.stimuli if hasattr(s, "draw") and callable(s.draw)]
        offset_flip_time = flip_time if n_frames == 1 or gratings else None
        if gratings and n_frames > 1:
            # Drift has an elapsed-time deadline so delayed refreshes cannot
            # silently lengthen adaptation by retaining a fixed frame budget.
            # The final drift frame targets duration minus one refresh period;
            # the next stage can hold its actual phase on the following flip.
            while True:
                t = max(drift_times[-1], float(self.win.getFutureFlipTime(clock=self.clock)))
                if t >= used:
                    # A delayed callback can miss the final candidate refresh.
                    # Keep the last submitted phase and close without drawing
                    # a new drifting frame beyond the requested deadline.
                    # This exceptional offset is a software decision timestamp.
                    self._stamp_close(offset_trigger)
                    self._emit_trigger(offset_trigger, when="now", wait=False,
                                       name=f"{self.label}_offset", meta={"kind": "late_drift_close"})
                    self.set_state(drift_late_close=True)
                    break
                shift = float(phase_drift_hz) * t
                for stim, base in zip(gratings, initial_phases):
                    stim.phase = (float(base[0]) + shift, float(base[1]))
                drift_times.append(t)
                drift_shifts.append(shift)
                for stim in visual_stims:
                    stim.draw()
                is_final = t >= used - self.frame_time - 1e-9
                if is_final:
                    self.win.callOnFlip(self._stamp_close, offset_trigger)
                    self._emit_trigger(offset_trigger, when="flip", wait=False,
                                       name=f"{self.label}_offset", meta={"kind": "offset"})
                offset_flip_time = self.win.flip()
                drift_flips.append(float(offset_flip_time))
                if is_final:
                    break
        elif n_frames > 1:
            for frame_i in range(n_frames - 1):
                for stim in visual_stims:
                    stim.draw()
                if frame_i == n_frames - 2:
                    # Flip-locked offset stamp + trigger on the final displayed frame.
                    self.win.callOnFlip(self._stamp_close, offset_trigger)
                    self._emit_trigger(
                        offset_trigger,
                        when="flip",
                        wait=False,
                        name=f"{self.label}_offset",
                        meta={"kind": "offset"},
                    )
                offset_flip_time = self.win.flip()

        if offset_flip_time is not None:
            self.set_state(offset_flip_time=offset_flip_time)

        if gratings:
            intervals = [b-a for a,b in zip(drift_flips, drift_flips[1:])]
            self.set_state(drift_frequency_hz=float(phase_drift_hz),
                           drift_initial_phases=[p.tolist() for p in initial_phases],
                           drift_final_phases=[s.phase.tolist() for s in gratings],
                           drift_sample_times_s=drift_times, drift_phase_shifts_cycles=drift_shifts,
                           drift_flip_times_s=[t-drift_flips[0] for t in drift_flips],
                           drift_frame_count=len(drift_flips),
                           drift_max_frame_interval_s=max(intervals or [0]),
                           drift_deadline_s=used,
                           drift_clock='PsychoPy anticipated flip from unit clock; actual flip intervals retained')

        self.log_unit()
        return self

    def capture_response(
        self,
        keys: list[str],
        duration: float | list | tuple,
        onset_trigger: int = None,
        response_trigger: int | dict[str, int] = None,
        timeout_trigger: int = None,
        terminate_on_response: bool = True,
        count_responses: bool = False,
        correct_keys: list[str] | None = None, 
        highlight_stim: visual.BaseVisualStim | dict[str, visual.BaseVisualStim] = None,  
        dynamic_highlight: bool = False,                                                  
    ) -> "StimUnit":
        """
        Wait for a keypress or timeout. Supports both time-based and frame-based duration.
        Triggers and onset time synced to visual flip.

        Parameters
        ----------
        keys : list[str]
            Keys to listen for.
        duration : float
            Response window duration in seconds.
        onset_trigger : int
            Trigger code sent at stimulus onset.
        response_trigger : int | dict[str, int]
            Trigger code for response, can be per-key.
        timeout_trigger : int
            Trigger code for timeout.
        correct_keys : list[str] | None
            If provided, only keys in this list count as hits.
        highlight_stim : VisualStim or dict
            If a single stim: draw it around whatever is chosen.
            If a dict: maps key names -> highlight stimuli.
        dynamic_highlight : bool
            If True, allow multiple key presses and update the highlight each time.
        count_responses : bool
            If True, retain every valid key and timestamp in ``responses`` and
            ``response_times`` while the response window remains open. Use with
            ``terminate_on_response=False`` for continuous-report paradigms.
        """
        # decide total duration
        local_rng = random.Random()
        if isinstance(duration, (list, tuple)):
            if len(duration) == 2:
                t_val = local_rng.uniform(*duration)
            elif len(duration) == 1:
                t_val = duration[0]
            else:
                raise ValueError(f"Duration list/tuple must have 1 or 2 elements, got {len(duration)}")
        elif isinstance(duration, (int, float)):
            t_val = duration
        else:
            raise TypeError(f"Invalid duration type: {type(duration)}")

        nominal = float(t_val)
        used, n_frames, scaled = self._qa_scale_duration(nominal)
        if scaled:
            self.set_state(duration_nominal=nominal, duration_scaled=used)
        self.set_state(duration=used)
        
        # --- Initial Flip (trigger locked to onset) ---
        sound_stims = []
        for stim in self.stimuli:
            if hasattr(stim, "play") and callable(stim.play):
                sound_stims.append(stim)
            else:
                stim.draw()

        # Flip-synced onset: clear events, reset the local clock, then stamp onset.
        self.win.callOnFlip(self.kb.clearEvents)
        self.win.callOnFlip(self._reset_keyboard_clock)
        self.win.callOnFlip(self.clock.reset)
        self.win.callOnFlip(self._stamp_onset, onset_trigger)
        self._emit_trigger(
            onset_trigger,
            when="flip",
            wait=False,
            name=f"{self.label}_onset",
            meta={"kind": "onset"},
        )
        for stim in sound_stims:
            self.win.callOnFlip(stim.play)
        if n_frames == 1:
            # Window rounds to a single frame: onset and close occur on the same flip.
            self.win.callOnFlip(self._stamp_close)
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)

         # if no correct_keys provided, any key in `keys` is valid
        if correct_keys is None:
            correct_keys = keys
        elif isinstance(correct_keys, str):
            correct_keys = [correct_keys]
        responded = False
        chosen_key = None  # track which key to highlight
        responses: list[str] = []
        response_times: list[float] = []

        # QA-mode responder injection (psyflow-level seam)
        ctx = get_context()
        responder = None
        if ctx is not None and ctx.mode in ("qa", "sim") and getattr(ctx, "responder", None) is not None:
            responder = ctx.responder

        sim_key = None
        sim_rt = None
        if responder is not None:
            obs = Observation(
                mode=getattr(ctx, "mode", "qa") if ctx is not None else "qa",
                trial_id=self.get_state("trial_id", self.get_state("trial_index", None)),
                block_id=self.get_state("block_id", None),
                phase=self.label,
                deadline_s=used,
                response_window_open=True,
                response_window_s=used,
                valid_keys=list(keys),
                t_phase_onset=self.get_state("onset_time", None),
                t_phase_onset_global=self.get_state("onset_time_global", None),
                stim_id=self.get_state("stim_id", None),
                stim_features=self.get_state("stim_features", None),
                condition_id=self.get_state("condition_id", None),
                task_factors=self.get_state("task_factors", None) or {},
            )
            adapter = ResponderAdapter(
                policy=str(getattr(getattr(ctx, "config", None), "sim_policy", "warn") or "warn"),
                default_rt_s=float(getattr(getattr(ctx, "config", None), "default_rt_s", 0.2) or 0.2),
                clamp_rt=bool(getattr(getattr(ctx, "config", None), "clamp_rt", False)),
                logger=getattr(ctx, "sim_logger", None) if ctx is not None else None,
                session=getattr(ctx, "session", None) if ctx is not None else None,
            )
            handled = None
            try:
                handled = adapter.handle_response(obs, responder)
            except ResponderActionError:
                # Strict mode intentionally raises; other modes degrade to timeout.
                raise
            except Exception:
                handled = None
            if handled is not None:
                sim_key = handled.used_action.key
                sim_rt = handled.used_action.rt_s

        visual_stims = [s for s in self.stimuli if hasattr(s, "draw") and callable(s.draw)]
        for frame_i in range(n_frames - 1):
            # draw or blank?
            if not (responded and terminate_on_response):
                for stim in visual_stims:
                    stim.draw()
            # draw highlight if requested
            if highlight_stim and (responded or dynamic_highlight):
                h = (highlight_stim.get(chosen_key)
                    if isinstance(highlight_stim, dict)
                    else highlight_stim)
                if h:
                    h.draw()    

            # If we run the full window, stamp stage-close on the final flip.
            if frame_i == n_frames - 2:
                self.win.callOnFlip(self._stamp_close)
            self.win.flip()

            # only listen for keys if we haven't responded or if dynamic_highlight=True
            if not responded or dynamic_highlight or count_responses:
                if responder is None:
                    keypress = self.kb.getKeys(keyList=keys, waitRelease=False)
                    if keypress:
                        kp = keypress[0]
                        k = kp.name
                        chosen_key = k
                        rt = kp.rt
                        if count_responses:
                            responses.append(k)
                            response_times.append(float(rt))
                        onset_time_global = self.get_state("onset_time_global", None)
                        response_time_global = (
                            onset_time_global + rt
                            if onset_time_global is not None
                            else core.getAbsTime()
                        )
                        if not count_responses or not responded:
                            self.set_state(
                                hit=k in correct_keys,
                                correct_keys=correct_keys,
                                response=k,
                                key_press=True,
                                rt=rt,
                                response_time=rt,
                                response_time_global=response_time_global,
                            )
                        code = (response_trigger.get(k, None)
                            if isinstance(response_trigger, dict)
                            else response_trigger)
                        self._emit_trigger(
                            code,
                            when="now",
                            wait=True,
                            name=f"{self.label}_response",
                            meta={"kind": "response", "key": k},
                        )
                        self.set_state(response_trigger=code)
                        responded = True

                        # if we should stop immediately, break out
                        if terminate_on_response and not dynamic_highlight:
                            # In terminate-on-response mode, the stage ends at the first response.
                            self.set_state(close_time=rt, close_time_global=response_time_global)
                            break
                else:
                    elapsed = self.clock.getTime()
                    if sim_key is not None and sim_rt is not None and elapsed >= sim_rt:
                        k = sim_key
                        chosen_key = k
                        rt = sim_rt
                        if count_responses:
                            responses.append(k)
                            response_times.append(float(rt))
                        onset_time_global = self.get_state("onset_time_global", None)
                        response_time_global = (
                            onset_time_global + rt
                            if onset_time_global is not None
                            else core.getAbsTime()
                        )
                        self.set_state(
                            hit=k in correct_keys,
                            correct_keys=correct_keys,
                            response=k,
                            key_press=True,
                            rt=rt,
                            response_time=rt,
                            response_time_global=response_time_global,
                        )
                        code = (response_trigger.get(k, None)
                            if isinstance(response_trigger, dict)
                            else response_trigger)
                        self._emit_trigger(
                            code,
                            when="now",
                            wait=True,
                            name=f"{self.label}_response",
                            meta={"kind": "response", "key": k},
                        )
                        self.set_state(response_trigger=code)
                        responded = True
                        sim_key = None
                        sim_rt = None

                        if terminate_on_response and not dynamic_highlight:
                            self.set_state(close_time=rt, close_time_global=response_time_global)
                            break


        if count_responses:
            self.set_state(
                responses=list(responses),
                response_times=list(response_times),
                response_count=len(responses),
                first_rt=response_times[0] if response_times else None,
            )

        if not responded: 
            self.set_state(
                hit=False, 
                correct_keys=correct_keys,
                response=None, 
                key_press=False,
                rt=None,
                response_time=None,
                response_time_global=None,
                timeout_trigger=timeout_trigger
            )
            self._emit_trigger(
                timeout_trigger,
                when="now",
                wait=True,
                name=f"{self.label}_timeout",
                meta={"kind": "timeout"},
            )

        # Optional responder feedback hook for adaptive plugins.
        if responder is not None and hasattr(responder, "on_feedback"):
            try:
                outcome = "timeout"
                if responded:
                    outcome = "hit" if bool(self.get_state("hit", False)) else "error"
                responder.on_feedback(
                    Feedback(
                        trial_id=self.get_state("trial_id", self.get_state("trial_index", "unknown")),
                        phase=self.label,
                        outcome=outcome,
                        reward=None,
                        meta={
                            "condition_id": self.get_state("condition_id", None),
                            "task_factors": self.get_state("task_factors", None),
                            "response": self.get_state("response", None),
                            "rt_s": self.get_state("rt", None),
                        },
                    )
                )
            except Exception:
                pass

        # Ensure close time exists (should be stamped on final flip for timeouts,
        # or set explicitly for terminate-on-response).
        if self.get_state("close_time", None) is None:
            self._stamp_close()

        self.log_unit()
        return self

    def capture_pointer_sequence(
        self,
        targets: dict[str, visual.BaseVisualStim],
        max_selections: int,
        duration: float,
        onset_trigger: int = None,
        selection_trigger: int | dict[str, int] = None,
        complete_trigger: int = None,
        timeout_trigger: int = None,
        highlight_targets: dict[str, visual.BaseVisualStim] | None = None,
        highlight_duration: float = 0.10,
    ) -> "StimUnit":
        """Collect an ordered pointer/touch sequence from named visual targets.

        Target hit-testing, timing, trigger emission, simulation injection, and
        stage data remain framework-owned. Tasks supply only named targets and
        the required sequence length.
        """
        if not isinstance(targets, dict) or not targets:
            raise ValueError("targets must be a non-empty mapping of names to visual stimuli")
        if any(not isinstance(stim, visual.BaseVisualStim) for stim in targets.values()):
            raise TypeError("all pointer targets must be PsychoPy visual stimuli")

        required = int(max_selections)
        if required <= 0:
            raise ValueError("max_selections must be a positive integer")

        nominal = float(duration)
        if nominal <= 0:
            raise ValueError("duration must be positive")
        used, n_frames, scaled = self._qa_scale_duration(nominal)
        if scaled:
            self.set_state(duration_nominal=nominal, duration_scaled=used)
        self.set_state(duration=used, target_names=list(targets), max_selections=required)

        visual_stims = [stim for stim in self.stimuli if hasattr(stim, "draw") and callable(stim.draw)]
        for stim in visual_stims:
            stim.draw()
        self.win.callOnFlip(self.clock.reset)
        self.win.callOnFlip(self._stamp_onset, onset_trigger)
        self._emit_trigger(
            onset_trigger,
            when="flip",
            wait=False,
            name=f"{self.label}_onset",
            meta={"kind": "onset"},
        )
        if n_frames == 1:
            self.win.callOnFlip(self._stamp_close)
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)

        ctx = get_context()
        responder = None
        if ctx is not None and ctx.mode in ("qa", "sim") and getattr(ctx, "responder", None) is not None:
            responder = ctx.responder

        simulated_actions: list[tuple[str, float]] = []
        if responder is not None:
            adapter = ResponderAdapter(
                policy=str(getattr(getattr(ctx, "config", None), "sim_policy", "warn") or "warn"),
                default_rt_s=float(getattr(getattr(ctx, "config", None), "default_rt_s", 0.2) or 0.2),
                clamp_rt=bool(getattr(getattr(ctx, "config", None), "clamp_rt", False)),
                logger=getattr(ctx, "sim_logger", None),
                session=getattr(ctx, "session", None),
            )
            base_factors = dict(self.get_state("task_factors", None) or {})
            previous_rt = 0.0
            for selection_index in range(required):
                obs = Observation(
                    mode=getattr(ctx, "mode", "qa"),
                    trial_id=self.get_state("trial_id", self.get_state("trial_index", None)),
                    block_id=self.get_state("block_id", None),
                    phase=self.label,
                    deadline_s=used,
                    response_window_open=True,
                    response_window_s=used,
                    valid_keys=list(targets),
                    t_phase_onset=self.get_state("onset_time", None),
                    t_phase_onset_global=self.get_state("onset_time_global", None),
                    stim_id=self.get_state("stim_id", None),
                    stim_features=self.get_state("stim_features", None),
                    condition_id=self.get_state("condition_id", None),
                    task_factors={**base_factors, "selection_index": selection_index},
                )
                handled = adapter.handle_response(obs, responder)
                action = handled.used_action
                if action.key is None or action.rt_s is None:
                    break
                action_rt = max(float(action.rt_s), previous_rt + (0.05 if simulated_actions else 0.0))
                if action_rt > used:
                    break
                simulated_actions.append((str(action.key), action_rt))
                previous_rt = action_rt

        original_mouse_visible = bool(getattr(self.win, "mouseVisible", False))
        mouse = None
        previous_pressed = False
        if responder is None:
            self.win.mouseVisible = True
            mouse = event.Mouse(win=self.win, visible=True)
            mouse.clickReset()

        selections: list[str] = []
        selection_times: list[float] = []
        selection_positions: list[list[float] | None] = []
        selection_triggers: list[int | None] = []
        next_simulated = 0
        last_highlight: str | None = None
        highlight_until = 0.0

        def accept_selection(name: str, rt: float, position: list[float] | None) -> None:
            nonlocal last_highlight, highlight_until
            selections.append(name)
            selection_times.append(float(rt))
            selection_positions.append(position)
            code = selection_trigger.get(name) if isinstance(selection_trigger, dict) else selection_trigger
            selection_triggers.append(code)
            self._emit_trigger(
                code,
                when="now",
                wait=True,
                name=f"{self.label}_selection",
                meta={"kind": "pointer_selection", "target": name, "index": len(selections) - 1},
            )
            last_highlight = name
            highlight_until = float(rt) + max(0.0, float(highlight_duration))

        try:
            for frame_i in range(max(0, n_frames - 1)):
                elapsed = float(self.clock.getTime())
                for stim in visual_stims:
                    stim.draw()
                if (
                    last_highlight is not None
                    and elapsed <= highlight_until
                    and highlight_targets is not None
                    and last_highlight in highlight_targets
                ):
                    highlight_targets[last_highlight].draw()

                if frame_i == n_frames - 2:
                    self.win.callOnFlip(self._stamp_close)
                self.win.flip()
                elapsed = float(self.clock.getTime())

                if responder is not None:
                    while next_simulated < len(simulated_actions) and elapsed >= simulated_actions[next_simulated][1]:
                        target_name, action_rt = simulated_actions[next_simulated]
                        accept_selection(target_name, action_rt, None)
                        next_simulated += 1
                        if len(selections) >= required:
                            break
                else:
                    pressed = bool(mouse.getPressed()[0]) if mouse is not None else False
                    if pressed and not previous_pressed and mouse is not None:
                        position = [float(value) for value in mouse.getPos()]
                        for target_name, target_stim in targets.items():
                            if target_stim.contains(position):
                                accept_selection(target_name, elapsed, position)
                                break
                    previous_pressed = pressed

                if len(selections) >= required:
                    self._emit_trigger(
                        complete_trigger,
                        when="now",
                        wait=True,
                        name=f"{self.label}_complete",
                        meta={"kind": "pointer_sequence_complete", "count": len(selections)},
                    )
                    self.set_state(complete_trigger=complete_trigger)
                    break
        finally:
            if responder is None:
                self.win.mouseVisible = original_mouse_visible

        completed = len(selections) >= required
        if not completed:
            self._emit_trigger(
                timeout_trigger,
                when="now",
                wait=True,
                name=f"{self.label}_timeout",
                meta={"kind": "timeout", "count": len(selections)},
            )

        last_rt = selection_times[-1] if selection_times else None
        first_rt = selection_times[0] if selection_times else None
        onset_time_global = self.get_state("onset_time_global", None)
        self.set_state(
            response=list(selections) if selections else None,
            responses=list(selections),
            response_count=len(selections),
            response_times=list(selection_times),
            response_positions=list(selection_positions),
            selection_triggers=list(selection_triggers),
            key_press=bool(selections),
            completed=completed,
            timed_out=not completed,
            first_rt=first_rt,
            rt=last_rt,
            response_time=last_rt,
            response_time_global=(onset_time_global + last_rt) if onset_time_global is not None and last_rt is not None else None,
            timeout_trigger=timeout_trigger if not completed else None,
        )
        if self.get_state("close_time", None) is None:
            self._stamp_close()

        if responder is not None and hasattr(responder, "on_feedback"):
            try:
                responder.on_feedback(
                    Feedback(
                        trial_id=self.get_state("trial_id", self.get_state("trial_index", "unknown")),
                        phase=self.label,
                        outcome="complete" if completed else "timeout",
                        reward=None,
                        meta={"responses": list(selections), "response_times": list(selection_times)},
                    )
                )
            except Exception:
                pass

        self.log_unit()
        return self

    def capture_pointer_pursuit(self, **options) -> "StimUnit":
        """Capture an opt-in circular moving target in software pixel units.

        The framework owns elapsed-time drawing, pointer polling, missing-data
        handling, duration-weighted scoring and synthetic QA responder injection.
        See :mod:`psyflow.pointer_pursuit` for the explicit sampling contract.
        """
        from .pointer_pursuit import capture_pursuit
        return capture_pursuit(self, **options)

    def capture_pointer_trace(
        self,
        path_points: Sequence[Sequence[float]],
        corridor_width: float,
        duration: float,
        cursor: visual.BaseVisualStim,
        transform: str = "identity",
        finish_radius: float = 0.4,
        completion_progress: float = 0.95,
        onset_trigger: int = None,
        start_trigger: int = None,
        error_trigger: int = None,
        complete_trigger: int = None,
        timeout_trigger: int = None,
        error_cursor: visual.BaseVisualStim | None = None,
        trail_color: Any = "#f6c453",
        trail_line_width: float = 2.0,
    ) -> "StimUnit":
        """Capture a continuous press-and-drag trace along an ordered path.

        PsyFlow owns pointer sampling, display-coordinate transformation, path
        geometry, trace metrics, triggers, and responder injection. Tasks supply
        only their path, corridor, cursor stimuli, timing, and trigger codes.
        """
        path = normalize_path(path_points)
        width = float(corridor_width)
        if width <= 0.0:
            raise ValueError("corridor_width must be positive")
        if not isinstance(cursor, visual.BaseVisualStim):
            raise TypeError("cursor must be a PsychoPy visual stimulus")
        if error_cursor is not None and not isinstance(error_cursor, visual.BaseVisualStim):
            raise TypeError("error_cursor must be a PsychoPy visual stimulus")
        transform_point((0.0, 0.0), transform)

        nominal = float(duration)
        if nominal <= 0.0:
            raise ValueError("duration must be positive")
        used, n_frames, scaled = self._qa_scale_duration(nominal)
        if scaled:
            self.set_state(duration_nominal=nominal, duration_scaled=used)
        self.set_state(
            duration=used,
            path_points=[list(point) for point in path],
            corridor_width=width,
            pointer_transform=transform,
            completion_progress=float(completion_progress),
            finish_radius=float(finish_radius),
        )

        visual_stims = [stim for stim in self.stimuli if hasattr(stim, "draw") and callable(stim.draw)]
        for stim in visual_stims:
            stim.draw()
        self.win.callOnFlip(self.clock.reset)
        self.win.callOnFlip(self._stamp_onset, onset_trigger)
        self._emit_trigger(
            onset_trigger,
            when="flip",
            wait=False,
            name=f"{self.label}_onset",
            meta={"kind": "onset"},
        )
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)

        ctx = get_context()
        responder = None
        if ctx is not None and ctx.mode in ("qa", "sim") and getattr(ctx, "responder", None) is not None:
            responder = ctx.responder

        original_mouse_visible = bool(getattr(self.win, "mouseVisible", False))
        mouse = None
        samples: list[dict[str, object]] = []
        physical_positions: list[list[float]] = []
        display_positions: list[list[float]] = []
        drawing_started = False
        start_time: float | None = None
        previous_pressed = False
        previous_inside = True
        pointer_lifts = 0
        max_progress = 0.0
        completed = False

        if responder is not None:
            adapter = ResponderAdapter(
                policy=str(getattr(getattr(ctx, "config", None), "sim_policy", "warn") or "warn"),
                default_rt_s=float(getattr(getattr(ctx, "config", None), "default_rt_s", 0.2) or 0.2),
                clamp_rt=bool(getattr(getattr(ctx, "config", None), "clamp_rt", False)),
                logger=getattr(ctx, "sim_logger", None),
                session=getattr(ctx, "session", None),
            )
            observation = Observation(
                mode=getattr(ctx, "mode", "qa"),
                trial_id=self.get_state("trial_id", self.get_state("trial_index", None)),
                block_id=self.get_state("block_id", None),
                phase=self.label,
                deadline_s=used,
                response_window_open=True,
                response_window_s=used,
                valid_keys=["trace"],
                t_phase_onset=self.get_state("onset_time", None),
                t_phase_onset_global=self.get_state("onset_time_global", None),
                stim_id=self.get_state("stim_id", None),
                stim_features=self.get_state("stim_features", None),
                condition_id=self.get_state("condition_id", None),
                task_factors=dict(self.get_state("task_factors", None) or {}),
            )
            handled = adapter.handle_response(observation, responder)
            action = handled.used_action
            if action.key == "trace":
                profile = str((action.meta or {}).get("trace_profile", "accurate"))
                sim_duration = min(used, max(0.01, float(action.rt_s or used * 0.8)))
                samples = build_simulated_trace(
                    path,
                    profile=profile,
                    duration_s=sim_duration,
                    corridor_width=width,
                )
                drawing_started = bool(samples)
                start_time = 0.0 if samples else None
                for sample in samples:
                    shown = sample["display"]
                    display_positions.append([float(shown[0]), float(shown[1])])
                    physical = transform_point(shown, transform)
                    physical_positions.append([physical[0], physical[1]])
                if drawing_started:
                    self._emit_trigger(
                        start_trigger,
                        when="now",
                        wait=True,
                        name=f"{self.label}_start",
                        meta={"kind": "pointer_trace_start"},
                    )
        else:
            self.win.mouseVisible = False
            mouse = event.Mouse(win=self.win, visible=False)
            mouse.clickReset()

        try:
            if responder is None:
                for frame_i in range(max(0, n_frames - 1)):
                    elapsed = float(self.clock.getTime())
                    physical = [float(value) for value in mouse.getPos()]
                    shown = transform_point(physical, transform)
                    distance, progress = nearest_path_position(shown, path)
                    inside = distance <= width / 2.0
                    pressed = bool(mouse.getPressed()[0])

                    if pressed and not previous_pressed and not drawing_started:
                        start_distance = ((shown[0] - path[0][0]) ** 2 + (shown[1] - path[0][1]) ** 2) ** 0.5
                        if start_distance <= float(finish_radius):
                            drawing_started = True
                            start_time = elapsed
                            self._emit_trigger(
                                start_trigger,
                                when="now",
                                wait=True,
                                name=f"{self.label}_start",
                                meta={"kind": "pointer_trace_start"},
                            )

                    if drawing_started and pressed:
                        trace_t = max(0.0, elapsed - float(start_time if start_time is not None else elapsed))
                        samples.append({"t": trace_t, "display": [shown[0], shown[1]]})
                        physical_positions.append(list(physical))
                        display_positions.append([shown[0], shown[1]])
                        max_progress = advance_ordered_progress(max_progress, progress)
                        if not inside and previous_inside:
                            self._emit_trigger(
                                error_trigger,
                                when="now",
                                wait=True,
                                name=f"{self.label}_error",
                                meta={"kind": "pointer_trace_excursion", "progress": progress},
                            )
                        previous_inside = inside
                        finish_distance = ((shown[0] - path[0][0]) ** 2 + (shown[1] - path[0][1]) ** 2) ** 0.5
                        if max_progress >= float(completion_progress) and finish_distance <= float(finish_radius):
                            completed = True

                    if drawing_started and previous_pressed and not pressed:
                        pointer_lifts += 1
                    previous_pressed = pressed

                    for stim in visual_stims:
                        stim.draw()
                    if len(display_positions) >= 2:
                        trail = visual.ShapeStim(
                            self.win,
                            vertices=display_positions,
                            closeShape=False,
                            lineColor=trail_color,
                            lineWidth=float(trail_line_width),
                            fillColor=None,
                            units=getattr(self.win, "units", None),
                        )
                        trail.draw()
                    cursor.pos = shown
                    active_cursor = error_cursor if drawing_started and not inside and error_cursor is not None else cursor
                    active_cursor.pos = shown
                    active_cursor.draw()
                    if frame_i == n_frames - 2:
                        self.win.callOnFlip(self._stamp_close)
                    self.win.flip()
                    if completed:
                        break
        finally:
            if responder is None:
                self.win.mouseVisible = original_mouse_visible

        metrics = evaluate_trace(
            samples,
            path,
            corridor_width=width,
            completion_progress=float(completion_progress),
            finish_radius=float(finish_radius),
        )
        completed = bool(metrics["completed"])
        if responder is not None:
            for _ in range(int(metrics["error_excursions"])):
                self._emit_trigger(
                    error_trigger,
                    when="now",
                    wait=True,
                    name=f"{self.label}_error",
                    meta={"kind": "pointer_trace_excursion", "simulated": True},
                )
        if completed:
            self._emit_trigger(
                complete_trigger,
                when="now",
                wait=True,
                name=f"{self.label}_complete",
                meta={"kind": "pointer_trace_complete"},
            )
        else:
            self._emit_trigger(
                timeout_trigger,
                when="now",
                wait=True,
                name=f"{self.label}_timeout",
                meta={"kind": "timeout"},
            )

        movement_time = metrics["movement_time"]
        onset_time_global = self.get_state("onset_time_global", None)
        self.set_state(
            response="complete" if completed else None,
            key_press=drawing_started,
            drawing_started=drawing_started,
            completed=completed,
            timed_out=not completed,
            rt=movement_time,
            response_time=movement_time,
            response_time_global=(onset_time_global + movement_time)
            if onset_time_global is not None and movement_time is not None
            else None,
            pointer_lifts=pointer_lifts,
            trajectory_physical=physical_positions,
            trajectory_display=display_positions,
            error_excursions=metrics["error_excursions"],
            off_path_duration=metrics["off_path_duration"],
            off_path_proportion=metrics["off_path_proportion"],
            rms_path_error=metrics["rms_path_error"],
            max_progress=metrics["max_progress"],
            sample_count=metrics["sample_count"],
            complete_trigger=complete_trigger if completed else None,
            timeout_trigger=timeout_trigger if not completed else None,
        )
        if self.get_state("close_time", None) is None:
            self._stamp_close()

        if responder is not None and hasattr(responder, "on_feedback"):
            try:
                responder.on_feedback(
                    Feedback(
                        trial_id=self.get_state("trial_id", self.get_state("trial_index", "unknown")),
                        phase=self.label,
                        outcome="complete" if completed else "timeout",
                        reward=None,
                        meta={key: metrics[key] for key in metrics},
                    )
                )
            except Exception:
                pass

        self.log_unit()
        return self

    def capture_pointer_reach(
        self,
        *,
        start: visual.BaseVisualStim,
        target: visual.BaseVisualStim,
        cursor: visual.BaseVisualStim,
        target_position: Sequence[float],
        target_distance: float,
        start_radius: float,
        target_radius: float,
        search_visibility_radius: float,
        start_hold_duration: float,
        movement_deadline: float,
        reaction_threshold: float,
        feedback_mode: str = "veridical",
        rotation_deg: float = 0.0,
        endpoint_freeze_duration: float = 0.05,
        onset_trigger: int = None,
        hold_trigger: int = None,
        target_trigger: int = None,
        movement_trigger: int = None,
        complete_trigger: int = None,
        hit_trigger: int = None,
        timeout_trigger: int = None,
    ) -> "StimUnit":
        """Capture a click-free centre-out reach with transformed cursor feedback.

        PsyFlow owns pointer homing, hold timing, continuous sampling, visual
        transformation, reach timing, endpoint geometry, triggers, and responder
        injection. Tasks supply only protocol geometry, timing, and stimuli.
        """
        for name, stim in (("start", start), ("target", target), ("cursor", cursor)):
            if not isinstance(stim, visual.BaseVisualStim):
                raise TypeError(f"{name} must be a PsychoPy visual stimulus")
        target_pos = [float(target_position[0]), float(target_position[1])]
        distance = float(target_distance)
        start_r = float(start_radius)
        target_r = float(target_radius)
        search_r = float(search_visibility_radius)
        hold_s = float(start_hold_duration)
        deadline_s = float(movement_deadline)
        reaction_r = float(reaction_threshold)
        freeze_s = max(0.0, float(endpoint_freeze_duration))
        if min(distance, start_r, target_r, search_r, hold_s, deadline_s, reaction_r) <= 0.0:
            raise ValueError("pointer reach geometry and timing values must be positive")
        if reaction_r >= distance:
            raise ValueError("reaction_threshold must be smaller than target_distance")
        transform_reach_point((0.0, 0.0), feedback_mode, rotation_deg)
        target.pos = target_pos
        self.set_state(
            target_position=target_pos,
            target_distance=distance,
            start_radius=start_r,
            target_radius=target_r,
            search_visibility_radius=search_r,
            start_hold_duration=hold_s,
            movement_deadline=deadline_s,
            reaction_threshold=reaction_r,
            feedback_mode=str(feedback_mode),
            rotation_deg=float(rotation_deg),
            endpoint_freeze_duration=freeze_s,
        )

        ctx = get_context()
        responder = None
        if ctx is not None and ctx.mode in ("qa", "sim") and getattr(ctx, "responder", None) is not None:
            responder = ctx.responder

        original_mouse_visible = bool(getattr(self.win, "mouseVisible", False))
        mouse = None
        samples: list[dict[str, object]] = []
        search_time = 0.0
        movement_started = False

        def draw_scene(physical: Sequence[float], *, show_target: bool, moving: bool) -> list[float]:
            for stim in self.stimuli:
                if hasattr(stim, "draw") and callable(stim.draw):
                    stim.draw()
            start.draw()
            if show_target:
                target.draw()
            physical_xy = [float(physical[0]), float(physical[1])]
            shown = list(transform_reach_point(physical_xy, feedback_mode, rotation_deg)) if moving else physical_xy
            visible = hypot(*physical_xy) <= search_r if not show_target else (not moving or feedback_mode != "none")
            if visible:
                cursor.pos = shown
                cursor.draw()
            return shown

        draw_scene((0.0, 0.0), show_target=False, moving=False)
        self.win.callOnFlip(self.clock.reset)
        self.win.callOnFlip(self._stamp_onset, onset_trigger)
        self._emit_trigger(onset_trigger, when="flip", wait=False, name=f"{self.label}_homing", meta={"kind": "onset"})
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)

        if responder is not None:
            adapter = ResponderAdapter(
                policy=str(getattr(getattr(ctx, "config", None), "sim_policy", "warn") or "warn"),
                default_rt_s=float(getattr(getattr(ctx, "config", None), "default_rt_s", 0.2) or 0.2),
                clamp_rt=bool(getattr(getattr(ctx, "config", None), "clamp_rt", False)),
                logger=getattr(ctx, "sim_logger", None),
                session=getattr(ctx, "session", None),
            )
            observation = Observation(
                mode=getattr(ctx, "mode", "qa"),
                trial_id=self.get_state("trial_id", self.get_state("trial_index", None)),
                block_id=self.get_state("block_id", None),
                phase=self.label,
                deadline_s=deadline_s,
                response_window_open=True,
                response_window_s=deadline_s,
                valid_keys=["pointer_reach"],
                t_phase_onset=self.get_state("onset_time", None),
                t_phase_onset_global=self.get_state("onset_time_global", None),
                stim_id=self.get_state("stim_id", None),
                stim_features=self.get_state("stim_features", None),
                condition_id=self.get_state("condition_id", None),
                task_factors=dict(self.get_state("task_factors", None) or {}),
            )
            action = adapter.handle_response(observation, responder).used_action
            meta = dict(action.meta or {})
            search_time = max(0.0, float(meta.get("search_time_s", 0.2)))
            self._emit_trigger(hold_trigger, when="now", wait=True, name=f"{self.label}_hold", meta={"kind": "pointer_hold", "simulated": True})
            self._emit_trigger(target_trigger, when="now", wait=True, name=f"{self.label}_target", meta={"kind": "target_onset", "simulated": True})
            if action.key == "pointer_reach" and not bool(meta.get("timeout", False)):
                reaction_time = max(0.0, float(meta.get("reaction_time_s", action.rt_s or 0.25)))
                movement_time = max(0.0, float(meta.get("movement_time_s", min(0.15, deadline_s * 0.5))))
                hand_angle = float(
                    meta.get(
                        "hand_angle_deg",
                        dict(observation.task_factors or {}).get("target_angle_deg", 0.0),
                    )
                )
                samples = build_simulated_reach(
                    target_distance=distance,
                    hand_angle_deg=hand_angle,
                    reaction_time_s=reaction_time,
                    movement_time_s=movement_time,
                    feedback_mode=feedback_mode,
                    rotation_deg=rotation_deg,
                )
                movement_started = True
                self._emit_trigger(movement_trigger, when="now", wait=True, name=f"{self.label}_movement", meta={"kind": "movement_onset", "simulated": True})
            metrics = evaluate_reach(
                samples,
                target_position=target_pos,
                target_distance=distance,
                target_radius=target_r,
                reaction_threshold=reaction_r,
                movement_deadline=deadline_s,
            )
        else:
            self.win.mouseVisible = False
            mouse = event.Mouse(win=self.win, visible=False)
            hold_started: float | None = None
            target_onset: float | None = None
            movement_onset: float | None = None
            try:
                while target_onset is None:
                    physical = [float(value) for value in mouse.getPos()]
                    elapsed = float(self.clock.getTime())
                    inside = hypot(*physical) <= start_r
                    if inside and hold_started is None:
                        hold_started = elapsed
                        search_time = elapsed
                        self._emit_trigger(hold_trigger, when="now", wait=True, name=f"{self.label}_hold", meta={"kind": "pointer_hold"})
                    elif not inside:
                        hold_started = None
                    draw_scene(physical, show_target=False, moving=False)
                    self.win.flip()
                    if hold_started is not None and elapsed - hold_started >= hold_s:
                        physical = [float(value) for value in mouse.getPos()]
                        draw_scene(physical, show_target=True, moving=False)
                        self._emit_trigger(target_trigger, when="flip", wait=False, name=f"{self.label}_target", meta={"kind": "target_onset"})
                        self.win.flip()
                        target_onset = float(self.clock.getTime())

                completed_live = False
                timed_out_live = False
                endpoint_physical = [float(value) for value in mouse.getPos()]
                while not completed_live and not timed_out_live:
                    elapsed = float(self.clock.getTime())
                    physical = [float(value) for value in mouse.getPos()]
                    radius = hypot(*physical)
                    if not movement_started and radius > start_r:
                        movement_started = True
                        movement_onset = elapsed
                        self._emit_trigger(movement_trigger, when="now", wait=True, name=f"{self.label}_movement", meta={"kind": "movement_onset"})
                    shown = draw_scene(physical, show_target=True, moving=movement_started)
                    self.win.flip()
                    if movement_started:
                        samples.append(
                            {
                                "t": elapsed - float(target_onset),
                                "physical": list(physical),
                                "display": list(shown),
                                "visible": feedback_mode != "none",
                            }
                        )
                        endpoint_physical = list(physical)
                        completed_live = radius >= distance
                        timed_out_live = elapsed - float(movement_onset) > deadline_s

                metrics = evaluate_reach(
                    samples,
                    target_position=target_pos,
                    target_distance=distance,
                    target_radius=target_r,
                    reaction_threshold=reaction_r,
                    movement_deadline=deadline_s,
                )
                if bool(metrics["completed"]) and freeze_s > 0.0:
                    freeze_frames = max(1, int(round(freeze_s / self.frame_time)))
                    for _ in range(freeze_frames):
                        draw_scene(endpoint_physical, show_target=True, moving=True)
                        self.win.flip()
            finally:
                self.win.mouseVisible = original_mouse_visible

        completed = bool(metrics["completed"])
        if completed:
            self._emit_trigger(complete_trigger, when="now", wait=True, name=f"{self.label}_complete", meta={"kind": "pointer_reach_complete"})
            if bool(metrics["cursor_hit"]):
                self._emit_trigger(hit_trigger, when="now", wait=True, name=f"{self.label}_hit", meta={"kind": "pointer_reach_hit"})
        else:
            self._emit_trigger(timeout_trigger, when="now", wait=True, name=f"{self.label}_timeout", meta={"kind": "timeout"})

        physical_positions = [list(sample["physical"]) for sample in samples]
        display_positions = [list(sample["display"]) for sample in samples]
        reaction_time = metrics["reaction_time"]
        onset_time_global = self.get_state("onset_time_global", None)
        self.set_state(
            response="complete" if completed else None,
            key_press=movement_started,
            completed=completed,
            timed_out=not completed,
            rt=reaction_time,
            response_time=reaction_time,
            response_time_global=(onset_time_global + reaction_time)
            if onset_time_global is not None and reaction_time is not None
            else None,
            search_time=search_time,
            reaction_time=reaction_time,
            movement_time=metrics["movement_time"],
            physical_endpoint=metrics["physical_endpoint"],
            display_endpoint=metrics["display_endpoint"],
            hand_angle_deg=metrics["hand_angle_deg"],
            cursor_angle_deg=metrics["cursor_angle_deg"],
            cursor_error_deg=metrics["cursor_error_deg"],
            cursor_hit=metrics["cursor_hit"],
            trajectory_physical=physical_positions,
            trajectory_display=display_positions,
            sample_count=metrics["sample_count"],
            complete_trigger=complete_trigger if completed else None,
            hit_trigger=hit_trigger if completed and bool(metrics["cursor_hit"]) else None,
            timeout_trigger=timeout_trigger if not completed else None,
        )
        self._stamp_close()
        if responder is not None and hasattr(responder, "on_feedback"):
            try:
                responder.on_feedback(
                    Feedback(
                        trial_id=self.get_state("trial_id", self.get_state("trial_index", "unknown")),
                        phase=self.label,
                        outcome="complete" if completed else "timeout",
                        reward=None,
                        meta={key: metrics[key] for key in metrics},
                    )
                )
            except Exception:
                pass
        self.log_unit()
        return self

    def wait_and_continue(
        self,
        keys: list[str] = ["space"],
        min_wait: Optional[float] = None,
        log_message: Optional[str] = None,
        terminate: bool = False
    ) -> "StimUnit":
        """
        Display the current stimuli (visual and sound) and wait for a key press to continue or quit.

        Parameters
        ----------
        keys : list[str]
            Keys that allow the trial to proceed (default: ["space"]).
        min_wait : float or None
            Minimum time to wait before accepting key press. If None, and any sound
            stimuli are present, it is automatically set to the longest sound duration.
        log_message : str, optional
            Optional log message (default: auto-generated).
        terminate : bool
            If True, the experiment will quit after key press.

        Returns
        -------
        StimUnit
        """
        self.set_state(wait_keys=keys)

        # auto-compute min_wait if not provided
        if min_wait is None:
            min_wait = 0.0
            for stim in self.stimuli:
                if hasattr(stim, "getDuration") and callable(stim.getDuration):
                    try:
                        dur = stim.getDuration()
                        if dur is not None:
                            min_wait = max(min_wait, dur)
                    except Exception:
                        continue

        # draw/play all stimuli at onset
        sound_stims = []
        for stim in self.stimuli:
            if hasattr(stim, "play") and callable(stim.play):
                sound_stims.append(stim)
            else:
                stim.draw()

        # Flip-synced onset stamps: evaluate times at flip-time, not schedule-time.
        self.win.callOnFlip(self.kb.clearEvents)
        self.win.callOnFlip(self._reset_keyboard_clock)
        self.win.callOnFlip(self.clock.reset)
        self.win.callOnFlip(self._stamp_onset)
        for stim in sound_stims:
            self.win.callOnFlip(stim.play)
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)

        ctx = get_context()
        responder = None
        if ctx is not None and ctx.mode in ("qa", "sim") and getattr(ctx, "responder", None) is not None:
            responder = ctx.responder

        sim_key = None
        sim_rt = None
        max_wait_s = None
        if responder is not None:
            max_wait_s = float(getattr(getattr(ctx, "config", None), "max_wait_s", 10.0) or 10.0)
            obs = Observation(
                mode=getattr(ctx, "mode", "qa") if ctx is not None else "qa",
                trial_id=self.get_state("trial_id", self.get_state("trial_index", None)),
                block_id=self.get_state("block_id", None),
                phase=self.label,
                valid_keys=list(keys),
                deadline_s=max_wait_s,
                t_phase_onset=self.get_state("onset_time", None),
                t_phase_onset_global=self.get_state("onset_time_global", None),
                stim_id=self.get_state("stim_id", None),
                stim_features=self.get_state("stim_features", None),
                condition_id=self.get_state("condition_id", None),
                task_factors=self.get_state("task_factors", None) or {},
                extras={"min_wait_s": float(min_wait or 0.0)},
            )
            adapter = ResponderAdapter(
                policy=str(getattr(getattr(ctx, "config", None), "sim_policy", "warn") or "warn"),
                default_rt_s=float(getattr(getattr(ctx, "config", None), "default_rt_s", 0.2) or 0.2),
                clamp_rt=bool(getattr(getattr(ctx, "config", None), "clamp_rt", False)),
                logger=getattr(ctx, "sim_logger", None) if ctx is not None else None,
                session=getattr(ctx, "session", None) if ctx is not None else None,
            )
            handled = None
            try:
                handled = adapter.handle_response(obs, responder)
            except ResponderActionError:
                raise
            except Exception:
                handled = None
            if handled is not None:
                sim_key = handled.used_action.key
                sim_rt = handled.used_action.rt_s
                if sim_rt is not None:
                    sim_rt = max(float(sim_rt), float(min_wait or 0.0))

        while True:
            for stim in self.stimuli:
                if not (hasattr(stim, "play") and callable(stim.play)):
                    stim.draw()
            self.win.flip()

            if responder is None:
                keys_pressed = self.kb.getKeys(keyList=keys, waitRelease=False)
                if keys_pressed:
                    kp = keys_pressed[0]
                    rt = kp.rt
                    if rt is None:
                        rt = self.clock.getTime()
                    if rt < min_wait:
                        continue

                    key = kp.name
                    onset_time_global = self.get_state("onset_time_global", None)
                    response_time_global = (
                        onset_time_global + rt
                        if onset_time_global is not None and rt is not None
                        else core.getAbsTime()
                    )
                    self.set_state(
                        response=key,
                        response_time=rt,
                        response_time_global=response_time_global,
                        close_time=rt,
                        close_time_global=response_time_global,
                    )
                    break
            else:
                elapsed = self.clock.getTime()
                if max_wait_s is not None and elapsed > max_wait_s:
                    raise RuntimeError(
                        f"QA wait_and_continue exceeded max_wait_s={max_wait_s} without response (unit={self.label!r})"
                    )
                if sim_key is not None and sim_rt is not None and elapsed >= sim_rt:
                    key = sim_key
                    rt = sim_rt
                    onset_time_global = self.get_state("onset_time_global", None)
                    response_time_global = (
                        onset_time_global + rt
                        if onset_time_global is not None and rt is not None
                        else core.getAbsTime()
                    )
                    self.set_state(
                        response=key,
                        response_time=rt,
                        response_time_global=response_time_global,
                        close_time=rt,
                        close_time_global=response_time_global,
                    )
                    break

        msg = log_message or (
            "Experiment ended by key press." if terminate else f"Continuing after key '{key}'"
        )
        logging.data(f"[StimUnit] wait_and_continue: {msg}")
        self.log_unit()

        if responder is not None and hasattr(responder, "on_feedback"):
            try:
                responder.on_feedback(
                    Feedback(
                        trial_id=self.get_state("trial_id", self.get_state("trial_index", "unknown")),
                        phase=self.label,
                        outcome="continue",
                        reward=None,
                        meta={
                            "response": self.get_state("response", None),
                            "response_time": self.get_state("response_time", None),
                        },
                    )
                )
            except Exception:
                pass

        if terminate:
            self.win.close()

        return self

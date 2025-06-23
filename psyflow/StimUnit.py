from psychopy import core, visual, logging, sound
from psychopy.hardware.keyboard import Keyboard
from typing import Callable, Optional, List, Dict, Any, Union
import random
from psyflow import TriggerSender

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
    - Logs detailed trial state to PsychoPy’s logging system.

    Parameters
    ----------
    win : visual.Window
        PsychoPy window where stimuli will be drawn.
    unit_label : str
        Identifier for the trial (used for logging/debugging).
    trigger : Trigger, optional
        External trigger handler (default: a dummy TriggerSender instance).
    frame_time : float
        Duration of a single frame in seconds (default: 1/60 for 60Hz).
    """

    def __init__(
    self,
    unit_label: str,
    win: visual.Window,
    kb: Optional[Keyboard] = None,
    triggersender: Optional[TriggerSender] = None
):
        self.win = win
        self.label = unit_label
        self.triggersender = triggersender
        self.stimuli: List[visual.BaseVisualStim] = []
        self.state: Dict[str, Any] = {}
        self.clock = core.Clock()
        self.kb = kb or Keyboard()
        self._hooks: Dict[str, List] = {"start": [], "response": [], "timeout": [], "end": []}
        self.frame_time = self.win.monitorFramePeriod

    def add_stim(self, *stims: Union[visual.BaseVisualStim, sound.Sound, List[Union[visual.BaseVisualStim, sound.Sound]]]) -> "StimUnit":
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
            if not isinstance(stim, (visual.BaseVisualStim, sound.Sound)):
                raise TypeError(f"add_stim expects visual or sound stimuli, got {type(stim)}")
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
    
    def get_dict(self, target: Optional[dict] = None) -> dict:
        """
        Return the internal state dictionary, or merge into an external one.

        Parameters
        ----------
        target : dict, optional
            If provided, updates this dict in-place and returns it.

        Returns
        -------
        dict
            The internal state (or merged result if target is provided).
        """
        return dict(self.state)

    def send_trigger(self, trigger_code: int) -> "StimUnit":
        """
        Send a trigger value via the connected trigger object.

        Parameters
        ----------
        trigger_code : int
            The value to send.

        Returns
        -------
        StimUnit
        """
        if self.triggersender is not None:
            self.triggersender.send(trigger_code)
        return self

    def log_unit(self) -> None:
        """Write the current trial state to PsychoPy logs.

        All key-value pairs stored in :attr:`state` are emitted using
        ``logging.data`` which allows post‑hoc reconstruction of each trial.

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

    def duration(self, duration: float | list | tuple): 
        """
        Auto-close the trial after a fixed or jittered duration.

        Parameters
        ----------
        duration : float or list
            Duration or (min, max) range for random sampling.
        """
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
        def auto_close(unit: 'StimUnit'):
            unit.set_state(
                duration=t_val,
                timeout_triggered=True,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
        return self.on_timeout(t_val, auto_close)

    def close_on(self, *keys: str):
        """
        Auto-close the trial on specific key press.

        Parameters
        ----------
        keys : str
            One or more response keys.
        """
        def close_fn(unit: 'StimUnit', key: str, rt: float):
            unit.set_state(
                keys=key,
                response_time=rt,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
        return self.on_response(list(keys), close_fn)


    def run(self,
            terminate_on_response: bool = True) -> "StimUnit":
        """Execute the full trial lifecycle.

        This method draws all registered stimuli, handles response and timeout
        events, executes registered hooks and logs the final state.

        Parameters
        ----------
        terminate_on_response : bool, optional
            If ``True`` the trial ends immediately once a response is
            registered. Defaults to ``True``.

        Returns
        -------
        StimUnit
            The instance itself for chaining.

        Examples
        --------
        >>> StimUnit("trial1", win).run()
        """
        self.set_state(global_time=core.getAbsTime())

        for hook in self._hooks["start"]:
            hook(self)

        # Initial flip with onset timestamp
        for stim in self.stimuli:
            stim.draw()
        
        self.win.callOnFlip(self.set_state, onset_time=self.clock.getTime(),onset_time_global=core.getAbsTime())
        self.win.callOnFlip(self.clock.reset)
        self.win.flip()
        self.kb.clearEvents()
        responded = False

        all_keys = list(set(k for k_list, _ in self._hooks["response"] for k in k_list))


        # Estimate total frame duration based on maximum timeout
        max_timeout = max((t for t, _ in self._hooks["timeout"]), default=5.0)
        n_frames = int(round(max_timeout / self.frame_time))

        for _ in range(n_frames-1):
            if not (responded and terminate_on_response):
                for stim in self.stimuli:
                    stim.draw()
            self.win.flip()

            keys = self.kb.getKeys(keyList=all_keys, waitRelease=False)
            for key_obj in keys:
                key_name, key_rt = key_obj.name, key_obj.rt
                for valid_keys, hook in self._hooks["response"]:
                    if key_name in valid_keys:
                        hook(self, key_name, key_rt)
                        responded = True


            elapsed = self.clock.getTime()
            for timeout_duration, timeout_hook in self._hooks["timeout"]:
                if elapsed >= timeout_duration and not responded:
                    self.set_state(
                        timeout_triggered=True,
                        duration=elapsed,
                        close_time=core.getTime(),
                        close_time_global=core.getAbsTime()
                    )
                    timeout_hook(self)
                    responded = True

        self.set_state(
            close_time=core.getTime(),
            close_time_global=core.getAbsTime()
        )
        for hook in self._hooks["end"]:
            hook(self)

        self.log_unit()
        return self

    
    def show(
        self,
        duration: float | list | tuple | None = None,
        onset_trigger: int = None,
        offset_trigger: int = None
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
            - None → automatically use max sound duration (if any)
        onset_trigger : int
            Trigger code to send at stimulus onset.
        offset_trigger : int
            Trigger code to send at stimulus offset.

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

        self.set_state(duration=t_val)

        # --- Initial Flip (trigger locked to onset) ---
        for stim in self.stimuli:
            if hasattr(stim, "play") and callable(stim.play):
                self.win.callOnFlip(stim.play)
            else:
                stim.draw()

        self.win.callOnFlip(self.send_trigger, onset_trigger)
        self.win.callOnFlip(
            self.set_state,
            onset_time=self.clock.getTime(),
            onset_time_global=core.getAbsTime(),
            onset_trigger=onset_trigger
        )
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)

        # --- Frame-based visual presentation ---
        visual_stims = [s for s in self.stimuli if hasattr(s, "draw") and callable(s.draw)]
        n_frames = int(round(t_val / self.frame_time))

        for frame_i in range(n_frames - 1):
            for stim in visual_stims:
                stim.draw()
            # if frame_i == n_frames - 2: # if it is the last frame, schedule the offset
            #     self.win.callOnFlip(
            #         self.set_state,
            #         offset_trigger=offset_trigger,
            #         close_time=self.clock.getTime(),
            #         close_time_global=core.getAbsTime()
            #     )
            #     self.win.callOnFlip(self.send_trigger, offset_trigger)
            self.win.flip()
        self.set_state(
            close_time=self.clock.getTime(),
            close_time_global=core.getAbsTime()
        )
        self.send_trigger(offset_trigger)

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
        self.set_state(duration=t_val)
        
        # initial draw + trigger scheduling
        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, onset_trigger)
        self.win.callOnFlip(self.set_state,
                        onset_time=self.clock.getTime(), 
                        onset_time_global=core.getAbsTime(),
                        onset_trigger=onset_trigger)
        self.win.callOnFlip(self.clock.reset)
        self.kb.clearEvents()
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)

         # if no correct_keys provided, any key in `keys` is valid
        if correct_keys is None:
            correct_keys = keys
        elif isinstance(correct_keys, str):
            correct_keys = [correct_keys]
        responded = False
        chosen_key = None  # track which key to highlight


        n_frames = int(round(t_val / self.frame_time))
        for _ in range(n_frames-1):
            # draw or blank?
            if not (responded and terminate_on_response):
                for stim in self.stimuli:
                    stim.draw()
            # draw highlight if requested
            if highlight_stim and (responded or dynamic_highlight):
                h = (highlight_stim.get(chosen_key)
                    if isinstance(highlight_stim, dict)
                    else highlight_stim)
                if h:
                    h.draw()    
            self.win.flip()

            # only listen for keys if we haven’t responded or if dynamic_highlight=True
            if not responded or dynamic_highlight:
                keypress = self.kb.getKeys(keyList=keys, waitRelease=False)
                if keypress:
                    k = keypress[0].name
                    chosen_key = k 
                    rt = self.clock.getTime()
                    self.set_state(
                        hit=k in correct_keys, 
                        correct_keys=correct_keys,
                        response=k, 
                        key_press=True,
                        rt=rt,
                        close_time=self.clock.getTime(),
                        close_time_global=core.getAbsTime()
                    )
                    code = (response_trigger.get(k, None)
                        if isinstance(response_trigger, dict)
                        else response_trigger)
                    self.send_trigger(code)
                    self.set_state(response_trigger=code)
                    responded = True
                     
                     # if we should stop immediately, break out
                    if terminate_on_response and not dynamic_highlight:
                        break


        if not responded: 
            self.set_state(
                hit=False, 
                correct_keys=correct_keys,
                response=None, 
                key_press=False,
                rt=None,
                close_time=self.clock.getTime(),
                close_time_global=core.getAbsTime(),
                timeout_trigger=timeout_trigger
            )
            self.send_trigger(timeout_trigger)

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
        for stim in self.stimuli:
            if hasattr(stim, "play") and callable(stim.play):
                self.win.callOnFlip(stim.play)
            else:
                stim.draw()

        self.win.callOnFlip(self.set_state,
                            onset_time=self.clock.getTime(),
                            onset_time_global=core.getAbsTime())
        self.win.callOnFlip(self.clock.reset)
        flip_time = self.win.flip()
        self.kb.clearEvents()
        self.set_state(flip_time=flip_time)

        while True:
            for stim in self.stimuli:
                if not (hasattr(stim, "play") and callable(stim.play)):
                    stim.draw()
            self.win.flip()

            keys_pressed = self.kb.getKeys(keyList=keys, waitRelease=False)
            if keys_pressed:
                elapsed = self.clock.getTime()
                if elapsed < min_wait:
                    continue

                key = keys_pressed[0].name
                rt = elapsed
                self.set_state(
                    response=key,
                    response_time=rt,
                    close_time=core.getTime(),
                    close_time_global=core.getAbsTime()
                )
                break

        msg = log_message or (
            "Experiment ended by key press." if terminate else f"Continuing after key '{key}'"
        )
        logging.data(f"[StimUnit] wait_and_continue: {msg}")
        self.log_unit()

        if terminate:
            self.win.close()

        return self



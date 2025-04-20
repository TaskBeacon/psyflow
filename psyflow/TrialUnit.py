from psychopy import core, visual, logging
from psychopy.hardware.keyboard import Keyboard
from typing import Callable, Optional, List, Dict, Any, Union
import random
from psyflow import TriggerSender

class TrialUnit:
    """
    TrialUnit(win, unit_label, trigger=None, frame_time=1/60)

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

    def __init__(self, win: visual.Window, unit_label: str, triggersender: Optional[Any] = None):
        self.win = win
        self.label = unit_label
        self.triggersender = triggersender
        self.stimuli: List[visual.BaseVisualStim] = []
        self.state: Dict[str, Any] = {}
        self.clock = core.Clock()
        self.keyboard = Keyboard()
        self._hooks: Dict[str, List] = {"start": [], "response": [], "timeout": [], "end": []}
        self.frame_time = self.win.monitorFramePeriod

    def add_stim(self, stim: visual.BaseVisualStim) -> "TrialUnit":
        """
        Add a visual stimulus to the trial.

        Parameters
        ----------
        stim : visual.BaseVisualStim
            A PsychoPy visual stimulus (e.g., TextStim, ImageStim).

        Returns
        -------
        TrialUnit
            Returns self for chaining.
        """
        self.stimuli.append(stim)
        return self

    def clear_stimuli(self) -> "TrialUnit":
        """
        Clear all previously added stimuli from the trial.

        Returns
        -------
        TrialUnit
        """
        self.stimuli.clear()
        return self

    def set_state(self, prefix: Optional[str] = None, **kwargs) -> "TrialUnit":
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


    def to_dict(self, target: Optional[dict] = None) -> dict:
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
        if target is not None:
            target.update(self.state)
            return target
        return dict(self.state)

    def send_trigger(self, trigger_code: int) -> "TrialUnit":
        """
        Send a trigger value via the connected trigger object.

        Parameters
        ----------
        trigger_code : int
            The value to send.

        Returns
        -------
        TrialUnit
        """
        if self.triggersender is not None:
            self.triggersender.send(trigger_code)
        return self

    def log_unit(self) -> None:
        """
        Log the current state using PsychoPy's logging mechanism.
        """
        logging.data(f"[TrialUnit] Data: {self.state}")


    def on_start(self, func: Optional[Callable[['TrialUnit'], None]] = None):
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

    def on_response(self, keys: List[str], func: Optional[Callable[['TrialUnit', str, float], None]] = None):
        """
        Register or decorate a function to call when a valid response key is pressed.

        Parameters
        ----------
        keys : list[str]
            Keys that trigger the callback.
        func : Callable or None
            A function accepting (TrialUnit, key, rt) or None to use as decorator.
        """
        if func is None:
            def decorator(f):
                self._hooks["response"].append((keys, f))
                return self
            return decorator
        else:
            self._hooks["response"].append((keys, func))
            return self

    def on_timeout(self, timeout: float, func: Optional[Callable[['TrialUnit'], None]] = None):
        """
        Register or decorate a function to call on timeout.

        Parameters
        ----------
        timeout : float
            Time in seconds after which timeout is triggered.
        func : Callable or None
            A function accepting (TrialUnit) or None to use as decorator.
        """
        if func is None:
            def decorator(f):
                self._hooks["timeout"].append((timeout, f))
                return self
            return decorator
        else:
            self._hooks["timeout"].append((timeout, func))
            return self

    def on_end(self, func: Optional[Callable[['TrialUnit'], None]] = None):
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

    def duration(self, t: float | tuple[float, float]):
        """
        Auto-close the trial after a fixed or jittered duration.

        Parameters
        ----------
        t : float or tuple
            Duration or (min, max) range for random sampling.
        """
        t_val = random.uniform(*t) if isinstance(t, tuple) else t

        def auto_close(unit: 'TrialUnit'):
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
        def close_fn(unit: 'TrialUnit', key: str, rt: float):
            unit.set_state(
                keys=key,
                response_time=rt,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
        return self.on_response(list(keys), close_fn)


    def run(self, 
            frame_based: bool = False,
            terminate_on_response: bool = True) -> "TrialUnit":
        """
        Full logic loop for displaying stimulus, collecting response, handling timeout,
        and logging with precision timing.

        Parameters:
        -----------
        frame_based : bool
            Whether to use frame-counted duration instead of time-based duration.
        terminate_on_response : bool
            Whether to terminate the trial upon receiving a response.
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
        self.keyboard.clearEvents()
        responded = False

        all_keys = list(set(k for k_list, _ in self._hooks["response"] for k in k_list))

        if frame_based:
            # Estimate total frame duration based on maximum timeout
            max_timeout = max((t for t, _ in self._hooks["timeout"]), default=5.0)
            n_frames = int(round(max_timeout / self.frame_time))

            for _ in range(n_frames-1):
                if not (responded and terminate_on_response):
                    for stim in self.stimuli:
                        stim.draw()
                self.win.flip()

                keys = self.keyboard.getKeys(keyList=all_keys, waitRelease=False)
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
        else:
            # Time-based loop
            while True:
                if not (responded and self.terminate_on_response):
                    for stim in self.stimuli:
                        stim.draw()
                self.win.flip()

                keys = self.keyboard.getKeys(keyList=all_keys, waitRelease=False)
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
        duration: float | list,
        onset_trigger: int = 0,
        frame_based: bool = True
    ) -> "TrialUnit":
        """
        Display the stimulus for a specified duration, either using frame-based timing
        (recommended for EEG/fMRI) or precise time-based loop.
        """
        local_rng = random.Random()
        t_val = local_rng.uniform(*duration) if isinstance(duration, list) else duration
        self.set_state(duration=t_val)

        # --- Initial Flip (trigger locked to onset) ---
        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, onset_trigger)
        self.win.callOnFlip(self.set_state, 
                            onset_time=self.clock.getTime(), 
                            onset_time_global=core.getAbsTime(),
                            onset_trigger=onset_trigger)
        flip_time = self.win.flip()  # clear to avoid flickering

        self.set_state(
            flip_time=flip_time
        )

        # --- Frame-based or precise timing ---
        tclock = core.Clock()
        tclock.reset()

        if frame_based:
            n_frames = int(round(t_val / self.frame_time))
            for _ in range(n_frames-1):
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()
        else:
            while tclock.getTime() < t_val:
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()

        self.set_state(
            close_time=self.clock.getTime(),
            close_time_global=core.getAbsTime()
        )
        self.log_unit()
        return self

    def capture_response(
        self,
        keys: list[str],
        duration: float | list,
        onset_trigger: int = None,
        response_trigger: int | dict[str, int] = None,
        timeout_trigger: int = None,
        frame_based: bool = True,
        terminate_on_response: bool = True
    ) -> "TrialUnit":
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
        frame_based : bool
            Whether to use frame counting instead of time-based control.
        """
        local_rng = random.Random()
        t_val = local_rng.uniform(*duration) if isinstance(duration, list) else duration
        self.set_state(duration=t_val)

        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, onset_trigger)
        self.win.callOnFlip(self.set_state,
                        onset_time=self.clock.getTime(), 
                        onset_time_global=core.getAbsTime(),
                        onset_trigger=onset_trigger)
        self.win.callOnFlip(self.clock.reset)
        self.keyboard.clearEvents()
        flip_time = self.win.flip()
        self.set_state(flip_time=flip_time)
      
        responded = False

        if frame_based:
            n_frames = int(round(t_val / self.frame_time))
            for _ in range(n_frames-1):
                # draw or blank?
                if not (responded and terminate_on_response):
                    for stim in self.stimuli:
                        stim.draw()
                self.win.flip()

                keypress = self.keyboard.getKeys(keyList=keys, waitRelease=False)
                if keypress:
                    k = keypress[0].name
                    rt = self.clock.getTime()
                    self.set_state(
                        hit=True, 
                        response=k, 
                        rt=rt,
                        close_time=self.clock.getTime(),
                        close_time_global=core.getAbsTime()
                    )
                    response_trigger = response_trigger.get(k, 1) if isinstance(response_trigger, dict) else response_trigger
                    self.send_trigger(response_trigger)
                    self.set_state(response_trigger=response_trigger)
                    responded = True

        else:

            while self.clock.getTime() < t_val:
                if not (responded and terminate_on_response):
                    for stim in self.stimuli:
                        stim.draw()
                self.win.flip()

                keypress = self.keyboard.getKeys(keyList=keys, waitRelease=False)
                if keypress:
                    k = keypress[0].name
                    rt = self.clock.getTime()
                    self.set_state(
                        hit=True, 
                        response=k, 
                        rt=rt,
                        close_time=self.clock.getTime(),
                        close_time_global=core.getAbsTime()
                    )

                    response_trigger = response_trigger.get(k, 1) if isinstance(response_trigger, dict) else response_trigger
                    self.send_trigger(response_trigger)
                    self.set_state(response_trigger=response_trigger)
                    responded = True


        if not responded: 
            self.set_state(
                hit=False, 
                response=None, 
                rt=0.0,
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
        log_message: Optional[str] = None,
        terminate: bool = False
    ) -> "TrialUnit":
        """
        Display the current stimuli and wait for a key press to continue or quit.

        Parameters
        ----------
        keys : list[str]
            Keys that allow the trial to proceed (default: ["space"]).
        log_message : str, optional
            Optional log message (default: auto-generated).
        terminate : bool
            If True, the experiment will quit after key press.

        Returns
        -------
        TrialUnit
        """
        self.set_state(wait_keys=keys)

        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.set_state, 
                        onset_time=self.clock.getTime(), 
                        onset_time_global=core.getAbsTime())
        self.win.callOnFlip(self.clock.reset)
        flip_time = self.win.flip()
        self.keyboard.clearEvents()
        self.set_state(flip_time=flip_time)
        while True:
            for stim in self.stimuli:
                stim.draw()
            self.win.flip()

            keys_pressed = self.keyboard.getKeys(keyList=keys, waitRelease=False)
            if keys_pressed:
                key = keys_pressed[0].name
                rt = self.clock.getTime()
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
        logging.data(f"[TrialUnit] wait_and_continue: {msg}")
        self.log_unit()

        if terminate:
            self.win.close()

        return self


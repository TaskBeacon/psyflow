from typing import Callable, Optional
from psychopy import logging, core

class TriggerSender:
    """
    A wrapper for sending EEG/MEG trigger codes with optional hooks and delays.

    Can be initialized with a real sending function or used in mock mode
    for development/testing without hardware.

    Examples
    --------
    >>> sender = TriggerSender(lambda c: port.write(bytes([c])))
    >>> sender.send(32)

    >>> sender = TriggerSender(mock=True)
    >>> sender.send(99)
    """

    def __init__(
        self,
        trigger_func: Optional[Callable[[int], None]] = None,
        *,
        mock: bool = False,
        post_delay: float = 0.001,
        on_trigger_start: Optional[Callable[[], None]] = None,
        on_trigger_end: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the trigger sender.

        Parameters
        ----------
        trigger_func : Callable, optional
            A function that accepts an int trigger code.
        mock : bool, default=False
            If True, use a mock print function instead of sending triggers.
        post_delay : float, default=0.001
            Time to wait (in seconds) after sending each trigger.
        on_trigger_start : Callable, optional
            Hook called before sending the trigger.
        on_trigger_end : Callable, optional
            Hook called after sending the trigger.
        """
        if mock or trigger_func is None:
            self.trigger_func = lambda code: print(f"[MockTrigger] Sent code: {code}")
        else:
            self.trigger_func = trigger_func

        self.post_delay = post_delay
        self.on_trigger_start = on_trigger_start
        self.on_trigger_end = on_trigger_end

    def send(self, code: Optional[int]):
        """
        Send a trigger code using the configured function and callbacks.

        Parameters
        ----------
        code : int or None
            The code to send. If ``None`` the method does nothing and logs a
            warning.

        Returns
        -------
        None

        Examples
        --------
        >>> sender.send(1)
        """
        if code is None:
            logging.warning("[Trigger] Skipping trigger send: code is None")
            return

        if self.on_trigger_start:
            self.on_trigger_start()

        try:
            self.trigger_func(code)
        except Exception as e:
            logging.error(f"[Trigger] Failed to send trigger {code}: {e}")
        else:
            print(f"[Trigger] Trigger sent: {code}")
            logging.data(f"[Trigger] Trigger sent: {code}")

        if self.post_delay:
            core.wait(self.post_delay)

        if self.on_trigger_end:
            self.on_trigger_end()

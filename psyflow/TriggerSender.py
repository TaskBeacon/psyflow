from typing import Callable, Optional
from psychopy import logging, core


class TriggerSender:
    """
    Generalized trigger sender. User provides the actual send function.

    Usage:
    >>> Trigger(lambda code: ser.write(bytes([code])))
    >>> Trigger(mock=True)  # For development/logging only
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
        Parameters:
        - trigger_func: The actual function to send the trigger (int -> None).
        - mock: If True, overrides with a mock print trigger.
        - post_delay: Time in seconds to wait after sending trigger (default 1ms).
        - on_trigger_start: Optional callable to be called before each trigger (e.g., port open).
        - on_trigger_end: Optional callable to be called after each trigger (e.g., port close).
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
        Send a trigger code via the registered trigger function.
        Handles pre/post callbacks and optional delay.
        
        Parameters
        ----------
        code : int or None
            Trigger code to send. If None, it is skipped with a warning.
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
            logging.data(f"[Trigger] Trigger sent: {code}")

        if self.post_delay:
            core.wait(self.post_delay)

        if self.on_trigger_end:
            self.on_trigger_end()






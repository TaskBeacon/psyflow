"""Experiment/window bootstrap utilities."""

from typing import Tuple

from psychopy import core, event, logging, monitors
from psychopy.hardware import keyboard
from psychopy.visual import Window


def initialize_exp(settings, screen_id: int = 1) -> Tuple[Window, keyboard.Keyboard]:
    """Set up the PsychoPy window, keyboard and logging."""
    mon = monitors.Monitor("tempMonitor")
    mon.setWidth(getattr(settings, "monitor_width_cm", 35.5))
    mon.setDistance(getattr(settings, "monitor_distance_cm", 60))
    mon.setSizePix(getattr(settings, "size", [1024, 768]))

    win = Window(
        size=getattr(settings, "size", [1024, 768]),
        fullscr=getattr(settings, "fullscreen", False),
        screen=screen_id,
        monitor=mon,
        units=getattr(settings, "units", "pix"),
        color=getattr(settings, "bg_color", [0, 0, 0]),
        gammaErrorPolicy="ignore",
    )

    kb = keyboard.Keyboard()
    win.mouseVisible = False

    try:
        event.globalKeys.clear()
    except Exception:
        pass

    event.globalKeys.add(
        key="q",
        modifiers=["ctrl"],
        func=lambda: (win.close(), core.quit()),
        name="shutdown",
    )

    try:
        settings.frame_time_seconds = win.monitorFramePeriod
        settings.win_fps = win.getActualFrameRate() or 60
    except Exception as e:
        print(f"[Warning] Could not determine frame rate: {e}")
        settings.frame_time_seconds = 1 / 60
        settings.win_fps = 60

    log_path = getattr(settings, "log_file", "experiment.log")
    logging.setDefaultClock(core.Clock())
    logging.LogFile(log_path, level=logging.DATA, filemode="a")
    logging.console.setLevel(logging.INFO)

    return win, kb


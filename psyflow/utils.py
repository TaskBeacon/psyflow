
def show_ports():
    """
    List all available serial ports with descriptions.
    """
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for i, p in enumerate(ports):
            print(f"[{i}] {p.device} - {p.description}")



import numpy as np
from typing import Any, List, Dict
import random
import numpy as np
from typing import Any, List, Optional

def generate_balanced_conditions(
    n_trials: int,
    condition_labels: List[Any],
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Generate a balanced sequence of condition labels without affecting global RNG state.

    Parameters
    ----------
    n_trials : int
        Total number of trials.
    condition_labels : list
        List of unique labels, e.g. ['go_left','go_right','stop_left','stop_right'].
    seed : int or None
        Seed for reproducibility. Uses a local RNG so global state is untouched.

    Returns
    -------
    np.ndarray
        Array of length n_trials with each label appearing as evenly as possible,
        with any remainder drawn at random and the entire sequence shuffled.
    """
    # local RNG
    rng = random.Random(seed)

    n_labels = len(condition_labels)
    n_per    = n_trials // n_labels
    extra    = n_trials % n_labels

    # build base list
    conditions = list(condition_labels) * n_per

    # handle the remainder with replacement
    if extra:
        # random.choices allows repeats
        conditions.extend(rng.choices(condition_labels, k=extra))

    # shuffle in-place using our local RNG
    rng.shuffle(conditions)

    return np.array(conditions, dtype=object)


import numpy as np
from typing import Any, Dict, List, Optional


from cookiecutter.main import cookiecutter
import importlib.resources as pkg_res
def taps(task_name: str, template: str = "cookiecutter-psyflow"):
    # locate the template folder inside the installed package
    tmpl_dir = pkg_res.files("psyflow") / template
    cookiecutter(
        str(tmpl_dir),
        no_input=True,
        extra_context={"project_name": task_name}
    )


from psychopy import visual, core
def count_down(win, seconds=3, **stim_kwargs):
    """
    Display a frame-accurate countdown using TextStim.

    Parameters
    ----------
    win : psychopy.visual.Window
        The PsychoPy window to display the countdown in.
    seconds : int
        How many seconds to count down from.
    **stim_kwargs : dict
        Additional keyword arguments for TextStim (e.g., font, height, color).
    """
    cd_clock = core.Clock()
    for i in reversed(range(1, seconds + 1)):
        stim = visual.TextStim(win=win, text=str(i), **stim_kwargs)
        cd_clock.reset()
        while cd_clock.getTime() < 1.0:
            stim.draw()
            win.flip()


from typing import Dict, List, Optional
import yaml
def load_config(config_file: str = 'config/config.yaml',
                extra_keys: Optional[List[str]] = None) -> Dict:
    """
    Load a config.yaml file and return a structured dictionary.

    Parameters
    ----------
    config_file : str
        Path to YAML config file.
    extra_keys : list of str, optional
        Additional top-level keys to extract as 'xxx_config'.

    Returns
    -------
    dict
        Dictionary with structured configs.
    """
    with open(config_file, encoding='utf-8') as f:
        config = yaml.safe_load(f)

    task_keys = ['window', 'task', 'timing']
    output = {
        'raw': config,
        'task_config': {k: v for key in task_keys for k, v in config.get(key, {}).items()},
        'stim_config': config.get('stimuli', {}),
        'subform_config': {
            'subinfo_fields': config.get('subinfo_fields', []),
            'subinfo_mapping': config.get('subinfo_mapping', {}),
        },
        'trigger_config': config.get('triggers', {}),
        'controller_config': config.get('controller', {}),
    }

    if extra_keys:
        for key in extra_keys:
            key_name = f'{key}_config'
            if key_name not in output:
                output[key_name] = config.get(key, {})

    return output

from psychopy.visual import Window
from psychopy.hardware import keyboard
from psychopy import event, core, logging, monitors
from psychopy.visual import Window
from psychopy.hardware import keyboard
from psychopy import event, core, logging
from typing import Tuple


def initialize_exp(settings, screen_id: int = 1) -> Tuple[Window, keyboard.Keyboard]:
    """
    Initialize the experiment environment including window, keyboard, logging, and global quit key.

    Parameters:
        settings: Configuration object with display, logging, and task settings.
        screen_id (int): ID of the screen to display the experiment window on.

    Returns:
        Tuple[Window, Keyboard]: The initialized PsychoPy window and keyboard objects.
    """
    # === Window Setup ===
    mon = monitors.Monitor('tempMonitor')
    mon.setWidth(getattr(settings, 'monitor_width_cm', 35.5))
    mon.setDistance(getattr(settings, 'monitor_distance_cm', 60))
    mon.setSizePix(getattr(settings, 'size', [1024, 768]))

    win = Window(
        size=getattr(settings, 'size', [1024, 768]),
        fullscr=getattr(settings, 'fullscreen', False),
        screen=screen_id,
        monitor=mon,
        units=getattr(settings, 'units', 'pix'),
        color=getattr(settings, 'bg_color', [0, 0, 0]),
        gammaErrorPolicy='ignore'
    )

    # === Keyboard Setup ===
    kb = keyboard.Keyboard()
    win.mouseVisible = False

    # === Global Quit Key (Ctrl+Q) ===
    try:
        event.globalKeys.clear()  # Ensure no duplicate 'q' entries
    except Exception:
        pass

    event.globalKeys.add(
        key='q',
        modifiers=['ctrl'],
        func=lambda: (win.close(), core.quit()),
        name='shutdown'
    )

    # === Frame Timing ===
    try:
        settings.frame_time_seconds = win.monitorFramePeriod
        settings.win_fps = win.getActualFrameRate() or 60  # fallback if FPS detection fails
    except Exception as e:
        print(f"[Warning] Could not determine frame rate: {e}")
        settings.frame_time_seconds = 1 / 60
        settings.win_fps = 60

    # === Logging Setup ===
    log_path = getattr(settings, 'log_file', 'experiment.log')
    logging.setDefaultClock(core.Clock())
    logging.LogFile(log_path, level=logging.DATA, filemode='a')
    logging.console.setLevel(logging.INFO)

    return win, kb

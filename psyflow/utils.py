
def show_ports():
    """List all available serial ports.

    The function prints a numbered list of connected serial ports with a short
    description. It is mainly intended for quick troubleshooting when choosing
    a port for trigger boxes or external devices.

    Returns
    -------
    None
        This function is executed for its side effect of printing to ``stdout``.
    """
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for i, p in enumerate(ports):
            print(f"[{i}] {p.device} - {p.description}")




from cookiecutter.main import cookiecutter
import importlib.resources as pkg_res


def taps(task_name: str, template: str = "cookiecutter-psyflow"):
    """Generate a task skeleton using the bundled template.

    Parameters
    ----------
    task_name : str
        Name of the new task directory to create.
    template : str, optional
        Name of the template folder inside the package. Defaults to
        ``"cookiecutter-psyflow"``.

    Returns
    -------
    str
        Path to the newly created project directory.

    Examples
    --------
    >>> taps("mytask")
    "mytask"
    """
    tmpl_dir = pkg_res.files("psyflow") / template
    cookiecutter(
        str(tmpl_dir),
        no_input=True,
        extra_context={"project_name": task_name}
    )
    return task_name


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

    Returns
    -------
    None
        The countdown is shown on ``win`` for its side effect.
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

    Examples
    --------
    >>> cfg = load_config('config/config.yaml')
    >>> cfg['task_config']['screen_width']
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
    """Set up the PsychoPy window, keyboard and logging.

    Parameters
    ----------
    settings : Any
        Configuration object with attributes describing window and logging
        settings.
    screen_id : int, optional
        Monitor index to open the window on. Defaults to ``1``.

    Returns
    -------
    tuple of (Window, Keyboard)
        The created PsychoPy ``Window`` and ``Keyboard`` objects.

    Examples
    --------
    >>> win, kb = initialize_exp(my_settings)
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



import asyncio
from edge_tts import VoicesManager
from typing import Optional
async def _list_supported_voices_async(filter_lang: Optional[str] = None):
    vm = await VoicesManager.create()
    voices = vm.voices
    if filter_lang:
        voices = [v for v in voices if v["Locale"].startswith(filter_lang)]
    return voices
def list_supported_voices(
    filter_lang: Optional[str] = None,
    human_readable: bool = False
):
    """Query available edge-tts voices.

    Parameters
    ----------
    filter_lang : str, optional
        Return only voices whose locale starts with this prefix.
    human_readable : bool, optional
        If ``True`` print a formatted table; otherwise return the raw list.

    Returns
    -------
    list of dict or None
        The raw voice dictionaries if ``human_readable`` is ``False``,
        otherwise ``None``.
    """
    voices = asyncio.run(_list_supported_voices_async(filter_lang))
    if not human_readable:
        return voices

    # Table header including the Personalities column
    header = (
        f"{'ShortName':25} {'Locale':10} {'Gender':8} "
        f"{'Personalities':30} {'FriendlyName'}"
    )
    separator = "-" * len(header)
    print(header)
    print(separator)

    for v in voices:
        short = v.get("ShortName", "")[:25]
        loc   = v.get("Locale", "")[:10]
        gen   = v.get("Gender", "")[:8]
        # Extract the personalities list and join with commas
        pers_list = v.get("VoiceTag", {}).get("VoicePersonalities", [])
        pers = ", ".join(pers_list)[:30]
        # Use FriendlyName as the display name
        disp  = v.get("FriendlyName", v.get("Name", ""))

        print(f"{short:25} {loc:10} {gen:8} {pers:30} {disp}")

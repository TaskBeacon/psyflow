
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
def generate_balanced_conditions(n_trials, condition_labels, seed=None):
    if seed is not None:
        np.random.seed(seed)
    n_per_cond = n_trials // len(condition_labels)
    extra = n_trials % len(condition_labels)
    conditions = condition_labels * n_per_cond + list(np.random.choice(condition_labels, extra))
    np.random.shuffle(conditions)
    return np.array(conditions)

import numpy as np
from typing import Any, Dict, List, Optional

def assign_stimuli(
    conditions: np.ndarray,
    stim_map: Dict[str, Any],
    components: Optional[List[str]] = None
) -> np.ndarray:
    """
    Assign stimuli to each condition, in one of two modes:

    1) **Multi‑component mode** (when `components` is a list of prefixes):
       Returns an array of dicts, each mapping component→stimulus, e.g.
         [{'cue': cue_win, 'target': target_win}, {'cue': cue_lose, ...}, ...]

    2) **Single‑component mode** (when `components` is None or empty):
       Returns a flat array of stimuli, each stim_map[condition].

    Parameters
    ----------
    conditions : np.ndarray[str]
        Array of condition labels, e.g. ['win','lose','neut',...]
    stim_map : dict
        If multi‑component mode: keys like 'cue_win','target_lose', etc.
        If single‑component mode: keys equal to each condition.
    components : list[str], optional
        Prefixes for multi‑component mode, e.g. ['cue','target','feedback'].
        If None or empty, single‑component mode is used.

    Returns
    -------
    np.ndarray
        - Multi‑component: dtype=object array of dicts
        - Single‑component: dtype=object array of individual stimuli
    """
    if components:
        # multi‑component mode
        seq = []
        for cond in conditions:
            bundle = {}
            for comp in components:
                key = f"{comp}_{cond}"
                if key not in stim_map:
                    raise KeyError(f"Missing stimulus '{key}' in stim_map")
                bundle[comp] = stim_map[key]
            seq.append(bundle)
        return np.array(seq, dtype=object)

    else:
        # single‑component mode
        seq = []
        for cond in conditions:
            if cond not in stim_map:
                raise KeyError(f"Condition '{cond}' not found in stim_map")
            seq.append(stim_map[cond])
        return np.array(seq, dtype=object)



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

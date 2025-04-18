
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

def assign_stimuli(
    conditions: np.ndarray,
    stim_map: Dict[str, Any],
    components: List[str] = ("cue", "target", "feedback")
) -> np.ndarray:
    """
    Assigns multiple stimuli per condition using a list of stimulus components.

    Parameters:
    - conditions: array of condition labels (e.g., ['win', 'lose', 'neut'])
    - stim_map: dict of available stimuli, typically from stim_bank.get_group("...")
    - components: list of stimulus types (prefixes), e.g., ['cue', 'target']

    Returns:
    - np.ndarray of dicts like {'cue': ..., 'target': ...}
    """
    stim_seq = []
    for cond in conditions:
        stim_bundle = {}
        for comp in components:
            key = f"{comp}_{cond}"
            if key in stim_map:
                stim_bundle[comp] = stim_map[key]
            else:
                raise KeyError(f"Stimulus '{key}' not found in stim_map.")
        stim_seq.append(stim_bundle)

    return np.array(stim_seq, dtype=object)


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

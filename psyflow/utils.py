
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

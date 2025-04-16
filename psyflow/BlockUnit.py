import numpy as np
from typing import Callable, Any, List, Dict, Optional, Tuple
from psychopy import core, logging

class BlockUnit:
    """
    A flexible and modular block container for trial execution and management.
    Supports chaining condition and stimulus generation, trial execution,
    lifecycle hooks, and block-level metadata collection.
    """

    def __init__(
        self,
        block_id: str,
        block_idx: int,
        settings: dict,
        stim_map: Optional[Dict[str, Any]] = None,
        window: Any = None,
        keyboard: Any = None,
        seed: Optional[int] = None,
        n_trials: Optional[int] = None
    ):
        """
        Initialize a BlockUnit.

        Parameters:
        - block_id (str): Unique identifier for the block.
        - settings (Any): Experiment-level settings/configuration object.
        - stim_map (dict, optional): A dictionary mapping stimulus keys to visual stimulus objects.
        - window (psychopy.visual.Window, optional): The PsychoPy window.
        - keyboard (psychopy.hardware.Keyboard, optional): The keyboard input handler.
        - seed (int, optional): Random seed for reproducibility.
        """
        self.block_id = block_id
        self.block_idx = block_idx
        self.n_trials = getattr(settings, "trials_per_block", 50) if n_trials is None else n_trials
        self.settings = settings
        self.win = window
        self.kb = keyboard
        self.seed = settings.block_seed[self.block_idx] if seed is None else seed
        self.stim_map = stim_map or {}

        self.conditions: Optional[np.ndarray] = None
        self.stimuli: Optional[np.ndarray] = None
        self.trials: List[Tuple[Any, Any]] = []

        self.results: List[Dict[str, Any]] = []
        self.meta: Dict[str, Any] = {}

        self._on_start: List[Callable[['BlockUnit'], None]] = []
        self._on_end: List[Callable[['BlockUnit'], None]] = []

    # ----------------------------
    # Chainable Setup
    # ----------------------------

    def generate_conditions(
        self,
        func: Callable[[int, List[str], Optional[int]], np.ndarray],
        n_trials: Optional[int] = None,
        condition_labels: Optional[List[str]] = None
    ):
        """
        Generate trial conditions using a user-defined function.

        Parameters:
        - func: A function that returns a numpy array of condition labels.
        - n_trials: Number of trials to generate (default: settings.trials_per_block).
        - condition_labels: Labels for conditions (default: settings.conditions).

        Returns:
        - self
        """
        n = n_trials or self.n_trials
        labels = condition_labels or getattr(self.settings, "conditions", ["A", "B", "C"])
        self.conditions = func(n, labels, seed=self.seed)
        return self

    def assign_stimuli(self, func: Callable[[np.ndarray, Dict[str, Any]], np.ndarray]):
        """
        Assign stimuli to conditions using a user-defined function.

        Parameters:
        - func: A function that takes the condition array and stim_map and returns an array of stimuli.

        Returns:
        - self
        """
        if self.conditions is None:
            raise ValueError("Must generate conditions before assigning stimuli.")
        self.stimuli = func(self.conditions, self.stim_map)
        self.trials = list(zip(self.conditions, self.stimuli))
        return self

    def generate_stim_sequence(
        self,
        generate_func: Callable,
        assign_func: Callable,
        n_trials: Optional[int] = None,
        condition_labels: Optional[List[str]] = None
    ):
        """
        Convenience method to generate both conditions and stimuli in a single chain.

        Parameters:
        - generate_func: Function to generate conditions.
        - assign_func: Function to assign stimuli.
        - n_trials: Optional number of trials to generate.
        - condition_labels: Optional list of condition labels.

        Returns:
        - self
        """
        return self.generate_conditions(generate_func, n_trials, condition_labels).assign_stimuli(assign_func)

    def add_trials(self, trial_list: List[Tuple[Any, Any]]):
        """
        Manually assign a list of (condition, stimulus) trial tuples.

        Parameters:
        - trial_list: A list of (condition, stimulus) tuples.

        Returns:
        - self
        """
        self.trials = trial_list
        return self

    # ----------------------------
    # Hooks
    # ----------------------------

    def on_start(self, func: Optional[Callable[['BlockUnit'], None]] = None):
        if func is None:
            def decorator(f):
                self._on_start.append(f)
                return self
            return decorator
        else:
            self._on_start.append(func)
            return self

    def on_end(self, func: Optional[Callable[['BlockUnit'], None]] = None):
        if func is None:
            def decorator(f):
                self._on_end.append(f)
                return self
            return decorator
        else:
            self._on_end.append(func)
            return self


    # ----------------------------
    # Core Execution
    # ----------------------------

    def run_trial(self, run_trial_func: Callable, **extra_args):
        """
        Execute all trials using the provided trial function.

        Parameters:
        - run_trial_func: A function with signature 
          `(win, kb, settings, condition, stimulus, **kwargs) -> dict`.
        - extra_args: Additional arguments to pass to each trial function.
        """
        self.meta['block_start_time'] = core.getAbsTime()
        logging.exp(f"Starting BlockUnit: {self.block_id}")

        for hook in self._on_start:
            hook(self)

        for i, (cond, stim) in enumerate(self.trials):
            result = run_trial_func(
                self.win, self.kb, self.settings, cond, stim, **extra_args
            )
            result.update({
                "trial_index": i,
                "block_id": self.block_id,
                "condition": cond,
                "stim_label": getattr(stim, 'name', str(stim))
            })
            self.results.append(result)

        for hook in self._on_end:
            hook(self)

        self.meta['block_end_time'] = core.getAbsTime()
        self.meta['duration'] = self.meta['block_end_time'] - self.meta['block_start_time']
        logging.exp(f"Finished BlockUnit '{self.block_id}' in {self.meta['duration']:.2f}s")

    def summarize(self, summary_func: Optional[Callable[['BlockUnit'], Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Summarize results after block completion.

        Parameters:
        - summary_func: Optional custom summary function. Must accept BlockUnit and return a dict.

        Returns:
        - A dictionary of summary statistics (also stored in self.meta["summary"]).
        """
        if summary_func:
            summary = summary_func(self)
        else:
            # Default summary: RT and hit rate per condition
            results = self.to_dict()
            conds = set(r["condition"] for r in results)
            summary = {}
            for cond in conds:
                subset = [r for r in results if r["condition"] == cond]
                hit_rate = np.mean([r.get("target_hit", 0) for r in subset])
                rt_values = [r["target_rt"] for r in subset if r.get("target_rt") is not None]
                avg_rt = np.mean(rt_values) if rt_values else None
                summary[cond] = {
                    "hit_rate": hit_rate,
                    "avg_rt": avg_rt
                }

        self.meta["summary"] = summary
        return summary
    def to_dict(self, target: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Return trial results or append to existing list.

        Parameters:
        - target: An optional list to append results to.

        Returns:
        - The list of trial result dictionaries.
        """
        if target is not None:
            target.extend(self.results)
            return target
        return self.results


    def __len__(self):
        """
        Returns:
        - The number of trials in the block.
        """
        return len(self.trials)

    def logging_block_info(self):
        """
        Print a basic summary of the block’s condition distribution.
        """
        cue_summary = {c: list(self.conditions).count(c) for c in set(self.conditions)} if self.conditions is not None else {}
        print(f"🧱 BlockUnit '{self.block_id}' — {len(self.trials)} trials")
        print(f"  Cue Distribution: {cue_summary}")
        logging.exp(f"BlockUnit '{self.block_id}' — {len(self.trials)} trials - Discription: {cue_summary}")

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

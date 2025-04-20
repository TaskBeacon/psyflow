import numpy as np
from typing import Callable, Any, List, Dict, Optional
from psychopy import core, logging

class BlockUnit:
    """
    A block container for trial‐condition execution and management.
    
    Only generates a sequence of conditions and runs a trial function on each.
    
    :param block_id: Unique identifier for the block.
    :type block_id: str
    :param block_idx: Index of this block within the experiment.
    :type block_idx: int
    :param settings: Experiment‐level settings (must have `.trials_per_block` and `.block_seed`).
    :type settings: dict
    :param window: PsychoPy Window instance.
    :type window: Any
    :param keyboard: PsychoPy Keyboard instance.
    :type keyboard: Any
    :param seed: Random seed for reproducibility (overrides `settings.block_seed`).
    :type seed: Optional[int]
    :param n_trials: Number of trials in this block (overrides `settings.trials_per_block`).
    :type n_trials: Optional[int]
    """

    def __init__(
        self,
        block_id: str,
        block_idx: int,
        settings: dict,
        window: Any = None,
        keyboard: Any = None,
        seed: Optional[int] = None,
        n_trials: Optional[int] = None
    ):
        self.block_id = block_id
        self.block_idx = block_idx
        self.n_trials = getattr(settings, "trials_per_block", 50) if n_trials is None else n_trials
        self.settings = settings
        self.win = window
        self.kb = keyboard
        self.seed = settings.block_seed[self.block_idx] if seed is None else seed

        self.conditions: Optional[np.ndarray] = None
        self.trials: List[Any] = []

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
    ) -> "BlockUnit":
        """
        Generate trial conditions using a user‐defined function.
        
        :param func: Callable that returns an array of labels for each trial.
                     Signature: func(n_trials, labels, seed) -> np.ndarray
        :type func: Callable[[int, List[str], Optional[int]], np.ndarray]
        :param n_trials: Number of trials to generate (default: self.n_trials).
        :type n_trials: Optional[int]
        :param condition_labels: List of possible condition labels
                                 (default: settings.conditions or ["A","B","C"]).
        :type condition_labels: Optional[List[str]]
        :returns: Self, to allow chaining.
        :rtype: BlockUnit
        """
        n = n_trials or self.n_trials
        labels = condition_labels or getattr(self.settings, "conditions", ["A", "B", "C"])
        self.conditions = func(n, labels, seed=self.seed)
        self.trials = list(self.conditions)
        return self

    def add_trials(self, trial_list: List[Any]) -> "BlockUnit":
        """
        Manually assign a list of condition labels as trials.
        
        :param trial_list: A list of condition labels.
        :type trial_list: List[Any]
        :returns: Self, to allow chaining.
        :rtype: BlockUnit
        """
        self.trials = trial_list
        return self

    # ----------------------------
    # Hooks
    # ----------------------------

    def on_start(self, func: Optional[Callable[['BlockUnit'], None]] = None):
        """
        Register a function to be called once at block start.
        
        :param func: A callable that takes this BlockUnit.
        :type func: Callable[[BlockUnit], None]
        """
        if func is None:
            def decorator(f):
                self._on_start.append(f)
                return self
            return decorator
        else:
            self._on_start.append(func)
            return self

    def on_end(self, func: Optional[Callable[['BlockUnit'], None]] = None):
        """
        Register a function to be called once at block end.
        
        :param func: A callable that takes this BlockUnit.
        :type func: Callable[[BlockUnit], None]
        """
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
        
        The trial function must accept:
          (win, kb, settings, condition, **extra_args) -> dict
        
        :param run_trial_func: Function to run each trial.
        :type run_trial_func: Callable[..., dict]
        :param extra_args: Additional keyword arguments passed to the trial function.
        """
        self.meta['block_start_time'] = core.getAbsTime()
        self.logging_block_info()

        for hook in self._on_start:
            hook(self)

        for i, cond in enumerate(self.trials):
            result = run_trial_func(
                self.win,
                self.kb,
                self.settings,
                cond,
                **extra_args
            )
            result.update({
                "trial_index": i,
                "block_id": self.block_id,
                "condition": cond
            })
            self.results.append(result)

        for hook in self._on_end:
            hook(self)

        self.meta['block_end_time'] = core.getAbsTime()
        self.meta['duration'] = self.meta['block_end_time'] - self.meta['block_start_time']
        logging.data(f"[BlockUnit] Finished '{self.block_id}' in {self.meta['duration']:.2f}s")

    def summarize(self, summary_func: Optional[Callable[['BlockUnit'], Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Summarize results after block completion.
        
        Default summary: computes hit rate and average RT per condition.
        
        :param summary_func: Custom summary function taking BlockUnit and returning a dict.
        :type summary_func: Optional[Callable[[BlockUnit], Dict[str, Any]]]
        :returns: Summary dictionary stored in self.meta["summary"].
        :rtype: Dict[str, Any]
        """
        if summary_func:
            summary = summary_func(self)
        else:
            results = self.to_dict()
            conds = set(r["condition"] for r in results)
            summary = {}
            for cond in conds:
                subset = [r for r in results if r["condition"] == cond]
                hit_vals = [r.get("target_hit", 0) for r in subset]
                rt_vals = [r.get("target_rt") for r in subset if r.get("target_rt") is not None]
                summary[cond] = {
                    "hit_rate": np.mean(hit_vals),
                    "avg_rt": np.mean(rt_vals) if rt_vals else None
                }
        self.meta["summary"] = summary
        return summary

    def to_dict(self, target: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Return or append trial result dictionaries.
        
        :param target: Optional list to extend with results.
        :type target: Optional[List[Dict[str, Any]]]
        :returns: List of result dicts.
        :rtype: List[Dict[str, Any]]
        """
        if target is not None:
            target.extend(self.results)
            return target
        return self.results

    def __len__(self) -> int:
        """
        :returns: Number of trials in the block.
        :rtype: int
        """
        return len(self.trials)

    def logging_block_info(self):
        """
        Log basic block information: ID, idx, seed, trial count, condition distribution.
        """
        dist = {c: list(self.trials).count(c) for c in set(self.trials)} if self.trials else {}
        logging.data(f"[BlockUnit] Blockid: {self.block_id}")
        logging.data(f"[BlockUnit] Blockidx: {self.block_idx}")
        logging.data(f"[BlockUnit] Blockseed: {self.seed}")
        logging.data(f"[BlockUnit] Blocktrials: {len(self.trials)}")
        logging.data(f"[BlockUnit] Blockdist: {dist}")
        logging.data(f"[BlockUnit] Blockconditions: {self.conditions}")

import numpy as np
from typing import Callable, Any, List, Dict, Optional
from psychopy import core, logging


class BlockUnit:
    """
    A container that manages a block of experimental trials.

    BlockUnit is responsible for generating trial conditions, running trials, 
    executing lifecycle hooks, and collecting trial-level results.
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
        """
        Initialize a BlockUnit.

        Parameters
        ----------
        block_id : str
            Unique identifier for the block.
        block_idx : int
            Index of this block in the experiment.
        settings : dict
            Experiment-level settings; must include `trials_per_block` and `block_seed`.
        window : Any, optional
            PsychoPy window object.
        keyboard : Any, optional
            PsychoPy keyboard object.
        seed : int, optional
            Random seed (overrides `settings.block_seed`).
        n_trials : int, optional
            Number of trials (overrides `settings.trials_per_block`).
        """
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

    def generate_conditions(
        self,
        func: Callable[[int, List[str], Optional[int]], np.ndarray],
        n_trials: Optional[int] = None,
        condition_labels: Optional[List[str]] = None
    ) -> "BlockUnit":
        """
        Generate trial conditions using a user-defined function.

        Parameters
        ----------
        func : Callable
            Function to generate conditions. Signature: (n_trials, labels, seed) -> np.ndarray.
        n_trials : int, optional
            Number of trials. Defaults to `self.n_trials`.
        condition_labels : list of str, optional
            List of possible condition labels. Defaults to `settings.conditions`.

        Returns
        -------
        BlockUnit
            The same instance for method chaining.
        """
        n = n_trials or self.n_trials
        labels = condition_labels or getattr(self.settings, "conditions", ["A", "B", "C"])
        self.conditions = func(n, labels, seed=self.seed)
        self.trials = list(self.conditions)
        return self

    def add_trials(self, trial_list: List[Any]) -> "BlockUnit":
        """
        Manually set the trial list.

        Parameters
        ----------
        trial_list : list
            A list of trial condition labels.

        Returns
        -------
        BlockUnit
            The same instance for method chaining.
        """
        self.trials = trial_list
        return self

    def on_start(self, func: Optional[Callable[['BlockUnit'], None]] = None):
        """
        Register a function to run at the start of the block.

        Parameters
        ----------
        func : Callable, optional
            A function that takes the BlockUnit as input.
        """
        if func is None:
            def decorator(f):
                self._on_start.append(f)
                return self
            return decorator
        self._on_start.append(func)
        return self

    def on_end(self, func: Optional[Callable[['BlockUnit'], None]] = None):
        """
        Register a function to run at the end of the block.

        Parameters
        ----------
        func : Callable, optional
            A function that takes the BlockUnit as input.
        """
        if func is None:
            def decorator(f):
                self._on_end.append(f)
                return self
            return decorator
        self._on_end.append(func)
        return self

    def run_trial(self, run_trial_func: Callable, **extra_args):
        """
        Run all trials using a specified trial function.

        Parameters
        ----------
        run_trial_func : Callable
            Function to run each trial. Must accept (win, kb, settings, condition, **extra_args).
        extra_args : dict
            Additional arguments passed to the trial function.
        """
        self.meta['block_start_time'] = core.getAbsTime()
        self.logging_block_info()

        for hook in self._on_start:
            hook(self)

        for i, cond in enumerate(self.trials):
            result = run_trial_func(self.win, self.kb, self.settings, cond, **extra_args)
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
        return self

    def summarize(self, summary_func: Optional[Callable[['BlockUnit'], Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Summarize trial results.

        Parameters
        ----------
        summary_func : Callable, optional
            Custom summary function. If None, hit rate and RT by condition are computed.

        Returns
        -------
        dict
            Summary results.
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

    def to_dict(self, target: Optional[List[Dict[str, Any]]] = None) -> "BlockUnit":
        """
        Append trial results to a target list, or return self for chaining.

        Parameters
        ----------
        target : list of dict, optional
            A list to append trial results to.

        Returns
        -------
        BlockUnit
            The BlockUnit itself for chaining.
        """
        if target is not None:
            target.extend(self.results)
        return self
    
    def get_dict(self) -> List[Dict[str, Any]]:
        """
        Return trial results without modifying anything.

        Returns
        -------
        list of dict
            Trial result dictionaries.
        """
        return self.results


    def __len__(self) -> int:
        """
        Return the number of trials in the block.

        Returns
        -------
        int
        """
        return len(self.trials)

    def logging_block_info(self):
        """
        Log block metadata including ID, index, seed, trial count, and condition distribution.
        """
        dist = {c: self.trials.count(c) for c in set(self.trials)} if self.trials else {}
        logging.data(f"[BlockUnit] Blockid: {self.block_id}")
        logging.data(f"[BlockUnit] Blockidx: {self.block_idx}")
        logging.data(f"[BlockUnit] Blockseed: {self.seed}")
        logging.data(f"[BlockUnit] Blocktrials: {len(self.trials)}")
        logging.data(f"[BlockUnit] Blockdist: {dist}")
        logging.data(f"[BlockUnit] Blockconditions: {self.conditions}")

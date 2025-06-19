import numpy as np
from typing import Callable, Any, List, Dict, Optional
from psychopy import core, logging
from typing import Union, List, Dict, Literal
import re
import random


class BlockUnit:
    """Block-level controller for trials.

    This object generates trial conditions, executes each trial, and stores
    metadata. It exposes hooks for custom start/end logic and summary methods.

    Attributes
    ----------
    block_id : str
        Identifier for the block.
    block_idx : int
        Index of this block in the experiment.
    n_trials : int
        Number of trials to execute.
    settings : dict
        Experiment settings container.
    win : Any
        PsychoPy window used for drawing.
    kb : Any
        PsychoPy keyboard used for responses.
    seed : int
        Seed used for randomisation.
    conditions : list of Any or None
        Ordered list of condition labels for each trial.
    results : list of dict
        Accumulated trial results after :meth:`run_trial`.
    meta : dict
        Additional block metadata such as start time and duration.
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

        self.results: List[Dict[str, Any]] = []
        self.meta: Dict[str, Any] = {}

        self._on_start: List[Callable[['BlockUnit'], None]] = []
        self._on_end: List[Callable[['BlockUnit'], None]] = []

    def generate_conditions(
        self,
        func: Optional[Callable] = None,
        n_trials: Optional[int] = None,
        condition_labels: Optional[List[Any]] = None,
        weights: Optional[List[float]] = None,
        order: Literal['random', 'sequential'] = 'random',
        seed: Optional[int] = None,
        **kwargs
    ) -> "BlockUnit":
        """
        Generate trial conditions for this block.

        If `func` is provided, delegate generation to it. Otherwise, use the built-in
        weighted, balanced generator with optional sequential vs. random ordering.

        Parameters
        ----------
        func : Callable, optional
            User-supplied generator with signature
            `(n_trials, condition_labels, seed=..., **kwargs) -> array-like`.
        n_trials : int, optional
            Number of trials in this block. Defaults to `self.n_trials`.
        condition_labels : list of Any, optional
            Labels for each condition. Defaults to `self.settings.conditions`.
        weights : list of float, optional
            Relative weight for each label; defaults to equal weights.
        order : {'random','sequential'}
            If 'sequential', interleave labels in the order given; if 'random',
            build the list then shuffle.
        seed : int, optional
            Overrides `self.seed` for this generation call, without mutating
            the block's stored seed.
        **kwargs : dict
            Extra keyword arguments passed to `func` when used.

        Returns
        -------
        BlockUnit
            Returns self for chaining.
        """
        # determine trial count and labels
        n = n_trials or self.n_trials
        labels = condition_labels or getattr(self.settings, "conditions", ["A", "B", "C"])

        # allow per-call seed override
        use_seed = seed if seed is not None else self.seed

        if func:
            logging.data(f"[BlockUnit] Generating via custom func {func.__name__} (seed={use_seed})")
            self.conditions = func(n, labels, seed=use_seed, **kwargs)
        else:
            # --- default weighted, balanced generation ---
   
            rng = random.Random(use_seed)
            n_labels = len(labels)

            # default to equal weights if none provided
            if weights is None:
                weights = [1.0] * n_labels
            elif len(weights) != len(labels):
                raise ValueError("Length of weights must match number of condition_labels.")

            total_w = sum(weights)

            # compute base counts (floor) and remainder
            raw = [n * w / total_w for w in weights]
            counts = [int(x) for x in raw]
            rem = n - sum(counts)

            # distribute remainder according to weights
            if rem > 0:
                extra = rng.choices(labels, weights=weights, k=rem)
                for lbl in extra:
                    counts[labels.index(lbl)] += 1

            # build the sequence
            if order == 'sequential':
                seq = []
                cnts = counts.copy()
                while sum(cnts) > 0:
                    for i, lbl in enumerate(labels):
                        if cnts[i] > 0:
                            seq.append(lbl)
                            cnts[i] -= 1
                result = seq
            else:
                result = []
                for lbl, cnt in zip(labels, counts):
                    result.extend([lbl] * cnt)
                rng.shuffle(result)

            self.conditions = result
        if not isinstance(self.conditions, list): # make sure the dist work
            self.conditions = list(self.conditions)
        print((f"[BlockUnit] Blockconditions: {self.conditions}"))
        return self


    def add_condition(self, condition_list: List[Any]) -> "BlockUnit":
        """
        Manually set the condition list.

        Parameters
        ----------
        condition_list : list
            A list of trial condition labels.

        Returns
        -------
        BlockUnit
            The same instance for method chaining.
        """
        self.conditions = condition_list
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

    def run_trial(self, func: Callable, **kwargs):
        """
        Run all trials using a specified trial function.

        Parameters
        ----------
        func : Callable
            Function to run each trial. Must accept ``(win, kb, settings, condition, **kwargs)``.
        **kwargs : dict
            Additional keyword arguments forwarded to ``func``.
        """
        self.meta['block_start_time'] = core.getAbsTime()
        self.logging_block_info()

        for hook in self._on_start:
            hook(self)

        for i, cond in enumerate(self.conditions):
            result = func(self.win, self.kb, self.settings, cond, **kwargs)
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
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """
        Return trial results without modifying anything.

        Returns
        -------
        list of dict
            Trial result dictionaries.
        """
        return self.results
    
    def get_trial_data(
        self,
        key: str,
        pattern: Union[str, List[str]],
        match_type: Literal['exact', 'startswith', 'endswith', 'regex'] = 'exact',
        negate: bool = False
    ) -> List[Dict]:
        """
        Filter trial data based on value of a key using matching rules.

        Parameters
        ----------
        key : str
            The key in each trial dict to match against.
        pattern : str or list of str
            One or more patterns to match.
        match_type : {'exact', 'startswith', 'endswith', 'regex'}
            Type of string matching to use.
        negate : bool
            If True, return trials that do NOT match the pattern(s).

        Returns
        -------
        List[Dict]
            Filtered list of trial dicts.
        """

        if not hasattr(self, 'results'):
            return []

        patterns = pattern if isinstance(pattern, list) else [pattern]

        def match(value: str) -> bool:
            for pat in patterns:
                if match_type == 'exact' and value == pat:
                    return True
                elif match_type == 'startswith' and value.startswith(pat):
                    return True
                elif match_type == 'endswith' and value.endswith(pat):
                    return True
                elif match_type == 'regex' and re.search(pat, value):
                    return True
            return False

        return [
            trial for trial in self.results
            if negate ^ match(str(trial.get(key, '')))
        ]

    def logging_block_info(self):
        """
        Log block metadata including ID, index, seed, trial count, and condition distribution.
        """
        dist = {c: self.conditions.count(c) for c in set(self.conditions)} if self.conditions else {}
        logging.data(f"[BlockUnit] Blockid: {self.block_id}")
        logging.data(f"[BlockUnit] Blockidx: {self.block_idx}")
        logging.data(f"[BlockUnit] Blockseed: {self.seed}")
        logging.data(f"[BlockUnit] Blocktrial-N: {len(self.conditions)}")
        logging.data(f"[BlockUnit] Blockdist: {dist}")
        logging.data(f"[BlockUnit] Blockconditions: {self.conditions}")

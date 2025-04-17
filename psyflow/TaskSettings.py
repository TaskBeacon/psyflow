from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from math import ceil
import random
import hashlib
from datetime import datetime
import os


@dataclass
class TaskSettings:
    """
    TaskSettings

    A configuration container for PsychoPy-based behavioral tasks.
    This dataclass manages all window settings, task structure parameters,
    response mappings, seeding strategies, and per-subject output paths.

    It supports loading from a flat dictionary (e.g., a YAML config), with
    additional keys promoted dynamically as attributes.

    Features:
    ---------
    - Window setup (size, monitor, screen, units)
    - Task design parameters (blocks, trials, conditions)
    - Response configuration (valid keys, default key)
    - Reproducible randomization:
        - `same_across_sub`: use a global seed for all participants
        - `same_within_sub`: derive a deterministic seed from `subject_id`
    - Per-subject file naming: `.log` and `.csv` files with timestamp
    - Dynamic extension via `from_dict` and `add_subinfo`

    Parameters:
    -----------
    size : list[int]
        Window resolution in pixels (e.g., [1920, 1080]).
    monitor : str
        Name of the PsychoPy monitor profile.
    units : str
        Units used for stimulus drawing (e.g., 'deg', 'pix', 'norm').
    screen : int
        Screen index (usually 0 or 1).
    bg_color : str
        Window background color (PsychoPy color string or RGB tuple).
    fullscreen : bool
        Whether to launch the experiment in full-screen mode.

    total_blocks : int
        Number of experimental blocks.
    total_trials : int
        Total number of trials across all blocks.
    
    response_key : str
        Default response key (e.g., 'space').
    key_list : list[str]
        Valid response keys for user input.

    conditions : list[str]
        Condition labels (e.g., ['reward', 'neutral', 'punishment']).
    block_seed : Optional[list[int]]
        List of seeds, one per block. If not provided, generated based on seed strategy.

    seed_mode : str
        Strategy to control seed generation. One of:
        - "same_across_sub": Use the same seed for every participant (requires `overall_seed`)
        - "same_within_sub": Use subject_id to generate a unique seed
    overall_seed : int
        The global seed used when `seed_mode == 'same_across_sub'`.
        Defaults to 2025 if not provided.

    trials_per_block : int
        Automatically computed as ceil(total_trials / total_blocks).

    log_file : Optional[str]
        Filename for log output, set by `add_subinfo()` using subject ID and timestamp.
    res_file : Optional[str]
        Filename for result CSV output, set by `add_subinfo()`.

    Methods:
    --------
    from_dict(config: dict) -> TaskSettings
        Load TaskSettings from a flat configuration dictionary, automatically
        applying known fields and promoting extras to instance attributes.

    add_subinfo(subinfo: dict)
        Accepts subject information (must include "subject_id") and:
            - updates seed (if seed_mode == "same_within_sub")
            - generates output filenames using subject ID + timestamp

    set_block_seed(seed_base: int)
        Uses the given seed base to generate a per-block seed list (one int per block).

    Example:
    --------
    >>> cfg = {'total_blocks': 3, 'total_trials': 30, 'seed_mode': 'same_within_sub'}
    >>> settings = TaskSettings.from_dict(cfg)
    >>> settings.add_subinfo({'subject_id': 'P001'})
    >>> print(settings.block_seed)  # deterministic per subject
    >>> print(settings.log_file)    # e.g., sub-P001_20250415-103355.log
    >>> print(settings.res_file)    # e.g., sub-P001_20250415-103355.csv
    """

    # --- Window settings ---
    size: List[int] = field(default_factory=lambda: [1920, 1080])
    monitor: str = 'testMonitor'
    units: str = 'norm'
    screen: int = 1
    bg_color: str = 'gray'
    fullscreen: bool = True

    # --- Basic experiment structure ---
    total_blocks: int = 1
    total_trials: int = 10

    # --- Response settings ---
    response_key: str = 'space'
    key_list: List[str] = field(default_factory=lambda: ['space'])

    # --- Trial logic ---
    conditions: List[str] = field(default_factory=list)
    block_seed: Optional[List[int]] = None

    # --- Seeding strategy ---
    seed_mode: str = 'same_across_sub'  # or 'same_within_sub'
    overall_seed: int = 2025

    # --- Derived fields ---
    trials_per_block: int = field(init=False)
    log_file: Optional[str] = None
    res_file: Optional[str] = None

    # --- save path ---
    save_path: Optional[str] = './data'
    session_name: Optional[str] = None

    def __post_init__(self):
        self.trials_per_block = ceil(self.total_trials / self.total_blocks)
        if self.block_seed is None:
            self.block_seed = [None] * self.total_blocks
    # Only auto-generate block_seed if not user-supplied
        if self.seed_mode == 'same_across_sub' and all(seed is None for seed in self.block_seed):
            self.set_block_seed(self.overall_seed)

    def set_block_seed(self, seed_base: Optional[int]):
        if seed_base is not None:
            rng = random.Random(seed_base)
            self.block_seed = [rng.randint(0, 99999) for _ in range(self.total_blocks)]

    def add_subinfo(self, subinfo: Dict[str, Any]):
        """
        Inject subject-specific info and set block seeds & file names based on subject ID.
        """
        for k, v in subinfo.items():
            setattr(self, k, v)

        subject_id = subinfo.get("subject_id")
        if not subject_id:
            raise ValueError("subject_id is required in subinfo")

        # Determine seeding behavior
        if self.seed_mode == 'same_within_sub' and all(seed is None for seed in self.block_seed):
            self.overall_seed = int(hashlib.sha256(str(subject_id).encode()).hexdigest(), 16) % (10**8)
            self.set_block_seed(self.overall_seed)

        # Ensure save path exists
        if self.save_path:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
                print(f"[INFO] Created output directory: {self.save_path}")
            else:
                print(f"[INFO] Output directory already exists: {self.save_path}")

        # Create filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if self.session_name:
            basename = f"sub-{subject_id}_session_{self.session_name}_{timestamp}"
        else:
            basename = f"sub-{subject_id}_{timestamp}"
        self.log_file = os.path.join(self.save_path, f"{basename}.log")
        self.res_file = os.path.join(self.save_path, f"{basename}.csv")

    def __repr__(self):
        base = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return f"{self.__class__.__name__}({base})"

    @classmethod
    def from_dict(cls, config: dict):
        known_keys = set(f.name for f in cls.__dataclass_fields__.values())
        init_args = {k: v for k, v in config.items() if k in known_keys}
        extras = {k: v for k, v in config.items() if k not in known_keys}

        settings = cls(**init_args)
        for k, v in extras.items():
            setattr(settings, k, v)
        return settings

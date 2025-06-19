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
    Configuration container for PsychoPy-based tasks.

    This dataclass holds core experimental parameters and provides utility
    methods to set per-subject seeds, construct output paths, and dynamically
    extend settings from external config dictionaries.

    Features
    --------
    - Window display settings
    - Experimental structure (blocks, trials, conditions)
    - Response keys
    - Flexible seeding strategies
    - Auto-generated per-subject filenames
    """

    # --- Window settings ---
    size: List[int] = field(default_factory=lambda: [1920, 1080])
    units: str = 'deg'
    screen: int = 1
    bg_color: str = 'gray'
    fullscreen: bool = True

    # --- Basic experiment structure ---
    total_blocks: int = 1
    total_trials: int = 10

    # --- Response settings ---
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
    json_file: Optional[str] = None

    # --- File path info ---
    save_path: Optional[str] = './data'
    task_name: Optional[str] = None

    def __post_init__(self):
        """
        Compute derived settings and auto-generate block seeds if needed.
        """
        self.trials_per_block = ceil(self.total_trials / self.total_blocks)

        if self.block_seed is None:
            self.block_seed = [None] * self.total_blocks

        if self.seed_mode == 'same_across_sub' and all(seed is None for seed in self.block_seed):
            self.set_block_seed(self.overall_seed)

    def set_block_seed(self, seed_base: Optional[int]):
        """
        Generate a list of per-block seeds from a base seed.

        Parameters
        ----------
        seed_base : int
            Base seed used to generate a list of integers for each block.
        """
        if seed_base is not None:
            rng = random.Random(seed_base)
            self.block_seed = [rng.randint(0, 99999) for _ in range(self.total_blocks)]

    def add_subinfo(self, subinfo: Dict[str, Any]):
        """
        Add subject-specific information and set seed/file names accordingly.

        Parameters
        ----------
        subinfo : dict
            Dictionary that must contain at least 'subject_id'. Also used to
            construct per-subject output file names.

        Raises
        ------
        ValueError
            If 'subject_id' is missing from subinfo.
        """
        for k, v in subinfo.items():
            setattr(self, k, v)

        subject_id = subinfo.get("subject_id")
        if not subject_id:
            raise ValueError("subject_id is required in subinfo")

        # Seed strategy based on subject_id
        if self.seed_mode == 'same_within_sub' and all(seed is None for seed in self.block_seed):
            self.overall_seed = int(hashlib.sha256(str(subject_id).encode()).hexdigest(), 16) % (10**8)
            self.set_block_seed(self.overall_seed)

        # Ensure save path exists
        if self.save_path and not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
            print(f"[INFO] Created output directory: {self.save_path}")
        else:
            print(f"[INFO] Output directory already exists: {self.save_path}")

        # Construct log/result filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if self.task_name:
            basename = f"sub-{subject_id}_task_{self.task_name}_{timestamp}"
        else:
            basename = f"sub-{subject_id}_{timestamp}"

        self.log_file = os.path.join(self.save_path, f"{basename}.log")
        self.res_file = os.path.join(self.save_path, f"{basename}.csv")
        self.json_file = os.path.join(self.save_path, f"{basename}.json")

    def __repr__(self):
        """
        Return a clean string representation of the current TaskSettings.
        """
        base = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return f"{self.__class__.__name__}({base})"
    
    def save_to_json(self):
        """
        Save the current TaskSettings instance to a JSON file.
        """
        if not self.json_file:
            raise ValueError("json_file path is not set. Make sure to call add_subinfo() first.")

        settings_dict = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_') and not callable(v)
        }
        # Handle types that JSON can't serialize directly
        for key, val in settings_dict.items():
            if isinstance(val, set):
                settings_dict[key] = list(val)

        with open(self.json_file, 'w', encoding='utf-8') as f:
            from json import dump
            dump(settings_dict, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Settings saved to {self.json_file}")


    @classmethod
    def from_dict(cls, config: dict):
        """
        Create a TaskSettings instance from a flat dictionary.

        Known fields are applied normally; unknown keys are attached as attributes.

        Parameters
        ----------
        config : dict
            Dictionary of configuration options.

        Returns
        -------
        TaskSettings
            An initialized instance with config applied.

        Examples
        --------
        >>> cfg = {'total_blocks': 2, 'total_trials': 20}
        >>> TaskSettings.from_dict(cfg)
        """
        known_keys = set(f.name for f in cls.__dataclass_fields__.values())
        init_args = {k: v for k, v in config.items() if k in known_keys}
        extras = {k: v for k, v in config.items() if k not in known_keys}

        settings = cls(**init_args)
        for k, v in extras.items():
            setattr(settings, k, v)
        return settings
    

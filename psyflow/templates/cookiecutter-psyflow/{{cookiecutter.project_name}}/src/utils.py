from __future__ import annotations

import random
from typing import Any

from psychopy import logging


class Controller:
    """Generic condition scheduler for template tasks."""

    def __init__(self, seed: int = 2026, shuffle: bool = True, enable_logging: bool = True):
        self.seed = int(seed)
        self.shuffle = bool(shuffle)
        self.enable_logging = bool(enable_logging)

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "Controller":
        raw = dict(config or {})
        defaults = {
            "seed": 2026,
            "shuffle": True,
            "enable_logging": True,
        }

        extra_keys = set(raw.keys()) - set(defaults.keys())
        if extra_keys:
            raise ValueError(f"[Controller] Unsupported config keys: {sorted(extra_keys)}")

        merged = {key: raw.get(key, default) for key, default in defaults.items()}
        return cls(**merged)

    def prepare_block(self, *, block_idx: int, n_trials: int, conditions: list[str] | None) -> list[str]:
        labels = [str(c) for c in (conditions or []) if str(c).strip()]
        if not labels:
            labels = ["default"]

        trial_count = max(1, int(n_trials))
        schedule = [labels[i % len(labels)] for i in range(trial_count)]

        if self.shuffle and len(schedule) > 1:
            rng = random.Random(self.seed + int(block_idx) * 1009)
            rng.shuffle(schedule)

        if self.enable_logging:
            logging.data(
                "[Controller] block=%s trial_count=%s conditions=%s"
                % (block_idx, trial_count, labels)
            )

        return schedule

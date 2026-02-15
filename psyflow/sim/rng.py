from __future__ import annotations

import hashlib
import random


def make_rng(seed: int) -> random.Random:
    return random.Random(int(seed))


def stable_int_hash(*parts: object, mod: int = 2**32) -> int:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
        h.update(b"|")
    return int.from_bytes(h.digest()[:8], "big") % int(mod)


def make_trial_seed(session_id: str, trial_id: int | str, phase: str, base_seed: int = 0) -> int:
    return stable_int_hash(session_id, trial_id, phase, base_seed)


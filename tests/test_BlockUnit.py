"""Tests for psyflow.BlockUnit."""

import sys
import unittest
from unittest.mock import MagicMock
from types import SimpleNamespace

import numpy as np

# Stub out PsychoPy before importing BlockUnit
_psychopy_stub = MagicMock()
_psychopy_stub.core.getAbsTime.return_value = 0.0
sys.modules.setdefault("psychopy", _psychopy_stub)
sys.modules.setdefault("psychopy.core", _psychopy_stub.core)
sys.modules.setdefault("psychopy.logging", _psychopy_stub.logging)

from psyflow.BlockUnit import BlockUnit  # noqa: E402


def _make_settings(**overrides):
    """Create a minimal settings-like object."""
    defaults = {
        "trials_per_block": 3,
        "block_seed": [42],
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_block(**overrides):
    """Build a BlockUnit without calling __init__ (avoids PsychoPy window)."""
    block = BlockUnit.__new__(BlockUnit)
    defaults = dict(
        block_id="test",
        block_idx=0,
        n_trials=3,
        settings=_make_settings(),
        win=MagicMock(),
        kb=MagicMock(),
        seed=42,
        conditions=None,
        results=[],
        meta={},
        _on_start=[],
        _on_end=[],
    )
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(block, k, v)
    return block


class TestRunTrialGuards(unittest.TestCase):
    """run_trial() should reject invalid state with clear errors."""

    def test_conditions_none_raises_runtime_error(self):
        block = _make_block(conditions=None)

        with self.assertRaises(RuntimeError) as ctx:
            block.run_trial(lambda win, kb, s, c: {"rt": 0.5})

        self.assertIn("conditions", str(ctx.exception).lower())

    def test_func_returning_none_raises_type_error(self):
        block = _make_block(conditions=np.array(["A"]))

        def bad_trial_func(win, kb, settings, cond):
            return None

        with self.assertRaises(TypeError) as ctx:
            block.run_trial(bad_trial_func)

        self.assertIn("dict", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()

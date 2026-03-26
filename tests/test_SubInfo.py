"""Tests for psyflow.SubInfo."""

import unittest
from unittest.mock import MagicMock

try:
    from psychopy import gui  # noqa: F401
    _HAS_PSYCHOPY = True
except ImportError:
    _HAS_PSYCHOPY = False

if _HAS_PSYCHOPY:
    import psyflow.SubInfo as _subinfo_mod
    from psyflow.SubInfo import SubInfo
    _gui = _subinfo_mod.gui


def _make_subinfo(**field_map_overrides):
    """Build a SubInfo without calling __init__."""
    info = SubInfo.__new__(SubInfo)
    info.fields = [
        {"name": "subject_id", "type": "int",
         "constraints": {"min": 101, "max": 999, "digits": 3}}
    ]
    info.field_map = {
        "Participant Information": "Info",
        "registration_failed": "Failed",
        "invalid_input": "Bad: {field}",
    }
    info.field_map.update(field_map_overrides)
    info.subject_data = None
    return info


@unittest.skipUnless(_HAS_PSYCHOPY, "requires psychopy")
class TestCollect(unittest.TestCase):
    """SubInfo.collect() control-flow edge cases."""

    def test_cancel_returns_none(self):
        info = _make_subinfo()

        mock_dlg = MagicMock()
        mock_dlg.show.return_value = None
        _gui.Dlg.return_value = mock_dlg

        result = info.collect(exit_on_cancel=False)
        self.assertIsNone(result)


@unittest.skipUnless(_HAS_PSYCHOPY, "requires psychopy")
class TestValidate(unittest.TestCase):
    """SubInfo.validate() error handling."""

    def test_keyboard_interrupt_propagates(self):
        info = _make_subinfo()

        class ExplodingStr:
            def __int__(self):
                raise KeyboardInterrupt("simulated Ctrl+C")
            def __str__(self):
                return "boom"

        with self.assertRaises(KeyboardInterrupt):
            info.validate([ExplodingStr()])


if __name__ == "__main__":
    unittest.main()

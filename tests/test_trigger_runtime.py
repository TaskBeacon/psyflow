import unittest


class WinStub:
    def __init__(self):
        self._calls = []

    def callOnFlip(self, func, *args, **kwargs):
        self._calls.append((func, args, kwargs))

    def flip(self):
        calls = list(self._calls)
        self._calls.clear()
        for func, args, kwargs in calls:
            func(*args, **kwargs)


class TestTriggerRuntime(unittest.TestCase):
    def test_emit_now_logs_planned_and_executed(self):
        from psyflow import TriggerEvent, TriggerRuntime, MockDriver

        events = []
        rt = TriggerRuntime(MockDriver(print_codes=False), event_logger=events.append)
        rt.emit(TriggerEvent(name="x", code=1), when="now")

        types = [e.get("type") for e in events]
        self.assertIn("trigger_planned", types)
        self.assertIn("trigger_executed", types)

    def test_emit_flip_logs_planned_then_executed_on_flip(self):
        from psyflow import TriggerEvent, TriggerRuntime, MockDriver

        events = []
        rt = TriggerRuntime(MockDriver(print_codes=False), event_logger=events.append)
        win = WinStub()

        rt.emit(TriggerEvent(name="x", code=2), when="flip", win=win, wait=False)
        planned = next(e for e in events if e.get("type") == "trigger_planned")
        self.assertEqual(planned.get("when"), "flip")
        self.assertTrue(planned.get("on_flip"))
        self.assertFalse(any(e.get("type") == "trigger_executed" for e in events))

        win.flip()
        executed = next(e for e in events if e.get("type") == "trigger_executed" and e.get("emit_id") == planned.get("emit_id"))
        self.assertEqual(executed.get("when"), "flip")
        self.assertTrue(executed.get("on_flip"))
        self.assertIsNotNone(executed.get("t_flip"))
        self.assertGreaterEqual(float(executed.get("t_sent")), float(planned.get("t_planned")))


if __name__ == "__main__":
    unittest.main()

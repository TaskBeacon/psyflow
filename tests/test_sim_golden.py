import tempfile
import unittest
from pathlib import Path


def _normalize_events(events: list[dict]) -> list[dict]:
    out: list[dict] = []
    for ev in events:
        rec = dict(ev)
        rec.pop("t", None)
        rec.pop("t_utc", None)
        out.append(rec)
    return out


class TestSimGolden(unittest.TestCase):
    def _run_session(self, seed: int, out_dir: Path) -> tuple[list[dict], list[dict]]:
        from psyflow.sim import Observation, ResponderAdapter, SessionInfo, iter_sim_events, load_responder, make_rng
        from psyflow.sim.logging import make_sim_jsonl_logger

        session = SessionInfo(
            participant_id="p001",
            session_id=f"sim-seed-{seed}",
            seed=seed,
            mode="sim",
            task_name="mid_demo",
            task_version="test",
        )
        rng = make_rng(seed)
        responder, _meta = load_responder(
            mode="sim",
            config={
                "responder": {
                    "type": "examples.sim.demo_responder:DemoResponder",
                    "kwargs": {"base_rt_s": 0.23, "jitter_s": 0.04},
                }
            },
            session=session,
            rng=rng,
            allow_fallback=False,
        )

        log_path = out_dir / "sim_events.jsonl"
        adapter = ResponderAdapter(
            policy="warn",
            default_rt_s=0.2,
            clamp_rt=False,
            logger=make_sim_jsonl_logger(log_path),
            session=session,
        )

        rows: list[dict] = []
        for trial_id in range(1, 9):
            obs = Observation(
                trial_id=trial_id,
                phase="target",
                valid_keys=["space"],
                deadline_s=0.5,
                block_id=1,
                condition_id="win" if trial_id % 2 else "lose",
                task_factors={"condition": "win" if trial_id % 2 else "lose"},
                mode="sim",
            )
            handled = adapter.handle_response(obs, responder)
            rows.append(
                {
                    "trial_id": trial_id,
                    "condition": obs.condition_id,
                    "response": handled.used_action.key,
                    "rt_s": handled.used_action.rt_s,
                    "validation": handled.validation.status,
                    "reason": handled.validation.reason_code,
                }
            )

        events = list(iter_sim_events(log_path))
        return events, rows

    def test_same_seed_reproduces_identical_events_and_rows(self):
        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            events1, rows1 = self._run_session(seed=42, out_dir=Path(td1))
            events2, rows2 = self._run_session(seed=42, out_dir=Path(td2))

        self.assertEqual(rows1, rows2)
        self.assertEqual(_normalize_events(events1), _normalize_events(events2))

    def test_different_seed_changes_rows(self):
        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            _events1, rows1 = self._run_session(seed=42, out_dir=Path(td1))
            _events2, rows2 = self._run_session(seed=99, out_dir=Path(td2))
        self.assertNotEqual(rows1, rows2)


if __name__ == "__main__":
    unittest.main()

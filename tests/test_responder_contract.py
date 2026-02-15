import contextlib
import os
import tempfile
import unittest
from pathlib import Path


@contextlib.contextmanager
def _patched_env(**updates):
    old = {}
    for k, v in updates.items():
        old[k] = os.environ.get(k)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = str(v)
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class TestResponderContract(unittest.TestCase):
    def test_null_responder_contract(self):
        from psyflow.sim import NullResponder, Observation, SessionInfo, make_rng

        responder = NullResponder()
        responder.start_session(
            SessionInfo(
                participant_id="p001",
                session_id="s001",
                seed=7,
                mode="sim",
                task_name="demo",
                task_version=None,
            ),
            make_rng(7),
        )
        action = responder.act(
            Observation(
                trial_id=1,
                phase="target",
                valid_keys=["space"],
                deadline_s=0.5,
                mode="sim",
            )
        )
        self.assertIsNone(action.key)
        self.assertIsNone(action.rt_s)
        responder.end_session()

    def test_scripted_responder_handles_optional_fields(self):
        from psyflow.sim import Observation, ScriptedResponder

        responder = ScriptedResponder(key=None, rt_s=0.1)
        obs = Observation(
            trial_id=1,
            phase="target",
            valid_keys=["left", "right"],
            deadline_s=0.5,
            mode="qa",
            extras={"min_wait_s": 0.2},
        )
        act = responder.act(obs)
        self.assertEqual(act.key, "left")
        self.assertGreaterEqual(float(act.rt_s), 0.2)

    def test_adapter_rejects_invalid_key_warn(self):
        from psyflow.sim import Observation, ResponderAdapter
        from psyflow.sim.contracts import Action

        class BadResponder:
            def act(self, obs):
                return Action(key="bad", rt_s=0.1)

        adapter = ResponderAdapter(policy="warn")
        handled = adapter.handle_response(
            Observation(
                trial_id=1,
                phase="target",
                valid_keys=["space"],
                deadline_s=0.5,
                mode="sim",
            ),
            BadResponder(),
        )
        self.assertEqual(handled.validation.status, "rejected")
        self.assertEqual(handled.validation.reason_code, "INVALID_KEY")
        self.assertIsNone(handled.used_action.key)
        self.assertIsNone(handled.used_action.rt_s)

    def test_adapter_strict_raises_on_invalid_key(self):
        from psyflow.sim import Observation, ResponderActionError, ResponderAdapter
        from psyflow.sim.contracts import Action

        class BadResponder:
            def act(self, obs):
                return Action(key="bad", rt_s=0.1)

        adapter = ResponderAdapter(policy="strict")
        with self.assertRaises(ResponderActionError):
            adapter.handle_response(
                Observation(
                    trial_id=1,
                    phase="target",
                    valid_keys=["space"],
                    deadline_s=0.5,
                    mode="sim",
                ),
                BadResponder(),
            )

    def test_adapter_coerce_missing_rt(self):
        from psyflow.sim import Observation, ResponderAdapter
        from psyflow.sim.contracts import Action

        class MissingRtResponder:
            def act(self, obs):
                return Action(key="space", rt_s=None)

        adapter = ResponderAdapter(policy="coerce", default_rt_s=0.25)
        handled = adapter.handle_response(
            Observation(
                trial_id=1,
                phase="target",
                valid_keys=["space"],
                deadline_s=0.2,
                mode="sim",
            ),
            MissingRtResponder(),
        )
        self.assertEqual(handled.validation.status, "coerced")
        self.assertEqual(handled.validation.reason_code, "MISSING_RT")
        self.assertEqual(handled.used_action.key, "space")
        self.assertLessEqual(float(handled.used_action.rt_s), 0.2)

    def test_loader_can_import_external_plugin(self):
        from psyflow.sim import SessionInfo, load_responder, make_rng

        session = SessionInfo(
            participant_id="p001",
            session_id="s001",
            seed=11,
            mode="sim",
            task_name="demo",
            task_version=None,
        )
        cfg = {
            "responder": {
                "class": "examples.sim.demo_responder:DemoResponder",
                "kwargs": {"base_rt_s": 0.2, "jitter_s": 0.01},
            }
        }
        with _patched_env(PSYFLOW_RESPONDER_CLASS=None, PSYFLOW_RESPONDER_KWARGS=None):
            responder, meta = load_responder(
                mode="sim",
                config=cfg,
                session=session,
                rng=make_rng(11),
                allow_fallback=False,
            )
        self.assertEqual(meta.get("fallback"), False)
        self.assertEqual(meta.get("name"), "DemoResponder")

    def test_context_from_env_reads_raw_yaml_style_config(self):
        from psyflow.qa.context import context_from_env

        with tempfile.TemporaryDirectory() as td:
            cfg = {
                "raw": {
                    "task": {"task_name": "mid_task", "task_version": "0.1"},
                    "sim": {
                        "seed": 123,
                        "policy": "coerce",
                        "output_dir": "outputs/sim",
                        "responder": {"kind": "null"},
                    },
                    "qa": {"output_dir": "outputs/qa"},
                }
            }
            with _patched_env(PSYFLOW_MODE="sim"):
                ctx = context_from_env(task_dir=Path(td), config=cfg)
            self.assertEqual(ctx.mode, "sim")
            self.assertEqual(ctx.config.sim_policy, "coerce")
            self.assertEqual(ctx.session.seed, 123)
            self.assertEqual(ctx.session.task_name, "mid_task")
            self.assertIsNotNone(ctx.responder)


if __name__ == "__main__":
    unittest.main()

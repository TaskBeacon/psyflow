from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional

from .contracts import Action, Observation, ResponderProtocol, SessionInfo


Policy = Literal["strict", "warn", "coerce"]


class ResponderActionError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ValidationResult:
    status: Literal["ok", "coerced", "rejected", "error"]
    reason_code: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class HandledResponse:
    raw_action: dict[str, Any] | None
    used_action: Action
    validation: ValidationResult


def _serialize_action(action: Any) -> dict[str, Any] | None:
    if action is None:
        return None
    if isinstance(action, Action):
        return action.to_dict()
    if isinstance(action, dict):
        out = dict(action)
        if "rt" in out and "rt_s" not in out:
            out["rt_s"] = out.get("rt")
        return out
    if isinstance(action, (tuple, list)):
        key = action[0] if len(action) >= 1 else None
        rt = action[1] if len(action) >= 2 else None
        return {"key": key, "rt_s": rt}
    return {"value": repr(action)}


def _coerce_to_action(action: Any) -> Action:
    if action is None:
        return Action(key=None, rt_s=None, meta={})
    if isinstance(action, Action):
        return action
    if isinstance(action, dict):
        key = action.get("key")
        rt = action.get("rt_s", action.get("rt"))
        meta = action.get("meta")
        return Action(key=key, rt_s=rt, meta=meta)
    if isinstance(action, (tuple, list)):
        key = action[0] if len(action) >= 1 else None
        rt = action[1] if len(action) >= 2 else None
        return Action(key=key, rt_s=rt, meta={})
    if hasattr(action, "key") and hasattr(action, "rt"):
        # Backward compatibility with legacy Action(key, rt).
        return Action(key=getattr(action, "key"), rt_s=getattr(action, "rt"), meta={})
    return Action(key=None, rt_s=None, meta={"parse_error": f"unsupported_action_type:{type(action).__name__}"})


class ResponderAdapter:
    """Central validation and policy layer for injected responses."""

    def __init__(
        self,
        *,
        policy: Policy = "warn",
        default_rt_s: float = 0.2,
        clamp_rt: bool = False,
        logger: Optional[Callable[[dict[str, Any]], None]] = None,
        session: SessionInfo | None = None,
    ):
        if policy not in ("strict", "warn", "coerce"):
            policy = "warn"
        self.policy: Policy = policy
        self.default_rt_s = float(default_rt_s)
        self.clamp_rt = bool(clamp_rt)
        self.logger = logger
        self.session = session

    def _log_observation_warning(self, obs: Observation, *, missing: list[str]) -> None:
        if self.logger is None:
            return
        try:
            self.logger(
                {
                    "type": "sim_observation_warning",
                    "session": self.session.to_dict() if self.session is not None else None,
                    "obs": obs.to_dict(),
                    "validation": {
                        "status": "warning",
                        "reason_code": "MISSING_OBS_FIELDS",
                        "message": f"Observation missing recommended required fields: {missing}",
                    },
                }
            )
        except Exception:
            return

    def _warn_if_missing_required_fields(self, obs: Observation) -> None:
        # Warning-only rollout for task context standardization in sim/qa modes.
        mode = str(obs.mode or "").strip().lower()
        if mode not in ("qa", "sim"):
            return
        missing: list[str] = []
        if obs.trial_id is None:
            missing.append("trial_id")
        if not str(obs.phase or "").strip():
            missing.append("phase")
        if obs.deadline_s is None and obs.response_window_s is None:
            missing.append("deadline_s")
        if not isinstance(obs.valid_keys, list) or not obs.valid_keys:
            missing.append("valid_keys")
        if missing:
            self._log_observation_warning(obs, missing=missing)

    def _log(
        self,
        *,
        obs: Observation,
        raw_action: dict[str, Any] | None,
        used_action: Action,
        validation: ValidationResult,
    ) -> None:
        if self.logger is None:
            return
        try:
            self.logger(
                {
                    "type": "sim_action",
                    "session": self.session.to_dict() if self.session is not None else None,
                    "obs": obs.to_dict(),
                    "raw_action": raw_action,
                    "used_action": used_action.to_dict(),
                    "validation": {
                        "status": validation.status,
                        "reason_code": validation.reason_code,
                        "message": validation.message,
                    },
                }
            )
        except Exception:
            # Sim logging must never break runtime.
            return

    def _reject(
        self,
        *,
        obs: Observation,
        raw_action: dict[str, Any] | None,
        code: str,
        message: str,
    ) -> HandledResponse:
        used = Action(key=None, rt_s=None, meta={"rejected": code})
        val = ValidationResult(status="rejected", reason_code=code, message=message)
        self._log(obs=obs, raw_action=raw_action, used_action=used, validation=val)
        return HandledResponse(raw_action=raw_action, used_action=used, validation=val)

    def _error(self, code: str, message: str) -> None:
        raise ResponderActionError(code=code, message=message)

    def handle_response(self, obs: Observation, responder: ResponderProtocol) -> HandledResponse:
        self._warn_if_missing_required_fields(obs)
        raw = None
        try:
            try:
                raw_obj = responder.act(obs)
            except TypeError:
                # Backward compatibility: legacy responders that expect dict input.
                raw_obj = responder.act(obs.to_dict())  # type: ignore[arg-type]
            raw = _serialize_action(raw_obj)
            action = _coerce_to_action(raw_obj)
        except ResponderActionError:
            raise
        except Exception as e:
            if self.policy == "strict":
                self._error("ACT_EXCEPTION", f"Responder.act failed: {e}")
            return self._reject(obs=obs, raw_action=raw, code="ACT_EXCEPTION", message=f"Responder.act failed: {e}")

        if not bool(obs.response_window_open):
            return self._reject(
                obs=obs,
                raw_action=raw,
                code="WINDOW_CLOSED",
                message="Response window is closed.",
            )

        valid_keys = list(obs.valid_keys or [])
        if not valid_keys:
            if self.policy == "strict":
                self._error("EMPTY_VALID_KEYS", "Observation.valid_keys is empty.")
            return self._reject(
                obs=obs,
                raw_action=raw,
                code="EMPTY_VALID_KEYS",
                message="Observation.valid_keys is empty.",
            )

        key = action.key
        rt_s = action.rt_s
        meta = dict(action.meta or {})

        if key is not None:
            key = str(key)
            if key not in valid_keys:
                if self.policy == "strict":
                    self._error("INVALID_KEY", f"Key {key!r} not in valid_keys={valid_keys!r}")
                return self._reject(
                    obs=obs,
                    raw_action=raw,
                    code="INVALID_KEY",
                    message=f"Key {key!r} not in valid_keys.",
                )

        # No key means no response.
        if key is None:
            if rt_s is not None:
                meta["ignored_rt_s"] = rt_s
            used = Action(key=None, rt_s=None, meta=meta)
            val = ValidationResult(status="ok", reason_code="NO_RESPONSE", message="Responder produced no key.")
            self._log(obs=obs, raw_action=raw, used_action=used, validation=val)
            return HandledResponse(raw_action=raw, used_action=used, validation=val)

        # Key present, RT required unless coerce policy.
        if rt_s is None:
            if self.policy == "coerce":
                deadline = obs.deadline_s if obs.deadline_s is not None else obs.response_window_s
                rt = float(self.default_rt_s)
                if deadline is not None:
                    rt = min(rt, float(deadline))
                used = Action(key=key, rt_s=max(0.0, rt), meta={**meta, "coerced": "MISSING_RT"})
                val = ValidationResult(status="coerced", reason_code="MISSING_RT", message="Filled missing rt_s.")
                self._log(obs=obs, raw_action=raw, used_action=used, validation=val)
                return HandledResponse(raw_action=raw, used_action=used, validation=val)
            if self.policy == "strict":
                self._error("MISSING_RT", "Action.key is set but rt_s is missing.")
            return self._reject(
                obs=obs,
                raw_action=raw,
                code="MISSING_RT",
                message="Action.key is set but rt_s is missing.",
            )

        try:
            rt = float(rt_s)
        except Exception:
            if self.policy == "strict":
                self._error("INVALID_RT_TYPE", f"rt_s is not numeric: {rt_s!r}")
            return self._reject(
                obs=obs,
                raw_action=raw,
                code="INVALID_RT_TYPE",
                message=f"rt_s is not numeric: {rt_s!r}",
            )

        deadline = obs.deadline_s if obs.deadline_s is not None else obs.response_window_s
        out_of_bounds = rt < 0.0 or (deadline is not None and rt > float(deadline))
        if out_of_bounds:
            if self.policy == "strict":
                self._error("RT_OUT_OF_BOUNDS", f"rt_s={rt} out of bounds for deadline={deadline}")
            if self.policy == "coerce" and self.clamp_rt and deadline is not None:
                clamped = min(max(0.0, rt), float(deadline))
                used = Action(key=key, rt_s=clamped, meta={**meta, "coerced": "RT_CLAMPED"})
                val = ValidationResult(status="coerced", reason_code="RT_CLAMPED", message="Clamped rt_s into bounds.")
                self._log(obs=obs, raw_action=raw, used_action=used, validation=val)
                return HandledResponse(raw_action=raw, used_action=used, validation=val)
            return self._reject(
                obs=obs,
                raw_action=raw,
                code="RT_OUT_OF_BOUNDS",
                message=f"rt_s={rt} out of bounds for deadline={deadline}",
            )

        used = Action(key=key, rt_s=rt, meta=meta)
        val = ValidationResult(status="ok", reason_code=None, message=None)
        self._log(obs=obs, raw_action=raw, used_action=used, validation=val)
        return HandledResponse(raw_action=raw, used_action=used, validation=val)

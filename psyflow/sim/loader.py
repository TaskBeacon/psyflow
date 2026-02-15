from __future__ import annotations

import importlib
import json
import os
from typing import Any

from .contracts import NullResponder, ScriptedResponder, SessionInfo


def _deep_get(mapping: dict[str, Any] | None, path: tuple[str, ...], default: Any = None) -> Any:
    cur: Any = mapping or {}
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _parse_json_env(name: str, default: Any) -> Any:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def _import_attr(import_path: str) -> Any:
    if ":" in import_path:
        mod_name, attr_name = import_path.split(":", 1)
    else:
        mod_name, attr_name = import_path.rsplit(".", 1)
    module = importlib.import_module(mod_name)
    return getattr(module, attr_name)


def _resolve_spec(mode: str, config: dict[str, Any] | None) -> tuple[str | None, dict[str, Any], str]:
    """Return (responder_class_path_or_kind, kwargs, source)."""
    if mode not in ("qa", "sim"):
        return None, {}, "disabled"

    # Env has highest priority.
    env_class = os.getenv("PSYFLOW_RESPONDER_CLASS", "").strip()
    if env_class:
        env_kwargs = _parse_json_env("PSYFLOW_RESPONDER_KWARGS", {})
        return env_class, dict(env_kwargs or {}), "env.class"

    # Config responder.class
    cfg_class = _deep_get(config, ("responder", "class"), None)
    if isinstance(cfg_class, str) and cfg_class.strip():
        cfg_kwargs = _deep_get(config, ("responder", "kwargs"), {}) or {}
        return cfg_class.strip(), dict(cfg_kwargs), "config.class"

    # Kind-based fallback.
    kind = os.getenv("PSYFLOW_QA_RESPONDER", "").strip().lower()
    if not kind:
        kind = str(_deep_get(config, ("responder", "kind"), "") or "").strip().lower()
    if not kind:
        kind = "scripted"

    kwargs = dict(_deep_get(config, ("responder", "kwargs"), {}) or {})
    # Legacy env knobs for scripted responder.
    key = os.getenv("PSYFLOW_QA_RESPONDER_KEY", "").strip() or None
    if key is not None:
        kwargs.setdefault("key", key)
    rt_raw = os.getenv("PSYFLOW_QA_RESPONDER_RT", "").strip()
    if rt_raw:
        try:
            kwargs.setdefault("rt_s", float(rt_raw))
        except Exception:
            pass
    return kind, kwargs, "kind"


def load_responder(
    *,
    mode: str,
    config: dict[str, Any] | None = None,
    session: SessionInfo | None = None,
    rng: Any = None,
    allow_fallback: bool = True,
) -> tuple[Any, dict[str, Any]]:
    """Load and initialize a responder plugin.

    Returns:
        (responder, meta)
    """
    spec, kwargs, source = _resolve_spec(mode, config)
    if spec is None:
        return None, {"source": source, "name": None}

    builtins: dict[str, Any] = {
        "scripted": ScriptedResponder,
        "null": NullResponder,
    }

    cls = None
    try:
        if spec in builtins:
            cls = builtins[spec]
        else:
            cls = _import_attr(spec)
        responder = cls(**kwargs) if callable(cls) else cls
    except Exception as e:
        if not allow_fallback:
            raise
        # Backward-compatible safe fallback.
        responder = ScriptedResponder()
        return responder, {
            "source": source,
            "name": "scripted",
            "fallback": True,
            "error": repr(e),
        }

    # Optional lifecycle hook.
    try:
        if session is not None and hasattr(responder, "start_session"):
            responder.start_session(session, rng)
    except Exception:
        # Keep runtime robust: responder lifecycle must not crash task startup.
        pass

    name = getattr(cls, "__name__", responder.__class__.__name__) if cls is not None else responder.__class__.__name__
    return responder, {"source": source, "name": name, "fallback": False}


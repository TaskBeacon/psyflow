from __future__ import annotations

import importlib
from typing import Any

from .contracts import NullResponder, ScriptedResponder, SessionInfo


def _deep_get(mapping: dict[str, Any] | None, path: tuple[str, ...], default: Any = None) -> Any:
    cur: Any = mapping or {}
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _import_attr(import_path: str) -> Any:
    if ":" in import_path:
        mod_name, attr_name = import_path.split(":", 1)
    else:
        mod_name, attr_name = import_path.rsplit(".", 1)
    module = importlib.import_module(mod_name)
    return getattr(module, attr_name)


def _resolve_spec(mode: str, config: dict[str, Any] | None) -> tuple[str | None, dict[str, Any], str]:
    """Return (responder_type_or_import_path, kwargs, source)."""
    if mode not in ("qa", "sim"):
        return None, {}, "disabled"

    responder_cfg = _deep_get(config, ("responder",), {})
    if not isinstance(responder_cfg, dict):
        responder_cfg = {}

    responder_type = responder_cfg.get("type")
    kwargs = dict(responder_cfg.get("kwargs") or {})
    if isinstance(responder_type, str) and responder_type.strip():
        return responder_type.strip(), kwargs, "config.type"

    return "scripted", kwargs, "default"


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
        spec_name = str(spec).strip()
        if spec_name.lower() in builtins:
            cls = builtins[spec_name.lower()]
        else:
            cls = _import_attr(spec_name)
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

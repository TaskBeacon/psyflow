from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    # Keep this module importable in minimal environments (e.g., CI smoke tests)
    # where optional dependencies are not installed.
    yaml = None


class StaticQAError(Exception):
    code = "CONFIG_INVALID"


class ConfigInvalidError(StaticQAError):
    code = "CONFIG_INVALID"


class AssetMissingError(StaticQAError):
    code = "ASSET_MISSING"


class ContractInvalidError(StaticQAError):
    code = "CONTRACT_INVALID"


class TriggerInvalidError(StaticQAError):
    code = "TRIGGER_INVALID"


class KeysInvalidError(StaticQAError):
    code = "KEYS_INVALID"


def load_yaml(path: str | Path) -> Any:
    if yaml is None:  # pragma: no cover
        raise ModuleNotFoundError(
            "PyYAML is required to load YAML files. Install with `pip install pyyaml`."
        )
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def contract_lint(acceptance: dict[str, Any]) -> None:
    if not isinstance(acceptance, dict):
        raise ContractInvalidError(f"acceptance_criteria must be a mapping, got {type(acceptance)}")

    cols = acceptance.get("required_columns")
    if cols is None:
        raise ContractInvalidError("acceptance_criteria missing 'required_columns'")
    if not isinstance(cols, list) or not cols or not all(isinstance(c, str) and c for c in cols):
        raise ContractInvalidError("'required_columns' must be a non-empty list of strings")

    expected_trial_count = acceptance.get("expected_trial_count")
    if expected_trial_count is not None and (not isinstance(expected_trial_count, int) or expected_trial_count <= 0):
        raise ContractInvalidError("'expected_trial_count' must be a positive integer if present")

    allowed_keys = acceptance.get("allowed_keys")
    if allowed_keys is not None:
        if not isinstance(allowed_keys, list) or not allowed_keys or not all(isinstance(k, str) and k for k in allowed_keys):
            raise ContractInvalidError("'allowed_keys' must be a non-empty list of strings if present")

    assets = acceptance.get("assets_required")
    if assets is not None and (not isinstance(assets, list) or not all(isinstance(a, str) for a in assets)):
        raise ContractInvalidError("'assets_required' must be a list of strings if present")

    triggers_required = acceptance.get("triggers_required")
    if triggers_required is not None and not isinstance(triggers_required, bool):
        raise ContractInvalidError("'triggers_required' must be a boolean if present")

    # Optional trigger expectations:
    # - trigger_codes_expected: [1,2,3]
    # - triggers_expected: {codes: [1,2,3]}
    trigger_codes = acceptance.get("trigger_codes_expected")
    if trigger_codes is not None:
        if not isinstance(trigger_codes, list) or not all(isinstance(c, int) for c in trigger_codes):
            raise ContractInvalidError("'trigger_codes_expected' must be a list of integers if present")
    triggers_expected = acceptance.get("triggers_expected")
    if triggers_expected is not None:
        if not isinstance(triggers_expected, dict):
            raise ContractInvalidError("'triggers_expected' must be a mapping if present")
        codes = triggers_expected.get("codes")
        if codes is not None and (not isinstance(codes, list) or not all(isinstance(c, int) for c in codes)):
            raise ContractInvalidError("'triggers_expected.codes' must be a list of integers if present")


def _extract_acceptance_from_config(cfg: Any) -> Any:
    if not isinstance(cfg, dict):
        return None
    qa_cfg = cfg.get("qa")
    if not isinstance(qa_cfg, dict):
        return None
    return qa_cfg.get("acceptance_criteria")


def _default_config_path(task_dir: Path) -> Path | None:
    qa_path = task_dir / "config" / "config_qa.yaml"
    if qa_path.exists():
        return qa_path
    base_path = task_dir / "config" / "config.yaml"
    if base_path.exists():
        return base_path
    return None


def _config_sanity(cfg: Any) -> None:
    if cfg is None:
        return
    if not isinstance(cfg, dict):
        raise ConfigInvalidError(f"config must be a mapping, got {type(cfg)}")

    # Common sections should be mappings when present.
    for k in ("window", "task", "timing", "stimuli", "triggers", "controller", "qa"):
        if k in cfg and cfg[k] is not None and not isinstance(cfg[k], dict):
            raise ConfigInvalidError(f"config section '{k}' must be a mapping, got {type(cfg[k])}")

    # Minimal timing sanity: all numeric entries in 'timing' should be > 0.
    timing = cfg.get("timing") if isinstance(cfg, dict) else None
    if isinstance(timing, dict):
        for tk, tv in timing.items():
            if isinstance(tv, (int, float)) and tv <= 0:
                raise ConfigInvalidError(f"timing.{tk} must be > 0, got {tv}")


def _keys_sanity(cfg: Any, acceptance: Any) -> None:
    if not isinstance(cfg, dict):
        return
    task = cfg.get("task")
    if task is None:
        return
    if not isinstance(task, dict):
        raise ConfigInvalidError("config.task must be a mapping")

    keys = task.get("key_list")
    if keys is None:
        return
    if not isinstance(keys, list) or not keys or not all(isinstance(k, str) and k for k in keys):
        raise KeysInvalidError("config.task.key_list must be a non-empty list of strings")

    if isinstance(acceptance, dict):
        allowed = acceptance.get("allowed_keys")
        if allowed is not None:
            if not isinstance(allowed, list) or not allowed or not all(isinstance(k, str) and k for k in allowed):
                raise KeysInvalidError("acceptance.allowed_keys must be a non-empty list of strings")
            extra = [k for k in keys if k not in allowed]
            if extra:
                raise KeysInvalidError(f"config.task.key_list contains keys not in acceptance.allowed_keys: {extra}")


def _triggers_sanity(cfg: Any, acceptance: Any) -> None:
    if not isinstance(cfg, dict):
        return
    triggers = cfg.get("triggers")
    if triggers is None:
        if isinstance(acceptance, dict) and acceptance.get("triggers_required") is True:
            raise TriggerInvalidError("acceptance.triggers_required=true but config.triggers is missing")
        return
    if not isinstance(triggers, dict):
        raise TriggerInvalidError("config.triggers must be a mapping")

    # Support both legacy and new trigger config shapes.
    trigger_map = triggers
    if isinstance(triggers.get("map"), dict):
        trigger_map = triggers.get("map") or {}

    codes = []
    for k, v in trigger_map.items():
        if v is None:
            continue
        if not isinstance(v, int):
            raise TriggerInvalidError(f"trigger code for '{k}' must be an int or null, got {type(v)}")
        codes.append(v)

    if not codes:
        if isinstance(acceptance, dict) and acceptance.get("triggers_required") is True:
            raise TriggerInvalidError("acceptance.triggers_required=true but config.triggers has no codes")
        return

    dup = sorted({c for c in codes if codes.count(c) > 1})
    if dup:
        raise TriggerInvalidError(f"Duplicate trigger codes detected: {dup}")

    if isinstance(acceptance, dict):
        expected_codes = None
        if isinstance(acceptance.get("trigger_codes_expected"), list):
            expected_codes = [c for c in acceptance.get("trigger_codes_expected") if isinstance(c, int)]
        if expected_codes is None:
            te = acceptance.get("triggers_expected")
            if isinstance(te, dict) and isinstance(te.get("codes"), list):
                expected_codes = [c for c in te.get("codes") if isinstance(c, int)]
        if expected_codes:
            missing = [c for c in expected_codes if c not in codes]
            if missing:
                raise TriggerInvalidError(f"Expected trigger codes missing from config.triggers: {missing}")


def static_qa(
    task_dir: str | Path,
    *,
    config_path: str | Path | None = None,
    acceptance_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run lightweight static checks for a task directory."""
    task_dir = Path(task_dir)
    out: dict[str, Any] = {
        "warnings": [],
        "config_path": None,
        "acceptance_path": None,
        "acceptance_source": None,
    }

    cfg_obj: Any = None
    if config_path is None:
        config_path = _default_config_path(task_dir)
    if config_path is not None:
        cp = Path(config_path)
        cfg = load_yaml(cp)
        _config_sanity(cfg)
        cfg_obj = cfg
        out["config_path"] = str(cp)
    else:
        out["warnings"].append("No config found (checked config/config_qa.yaml then config/config.yaml); config checks skipped.")

    acceptance_obj: Any = None
    if acceptance_path is not None:
        ap = Path(acceptance_path)
        acc = load_yaml(ap)
        contract_lint(acc)
        acceptance_obj = acc
        out["acceptance_path"] = str(ap)
        out["acceptance_source"] = "file"
    else:
        acc = _extract_acceptance_from_config(cfg_obj)
        if acc is not None:
            contract_lint(acc)
            acceptance_obj = acc
            out["acceptance_source"] = "config:qa.acceptance_criteria"
        else:
            out["warnings"].append("qa.acceptance_criteria not found in config; schema checks will be limited.")

    if isinstance(acceptance_obj, dict):
        assets = acceptance_obj.get("assets_required")
        if isinstance(assets, list):
            missing = [a for a in assets if not (task_dir / a).exists()]
            if missing:
                raise AssetMissingError(f"Missing required assets: {missing}")

    _keys_sanity(cfg_obj, acceptance_obj)
    _triggers_sanity(cfg_obj, acceptance_obj)

    return out

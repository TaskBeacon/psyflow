"""Config validation/loading utilities."""

import os
from typing import Any, Dict, Iterable, List, Optional

import yaml


def validate_config(
    raw_config: Any,
    *,
    required_sections: Optional[Iterable[str]] = None,
) -> None:
    """Lightweight validation for a psyflow-style YAML config dict."""
    if not isinstance(raw_config, dict):
        raise TypeError(f"Config must be a dict, got {type(raw_config)}")

    required = list(required_sections) if required_sections is not None else []
    missing = [k for k in required if k not in raw_config]
    if missing:
        raise ValueError(f"Missing top-level config sections: {missing}")

    for k in ("window", "task", "timing", "stimuli", "triggers", "controller"):
        if k in raw_config and raw_config[k] is not None and not isinstance(raw_config[k], dict):
            raise TypeError(f"Config section '{k}' must be a dict, got {type(raw_config[k])}")


def load_config(
    config_file: str = "config/config.yaml",
    extra_keys: Optional[List[str]] = None,
    *,
    validate: bool = False,
    required_sections: Optional[Iterable[str]] = None,
) -> Dict:
    """Load a config.yaml file and return a structured dictionary."""
    if config_file == "config/config.yaml":
        config_file = os.getenv("PSYFLOW_CONFIG", config_file)

    with open(config_file, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if validate:
        validate_config(config, required_sections=required_sections)

    task_keys = ["window", "task", "timing"]

    # Trigger config supports two shapes:
    # 1) legacy: triggers: {event_name: code, ...}
    # 2) new:    triggers: {map: {...}, driver: {...}, policy: {...}, timing: {...}}
    triggers_section = config.get("triggers", {}) or {}
    trigger_map = triggers_section
    trigger_driver = {}
    trigger_policy = {}
    trigger_timing = {}
    if isinstance(triggers_section, dict):
        maybe_map = triggers_section.get("map")
        if isinstance(maybe_map, dict):
            trigger_map = maybe_map
            driver = triggers_section.get("driver", {})
            policy = triggers_section.get("policy", {})
            timing = triggers_section.get("timing", {})
            trigger_driver = driver if isinstance(driver, dict) else {}
            trigger_policy = policy if isinstance(policy, dict) else {}
            trigger_timing = timing if isinstance(timing, dict) else {}

    output = {
        "raw": config,
        "task_config": {k: v for key in task_keys for k, v in config.get(key, {}).items()},
        "stim_config": config.get("stimuli", {}),
        "subform_config": {
            "subinfo_fields": config.get("subinfo_fields", []),
            "subinfo_mapping": config.get("subinfo_mapping", {}),
        },
        "trigger_config": trigger_map if isinstance(trigger_map, dict) else {},
        "trigger_driver_config": trigger_driver,
        "trigger_policy_config": trigger_policy,
        "trigger_timing_config": trigger_timing,
        "controller_config": config.get("controller", {}),
    }

    if extra_keys:
        for key in extra_keys:
            key_name = f"{key}_config"
            if key_name not in output:
                output[key_name] = config.get(key, {})

    return output

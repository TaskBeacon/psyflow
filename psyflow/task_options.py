from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


DEFAULT_MODES: tuple[str, ...] = ("human", "qa", "sim")


@dataclass(frozen=True)
class TaskRunOptions:
    mode: str
    config_path: Path


def _fail(parser: argparse.ArgumentParser | None, message: str) -> None:
    if parser is not None:
        parser.error(message)
    raise ValueError(message)


def resolve_mode(
    positional_mode: str | None,
    flag_mode: str | None,
    *,
    parser: argparse.ArgumentParser | None = None,
    default_mode: str = "human",
    modes: Sequence[str] = DEFAULT_MODES,
) -> str:
    mode_pos = (positional_mode or "").strip().lower() or None
    mode_flag = (flag_mode or "").strip().lower() or None
    if mode_pos and mode_flag and mode_pos != mode_flag:
        _fail(parser, f"Conflicting mode values: positional={mode_pos!r}, --mode={mode_flag!r}")
    mode = mode_flag or mode_pos or default_mode
    if mode not in modes:
        _fail(parser, f"Unsupported mode: {mode!r}. Allowed: {list(modes)!r}")
    return mode


def resolve_config_path(
    task_root: Path,
    *,
    mode: str,
    config_arg: str | None,
    default_config_by_mode: Mapping[str, str],
) -> Path:
    if mode not in default_config_by_mode:
        raise KeyError(f"No default config mapping for mode={mode!r}")

    if config_arg:
        cfg = Path(config_arg)
        cfg = cfg if cfg.is_absolute() else (task_root / cfg)
    else:
        cfg = task_root / default_config_by_mode[mode]
    if not cfg.exists():
        raise FileNotFoundError(f"Config file not found: {cfg}")
    return cfg


def _default_config_help(default_config_by_mode: Mapping[str, str]) -> str:
    parts = [f"{mode}={path}" for mode, path in default_config_by_mode.items()]
    mapping = ", ".join(parts)
    return f"Config YAML path. If omitted, defaults by mode: {mapping}"


def build_task_arg_parser(
    *,
    description: str,
    modes: Sequence[str] = DEFAULT_MODES,
    default_config_by_mode: Mapping[str, str] | None = None,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("mode", nargs="?", choices=modes, help="Optional positional mode.")
    parser.add_argument("--mode", dest="mode_flag", choices=modes, default=None, help="Execution mode.")
    config_help = "Config YAML path."
    if default_config_by_mode:
        config_help = _default_config_help(default_config_by_mode)
    parser.add_argument("--config", default=None, help=config_help)
    return parser


def parse_task_run_options(
    *,
    task_root: Path,
    description: str,
    default_config_by_mode: Mapping[str, str],
    argv: Sequence[str] | None = None,
    modes: Sequence[str] = DEFAULT_MODES,
) -> TaskRunOptions:
    parser = build_task_arg_parser(
        description=description,
        modes=modes,
        default_config_by_mode=default_config_by_mode,
    )
    ns = parser.parse_args(argv)
    mode = resolve_mode(ns.mode, ns.mode_flag, parser=parser, modes=modes)
    config_path = resolve_config_path(
        task_root=task_root,
        mode=mode,
        config_arg=ns.config,
        default_config_by_mode=default_config_by_mode,
    )
    return TaskRunOptions(mode=mode, config_path=config_path)

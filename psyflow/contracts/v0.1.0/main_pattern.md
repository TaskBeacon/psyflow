# main.py Pattern (v0.1.0)

A compliant task `main.py` should look like this (shape, not exact code):

```python
from pathlib import Path
from contextlib import nullcontext

from psyflow import (
    TaskRunOptions,
    parse_task_run_options,
    context_from_config,
    runtime_context,
    load_config,
)

MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_sim.yaml",
}


def run(options: TaskRunOptions):
    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))

    runtime_ctx = None
    runtime_scope = nullcontext()
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        # one auditable flow for human/qa/sim
        pass


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = parse_task_run_options(
        task_root=task_root,
        description="Run task in human/qa/sim mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )
    run(options)


if __name__ == "__main__":
    main()
```

Key requirements:
- explicit mode handling (`human`, `qa`, `sim`)
- deterministic config resolution
- single task flow with mode-specific hooks
- no hidden env-only mode switching

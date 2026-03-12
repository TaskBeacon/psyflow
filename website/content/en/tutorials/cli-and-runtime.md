# CLI shortcuts and runtime modes

The CLI model is simpler than the old docs suggested:

- `psyflow` is the root command, mainly for scaffolding
- task execution stays task-local
- shortcut launchers call the task's `main.py` in the right mode

Do **not** rely on older descriptions of `psyflow qa` or `psyflow sim` as root subcommands. The maintained entrypoints are different now.

## Current entrypoints

These are the maintained commands defined in `pyproject.toml`:

| Command | Purpose |
| --- | --- |
| `psyflow` | root CLI, including `psyflow init` |
| `psyflow-run` | launch a task in human mode |
| `psyflow-qa` | launch a task in QA mode and validate QA artifacts |
| `psyflow-sim` | launch a task in simulation mode |
| `psyflow-validate` | run static contract/config/package validation |

## Scaffold a new task

```bash
psyflow init my-new-task
```

Initialize the current directory instead:

```bash
psyflow init
```

## Run a task in human mode

```bash
psyflow-run path/to/task
```

This resolves the task entry and forwards into the task-local `main.py`.

You can still run the file directly:

```bash
python main.py
```

but the shortcut is better for consistent task-path handling.

## Run QA mode

```bash
psyflow-qa path/to/task --config config/config_qa.yaml
```

What QA mode does now:

- runs the task in QA mode
- validates generated QA artifacts
- can update `taskbeacon.yaml` maturity on pass
- can update the README maturity badge on pass

Use `--set-maturity` if you want promotion behavior:

```bash
psyflow-qa path/to/task --config config/config_qa.yaml --set-maturity smoke_tested
```

Typical QA artifacts live under `outputs/qa/`:

- `qa_report.json`
- `static_report.json`
- `contract_report.json`
- `qa_trace.csv`
- `qa_events.jsonl`

## Run simulation mode

```bash
psyflow-sim path/to/task --config config/config_scripted_sim.yaml
```

For task-specific responders, switch to the sampler profile:

```bash
psyflow-sim path/to/task --config config/config_sampler_sim.yaml
```

The older docs used `config/config_sim.yaml`. That is no longer the current standard.

## Validate the task package

```bash
psyflow-validate path/to/task
```

Validation now covers more than folder existence. The current validator also checks:

- contract compliance
- config rules
- reference-artifact requirements
- README structure requirements
- localization-safe runtime policy for participant-facing text

## How mode-specific config resolution works

Task-local parsing is handled through the `task_options` helpers:

- `build_task_arg_parser()`
- `parse_task_run_options()`
- `resolve_mode()`
- `resolve_config_path()`

This keeps the task entry consistent across `human`, `qa`, and `sim` without spreading path logic across multiple scripts.

## Recommended command sequence

For a fresh task:

```bash
psyflow init my-task
cd my-task
psyflow-run .
psyflow-qa . --config config/config_qa.yaml
psyflow-sim . --config config/config_scripted_sim.yaml
psyflow-validate .
```

That sequence maps well to local development, smoke validation, simulation coverage, and packaging checks.

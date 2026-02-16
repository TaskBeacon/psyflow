# psyflow contracts v0.1.0

These contracts define practical standards for building auditable psyflow/TAPS tasks.

## What is enforced
- Task file/folder skeleton
- `.gitignore` artifact-ignore rules
- Task metadata (`taskbeacon.yaml`)
- Config structure and explicit value/type constraints
  - mandatory/optional/recommended keys and value specs
  - stimulus type standards and asset-backed path conventions
  - smoke-profile rules for `config_qa.yaml` and sim configs (shorter than base but condition-covering)
- Runtime entrypoint pattern (`main.py`)
- Trial runtime pattern (`src/run_trial.py`)
- Responder/sampler plugin standards (`config_scripted_sim.yaml`, `config_sampler_sim.yaml`, `responders/`)
- README metadata rows
- Changelog format
- QA/sim artifact presence conventions

## How to validate
- `psyflow-validate <task_path>`
- `psyflow-validate <task_path> --strict-warn`
- `psyflow-validate <task_path> --json-report <path>`

## Pattern references
- `main_pattern.md`
- `run_trial_pattern.md`

The goal is standardization without overdesign: clear expectations, easy audits, and room for task-specific logic.

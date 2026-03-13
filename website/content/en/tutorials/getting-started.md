# Getting started with a canonical local task

PsyFlow is built around a local, auditable task package. The goal is not to hide PsychoPy, but to keep the repetitive parts of task setup, configuration, QA, and simulation out of your way.

## Install PsyFlow

Use a fresh Python environment when possible.

```bash
pip install psyflow
```

If you need the latest repository state instead of the published package:

```bash
pip install https://github.com/TaskBeacon/psyflow.git
```

## Scaffold a task package

Create a new task from the bundled template:

```bash
psyflow init my-task
```

You can also initialize the current directory in place:

```bash
mkdir my-task
cd my-task
psyflow init
```

The current scaffold is broader than the old docs implied. A typical generated task now includes:

```text
my-task/
├─ main.py
├─ README.md
├─ taskbeacon.yaml
├─ assets/
├─ config/
│  ├─ config.yaml
│  ├─ config_qa.yaml
│  ├─ config_scripted_sim.yaml
│  └─ config_sampler_sim.yaml
├─ outputs/
├─ references/
├─ responders/
└─ src/
   ├─ __init__.py
   └─ run_trial.py
```

That structure matters. `config/`, `references/`, `responders/`, and `taskbeacon.yaml` are part of the modern workflow, especially once QA and validation enter the loop.

## Understand the runtime split

PsyFlow still assumes a task-local `main.py`, but the runtime modes are now explicit:

- `human`: real participant run
- `qa`: smoke-test run with QA artifacts and maturity update path
- `sim`: responder-driven simulation

The framework ships shortcut commands so you do not have to remember mode-specific `python main.py ...` invocations:

```bash
psyflow-run task-path
psyflow-qa task-path
psyflow-sim task-path --config config/config_scripted_sim.yaml
psyflow-validate task-path
```

## Load config the current way

The maintained pattern is:

1. Use `load_config()` to read and normalize config.
2. Build `TaskSettings` from `cfg["task_config"]`.
3. Collect participant info from `cfg["subform_config"]`.
4. Initialize the experiment and preload stimuli.

```python
from psyflow import (
    StimBank,
    SubInfo,
    TaskSettings,
    initialize_exp,
    load_config,
)

cfg = load_config("config/config.yaml")

subform = SubInfo(cfg["subform_config"])
subject_data = subform.collect()

settings = TaskSettings.from_dict(cfg["task_config"])
settings.add_subinfo(subject_data)

win, kb = initialize_exp(settings)
stim_bank = StimBank(win, cfg["stim_config"]).preload_all()
```

Two details here changed relative to the older docs:

- the subject form key is `subform_config`, not `subinfo_config`
- `TaskSettings` now expects the flattened task config that `load_config()` prepares for you

## Keep trial logic in `run_trial.py`

PsyFlow works best when `main.py` orchestrates and `src/run_trial.py` owns the within-trial procedure.

At minimum, your trial code should:

- build or fetch the stimuli it needs
- capture timing and responses through `StimUnit`
- keep participant-facing text config-driven
- avoid burying control logic in anonymous callbacks or scattered globals

## Run the first human pass

From the task root:

```bash
psyflow-run .
```

If you are still iterating quickly, you can also call the task directly:

```bash
python main.py
```

Use the shortcut when you want PsyFlow to handle the task-path resolution consistently.

## Where outputs go now

`TaskSettings` defaults to `./outputs/human`, not the older `./data` examples from the Sphinx docs. Once you call `settings.add_subinfo(...)`, it derives:

- `log_file`
- `res_file`
- `json_file`

from that output root plus `subject_id`, `task_name`, and a timestamp.

## What to do next

- Read [CLI and runtime modes](/tutorials/cli-and-runtime/) before using QA or sim.
- Read [TaskSettings](/tutorials/task-settings/) before adding seeds, weights, or custom paths.
- Read [QA and validation](/tutorials/qa-and-validation/) before you treat a task as release-ready.

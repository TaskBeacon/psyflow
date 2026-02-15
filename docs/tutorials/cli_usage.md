# Command-Line Interface

## Overview

`psyflow` provides one root CLI with subcommands:
- `psyflow init`: scaffold a new PsychoPy task from the bundled template.
- `psyflow qa`: run static QA checks and optional runtime QA.
- `psyflow sim`: run simulation mode with responder plugins.

## Quick Reference

| Command | Purpose | Example |
| --- | --- | --- |
| `psyflow init <name>` | Create a new folder `<name>` with project files | `psyflow init my-new-task` |
| `psyflow init` | Initialize current directory in-place | `cd existing && psyflow init` |
| `psyflow qa <task_dir>` | Run static QA + optional runtime QA | `psyflow qa . --runtime-cmd "python main.py"` |
| `psyflow sim <task_dir>` | Run simulation mode | `psyflow sim . --runtime-cmd "python main.py"` |

## 1. Creating a New Project

```bash
psyflow init my-new-task
```

## 2. In-Place Initialization

```bash
mkdir my-existing-project
cd my-existing-project
psyflow init
```

## 3. QA Runner

```bash
psyflow qa . --runtime-cmd "python main.py"
```

Artifacts are written under `outputs/qa/` (including `qa_report.json`, `static_report.json`, and `contract_report.json`).

## 4. Simulation Runner

```bash
psyflow sim . --runtime-cmd "python main.py" --seed 42 --participant-id sim001
```

Artifacts are written under `outputs/sim/` (including `sim_report.json`, `sim_events.jsonl`, and `qa_trace.csv`).

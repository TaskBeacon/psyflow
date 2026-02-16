# Command-Line Interface

## Overview

`psyflow` provides one root CLI command:
- `psyflow init`: scaffold a new PsychoPy task from the bundled template.

Task execution mode (`human` / `qa` / `sim`) is handled by each task's `main.py`.
For convenience, psyflow also provides task launch shortcuts:
- `psyflow-run <task>`
- `psyflow-qa <task>`
- `psyflow-sim <task>`

## Quick Reference

| Command | Purpose | Example |
| --- | --- | --- |
| `psyflow init <name>` | Create a new folder `<name>` with project files | `psyflow init my-new-task` |
| `psyflow init` | Initialize current directory in-place | `cd existing && psyflow init` |
| `python main.py` | Run task in human mode (default) | `python main.py` |
| `python main.py qa` | Run task in QA mode | `python main.py qa --config config/config_qa.yaml` |
| `python main.py sim` | Run task in simulation mode | `python main.py sim --config config/config_sim.yaml` |
| `psyflow-run <task>` | Run task in human mode via shortcut | `psyflow-run T000006-mid` |
| `psyflow-qa <task>` | Run task in QA mode via shortcut | `psyflow-qa T000006-mid --config config/config_qa.yaml` |
| `psyflow-sim <task>` | Run task in simulation mode via shortcut | `psyflow-sim T000006-mid --config config/config_sim.yaml` |

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

## 3. Run QA Mode

```bash
python main.py qa --config config/config_qa.yaml
```

QA artifacts are written by task runtime config (typically `outputs/qa/`).

## 4. Run Simulation Mode

```bash
python main.py sim --config config/config_sim.yaml
```

Simulation artifacts are written by task runtime config (typically `outputs/sim/`).

## 5. Shortcut Launchers

```bash
psyflow-run T000006-mid
psyflow-qa T000006-mid --config config/config_qa.yaml
psyflow-sim T000006-mid --config config/config_sim.yaml
```

Each shortcut calls the task's `main.py` with explicit mode, so task-local argument/config logic remains authoritative.

`psyflow-qa` also validates QA artifacts and can update maturity metadata on pass:

```bash
psyflow-qa T000006-mid --config config/config_qa.yaml --set-maturity smoke_tested
```

# Command-Line Interface

## Overview

`psyflow` provides one root CLI command:
- `psyflow init`: scaffold a new PsychoPy task from the bundled template.

Task execution mode (`human` / `qa` / `sim`) is handled by each task's `main.py`.

## Quick Reference

| Command | Purpose | Example |
| --- | --- | --- |
| `psyflow init <name>` | Create a new folder `<name>` with project files | `psyflow init my-new-task` |
| `psyflow init` | Initialize current directory in-place | `cd existing && psyflow init` |
| `python main.py` | Run task in human mode (default) | `python main.py` |
| `python main.py qa` | Run task in QA mode | `python main.py qa --config config/config_dev.yaml` |
| `python main.py sim` | Run task in simulation mode | `python main.py sim --config config/config_sim.yaml` |

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
python main.py qa --config config/config_dev.yaml
```

QA artifacts are written by task runtime config (typically `outputs/qa/`).

## 4. Run Simulation Mode

```bash
python main.py sim --config config/config_sim.yaml
```

Simulation artifacts are written by task runtime config (typically `outputs/sim/`).

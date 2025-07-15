## Overview

`psyflow-init` is the command-line interface (CLI) entrypoint for scaffolding new PsychoPy experiments using the built‑in template. It uses Cookiecutter under the hood to generate a standardized project layout, so you can focus on your task logic rather than boilerplate.

Key benefits:

- **Standardization**: Enforce a consistent folder structure across all experiments
- **Rapid setup**: Create a full project scaffold with one command
- **Flexible modes**: Support both new-directory and in-place initialization

## Quick Reference

| Command                      | Purpose                                         | Example                       |
| ---------------------------- | ----------------------------------------------- | ----------------------------- |
| `psyflow-init <name>`        | Create a new folder `<name>` with project files | `psyflow-init my-new-task`    |
| `psyflow-init` (no argument) | Initialize current directory in-place           | `cd existing && psyflow-init` |

## 1. Creating a New Project

To start from scratch, navigate to the parent directory and run:

```bash
psyflow-init my-new-task
```

This will create a new folder `my-new-task/` containing all the necessary files and subdirectories:

```
my-new-task/
├── main.py
├── README.md
├── assets/
├── config/
│   └── config.yaml
├── data/
└── src/
    ├── __init__.py
    ├── run_trial.py
    └── utils.py
```

## 2. In‑Place Initialization

If you already have (or have just created) an empty directory and wish to populate it with the `psyflow` scaffold, run the command without any arguments:

```bash
mkdir my-existing-project
cd my-existing-project
psyflow-init
```

Before copying template files, the CLI checks for existing files or folders with the same names. If any conflicts are found, you will be prompted:

```
⚠ Existing file 'main.py' detected. Overwrite this and all remaining? [y/N]:
```

- Enter `y` to proceed and replace all existing files.
- Enter `n` (or press Enter) to skip that file and continue with others.

This interactive confirmation prevents unintentional data loss during in-place initialization.

## 3. How It Works Internally
1. **Locate template**: Uses `importlib.resources` to find the `psyflow.templates` package and the `cookiecutter-psyflow` folder.
2. **Cookiecutter render**:
   - **New‑directory mode**: Directly runs Cookiecutter into `./<project_name>`.
   - **In‑place mode**: Renders into a temporary directory, then copies files into the current folder.
3. **Cleanup**: In-place mode deletes the temporary render directory when finished.

## Next Steps

Now that you know how to initialize a project, you're ready to start building your experiment:

- **Getting Started**: Follow the [Getting Started tutorial](getting_started.md) to build a simple task from scratch.
- **Learn the Core Concepts**: Dive into the [StimBank](build_stimulus.md), [StimUnit](build_stimunit.md), and [BlockUnit](build_blocks.md) tutorials to understand the key components of PsyFlow.


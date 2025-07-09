# Command-Line Interface (CLI)

`psyflow` includes a command-line interface (CLI) to streamline your project setup. The CLI helps you create a new task with a standardized and recommended project structure, so you can get to the science faster.

## Creating a New Project with `psyflow-init`

The primary command is `psyflow-init`, which scaffolds a new project directory for you.

### Basic Usage

To create a new project, open your terminal, navigate to the directory where you want to create your project, and run:

```bash
psyflow-init my-new-task
```

This command will create a new folder named `my-new-task` inside your current directory. This new folder contains all the necessary files and subdirectories to start your experiment.

### Project Structure

After running the command, you will see the following structure:

```
my-new-task/
├── main.py
├── meta.json
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

This structure helps organize your code, configuration, and data from the very beginning.

### In-Place Initialization

Sometimes, you might have already created a directory for your project and want to initialize it with the `psyflow` structure. You can do this by running `psyflow-init` without any arguments inside that directory:

```bash
mkdir my-existing-folder
cd my-existing-folder
psyflow-init
```

This will populate the `my-existing-folder` with the same project structure without creating a new subdirectory. This is useful for integrating `psyflow` into an existing project structure.
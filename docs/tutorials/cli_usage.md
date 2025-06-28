# Command-Line Tools: Quick Project Setup

## Overview

Psyflow provides command-line tools to help you quickly set up new projects and streamline your workflow. These tools allow you to create new experiments from templates, reducing boilerplate code and ensuring best practices from the start.

The command-line tools solve several common challenges:

- **Project setup**: Create new experiments with the correct structure
- **Boilerplate reduction**: Avoid writing repetitive code for common experiment components
- **Standardization**: Ensure consistent project organization across experiments
- **Time savings**: Get started with a working experiment in seconds

## Key Features

| Feature | Description |
|---------|-------------|
| Project templates | Pre-configured experiment templates for common paradigms |
| Customization | Prompts for experiment name, author, and other metadata |
| Directory structure | Creates organized folder structure for code, data, and resources |
| Configuration files | Generates YAML configuration files with sensible defaults |
| Example code | Includes working example code to demonstrate psyflow usage |

## Quick Reference

| Tool | Purpose | Example |
|------|---------|--------|
| `psyflow-init` | Create a new project from template | `psyflow-init` |
| `psyflow.utils.taps()` | Create a project programmatically | `from psyflow.utils import taps; taps()` |

## Detailed Usage Guide

### 1. Using `psyflow-init`

The `psyflow-init` command is the easiest way to create a new psyflow project. When you run this command, it will guide you through a series of prompts to customize your project.

```bash
# Open a terminal/command prompt and run:
psyflow-init
```

You'll be prompted for information about your project:

```
project_name [My Psyflow Project]: Stroop Task
author_name [Your Name]: Jane Researcher
author_email [your.email@example.com]: jane@university.edu
project_slug [stroop-task]: stroop_task
project_short_description [A short description of the project.]: A Stroop task implementation using psyflow
version [0.1.0]: 
use_pytest [n]: y
command_line_interface [Click]: 
open_source_license [MIT]: 
```

After answering these prompts, `psyflow-init` will create a new directory with your project structure:

```
stroop_task/
├── .gitignore
├── LICENSE
├── README.md
├── config/
│   └── config.yaml
├── data/
├── requirements.txt
├── setup.py
├── stroop_task/
│   ├── __init__.py
│   ├── cli.py
│   └── experiment.py
└── tests/
    ├── __init__.py
    └── test_stroop_task.py
```

### 2. Using `psyflow.utils.taps()`

If you prefer to create a project programmatically or want to integrate project creation into your own scripts, you can use the `taps()` function:

```python
from psyflow.utils import taps

# Create a new project with default settings
taps()

# Or specify custom settings
taps(
    output_dir="my_experiments",
    no_input=True,  # Use defaults without prompting
    extra_context={
        "project_name": "Flanker Task",
        "author_name": "John Researcher",
        "author_email": "john@university.edu",
        "project_slug": "flanker_task",
        "project_short_description": "A Flanker task implementation using psyflow"
    }
)
```

This will create a project with the same structure as `psyflow-init`, but allows for automation and customization in Python code.

### 3. Project Structure

The generated project includes:

#### Configuration Files

```yaml
# config/config.yaml
task_name: stroop_task
window_size: [1024, 768]
fullscreen: false
bg_color: black
data_dir: data

timing:
  fixation_duration: 0.5
  stimulus_duration: 2.0
  feedback_duration: 1.0
  iti: 0.8

subinfo_fields:
  - name: subject_id
    type: int
    constraints:
      min: 101
      max: 999
      digits: 3
  - name: age
    type: int
    constraints:
      min: 18
      max: 100
  - name: gender
    type: choice
    choices: [Male, Female, Non-binary, Prefer not to say]
```

#### Main Experiment File

```python
# stroop_task/experiment.py
from psychopy import visual, core, event
from psyflow import SubInfo, TaskSettings, StimBank, StimUnit, BlockUnit
import yaml
import sys
import os

def main():
    # Load configuration
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Collect subject information
    subinfo = SubInfo({
        "subinfo_fields": config.get("subinfo_fields", [])
    })
    subject_data = subinfo.collect()
    
    if subject_data is None:
        print("Experiment cancelled")
        sys.exit(0)
    
    # Configure task settings
    settings = TaskSettings.from_dict(config)
    settings.add_subinfo(subject_data)
    
    # Create subject directory if it doesn't exist
    os.makedirs(settings.subject_dir, exist_ok=True)
    
    # Create PsychoPy window
    win = visual.Window(
        size=settings.window_size,
        fullscr=settings.fullscreen,
        color=settings.bg_color,
        units="deg"
    )
    
    # Run experiment
    try:
        run_experiment(win, settings)
    finally:
        # Clean up
        win.close()
        core.quit()

def run_experiment(win, settings):
    # Your experiment code here
    pass

if __name__ == "__main__":
    main()
```

#### Command-Line Interface

```python
# stroop_task/cli.py
import click
from . import experiment

@click.command()
def main():
    """Run the Stroop Task experiment."""
    experiment.main()

if __name__ == '__main__':
    main()
```

### 4. Customizing Templates

The project templates are based on [cookiecutter](https://cookiecutter.readthedocs.io/), a powerful Python tool for creating project templates. If you want to customize the default templates or create your own:

1. Find the template directory in your psyflow installation:
   ```python
   import psyflow
   print(psyflow.__path__[0] + "/templates")
   ```

2. Copy the template directory to your own location and modify it.

3. Use your custom template:
   ```python
   from psyflow.utils import taps
   taps(template="path/to/your/custom/template")
   ```

## Complete Example

Here's a complete example of creating and running a new project:

```bash
# Create a new project
psyflow-init

# Navigate to the project directory
cd my_project

# Install the project in development mode
pip install -e .

# Run the experiment
python -m my_project.cli
```

Or using Python:

```python
# Create a new project
from psyflow.utils import taps
taps(output_dir="experiments")

# Run the experiment
import sys
import os

# Add the project to the Python path
sys.path.append(os.path.abspath("experiments/my_project"))

# Import and run the experiment
from my_project import experiment
experiment.main()
```

## Advanced Usage

### Creating Multiple Projects

You can create multiple projects with different configurations:

```python
from psyflow.utils import taps
import os

# Define project configurations
projects = [
    {
        "project_name": "Stroop Task",
        "project_slug": "stroop_task",
        "project_short_description": "A Stroop task implementation"
    },
    {
        "project_name": "Flanker Task",
        "project_slug": "flanker_task",
        "project_short_description": "A Flanker task implementation"
    },
    {
        "project_name": "N-Back Task",
        "project_slug": "n_back_task",
        "project_short_description": "An N-Back task implementation"
    }
]

# Create each project
for project in projects:
    taps(
        output_dir="experiments",
        no_input=True,
        extra_context={
            **project,
            "author_name": "Research Lab",
            "author_email": "lab@university.edu"
        }
    )
```

### Custom Project Structure

You can create a more complex project structure by modifying the generated files:

```python
from psyflow.utils import taps
import os
import shutil

# Create a basic project
taps(
    output_dir="experiments",
    no_input=True,
    extra_context={
        "project_name": "Multi-Task Battery",
        "project_slug": "task_battery"
    }
)

# Add custom directories
project_dir = "experiments/task_battery"
os.makedirs(f"{project_dir}/task_battery/tasks/stroop", exist_ok=True)
os.makedirs(f"{project_dir}/task_battery/tasks/flanker", exist_ok=True)
os.makedirs(f"{project_dir}/task_battery/tasks/n_back", exist_ok=True)
os.makedirs(f"{project_dir}/config/tasks", exist_ok=True)

# Create task-specific config files
with open(f"{project_dir}/config/tasks/stroop.yaml", "w") as f:
    f.write("task_name: stroop\n")

with open(f"{project_dir}/config/tasks/flanker.yaml", "w") as f:
    f.write("task_name: flanker\n")

with open(f"{project_dir}/config/tasks/n_back.yaml", "w") as f:
    f.write("task_name: n_back\n")
```

## Best Practices

1. **Use version control**: Initialize a git repository in your new project directory to track changes.

2. **Customize the README**: Update the generated README.md with specific information about your experiment.

3. **Update requirements**: Add any additional dependencies to requirements.txt.

4. **Organize stimuli**: Create a dedicated directory for stimuli and resources.

5. **Document your code**: Add docstrings and comments to explain your experiment logic.

6. **Use configuration files**: Keep all experiment parameters in the YAML configuration file.

7. **Write tests**: Use the generated tests directory to add unit tests for your experiment.

## Troubleshooting

- **Command not found**: If `psyflow-init` is not found, ensure that psyflow is installed correctly and that your Python scripts directory is in your PATH.

- **Template errors**: If you encounter errors with the template, try updating psyflow to the latest version.

- **Import errors**: If you get import errors when running your project, ensure that it's installed in development mode (`pip install -e .`) or that the project directory is in your Python path.

- **Configuration issues**: If your experiment doesn't load the configuration correctly, check the path to your config.yaml file.

## Next Steps

Now that you know how to create new projects, you can:

- Learn about [TaskSettings](task_settings.md) for configuring your experiment
- Explore [SubInfo](get_subinfo.md) for collecting participant information
- Check out [StimBank](build_stimulus.md) for managing stimuli
- See [StimUnit](build_trialunit.md) for creating individual trials
- Learn about [BlockUnit](build_blocks.md) for organizing trials into blocks

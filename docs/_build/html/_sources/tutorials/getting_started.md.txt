# Getting Started with PsyFlow

## What is PsyFlow?

PsyFlow is a high-level wrapper for PsychoPy designed to streamline the development of cognitive neuroscience experiments. It promotes a **declarative** and **organized** workflow, allowing you to focus more on your experimental logic and less on boilerplate code.

Key features include:

- **Declarative Syntax**: Define stimuli, timings, and task structure in easy-to-read YAML files.
- **Structured Project Layout**: A command-line tool (`psyflow-init`) generates a standardized, organized folder structure for your projects.
- **Simplified API**: High-level classes like `StimUnit` and `BlockUnit` handle the complexities of stimulus presentation, response capturing, and data logging.
- **Extensibility**: Easily integrate hardware triggers (EEG, fMRI) and eye-trackers for advanced use cases.

This guide will walk you through creating a simple reaction time task from scratch, demonstrating the core concepts of PsyFlow.

## Installation

You can install PsyFlow using `pip`.
Python >= 3.10 is required.

#### From PyPI (Recommended)

For the latest stable version, run:

```bash
pip install psyflow
```

#### From GitHub (Development Version)

To get the very latest features and updates, you can install directly from the GitHub repository:

```bash
pip install https://github.com/TaskBeacon/psyflow.git
```

## Step 1: Create a New Project

First, let's create a standardized project structure using the `psyflow-init` command-line tool. Open your terminal, navigate to where you want your project to live, and run:

```bash
psyflow-init my-simple-task
```

This command creates a new folder named `my-simple-task` with the following layout:

```
my-simple-task/
├── main.py
├── README.md
├── config/
│   └── config.yaml
├── data/
└── src/
    ├── __init__.py
    ├── run_trial.py
    └── utils.py
```

This structure separates your configuration (`config/`), core logic (`src/`), and data (`data/`), keeping your project organized.

## Step 2: Define Your Experiment in `config.yaml`

PsyFlow is designed around a declarative approach: you *define* your experiment's components in a YAML file instead of hard-coding them in Python. This makes your experiment easier to read, modify, and share.

Open `config/config.yaml` and replace its contents with the following:

```yaml
# config/config.yaml

# === Subject info form ===
subinfo_fields:
  - name: subject_id
    type: int
    constraints:
      min: 1
      max: 999
  - name: gender
    type: choice
    choices: [Male, Female]

# === Window settings ===
window:
  size: [1280, 720]
  bg_color: gray
  fullscreen: False

# === Task-level settings ===
task:
  task_name: "simple_rt"
  total_blocks: 2
  trial_per_block: 10
  conditions: [go] # We only have one condition in this simple task
  key_list: [space]

# === Stimuli Definitions ===
stimuli:
  instruction:
    type: textbox
    text: |
      Welcome!
      Press the spacebar as fast as you can
      when you see the green circle.
      Press space to begin.
    color: white
    font: Arial
    letterHeight: 0.8

  fixation:
    type: text
    text: "+"
    color: white
    height: 2

  target:
    type: circle
    radius: 3
    fillColor: green
    lineColor: black

# === Timing ===
timing:
  fixation_duration: [0.5, 1.0] # Random duration between 500ms and 1000ms
  response_window: 2.0 # 2 seconds to respond
```

In this file, we've defined:
- A simple subject info form.
- Basic window settings.
- High-level task parameters (2 blocks of 10 trials).
- All our visual stimuli (`instruction`, `fixation`, `target`).
- Timing parameters for the trial.

## Step 3: Write the Trial Logic

Now, let's define what happens in a single trial. Open `src/run_trial.py` and add the following code. This function will be called for every trial in your experiment.

```python
# src/run_trial.py

from psyflow import StimUnit
from functools import partial

def run_trial(win, kb, settings, condition, stim_bank):
    """
    Runs a single trial of the reaction time task.
    """
    # Create a dictionary to store data for this trial
    trial_data = {"condition": condition}

    # Use a partial function to pre-fill common StimUnit arguments
    make_unit = partial(StimUnit, win=win, kb=kb)

    # 1. Show fixation cross
    make_unit(unit_label='fixation') \
        .add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.fixation_duration) \
        .to_dict(trial_data)

    # 2. Show target and capture response
    make_unit(unit_label='target') \
        .add_stim(stim_bank.get("target")) \
        .capture_response(
            keys=settings.key_list,
            duration=settings.response_window
        ) \
        .to_dict(trial_data)

    return trial_data
```
Here, we use `StimUnit` to chain together the events of a trial: show a fixation, then show a target and wait for a keypress. All data (like reaction time) is automatically collected and stored in `trial_data`.

## Step 4: The Main Script

Finally, let's tie everything together in `main.py`. This script will load the configuration, set up the experiment, run the blocks of trials, and save the data.

Replace the contents of `main.py` with this:

```python
# main.py

from psyflow import (
    BlockUnit, StimBank, SubInfo, TaskSettings,
    load_config, initialize_exp, count_down
)
import pandas as pd
from psychopy import core
from functools import partial
from src.run_trial import run_trial

# 1. Load all configurations from the YAML file
cfg = load_config()

# 2. Collect subject information
subform = SubInfo(cfg['subinfo_config'])
subject_data = subform.collect()

# 3. Set up task settings
settings = TaskSettings.from_dict(cfg['task_config'])
settings.add_subinfo(subject_data)

# 4. Set up window and keyboard
win, kb = initialize_exp(settings)

# 5. Load all stimuli defined in the config
stim_bank = StimBank(win, cfg['stim_config']).preload_all()

# 6. Display instructions and wait to start
StimUnit('instruction', win, kb) \
    .add_stim(stim_bank.get('instruction')) \
    .wait_and_continue()

# 7. Run all blocks and trials
all_data = []
for block_i in range(settings.total_blocks):
    count_down(win, 3) # Show a 3-second countdown before the block
    block = BlockUnit(
        block_id=f"block_{block_i}",
        settings=settings,
        window=win,
        keyboard=kb
    ).generate_conditions() \
     .run_trial(partial(run_trial, stim_bank=stim_bank)) \
     .to_dict(all_data)

# 8. Save the collected data
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)
print(f"Data saved to {settings.res_file}")

# 9. Clean up and exit
core.quit()
```

## Step 5: Run Your Experiment!

That's it! Your simple reaction time task is complete. To run it, open your terminal, navigate to the `my-simple-task` directory, and execute:

```bash
python main.py
```

PsychoPy will start, display the subject info form, show the instructions, and then run your task.

## Next Steps

You've now built a basic experiment using PsyFlow's core components. From here, you can explore more advanced features:

- **Define Stimuli**: Learn how to define all your stimuli in one place in the [StimBank tutorial](build_stimulus.md).
- **Build Complex Trials**: Learn how to create more complex trials with multiple stimuli and response types in the [StimUnit tutorial](build_stimunit.md).
- **Organize Blocks**: See the [BlockUnit tutorial](build_blocks.md) to learn how to organize trials into blocks.
- **Send Hardware Triggers**: See the [TriggerSender tutorial](send_trigger.md) to learn how to integrate EEG, fMRI, or eye-tracking triggers.

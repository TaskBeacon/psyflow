# Getting Started with psyflow

Welcome to **psyflow**, a powerful yet lightweight framework for building PsychoPy experiments with modular, chainable components. This guide will walk you through installation, basic setup, and running your first experiment.

## What is psyflow?

Psyflow is a framework that simplifies the creation of cognitive and behavioral experiments by providing:

- **Modular components** that can be easily combined and reused
- **Chainable methods** for intuitive experiment construction
- **EEG/MEG-friendly** trigger handling for precise timing
- **Flexible stimulus management** through code or configuration files
- **Structured data collection** for consistent experimental design

## Installation

### Prerequisites

Before installing psyflow, make sure you have PsychoPy installed:

```bash
pip install psychopy
```

### Installing psyflow

You can install psyflow directly from PyPI:

```bash
pip install psyflow==0.1.1
```

Or if you prefer to work with the source code:

```bash
git clone https://github.com/TaskBeacon/psyflow.git
cd psyflow
pip install -e .
```

## Basic Experiment Structure

A typical psyflow experiment follows these core steps:

1. **Configure experiment settings** using `TaskSettings`
   - Define blocks, trials, conditions, and randomization
   - Set up display parameters and response keys

2. **Collect participant information** with `SubInfo`
   - Create customizable input forms
   - Validate participant data

3. **Build stimuli** using `StimBank`
   - Register visual and auditory stimuli
   - Load stimuli from configuration files or code

4. **Define triggers** with `TriggerSender`
   - Set up EEG/MEG compatible triggers
   - Configure timing and callbacks

5. **Create trials** with `StimUnit`
   - Combine stimuli into trial sequences
   - Add response handling and timing control

6. **Organize blocks** using `BlockUnit`
   - Group trials into experimental blocks
   - Manage condition balancing and randomization

7. **Run the experiment and collect data**
   - Execute trials and blocks
   - Save results in structured formats

## Step-by-Step Guide

### 1. Configure Your Task

The `TaskSettings` class provides a centralized way to manage experiment parameters:

```python
from psyflow import TaskSettings

# Create settings from a dictionary
config = {
    "total_blocks": 2,                  # Number of experimental blocks
    "total_trials": 20,                # Total trials across all blocks
    "seed_mode": "same_within_sub",    # Randomization strategy
    "key_list": ["left", "right"],     # Response keys
    "conditions": ["reward", "neutral"], # Experimental conditions
    "bg_color": "black",               # Window background color
    "size": [1920, 1080],              # Window size in pixels
    "fullscreen": True                 # Fullscreen mode
}
settings = TaskSettings.from_dict(config)
```

After collecting participant information, you can add it to your settings:

```python
# Add subject information to generate file paths and seeds
settings.add_subinfo({"subject_id": "001", "session_name": "A"})
```

This automatically creates:
- `settings.block_seed`: Random seeds for each block
- `settings.log_file`: Path for PsychoPy log file
- `settings.res_file`: Path for results data file

### 2. Collect Participant Information

The `SubInfo` class creates customizable GUI dialogs for collecting participant data:

```python
import yaml
from psyflow import SubInfo

# Load configuration from YAML file
with open("subinfo.yaml") as f:
    config = yaml.safe_load(f)

# Example YAML configuration:
# subinfo_fields:
#   - name: subject_id
#     type: int
#     constraints: {min: 101, max: 999, digits: 3}
#   - name: age
#     type: int
#     constraints: {min: 18, max: 100}
#   - name: condition
#     type: choice
#     choices: [control, experimental]
# subinfo_mapping:
#   subject_id: "Participant ID"
#   age: "Age (years)"
#   condition: "Condition Group"

# Create collector and show dialog
collector = SubInfo(config)
subinfo = collector.collect()  # Opens GUI dialog

# Result example: {'subject_id': '001', 'age': 25, 'condition': 'control'}
```

Pass this information to your settings:

```python
settings.add_subinfo(subinfo)
```

### 3. Build Your Stimuli

The `StimBank` class provides a flexible way to manage stimuli:

```python
from psyflow import StimBank
from psychopy.visual import TextStim, Circle, Window

# Create PsychoPy window
win = Window(size=settings.size, fullscr=settings.fullscreen, 
             color=settings.bg_color, units=settings.units)

# Create stimulus bank
stim_bank = StimBank(win)

# Method 1: Register stimuli using decorators
@stim_bank.define("fixation")
def make_fixation(win):
    return TextStim(win, text="+", color="white", height=1.0)

@stim_bank.define("feedback_correct")
def make_feedback(win):
    return TextStim(win, text="Correct!", color="green", height=0.8)

# Method 2: Register stimuli from dictionary/YAML
stim_bank.add_from_dict({
    "target": {
        "type": "circle",
        "radius": 0.5,
        "fillColor": "red",
        "lineColor": "white"
    },
    "cue": {
        "type": "text",
        "text": ">",
        "color": "yellow",
        "height": 1.2
    }
})

# Preload all stimuli (optional but recommended)
stim_bank.preload_all()

# Retrieve stimuli when needed
fixation = stim_bank.get("fixation")
target = stim_bank.get("target")
```

### 4. Set Up Triggers

The `TriggerSender` class handles EEG/MEG trigger codes:

```python
import yaml
from psyflow import TriggerSender

# Load trigger codes from YAML
with open("triggers.yaml") as f:
    triggers = yaml.safe_load(f)

# Example YAML content:
# fix_onset: 1
# target_onset: 2
# resp_L: 11
# resp_R: 12
# timeout: 99

# For real hardware (e.g., parallel port)
# import parallel
# port = parallel.ParallelPort(address=0x0378)  # Adjust address as needed
# sender = TriggerSender(lambda code: port.write(bytes([code])))

# For development/testing (mock mode)
sender = TriggerSender(mock=True)

# Test trigger
sender.send(triggers["fix_onset"])  # Prints: [MockTrigger] Sent code: 1
```

### 5. Create & Run a Trial

The `StimUnit` class manages individual trials:

```python
from psychopy.hardware.keyboard import Keyboard
from psyflow import StimUnit

# Create keyboard for responses
kb = Keyboard()

# Create trial unit
trial = StimUnit("trial_1", win, kb, triggersender=sender)

# Configure trial using chainable methods
trial \
    .add_stim(fixation, target) \
    .on_start(lambda unit: unit.send_trigger(triggers["fix_onset"])) \
    .show_stim(fixation, duration=0.5) \
    .show_stim(target, duration=1.0, trigger=triggers["target_onset"]) \
    .capture_response(
        keys=["left", "right"],
        duration=2.0,
        onset_trigger=triggers["target_onset"],
        response_trigger={
            "left": triggers["resp_L"], 
            "right": triggers["resp_R"]
        },
        timeout_trigger=triggers["timeout"],
        correct_keys=["left"],
    ) \
    .on_end(lambda unit: print(f"Response: {unit.state}")) \
    .run(frame_based=True)

# Access trial results
print(f"RT: {trial.state.get('rt')}")
print(f"Correct: {trial.state.get('correct')}")
```

### 6. Organizing Blocks

The `BlockUnit` class helps manage multiple trials:

```python
from psyflow import BlockUnit

# Create a block
block = BlockUnit(
    block_id="block_1",
    block_idx=0,
    settings=settings,
    window=win,
    keyboard=kb
)

# Generate balanced conditions
block.generate_conditions(
    condition_labels=settings.conditions,
    order="random"
)

# Define trial execution function
def run_trial(condition, trial_idx, block):
    # Create trial
    trial = StimUnit(f"trial_{trial_idx}", win, kb, triggersender=sender)
    
    # Configure based on condition
    if condition == "reward":
        target_color = "gold"
    else:  # neutral
        target_color = "blue"
    
    # Update stimulus
    target = stim_bank.rebuild("target", fillColor=target_color)
    
    # Run trial (simplified)
    trial \
        .add_stim(fixation, target) \
        .show_stim(fixation, duration=0.5) \
        .show_stim(target, duration=1.0) \
        .capture_response(keys=settings.key_list, duration=2.0) \
        .run()
    
    # Return trial data
    return trial.to_dict()

# Run all trials in the block
block.run_trials(run_trial)

# Get block results
block_results = block.to_dict()
```

### 7. Putting It All Together

Here's how to combine everything into a complete experiment:

```python
# Initialize experiment components
settings = TaskSettings.from_dict(config)
subinfo = SubInfo(subinfo_config).collect()
settings.add_subinfo(subinfo)

win = Window(size=settings.size, fullscr=settings.fullscreen, 
             color=settings.bg_color, units=settings.units)
kb = Keyboard()

stim_bank = StimBank(win)
# ... register stimuli ...

sender = TriggerSender(mock=True)

# Run blocks
all_results = []
for b_idx in range(settings.total_blocks):
    # Create block
    block = BlockUnit(
        block_id=f"block_{b_idx+1}",
        block_idx=b_idx,
        settings=settings,
        window=win,
        keyboard=kb
    )
    
    # Generate conditions
    block.generate_conditions(condition_labels=settings.conditions)
    
    # Add block start/end hooks
    block.on_start(lambda b: win.flip())
    block.on_end(lambda b: win.flip())
    
    # Run all trials
    block.run_trials(run_trial)
    
    # Save block results
    block.to_dict(target_list=all_results)
    
    # Show break between blocks (except after last block)
    if b_idx < settings.total_blocks - 1:
        break_text = TextStim(win, text="Take a break. Press space to continue.", 
                             color="white", height=0.8)
        break_text.draw()
        win.flip()
        kb.waitKeys(keyList=["space"])

# Save all results
import pandas as pd
df = pd.DataFrame(all_results)
df.to_csv(settings.res_file, index=False)

# Clean up
win.close()
```

## Next Steps

Congratulations! You've learned the basics of creating experiments with psyflow. To dive deeper into specific components, check out these tutorials:

- [Collecting Participant Information](get_subinfo.md)
- [Configuring Task Settings](task_settings.md)
- [Building Experimental Blocks](build_blocks.md)
- [Creating Trial Units](build_trialunit.md)
- [Managing Stimuli](build_stimulus.md)
- [Sending EEG/MEG Triggers](send_trigger.md)
- [Using the Command Line Interface](cli_usage.md)

Happy experimenting!

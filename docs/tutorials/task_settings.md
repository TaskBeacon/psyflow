# TaskSettings: Configuring Your Experiment

## Overview

The `TaskSettings` class provides a centralized way to manage experiment configuration, including collected subject information, data paths, timing parameters, window settings, and more. It helps standardize experiment setup and ensures consistent configuration across different parts of the experiment. 

Under the hood, `TaskSettings` is used throughout your code wherever you need to read or write experiment parameters. For example:  
- In `run_trial.py`, to retrieve the duration of a specific stimulus  
- During block creation in `main.py`, to determine the number of blocks and trials and to seed the randomization of conditions  



## Key Features

| Feature                | Description                                                                          |
|------------------------|--------------------------------------------------------------------------------------|
| Dictionary initialization | Create settings from Python dictionaries or YAML files                             |
| Subject integration    | Incorporate collected subject info for per-subject seeds, file names, and paths      |
| Path & directory generation | Automatically create output directories and construct timestamped log/CSV/JSON paths |
| Seed management        | Flexible seeding strategies (`same_across_sub` or `same_within_sub`) with auto-generated per-block seeds |
| Dynamic extension      | Load extra, unknown config keys via `from_dict()`                                    |
| JSON export            | Save the full `TaskSettings` to JSON (`save_to_json()`) for archiving or analysis    |
| Human-readable repr    | Clean `__repr__()` for easy inspection or logging of all current settings            |
| Default values         | Sensible built-in defaults for window, timing, blocks/trials, keys, etc.             |


## Quick Reference

| Purpose | Method | Example |
|---------|--------|--------|
| Initialize from dict | `TaskSettings.from_dict(config)` | `settings = TaskSettings.from_dict(config)` |
| Add subject info | `.add_subinfo(subject_data)` | `settings.add_subinfo(subject_data)` |
| Access setting | Dot notation | `settings.window_size` |
| Get all settings | `.to_dict()` | `all_settings = settings.to_dict()` |

## Detailed Usage Guide

### 1. Creating TaskSettings

#### Option A: From a Dictionary
在实际使用时，我们使用load_config方法从配置文件中加载配置,从而获得相关的设置
```python
from psyflow import TaskSettings

config = {
    "task_name": "stroop",
    "window_size": [1024, 768],
    "fullscreen": False,
    "bg_color": "black",
    "data_dir": "data",
    "block_seed": 42,
    "trial_seed": 43,
    "timing": {
        "fixation_duration": 0.5,
        "stimulus_duration": 2.0,
        "feedback_duration": 1.0,
        "iti": 0.8
    }
}

settings = TaskSettings.from_dict(config)
```

#### Option B: From a YAML File

```yaml
# config.yaml
task_name: stroop
window_size: [1024, 768]
fullscreen: false
bg_color: black
data_dir: data
block_seed: 42
trial_seed: 43
timing:
  fixation_duration: 0.5
  stimulus_duration: 2.0
  feedback_duration: 1.0
  iti: 0.8
```

```python
import yaml
from psyflow import TaskSettings

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

settings = TaskSettings.from_dict(config)
```

### 2. Adding Subject Information
被试信息是必须的，这涉及被试specific的配置，比如被试ID，被试的性别，被试的出生年份等等。这将用于生成相关的存储文件的名称，包括json, log和csv文件的信息
Integrating subject information allows `TaskSettings` to create subject-specific paths and seeds:

```python
from psyflow import SubInfo, TaskSettings
import yaml

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Collect subject information
subinfo = SubInfo({
    "subinfo_fields": config.get("subinfo_fields", [])
})
subject_data = subinfo.collect()

if subject_data is None:
    print("Experiment cancelled")
    import sys
    sys.exit(0)

# Create TaskSettings with subject info
settings = TaskSettings.from_dict(config)
settings.add_subinfo(subject_data)

# Now you have subject-specific paths
print(f"Data will be saved to: {settings.res_file}")
```

### 3. Accessing Settings

You can access settings using dot notation, which is cleaner and more intuitive than dictionary access:

```python
# Access window settings
win_size = settings.window_size
fullscreen = settings.fullscreen
bg_color = settings.bg_color

# Access timing parameters
fixation_time = settings.timing.fixation_duration
stimulus_time = settings.timing.stimulus_duration

# Access paths
data_dir = settings.data_dir
res_file = settings.res_file  # Only available after add_subinfo()
```

### 4. Path Management

`TaskSettings` automatically generates several useful paths based on your configuration and subject information:

```python
# Basic paths (available immediately)
print(f"Data directory: {settings.data_dir}")

# Subject-specific paths (available after add_subinfo())
print(f"Subject directory: {settings.subject_dir}")
print(f"Results file: {settings.res_file}")
print(f"Log file: {settings.log_file}")
```

By default, paths follow this structure:

```
data_dir/
  └── subject_id/
      ├── subject_id_results.csv  (res_file)
      └── subject_id_log.txt      (log_file)
```

### 5. Seed Management

`TaskSettings` helps manage random seeds for reproducible experiments:

```python
# Set seeds in configuration
config = {
    "task_name": "stroop",
    "block_seed": 42,  # For block-level randomization
    "trial_seed": 43   # For trial-level randomization
}

settings = TaskSettings.from_dict(config)

# Access seeds for use in your experiment
block_seed = settings.block_seed
trial_seed = settings.trial_seed

# Use seeds with random number generators
import random
import numpy as np

# For block randomization
block_rng = random.Random(block_seed)
block_conditions = ["condition_a", "condition_b", "condition_c"]
block_rng.shuffle(block_conditions)

# For trial randomization
trial_rng = np.random.RandomState(trial_seed)
trial_jitter = trial_rng.uniform(-0.1, 0.1, 100)  # 100 jittered values
```

## Complete Example

Here's a complete example showing how to use `TaskSettings` in an experiment:

```python
from psychopy import visual, core
from psyflow import SubInfo, TaskSettings, StimBank, StimUnit
import yaml
import sys
import os

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Step 1: Collect subject information
subinfo = SubInfo({
    "subinfo_fields": config.get("subinfo_fields", [])
})
subject_data = subinfo.collect()

if subject_data is None:
    print("Experiment cancelled")
    sys.exit(0)

# Step 2: Configure task settings
settings = TaskSettings.from_dict(config)
settings.add_subinfo(subject_data)

# Create subject directory if it doesn't exist
os.makedirs(settings.subject_dir, exist_ok=True)

# Step 3: Create PsychoPy window
win = visual.Window(
    size=settings.window_size,
    fullscr=settings.fullscreen,
    color=settings.bg_color,
    units="deg"
)

# Step 4: Create stimulus bank
stim_bank = StimBank()

# Register stimuli
stim_bank.register({
    "fixation": visual.TextStim(win, text="+", height=1.0),
    "instructions": visual.TextStim(win, text="Press any key to begin", height=0.8),
    "feedback_correct": visual.TextStim(win, text="Correct!", height=0.8, color="green"),
    "feedback_incorrect": visual.TextStim(win, text="Incorrect", height=0.8, color="red")
})

# Step 5: Run a simple trial
trial = StimUnit(win)
trial.add(stim_bank.get("instructions"))
trial.show()

# Wait for keypress
from psychopy.event import waitKeys
waitKeys()

# Run a trial with timing from settings
fixation_trial = StimUnit(win)
fixation_trial.add(stim_bank.get("fixation"))
fixation_trial.show(duration=settings.timing.fixation_duration)

# Clean up
win.close()
core.quit()
```

## Advanced Usage

### Nested Configuration

`TaskSettings` supports nested configuration structures, which helps organize related settings:

```python
config = {
    "task_name": "flanker",
    "window": {
        "size": [1024, 768],
        "fullscreen": False,
        "color": "gray",
        "units": "deg"
    },
    "timing": {
        "fixation": 0.5,
        "stimulus": 1.5,
        "response_window": 2.0,
        "feedback": 1.0,
        "iti": [0.8, 1.2]  # Range for jittered ITI
    },
    "stimuli": {
        "sizes": {
            "fixation": 1.0,
            "target": 2.0,
            "feedback": 1.5
        },
        "colors": {
            "correct": "green",
            "error": "red",
            "neutral": "white"
        }
    }
}

settings = TaskSettings.from_dict(config)

# Access nested settings
win_size = settings.window.size
fixation_size = settings.stimuli.sizes.fixation
correct_color = settings.stimuli.colors.correct
```

### Custom Path Generation

You can customize how paths are generated by subclassing `TaskSettings`:

```python
class CustomTaskSettings(TaskSettings):
    def _generate_paths(self):
        # Call the parent method first
        super()._generate_paths()
        
        # Add custom paths
        if hasattr(self, "subject_id"):
            # Create a path for eye-tracking data
            self.eyetrack_file = os.path.join(
                self.subject_dir, 
                f"{self.subject_id}_eyetracking.csv"
            )
            
            # Create a path for physiological data
            self.physio_dir = os.path.join(
                self.subject_dir, 
                "physio"
            )
            
            # Create a path for stimuli presented to this subject
            self.stim_log = os.path.join(
                self.subject_dir,
                f"{self.subject_id}_stimuli.json"
            )
```

### Dynamic Settings Updates

You can update settings dynamically during an experiment:

```python
# Start with default settings
settings = TaskSettings.from_dict(config)

# Update based on subject performance
def adjust_difficulty(settings, accuracy):
    """Adjust task difficulty based on accuracy."""
    if accuracy > 0.85:  # Too easy
        settings.timing.stimulus_duration *= 0.8  # Reduce stimulus time
        settings.difficulty_level = "hard"
    elif accuracy < 0.65:  # Too hard
        settings.timing.stimulus_duration *= 1.2  # Increase stimulus time
        settings.difficulty_level = "easy"
    else:
        settings.difficulty_level = "medium"
    
    return settings

# Use in experiment
block_accuracy = 0.90  # Example accuracy from a block
settings = adjust_difficulty(settings, block_accuracy)
print(f"New difficulty: {settings.difficulty_level}")
print(f"New stimulus duration: {settings.timing.stimulus_duration}")
```

## Best Practices

1. **Use YAML for configuration**: Store settings in YAML files for easy editing without changing code.

2. **Group related settings**: Use nested structures to organize related settings (e.g., `window`, `timing`, `stimuli`).

3. **Set reasonable defaults**: Provide sensible default values for common parameters.

4. **Document your settings**: Include comments in YAML files to explain what each setting does.

5. **Use consistent naming**: Follow a consistent naming convention for settings.

6. **Validate critical settings**: Check that essential settings are present and valid.

7. **Keep settings separate from code**: Avoid hardcoding values that might need to change.

## Troubleshooting

- **AttributeError**: If you get an `AttributeError` when accessing a setting, check that the setting exists in your configuration dictionary.

- **Path issues**: Ensure that `data_dir` is set correctly and that you have write permissions for that directory.

- **Subject-specific paths**: Remember that `res_file`, `log_file`, and other subject-specific paths are only available after calling `add_subinfo()`.

- **Type errors**: Ensure that settings have the expected types (e.g., `window_size` should be a list of two integers).

## Next Steps

Now that you understand how to use `TaskSettings`, you can:

- Learn about [SubInfo](get_subinfo.md) for collecting participant information
- Explore [StimBank](build_stimulus.md) for managing stimuli
- Check out [BlockUnit](build_blocks.md) for organizing trials into blocks
- See [StimUnit](build_trialunit.md) for creating individual trials
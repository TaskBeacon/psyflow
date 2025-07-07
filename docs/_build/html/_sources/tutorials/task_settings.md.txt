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
| Access setting | Dot notation | `settings.size` |
| Get all settings | `.to_dict()` | `all_settings = settings.to_dict()` |


## Detailed Usage Guide

### 1. Creating TaskSettings

#### Option A: From a YAML File

1. **Define** separate sections in `config.yaml`:
   ```yaml
   window:
     size: [1920, 1080]
     fullscreen: true
     units: "deg"
     bg_color: "gray"

   task:
     task_name: "stroop"
     total_blocks: 2
     total_trials: 40
     conditions: ["congruent","incongruent"]
     key_list: ["space"]
     seed_mode: "same_across_sub"

   timing:
     fixation_duration: [0.5, 0.7]
     cue_duration: 0.3
     stimulus_duration: 1.0
     feedback_duration: 0.5
   ```
2. **Load** and **flatten**:
   ```python
   import yaml
   from psyflow import TaskSettings

   with open('config.yaml', 'r') as f:
       cfg = yaml.safe_load(f)

   merged = {**cfg.get('window', {}), **cfg.get('task', {}), **cfg.get('timing', {})}
   settings = TaskSettings.from_dict(merged)
   ```

> **Note:** `window`, `task`, and `timing` are the primary sections for `TaskSettings`. They must be flattened into a single dict passed to `from_dict()`. Other configurations (e.g., `triggers`, `controllers`) can be added as nested attributes:
>
> ```python
> settings.triggers = cfg['trigger_config']
> ```
>
> The `load_config()` utility often auto-flattens `window`, `task`, and `timing` into `cfg['task_config']`, so you can initialize directly:
>
> ````python
> cfg = load_config('config.yaml')
> settings = TaskSettings.from_dict(cfg['task_config'])
> ```python
> cfg = load_config('config.yaml')
> settings = TaskSettings.from_dict(cfg['task_config'])
> ````

#### Option B: From a Dictionary

You can initialize `TaskSettings` directly from Python dictionaries in two ways:

1. **Flat dictionary**: merge all parameters (including custom fields) into a single dict.
2. **Nested sections**: keep logical subsections (e.g., `window`, `task`, `timing`) as nested dicts, then flatten at call time.

**Example YAML sections** (as reference):

```yaml
window:
  size: [1920, 1080]
  fullscreen: true
  units: "deg"
  bg_color: "gray"

task:
  task_name: "stroop"
  total_blocks: 2
  total_trials: 40
  conditions: ["congruent", "incongruent"]
  key_list: ["space"]
  seed_mode: "same_across_sub"

timing:
  fixation_duration: [0.5, 0.7]
  cue_duration: 0.3
  stimulus_duration: 1.0
  feedback_duration: 0.5
```

##### 1. Flat dict approach

```python
from psyflow import TaskSettings

# Merge all settings into one dict
config_flat = {
    # window settings
    'size': [1920, 1080],
    'fullscreen': True,
    'units': 'deg',
    'bg_color': 'gray',

    # task settings
    'task_name': 'stroop',
    'total_blocks': 2,
    'total_trials': 40,
    'conditions': ['congruent', 'incongruent'],
    'key_list': ['space'],
    'seed_mode': 'same_across_sub',

    # timing settings
    'fixation_duration': [0.5, 0.7],
    'cue_duration': 0.3,
    'stimulus_duration': 1.0,
    'feedback_duration': 0.5,

    # custom nested field
    'trigger_config': {'onset': 5, 'offset': 6}
}

settings = TaskSettings.from_dict(config_flat)
print(settings)
print('Trigger:', settings.trigger_config)
```

##### 2. Nested dict approach

```python
from psyflow import TaskSettings

# Keep sections nested for readability
config_nested = {
    'window': {
        'size': [1920, 1080],
        'fullscreen': True,
        'units': 'deg',
        'bg_color': 'gray'
    },
    'task': {
        'task_name': 'stroop',
        'total_blocks': 2,
        'total_trials': 40,
        'conditions': ['congruent', 'incongruent'],
        'key_list': ['space'],
        'seed_mode': 'same_across_sub'
    },
    'timing': {
        'fixation_duration': [0.5, 0.7],
        'cue_duration': 0.3,
        'stimulus_duration': 1.0,
        'feedback_duration': 0.5
    },
    'trigger_config': {
        'onset': 5,
        'offset': 6
    }
}

# Flatten nested sections when initializing
config_flat = {
    **config_nested['window'],
    **config_nested['task'],
    **config_nested['timing'],
    'trigger_config': config_nested['trigger_config']
}

settings = TaskSettings.from_dict(config_flat)
print(settings.conditions)
print(settings.fixation_duration)
print(settings.trigger_config)
```

In both cases, `from_dict()` will apply known fields and attach unknown keys (like `trigger_config`) as attributes on the `settings` object.

### 2. Adding Subject Information

Provide a dict with at least `subject_id` (others optional) to:

- Validate inputs
- Derive subject‑specific seed (in `same_within_sub` mode)
- Create output directory
- Construct timestamped file names

```python
subinfo = {'subject_id': 'S01', 'age': 24, 'gender': 'F'}
settings.add_subinfo(subinfo)
```

### 3. Path Management Path Management

After `add_subinfo()`, these attributes are set:

| Attribute   | Description                                  |
| ----------- | -------------------------------------------- |
| `save_path` | Base directory (default `./data`)            |
| `log_file`  | Full path to `.log` for PsychoPy logs        |
| `res_file`  | Full path to `.csv` with trial‐level results |
| `json_file` | Full path to `.json` dumping all settings    |

After calling `settings.add_subinfo(subinfo)`, you’ll see console output and the generated file paths:

```python
settings.add_subinfo(subinfo)
# [INFO] Created output directory: ./data

print('Log file:', settings.log_file)
# Log file: ./data/sub-S01_task_flanker_20250706_094730.log

print('Results file:', settings.res_file)
# Results file: ./data/sub-S01_task_flanker_20250706_094730.csv

print('Config JSON file:', settings.json_file)
# Config JSON file: ./data/sub-S01_task_flanker_20250706_094730.json
```

**Example directory layout**:

```
./data/
└─ S01/
   ├─ sub-S01_task-stroop_20250706_091500.log
   ├─ sub-S01_task-stroop_20250706_091500.csv
   └─ sub-S01_task-stroop_20250706_091500.json
```

### 4. Seed Management

`TaskSettings` uses three related fields to control randomization and reproducibility:

- `overall_seed`(integer, default 2025): the base seed for generating block-specific seeds. Change this value in your config or at runtime to alter the overall randomization pattern.
- `block_seed`(list of ints or `None`): one seed per block, used to initialize block-level randomization (e.g., shuffling condition order). If unset, seeds are generated automatically based on `overall_seed` and `seed_mode`.
- `seed_mode`(`"same_across_sub"` or `"same_within_sub"`)``: determines whether block seeds are shared across participants or personalized per subject.

#### Controlling condition order per block

Each entry in `block_seed` seeds the random number generator (RNG) for that block. By assigning a specific seed to each block, you ensure that:

1. **Deterministic shuffle:** The order in which `settings.conditions` are shuffled in block *n* is fully determined by `block_seed[n]`.
2. **Reproducible blocks:** Re-running the experiment with the same seeds will recreate identical block-level condition orders.

Example:

```python
import random
for i, seed in enumerate(settings.block_seed):
    rng = random.Random(seed)
    block_order = settings.conditions.copy()
    rng.shuffle(block_order)
    print(f"Block {i+1} order:", block_order)
```

#### How to override seeds

- **Via config**: set `overall_seed` in your dict or YAML before initializing:
  ```python
  config = {'overall_seed': 9999, 'seed_mode': 'same_across_sub', ...}
  settings = TaskSettings.from_dict(config)
  ```
- **At runtime**: regenerate block seeds from a new base:
  ```python
  settings.set_block_seed(123456)
  print('New block seeds:', settings.block_seed)
  ```

#### Choosing a seed mode

- `same_across_sub` (default)\
  All participants share the same `block_seed` list generated from `overall_seed`. Use this when you need identical block randomization across the group (e.g., counterbalancing at the cohort level).

- `same_within_sub`\
  Each subject receives a unique set of block seeds derived from their `subject_id`, ensuring reproducible yet individualized randomization. This approach:

  - **Reproducibility:** Allows precise reconstruction of any subject’s experimental sequence from their ID.
  - **Distributed order effects:** Varies block order across participants when group-level consistency isn’t required.

> **Note:** The final `block_seed` list is stored in the `settings` object and included in the JSON file produced by `save_to_json()`. This makes debugging and post-hoc analyses transparent, as you can see exactly which seeds were used for each block.

### 5. Accessing Settings

Many psyflow utilities and your custom trial functions will read values directly from the `settings` object. Use Python’s attribute access (or `getattr`) to pull in display parameters, timing values, and custom triggers without boilerplate.

#### Window & Monitor Setup

Many experiments use the same monitor and window settings. Below are two ways to apply those values from `settings`:

**Example 1: Direct dot‐attribute access**

```python
from psychopy import monitors, visual

# Dot access assumes the attribute exists
mon = monitors.Monitor('tempMonitor')
mon.setWidth(settings.monitor_width_cm)
mon.setDistance(settings.monitor_distance_cm)
mon.setSizePix(settings.size)

win = visual.Window(
    size=settings.size,
    fullscr=settings.fullscreen,
    screen=settings.screen,
    monitor=mon,
    units=settings.units,
    color=settings.bg_color,
    gammaErrorPolicy='ignore'
)
```

**Example 2: Safe access with**

```python
from psychopy import monitors, visual

# getattr provides a fallback in case a field is missing
mon = monitors.Monitor('tempMonitor')
mon.setWidth(getattr(settings, 'monitor_width_cm', 60))
mon.setDistance(getattr(settings, 'monitor_distance_cm', 65))
mon.setSizePix(getattr(settings, 'size', [1024, 768]))

win = visual.Window(
    size=getattr(settings, 'size', [1024, 768]),
    fullscr=getattr(settings, 'fullscreen', False),
    screen=getattr(settings, 'screen', 0),
    monitor=mon,
    units=getattr(settings, 'units', 'pix'),
    color=getattr(settings, 'bg_color', [0, 0, 0]),
    gammaErrorPolicy='ignore'
)
```

> **Tip:** Using `getattr(settings, 'attr', default)` lets you specify a fallback when a setting may not exist.: **Using `getattr(settings, 'attr', default)`** lets you specify a fallback when a setting may not exist.

#### Accessing Timing & Triggers in `run_trial.py`

Below is a concise snippet showing how to pull timing values and onset triggers from `settings` in your trial code:

```python
# run_trial.py (concise)
def run_trial(settings, stim_bank, condition):
    # Retrieve cue duration and onset trigger
    duration = settings.cue_duration
    trigger  = settings.triggers.get(f"{condition}_cue_onset")

    # Present the cue stimulus
    cue_stim = stim_bank.get(f"{condition}_cue")
    cue_stim.show(duration=duration, onset_trigger=trigger)

    # ... other trial units follow similarly ...
```

## Design considerations for this class

TaskSettings groups the most essential experiment parameters—display (`window`), structure (`task`), and timing—into top-level attributes for direct, predictable access and sensible defaults. Parameters that are used less frequently (such as `triggers` or controller settings) can be supplied as nested dictionaries and retrieved only when needed, keeping the core settings clean. Stimulus-specific configurations (e.g., images, sounds) are managed separately by the `StimBank`, allowing the settings class to focus on overall experiment flow rather than individual asset details.

 `TaskSettings` is designed for extensibility and reproducibility. Unknown keys passed to `from_dict()` become dynamic attributes, so you can tailor settings without modifying the class source. Dual seeding modes (`same_across_sub`, `same_within_sub`) let you choose between group‐level consistency or subject‐specific randomness. Finally, the combination of a concise `__repr__()`, JSON export of all settings, and built‑in directory/file management ensures that your experiment’s configuration is transparent, easy to log, and straightforward to debug.

## Next Steps

Now that you understand how to use `TaskSettings`, you can:

- Learn about [SubInfo](get_subinfo.md) for collecting participant information
- Explore [StimBank](build_stimulus.md) for managing stimuli
- Check out [BlockUnit](build_blocks.md) for organizing trials into blocks
- See [StimUnit](build_trialunit.md) for creating individual trials
# Utility Functions

The `psyflow.utils` module provides a collection of helper functions designed to simplify common tasks and reduce boilerplate code in your PsychoPy experiments.

Here are some of the most useful functions you might need.

## `load_config()`

This function is your primary tool for loading experiment settings. It reads your `config.yaml` file and organizes the settings into a structured Python dictionary.

```python
from psyflow.utils import load_config

# Load the default config file (config/config.yaml)
settings = load_config()

# Access different parts of the configuration
task_settings = settings['task_config']
stimuli = settings['stim_config']
window_settings = settings['task_config'] 

print(f"The experiment will run in a window of size {window_settings['size']}.")
```
`load_config` intelligently separates your raw configuration into different sections like `task_config`, `stim_config`, `subform_config`, etc., making it easy to access the settings you need.

If you want to fail fast on missing top-level sections or obvious type mismatches, you can enable lightweight validation:

```python
from psyflow.utils import load_config

cfg = load_config(
    "config/config.yaml",
    validate=True,
    required_sections=["window", "task", "timing"],
)
```

## `validate_config()`

`validate_config()` is the underlying helper used by `load_config(..., validate=True, ...)`. It performs minimal top-level checks (intentionally not a full schema validator).

## `initialize_exp()`

Setting up the PsychoPy window, keyboard, and log file is a repetitive task. `initialize_exp()` handles all of it for you in a single function call. It takes a configuration object and returns the initialized `Window` and `Keyboard` objects.

```python
from psyflow.utils import load_config, initialize_exp
from psyflow.TaskSettings import TaskSettings

# 1. Load configuration
config = load_config()

# 2. Create a TaskSettings object (or any object with attributes)
settings = TaskSettings.from_dict(config['task_config'])

# 3. Initialize the experiment
win, kb = initialize_exp(settings)

# Now you are ready to run your experiment!
win.flip()
# ... your experiment logic ...
win.close()
```
This function also sets up a global quit key (`Ctrl+Q`) and configures logging to save your data.

## `count_down()`

A countdown is a common way to start a trial or a block. `count_down()` displays a simple numeric countdown on the screen.

```python
from psyflow.utils import count_down

# Assuming 'win' is your PsychoPy window from initialize_exp()
# win, _ = initialize_exp(settings) # if you need to run this snippet
# count_down(win, seconds=3, color="white", height=50)
```

*Note: To run the line above, you need a `win` object created by `initialize_exp()`.*

You can customize the appearance of the countdown numbers by passing keyword arguments that will be forwarded to PsychoPy's `TextStim`.

## `show_ports()`

If you are using hardware that connects via a serial port (like a trigger box), `show_ports()` can help you find the correct port name on your system.

```python
from psyflow.utils import show_ports

# This will print a list of available serial ports
show_ports()
```
Example output:
```
Available serial ports:
[0] /dev/ttyS0 - ttyS0
[1] /dev/ttyUSB0 - USB-Serial Controller
```

## `list_supported_voices()`

If you are using text-to-speech features, this function lists the voices available through `edge-tts`.

```python
from psyflow.utils import list_supported_voices

# Get a list of all English voices and print them in a table
list_supported_voices(filter_lang="en", human_readable=True)
```
This helps you find the right voice for your experiment's needs.

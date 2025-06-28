# TriggerSender: Precise Event Marking for EEG/MEG Experiments

## Overview

The `TriggerSender` class provides a flexible and reliable way to send event markers (triggers) to EEG/MEG recording systems. It solves several common challenges in neuroscience experiments:

- **Consistent timing**: Ensure precise timing of event markers
- **Flexible configuration**: Support various hardware interfaces
- **Mock mode**: Test experiments without actual hardware
- **Pre/post hooks**: Execute custom code before/after sending triggers
- **Centralized trigger management**: Organize all event codes in one place

Whether you're using a parallel port, serial port, USB device, or network-based trigger system, `TriggerSender` provides a unified interface that makes your experiment code cleaner and more maintainable.

## Key Features

| Feature | Description |
|---------|-------------|
| Hardware abstraction | Works with any trigger hardware via custom send function |
| Mock mode | Test experiments without actual hardware |
| Pre/post hooks | Execute custom code before/after sending triggers |
| Post-delay | Configurable delay after sending triggers |
| Trigger dictionary | Organize event codes with meaningful labels |
| Integration with StimUnit | Seamless use with psyflow's trial controller |

## Quick Reference

| Purpose | Method | Example |
|---------|--------|--------|
| Initialize | `TriggerSender(send_fn)` | `trigger = TriggerSender(send_func)` |
| Mock mode | `TriggerSender(mock=True)` | `trigger = TriggerSender(mock=True)` |
| Send trigger | `.send(code)` | `trigger.send(10)` |
| Add pre-hook | `on_trigger_start` | `TriggerSender(on_trigger_start=fn)` |
| Add post-hook | `on_trigger_end` | `TriggerSender(on_trigger_end=fn)` |
| Set post-delay | `post_delay` | `TriggerSender(post_delay=0.01)` |

## Detailed Usage Guide

### 1. Creating a Trigger Dictionary

Before setting up the `TriggerSender`, it's good practice to organize your event codes in a dictionary. This makes your experiment code more readable and maintainable.

#### Option A: Define Manually in Python

```python
trigger_codes = {
    # Stimulus events
    "fixation_onset": 1,
    "cue_onset": 2,
    "target_onset": 3,
    
    # Response events
    "left_response": 11,
    "right_response": 12,
    "timeout": 19,
    
    # Block events
    "block_start": 21,
    "block_end": 22,
    
    # Condition markers
    "condition_a": 31,
    "condition_b": 32,
    
    # Special events
    "experiment_start": 91,
    "experiment_end": 92,
    "error": 99
}
```

#### Option B: Load from YAML Configuration

YAML file (`triggers.yaml`):

```yaml
triggers:
  # Stimulus events
  fixation_onset: 1
  cue_onset: 2
  target_onset: 3
  
  # Response events
  left_response: 11
  right_response: 12
  timeout: 19
  
  # Block events
  block_start: 21
  block_end: 22
  
  # Condition markers
  condition_a: 31
  condition_b: 32
  
  # Special events
  experiment_start: 91
  experiment_end: 92
  error: 99
```

Loading in Python:

```python
import yaml

with open("triggers.yaml", "r") as f:
    config = yaml.safe_load(f)
    trigger_codes = config["triggers"]
```

### 2. Initializing TriggerSender

#### Option A: Mock Mode (for Testing)

```python
from psyflow import TriggerSender

# Create a mock trigger sender for testing
trigger = TriggerSender(mock=True)
```

In mock mode, triggers are printed to the console but not actually sent to any hardware.

#### Option B: Serial Port

```python
import serial
from psyflow import TriggerSender

# Open serial port
port = serial.Serial('COM3', baudrate=9600)

# Define send function
def send_to_serial(code):
    port.write(bytes([code]))

# Create trigger sender
trigger = TriggerSender(
    send_fn=send_to_serial,
    post_delay=0.001  # 1ms delay after sending
)
```

#### Option C: Parallel Port

```python
import parallel
from psyflow import TriggerSender

# Open parallel port
port = parallel.Parallel(port=0)  # Usually 0x378 or 0x3BC

# Define send function
def send_to_parallel(code):
    port.setData(code)

# Create trigger sender
trigger = TriggerSender(send_fn=send_to_parallel)
```

#### Option D: LabStreamingLayer (LSL)

```python
from pylsl import StreamInfo, StreamOutlet
from psyflow import TriggerSender

# Create LSL outlet
info = StreamInfo('PsychoPy_Markers', 'Markers', 1, 0, 'int32', 'trigger')
outlet = StreamOutlet(info)

# Define send function
def send_to_lsl(code):
    outlet.push_sample([code])

# Create trigger sender
trigger = TriggerSender(send_fn=send_to_lsl)
```

### 3. Sending Triggers

Once you have a `TriggerSender` instance, sending triggers is straightforward:

```python
# Send a trigger directly with a code
trigger.send(10)

# Send a trigger using the dictionary
trigger.send(trigger_codes["fixation_onset"])

# Send a trigger with condition-specific code
def send_condition_trigger(condition):
    if condition == "a":
        trigger.send(trigger_codes["condition_a"])
    else:  # condition == "b"
        trigger.send(trigger_codes["condition_b"])
```

### 4. Using Pre/Post Hooks

You can register functions to be called before and after sending a trigger:

```python
# Define hook functions
def before_trigger():
    print("Preparing to send trigger...")
    # Additional setup if needed

def after_trigger():
    print("Trigger sent successfully.")
    # Additional cleanup if needed

# Create trigger sender with hooks
trigger = TriggerSender(
    send_fn=send_to_serial,
    on_trigger_start=before_trigger,
    on_trigger_end=after_trigger,
    post_delay=0.002  # 2ms delay after sending
)
```

These hooks are useful for operations like:
- Opening/closing ports
- Setting up hardware before sending
- Logging trigger events
- Synchronizing with other equipment

### 5. Integration with StimUnit

The `TriggerSender` integrates seamlessly with `StimUnit` for trial-based experiments:

```python
from psyflow import StimUnit, TriggerSender

# Create trigger sender
trigger = TriggerSender(send_fn=send_function)

# Create trial unit with trigger sender
trial = StimUnit(
    win=window,
    unit_label="trial",
    triggersender=trigger
)

# Use in a trial with automatic trigger sending
trial.add_stim(target).capture_response(
    keys=["left", "right"],
    duration=2.0,
    onset_trigger=trigger_codes["target_onset"],
    response_trigger={
        "left": trigger_codes["left_response"],
        "right": trigger_codes["right_response"]
    },
    timeout_trigger=trigger_codes["timeout"]
)
```

## Complete Example

Here's a complete example showing how to use `TriggerSender` in an experiment:

```python
from psychopy import visual, core
from psychopy.hardware.keyboard import Keyboard
from psyflow import TriggerSender, StimUnit
import yaml
import random

# Load trigger codes from YAML
with open("triggers.yaml", "r") as f:
    config = yaml.safe_load(f)
    trigger_codes = config["triggers"]

# Setup PsychoPy window and keyboard
win = visual.Window(size=[1024, 768], color="black", units="deg")
kb = Keyboard()

# Create trigger sender (mock mode for testing)
trigger = TriggerSender(mock=True)

# Create stimuli
fixation = visual.TextStim(win, text="+", height=1.0, color="white")
target = visual.Circle(win, radius=0.8, fillColor="red")
feedback = visual.TextStim(win, text="", height=0.8, pos=[0, -3])

# Run a trial
def run_trial(condition):
    # Send block start trigger
    trigger.send(trigger_codes["block_start"])
    
    # Show fixation
    fix_unit = StimUnit(win, "fixation", trigger)
    fix_unit.add_stim(fixation).show(
        duration=0.5,
        onset_trigger=trigger_codes["fixation_onset"]
    )
    
    # Send condition-specific trigger
    if condition == "a":
        condition_trigger = trigger_codes["condition_a"]
    else:  # condition == "b"
        condition_trigger = trigger_codes["condition_b"]
    trigger.send(condition_trigger)
    
    # Show target and collect response
    trial = StimUnit(win, "target", trigger)
    trial.add_stim(target).capture_response(
        keys=["left", "right"],
        duration=2.0,
        onset_trigger=trigger_codes["target_onset"],
        response_trigger={
            "left": trigger_codes["left_response"],
            "right": trigger_codes["right_response"]
        },
        timeout_trigger=trigger_codes["timeout"]
    )
    
    # Show feedback
    feedback_unit = StimUnit(win, "feedback", trigger)
    if trial.state.get("response") is not None:
        feedback.text = f"You pressed {trial.state['response']}"
    else:
        feedback.text = "No response"
    
    feedback_unit.add_stim(feedback).show(duration=1.0)
    
    # Send block end trigger
    trigger.send(trigger_codes["block_end"])
    
    return trial.to_dict()

# Run experiment
trigger.send(trigger_codes["experiment_start"])

results = []
conditions = ["a", "b"] * 3  # 6 trials total
random.shuffle(conditions)

for condition in conditions:
    result = run_trial(condition)
    results.append(result)
    core.wait(0.5)  # Inter-trial interval

trigger.send(trigger_codes["experiment_end"])

# Clean up
win.close()
```

## Advanced Usage

### Custom Trigger Protocols

Some EEG/MEG systems require specific trigger protocols. You can implement these in your send function:

```python
# Example: BrainProducts trigger protocol
def send_to_brainproducts(code):
    # Send start byte
    port.write(bytes([0xA0]))
    # Send code
    port.write(bytes([code]))
    # Send end byte
    port.write(bytes([0xB0]))

trigger = TriggerSender(send_fn=send_to_brainproducts)
```

### Trigger Sequences

For complex event marking, you might need to send sequences of triggers:

```python
def send_trigger_sequence(base_code, condition_code):
    # Send base code
    trigger.send(base_code)
    # Wait a short time
    core.wait(0.01)  # 10ms
    # Send condition modifier
    trigger.send(condition_code)

# Usage
send_trigger_sequence(10, 1)  # e.g., 10 = target, 1 = condition A
```

### Trigger Validation

For critical applications, you might want to validate that triggers were actually sent:

```python
def validated_send(code):
    # Send the trigger
    port.write(bytes([code]))
    # Read back to verify
    readback = port.read(1)
    if readback and ord(readback) == code:
        print(f"Trigger {code} successfully sent and verified")
    else:
        print(f"WARNING: Trigger {code} may not have been sent correctly")

trigger = TriggerSender(send_fn=validated_send)
```

## Best Practices

1. **Use meaningful trigger codes**: Organize your trigger codes logically (e.g., 1-10 for stimuli, 11-20 for responses).

2. **Document your trigger codes**: Keep a detailed record of what each code represents.

3. **Test with mock mode**: Always test your experiment with `mock=True` before connecting real hardware.

4. **Use post-delays**: Add a small delay (1-5ms) after sending triggers to ensure they're registered properly.

5. **Validate timing**: Use an oscilloscope or recording software to verify trigger timing during development.

6. **Handle errors gracefully**: Wrap trigger sending in try/except blocks to prevent experiment crashes.

7. **Centralize trigger management**: Keep all trigger codes in one configuration file.

## Troubleshooting

- **Missing triggers**: Check hardware connections and verify your send function works correctly.

- **Timing issues**: Ensure your post-delay is appropriate for your hardware and that your computer isn't overloaded.

- **Code conflicts**: Verify that your trigger codes don't conflict with other signals in your system.

- **Serial port problems**: Check port settings (baud rate, parity, etc.) and ensure the port is not being used by another program.

## Next Steps

Now that you understand how to use `TriggerSender`, you can:

- Explore the [StimUnit tutorial](build_trialunit.md) to learn how to create trial sequences with integrated triggers
- Check out the [BlockUnit tutorial](build_blocks.md) to organize trials into blocks
- Learn about [StimBank](build_stimulus.md) for flexible stimulus management

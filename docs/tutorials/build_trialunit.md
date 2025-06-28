# 🎯 StimUnit: Modular Trial Controller for PsychoPy

## Overview

`StimUnit` is a powerful trial-level controller for PsychoPy experiments that encapsulates all the components of a single trial:

- **Stimulus presentation**: Display multiple stimuli with precise timing
- **Response collection**: Capture keyboard responses with reaction times
- **Event triggers**: Send EEG/MEG trigger codes at critical moments
- **Timing control**: Frame-based or time-based precision
- **State management**: Track trial data in a centralized state object
- **Event hooks**: Execute custom code at key trial moments

With `StimUnit`, you can create complex trial structures using a clean, chainable API that makes your experiment code more readable and maintainable.

## Key Features

| Feature | Description |
|---------|-------------|
| Chainable API | Fluent interface for building trials with method chaining |
| Multiple timing modes | Choose between frame-based or clock-based timing |
| Event hooks | Register callbacks for trial start, response, timeout, and end |
| Flexible response handling | Capture specific keys with automatic RT measurement |
| Integrated trigger sending | Send EEG/MEG triggers at stimulus onset, response, and timeout |
| State management | Centralized data collection for all trial events |
| Response highlighting | Automatically highlight selected responses |
| Jittered timing | Support for randomized stimulus durations |

## Quick Reference

| Purpose | Method | Example |
|---------|--------|--------|
| Initialize | `StimUnit(label, win, kb, triggersender=sender)` | `trial = StimUnit("cue", win, kb, triggersender=sender)` |
| Add stimuli | `.add_stim(stim)` | `trial.add_stim(fixation)` |
| Register start hook | `.on_start(fn)` | `@trial.on_start()` |
| Register response hook | `.on_response(keys, fn)` | `@trial.on_response(['left', 'right'])` |
| Register timeout hook | `.on_timeout(sec, fn)` | `@trial.on_timeout(2.0)` |
| Register end hook | `.on_end(fn)` | `@trial.on_end()` |
| Set auto-close duration | `.duration(t)` | `trial.duration(1.5)` |
| Set auto-close keys | `.close_on(keys)` | `trial.close_on('space')` |
| Simple display | `.show(duration)` | `trial.show(1.0)` |
| Response capture | `.capture_response(keys)` | `trial.capture_response(['left', 'right'])` |
| Full trial control | `.run()` | `trial.run()` |
| Pause for input | `.wait_and_continue(keys)` | `trial.wait_and_continue(['space'])` |
| Update state | `.set_state(**kwargs)` | `trial.set_state(correct=True)` |
| Get state | `.state` or `.to_dict()` | `data = trial.to_dict()` |

## Detailed Usage Guide

### 1. Initialization

Create a new `StimUnit` by passing your PsychoPy window, a label, and optionally a `TriggerSender`:

```python
from psychopy import visual
from psychopy.hardware.keyboard import Keyboard
from psyflow import StimUnit, TriggerSender

# Create window and keyboard
win = visual.Window(size=[1024, 768], color="black", units="deg")
kb = Keyboard()

# Create a trigger sender (mock mode for testing)
sender = TriggerSender(mock=True)

# Initialize a trial unit
trial = StimUnit("cue", win, kb, triggersender=sender)
```

For real EEG/MEG experiments, you would use a real trigger function:

```python
# Example with a serial port
import serial
port = serial.Serial('COM3', 9600)

# Create trigger sender with a real function
trigger = TriggerSender(
    send_fn=lambda code: port.write(bytes([code])),
    post_delay=0.01  # 10ms delay after sending
)
```

### 2. Adding Stimuli

Attach visual components to your trial unit. You can add individual stimuli, multiple stimuli, or lists of stimuli:

```python
# Create some PsychoPy stimuli
fixation = visual.TextStim(win, text="+", height=1.0)
target = visual.Circle(win, radius=0.5, fillColor="red")
feedback = visual.TextStim(win, text="Correct!", pos=[0, -2])

# Add a single stimulus
trial.add_stim(fixation)

# Add multiple stimuli at once
trial.add_stim(target, feedback)

# Add a list of stimuli
stim_list = [fixation, target, feedback]
trial.add_stim(stim_list)

# Chain multiple add_stim calls
trial.add_stim(fixation).add_stim(target).add_stim(feedback)

# Clear all stimuli
trial.clear_stimuli()
```

All added stimuli will be drawn together when the trial is presented.

### 3. Lifecycle Hooks

Register callback functions that execute at key moments in the trial lifecycle:

```python
# Using decorator syntax
@trial.on_start()
def prepare_trial(unit):
    print(f"Starting {unit.label}")
    unit.set_state(start_time=core.getTime())

@trial.on_response(['left', 'right'])
def handle_response(unit, key, rt):
    print(f"Response: {key}, RT: {rt:.3f}s")
    unit.set_state(response=key, rt=rt)
    
    # Check if response is correct
    if key == unit.state.get('correct_key'):
        unit.set_state(correct=True)
    else:
        unit.set_state(correct=False)

@trial.on_timeout(2.0)
def handle_timeout(unit):
    print("Response timeout")
    unit.set_state(timeout=True)

@trial.on_end()
def finalize_trial(unit):
    print(f"Trial complete: {unit.to_dict()}")
    # Save data, prepare for next trial, etc.
```

Alternatively, you can use method chaining:

```python
trial.on_start(prepare_trial) \
     .on_response(['left', 'right'], handle_response) \
     .on_timeout(2.0, handle_timeout) \
     .on_end(finalize_trial)
```

### 4. Auto-Closing Options

Set conditions for automatically ending the trial:

#### Fixed or Jittered Duration

```python
# Close after exactly 1.5 seconds
trial.duration(1.5)

# Close after a random duration between 1.0 and 2.0 seconds
trial.duration((1.0, 2.0))
```

#### Close on Specific Key Presses

```python
# Close when 'space' is pressed
trial.close_on('space')

# Close when any of these keys are pressed
trial.close_on('left', 'right', 'escape')
```

These settings automatically record the key pressed, reaction time, and closing time into the trial's state.

### 5. Simple Display with `show()`

For basic stimulus presentation with optional trigger:

```python
# Show stimuli for 1 second
trial.add_stim(fixation).show(duration=1.0)

# Show with trigger code at onset
trial.add_stim(target).show(
    duration=1.0,
    onset_trigger=10,  # Send trigger code 10 at stimulus onset
    frame_based=True   # Use frame-based timing (vs. clock-based)
)

# Show with jittered duration
trial.add_stim(cue).show(
    duration=(0.8, 1.2),  # Random duration between 0.8-1.2s
    onset_trigger=20
)
```

### 6. Stimulus + Response Window with `capture_response()`

For trials requiring response collection:

```python
# Basic response capture
trial.add_stim(target).capture_response(
    keys=['left', 'right'],  # Valid response keys
    duration=2.0             # Response window duration
)

# Advanced response capture with triggers and highlighting
trial.add_stim(left_arrow, right_arrow).capture_response(
    keys=['left', 'right'],
    duration=2.0,
    onset_trigger=10,                         # Trigger at stimulus onset
    response_trigger={'left': 11, 'right': 12},  # Key-specific triggers
    timeout_trigger=19,                       # Trigger if no response
    correct_keys=['right'],                   # Define correct response
    highlight_stim={'left': left_highlight, 'right': right_highlight},
    dynamic_highlight=True                    # Redraw on multiple presses
)
```

The `capture_response()` method automatically handles:
- Displaying stimuli
- Sending onset triggers
- Collecting responses and reaction times
- Sending response-specific triggers
- Highlighting selected responses
- Sending timeout triggers
- Updating the trial state with all relevant data

### 7. Full Trial Loop with `run()`

For maximum flexibility, use the `run()` method after setting up hooks:

```python
# Set up the trial
trial.add_stim(fixation, target) \
     .on_start(start_fn) \
     .on_response(['left', 'right'], response_fn) \
     .on_timeout(2.0, timeout_fn) \
     .on_end(end_fn) \
     .duration(2.0)

# Run the trial
trial.run(
    terminate_on_response=True   # Stop drawing after response
)

# Access trial data
result = trial.to_dict()
print(f"Response: {result.get('response')}, RT: {result.get('rt')}")
```

The `run()` method gives you complete control over the trial execution, while still benefiting from the automatic state management and event handling.

### 8. Pause & Continue with `wait_and_continue()`

For instruction screens or breaks that require a keypress to continue:

```python
# Show instructions and wait for space
instructions = visual.TextStim(
    win, 
    text="Press SPACE to begin the experiment",
    height=0.7
)

trial.add_stim(instructions).wait_and_continue(
    keys=['space'],
    log_message="Instructions shown",
    terminate=False  # Continue execution after keypress
)

# Show end screen and terminate
end_text = visual.TextStim(
    win,
    text="Experiment complete. Thank you!",
    height=0.7
)

trial.clear_stimuli().add_stim(end_text).wait_and_continue(
    keys=['space'],
    log_message="Experiment ended",
    terminate=True  # End the experiment after keypress
)
```

### 9. State Management

The `StimUnit` maintains an internal state dictionary that tracks all trial events and data:

```python
# Update state with custom data
trial.set_state(
    condition="reward",
    block_num=2,
    trial_num=15
)

# Access state values
print(f"Condition: {trial.state.get('condition')}")
print(f"Response: {trial.state.get('response')}")
print(f"RT: {trial.state.get('rt')}")

# Get complete state as dictionary
full_data = trial.to_dict()

# Log state to console (useful for debugging)
trial.log_unit()
```

The state automatically includes:
- Trial label
- Timestamps for start, response, and end
- Response key and reaction time
- Trigger codes sent
- Any custom data added with `set_state()`

## Complete Example

Here's a complete example showing how to use `StimUnit` in an experiment:

```python
from psychopy import visual, core
from psychopy.hardware.keyboard import Keyboard
from psyflow import StimUnit, TriggerSender
import random

# Setup
win = visual.Window(size=[1024, 768], color="black", units="deg")
kb = Keyboard()
sender = TriggerSender(mock=True)

# Create stimuli
fixation = visual.TextStim(win, text="+", height=1.0, color="white")
left_target = visual.Circle(win, radius=0.8, fillColor="blue", pos=[-5, 0])
right_target = visual.Circle(win, radius=0.8, fillColor="red", pos=[5, 0])
left_highlight = visual.Rect(win, width=3, height=3, lineColor="yellow", 
                            lineWidth=3, pos=[-5, 0], fillColor=None)
right_highlight = visual.Rect(win, width=3, height=3, lineColor="yellow", 
                             lineWidth=3, pos=[5, 0], fillColor=None)
feedback_correct = visual.TextStim(win, text="Correct!", height=0.8, 
                                  color="green", pos=[0, -3])
feedback_incorrect = visual.TextStim(win, text="Incorrect", height=0.8, 
                                    color="red", pos=[0, -3])

# Run a trial
def run_trial(condition):
    # Determine correct response for this condition
    if condition == "left":
        correct_key = "left"
        target_trigger = 11
    else:  # condition == "right"
        correct_key = "right"
        target_trigger = 12
    
    # Create trial unit
    trial = StimUnit("choice", win, kb, triggersender=sender)
    
    # Register response handler
    @trial.on_response(["left", "right"])
    def handle_response(unit, key, rt):
        # Check if response is correct
        is_correct = (key == correct_key)
        unit.set_state(correct=is_correct)
        
        # Show appropriate feedback
        unit.clear_stimuli()
        if is_correct:
            unit.add_stim(feedback_correct)
        else:
            unit.add_stim(feedback_incorrect)
    
    # Show fixation
    fixation_trial = StimUnit("fixation", win, kb, triggersender=sender)
    fixation_trial.add_stim(fixation).show(
        duration=(0.8, 1.2),  # Jittered duration
        onset_trigger=10
    )
    
    # Show targets and collect response
    trial.add_stim(left_target, right_target)
    trial.set_state(condition=condition, correct_key=correct_key)
    trial.capture_response(
        keys=["left", "right"],
        duration=2.0,
        onset_trigger=target_trigger,
        response_trigger={"left": 21, "right": 22},
        timeout_trigger=29,
        correct_keys=[correct_key],
        highlight_stim={"left": left_highlight, "right": right_highlight}
    )
    
    # Show feedback for 1 second
    core.wait(1.0)
    
    # Return trial data
    return trial.to_dict()

# Run a block of trials
results = []
conditions = ["left", "right"] * 5  # 10 trials total
random.shuffle(conditions)

for i, condition in enumerate(conditions):
    print(f"Trial {i+1}/{len(conditions)}")
    trial_data = run_trial(condition)
    trial_data["trial_num"] = i + 1
    results.append(trial_data)
    core.wait(0.5)  # Inter-trial interval

# Show completion message
end_trial = StimUnit("end", win, kb, triggersender=sender)
end_text = visual.TextStim(
    win,
    text="Experiment complete. Thank you!",
    height=0.7
)
end_trial.add_stim(end_text).wait_and_continue(
    keys=["space"],
    terminate=True
)

# Clean up
win.close()

# Analyze results
correct_count = sum(1 for trial in results if trial.get("correct", False))
accuracy = correct_count / len(results) * 100
print(f"Accuracy: {accuracy:.1f}%")
```

## Advanced Usage

### Frame-Based vs. Clock-Based Timing

`StimUnit` supports two timing modes:

```python
# Frame-based timing (more precise for short durations)
trial.show(duration=0.5, frame_based=True)

# Clock-based timing (better for longer durations)
trial.show(duration=10.0, frame_based=False)
```

Frame-based timing counts the number of screen refreshes, while clock-based timing uses the system clock. Frame-based timing is generally more precise for short durations but requires a stable frame rate.

### Custom Trigger Sequences

You can send custom trigger sequences at any point:

```python
@trial.on_start()
def custom_triggers(unit):
    # Send a sequence of triggers with delays
    unit.triggersender.send(101)  # First trigger
    core.wait(0.05)               # 50ms delay
    unit.triggersender.send(102)  # Second trigger
    core.wait(0.05)               # 50ms delay
    unit.triggersender.send(103)  # Third trigger
```

### Dynamic Stimulus Updates

You can modify stimuli during the trial:

```python
@trial.on_response(["left", "right"])
def update_stimulus(unit, key, rt):
    # Get the stimulus from the unit
    for stim in unit.stimuli:
        if hasattr(stim, "text"):
            # Update text based on response
            stim.text = f"You pressed {key} in {rt:.3f}s"
```

### Nested Trial Units

You can create complex trial structures by nesting `StimUnit` instances:

```python
def run_complex_trial():
    # Fixation phase
    fix_unit = StimUnit("fixation", win, kb, triggersender=sender)
    fix_unit.add_stim(fixation).show(duration=0.5, onset_trigger=1)
    
    # Cue phase
    cue_unit = StimUnit("cue", win, kb, triggersender=sender)
    cue_unit.add_stim(cue).show(duration=0.8, onset_trigger=2)
    
    # Target phase with response
    target_unit = StimUnit("target", win, kb, triggersender=sender)
    target_unit.add_stim(target).capture_response(
        keys=["left", "right"],
        duration=2.0,
        onset_trigger=3
    )
    
    # Feedback phase
    feedback_unit = StimUnit("feedback", win, kb, triggersender=sender)
    if target_unit.state.get("correct", False):
        feedback_unit.add_stim(feedback_correct)
    else:
        feedback_unit.add_stim(feedback_incorrect)
    feedback_unit.show(duration=1.0, onset_trigger=4)
    
    # Combine all data
    return {
        "fixation": fix_unit.to_dict(),
        "cue": cue_unit.to_dict(),
        "target": target_unit.to_dict(),
        "feedback": feedback_unit.to_dict()
    }
```

## Best Practices

1. **Use descriptive labels**: Choose meaningful `unit_label` values to make your state data more readable.

2. **Chain methods**: Take advantage of the chainable API to write concise, readable code.

3. **Separate trial phases**: For complex trials, use multiple `StimUnit` instances for different phases.

4. **Predefine stimuli**: Create all stimuli before the trial loop to avoid performance issues.

5. **Test with mock triggers**: Use `TriggerSender(mock=True)` during development and testing.

6. **Log liberally**: Use `set_state()` to record all relevant trial information.

7. **Handle errors gracefully**: Use try/except blocks in your hooks to prevent crashes.

## Troubleshooting

- **Timing issues**: If timing seems off, check if you're using the appropriate timing mode (frame-based vs. clock-based).

- **Missing responses**: Ensure your keyboard is properly initialized and that you're listening for the correct keys.

- **Stimulus not appearing**: Check that you've added all stimuli to the unit with `add_stim()`.

- **Trigger problems**: Verify your `TriggerSender` is properly configured and test with `mock=True` first.

## Next Steps

Now that you understand how to use `StimUnit`, you can:

- Explore the [BlockUnit tutorial](build_blocks.md) to organize trials into blocks
- Learn about [StimBank](build_stimulus.md) for flexible stimulus management
- Check out [trigger sending](send_trigger.md) for EEG/MEG experiments

# StimBank: Flexible Stimulus Management for PsychoPy

## Overview

`StimBank` is a powerful stimulus management system for PsychoPy experiments that solves several common challenges:

- **Centralized stimulus management**: Define all visual elements in one place
- **Multiple definition methods**: Use Python code or configuration files
- **Lazy loading**: Only instantiate stimuli when needed
- **Dynamic formatting**: Update text stimuli with variable content
- **Batch operations**: Preview, export, and validate multiple stimuli

Whether you're building a simple experiment or a complex protocol with dozens of visual elements, `StimBank` helps keep your code organized, maintainable, and flexible.

## Key Features

| Feature | Description |
|---------|-------------|
| Dual registration | Define stimuli via decorators or YAML/dictionaries |
| Lazy instantiation | Create stimuli only when needed to optimize performance |
| Grouping | Retrieve related stimuli by prefix or explicit selection |
| Text formatting | Insert dynamic values into text stimuli |
| Stimulus rebuilding | Modify stimulus properties on-the-fly |
| Preview functionality | Visually inspect all stimuli during development |
| Configuration export | Save stimulus definitions to YAML for reuse |

## Quick Reference

| Purpose | Method | Example |
|---------|--------|--------|
| Initialize | `StimBank(win)` | `bank = StimBank(win)` |
| Register (decorator) | `@bank.define(name)` | `@bank.define("fixation")` |
| Register (dict) | `.add_from_dict(dict)` | `bank.add_from_dict(config)` |
| Get stimulus | `.get(name)` | `stim = bank.get("target")` |
| Get multiple | `.get_selected(keys)` | `stims = bank.get_selected(["fix", "cue"])` |
| Get by prefix | `.get_group(prefix)` | `cues = bank.get_group("cue_")` |
| Format text | `.get_and_format(name, **kwargs)` | `bank.get_and_format("msg", name="John")` |
| Modify stimulus | `.rebuild(name, **kwargs)` | `bank.rebuild("target", fillColor="blue")` |
| Preview all | `.preview_all()` | `bank.preview_all()` |
| Export config | `.export_to_yaml(file)` | `bank.export_to_yaml("stimuli.yaml")` |

## Detailed Usage Guide

### 1. Initialization

Create a `StimBank` instance with your PsychoPy window:

```python
from psychopy.visual import Window
from psyflow import StimBank

# Create PsychoPy window
win = Window(size=[1024, 768], color="black", units="deg")

# Initialize stimulus bank
stim_bank = StimBank(win)
```

You can also provide an initial configuration dictionary:

```python
config = {
    "fixation": {"type": "text", "text": "+", "height": 1.0, "color": "white"}
}
stim_bank = StimBank(win, config=config)
```

### 2. Registering Stimuli

#### Method 1: Using Decorators

The decorator approach gives you full flexibility with Python code:

```python
from psychopy.visual import TextStim, Circle, ImageStim

@stim_bank.define("fixation")
def make_fixation(win):
    return TextStim(win, text="+", color="white", height=1.0)

@stim_bank.define("target")
def make_target(win):
    return Circle(
        win, 
        radius=0.5, 
        fillColor="red", 
        lineColor="white", 
        lineWidth=2
    )

@stim_bank.define("feedback_correct")
def make_feedback(win):
    return TextStim(
        win,
        text="Correct!",
        color="green",
        height=0.8,
        pos=[0, -2]
    )

# Complex stimuli with multiple components
@stim_bank.define("compound_stimulus")
def make_compound(win):
    # Create a container (ShapeStim) with multiple elements
    container = ShapeStim(win, fillColor=None, lineColor=None)
    
    # Add child stimuli
    circle = Circle(win, radius=1.0, fillColor="blue")
    text = TextStim(win, text="A", color="white")
    
    # Return the container with references to children
    container._circle = circle
    container._text = text
    
    # Define a custom draw method
    original_draw = container.draw
    def custom_draw():
        circle.draw()
        text.draw()
        original_draw()
    container.draw = custom_draw
    
    return container
```

#### Method 2: Using Dictionaries or YAML

The dictionary approach is more declarative and can be loaded from YAML files:

```python
# Direct dictionary definition
stim_config = {
    "instructions": {
        "type": "text",
        "text": "Press SPACE to begin",
        "height": 0.7,
        "color": "white",
        "pos": [0, 3]
    },
    "left_target": {
        "type": "circle",
        "radius": 0.8,
        "pos": [-5, 0],
        "fillColor": "blue"
    },
    "right_target": {
        "type": "circle",
        "radius": 0.8,
        "pos": [5, 0],
        "fillColor": "red"
    },
    "image_stimulus": {
        "type": "image",
        "image": "images/stimulus.png",
        "size": [4, 3]
    }
}

# Add to stimulus bank
stim_bank.add_from_dict(stim_config)
```

Loading from YAML file:

```python
import yaml

# Load from YAML file
with open("stimuli.yaml", "r") as f:
    yaml_config = yaml.safe_load(f)

stim_bank.add_from_dict(yaml_config)
```

Example YAML file (`stimuli.yaml`):

```yaml
fixation:
  type: text
  text: +
  height: 1.0
  color: white

target:
  type: circle
  radius: 0.5
  fillColor: red
  lineColor: white

feedback:
  type: text
  text: "Correct: {score} points"
  height: 0.8
  color: green
  pos: [0, -2]
```

### 3. Retrieving Stimuli

#### Getting Individual Stimuli

```python
# Get a single stimulus (instantiated lazily)
fixation = stim_bank.get("fixation")
fixation.draw()
win.flip()

# Check if a stimulus exists
if stim_bank.has("target"):
    target = stim_bank.get("target")
    target.draw()
```

#### Getting Multiple Stimuli

```python
# Get specific stimuli by name
selected_stimuli = stim_bank.get_selected(["fixation", "target", "feedback"])
for stim in selected_stimuli:
    stim.draw()

# Get all stimuli with a common prefix
cue_stimuli = stim_bank.get_group("cue_")
# Returns all stimuli with keys like "cue_left", "cue_right", etc.

# Get all available stimulus keys
all_keys = stim_bank.keys()
print(f"Available stimuli: {all_keys}")
```

### 4. Dynamic Text Formatting

For `TextStim` objects, you can use Python's string formatting syntax in the text and then insert values at runtime:

```python
# Define a text stimulus with placeholders
stim_bank.add_from_dict({
    "score_message": {
        "type": "text",
        "text": "Score: {points} points\nAccuracy: {accuracy}%",
        "height": 0.7,
        "color": "white"
    },
    "welcome": {
        "type": "text",
        "text": "Welcome, {participant_name}!",
        "height": 1.0,
        "color": "yellow"
    }
})

# Format with values at runtime
score_text = stim_bank.get_and_format("score_message", 
                                    points=150, 
                                    accuracy=87.5)
score_text.draw()

# Format with participant name
welcome_text = stim_bank.get_and_format("welcome", 
                                      participant_name="Alex")
welcome_text.draw()
```

### 5. Rebuilding and Modifying Stimuli

You can modify stimulus properties on-the-fly:

```python
# Rebuild a stimulus with new properties
blue_target = stim_bank.rebuild("target", fillColor="blue", radius=0.7)
blue_target.draw()

# The original definition remains unchanged
original_target = stim_bank.get("target")  # Still red with radius=0.5
```

This is particularly useful for condition-dependent stimuli:

```python
def run_trial(condition):
    if condition == "reward":
        target = stim_bank.rebuild("target", fillColor="gold")
    else:  # "neutral" condition
        target = stim_bank.rebuild("target", fillColor="gray")
    
    # Run trial with the modified target
    # ...
```

### 6. Previewing Stimuli

During development, you can preview all stimuli to ensure they appear as expected:

```python
# Preview all stimuli (one at a time with key press to advance)
stim_bank.preview_all()

# Preview specific stimuli
stim_bank.preview_selected(["fixation", "target"])

# Preview stimuli with a common prefix
stim_bank.preview_group("feedback_")
```

### 7. Exporting Configurations

You can export stimulus definitions to YAML for reuse or documentation:

```python
# Export all stimuli to YAML
stim_bank.export_to_yaml("exported_stimuli.yaml")

# Export selected stimuli
stim_bank.export_to_yaml("targets.yaml", 
                        keys=["left_target", "right_target"])
```

### 8. Advanced: Sound Stimuli

In addition to visual stimuli, `StimBank` can also manage sound stimuli:

```python
from psychopy.sound import Sound

# Using decorator
@stim_bank.define("beep")
def make_beep(win):
    return Sound(value=1000, secs=0.5)  # 1000 Hz tone for 0.5 seconds

# Using dictionary
stim_bank.add_from_dict({
    "correct_sound": {
        "type": "sound",
        "value": "sounds/correct.wav"
    },
    "error_sound": {
        "type": "sound",
        "value": "sounds/error.wav"
    }
})

# Play a sound
beep = stim_bank.get("beep")
beep.play()
```

### 9. Advanced: Text-to-Speech

Psyflow includes experimental support for text-to-speech using Microsoft Edge TTS:

```python
# Define a TTS stimulus
stim_bank.add_from_dict({
    "instructions_tts": {
        "type": "tts",
        "text": "Welcome to the experiment. Press space to begin.",
        "voice": "en-US-AriaNeural",  # Microsoft Edge TTS voice
        "rate": "+0%",               # Speed adjustment
        "volume": "+0%"              # Volume adjustment
    }
})

# Get and play TTS
tts = stim_bank.get("instructions_tts")
tts.play()
```

## Complete Example

Here's a complete example showing how to use `StimBank` in an experiment:

```python
from psychopy import visual, core, event
from psychopy.hardware.keyboard import Keyboard
from psyflow import StimBank
import yaml

# Create window and keyboard
win = visual.Window(size=[1024, 768], color="black", units="deg")
kb = Keyboard()

# Initialize stimulus bank
stim_bank = StimBank(win)

# Load stimuli from YAML
with open("experiment_stimuli.yaml", "r") as f:
    stim_config = yaml.safe_load(f)

stim_bank.add_from_dict(stim_config)

# Add programmatic stimuli
@stim_bank.define("fixation")
def make_fixation(win):
    return visual.TextStim(win, text="+", height=1.0, color="white")

# Run a simple trial
def run_trial(condition, participant_name):
    # Show welcome with participant name
    welcome = stim_bank.get_and_format("welcome", participant_name=participant_name)
    welcome.draw()
    win.flip()
    core.wait(2.0)
    
    # Show fixation
    fixation = stim_bank.get("fixation")
    fixation.draw()
    win.flip()
    core.wait(0.5)
    
    # Show condition-specific target
    if condition == "reward":
        target = stim_bank.rebuild("target", fillColor="gold")
    else:
        target = stim_bank.rebuild("target", fillColor="silver")
    
    target.draw()
    win.flip()
    
    # Wait for response
    keys = kb.waitKeys(keyList=["left", "right"])
    response = keys[0].name if keys else None
    rt = keys[0].rt if keys else None
    
    # Show feedback
    if response == "left":
        feedback = stim_bank.get_and_format("feedback", 
                                          correct=True, 
                                          points=10)
    else:
        feedback = stim_bank.get_and_format("feedback", 
                                          correct=False, 
                                          points=0)
    
    feedback.draw()
    win.flip()
    core.wait(1.0)
    
    return {"condition": condition, "response": response, "rt": rt}

# Run experiment
results = []
for condition in ["neutral", "reward", "neutral", "reward"]:
    trial_result = run_trial(condition, "Participant")
    results.append(trial_result)

# Clean up
win.close()
```

Example YAML file (`experiment_stimuli.yaml`):

```yaml
welcome:
  type: text
  text: "Welcome, {participant_name}!"
  height: 1.0
  color: "yellow"
  pos: [0, 0]

target:
  type: circle
  radius: 0.8
  fillColor: "red"
  lineColor: "white"
  lineWidth: 2
  pos: [0, 0]

feedback:
  type: text
  text: "{correct|Correct!|Incorrect!} You earned {points} points."
  height: 0.8
  color: "white"
  pos: [0, -2]
```

## Best Practices

1. **Organize by function**: Group related stimuli with common prefixes (e.g., `cue_left`, `cue_right`).

2. **Separate content from presentation**: Use configuration files for content that might change (text, images) and code for complex presentation logic.

3. **Preload when needed**: Call `stim_bank.preload_all()` before the experiment starts if you want to front-load initialization time.

4. **Use rebuilding sparingly**: While convenient, rebuilding stimuli frequently can impact performance. For stimuli that change on every trial, consider registering separate versions.

5. **Document your stimuli**: Include comments in your YAML files or code to explain the purpose of each stimulus.

## Troubleshooting

- **Stimulus not appearing**: Check if the stimulus is properly registered and that its properties (like position and color) are valid.

- **Format errors**: Ensure that placeholders in text stimuli match the keywords provided to `get_and_format()`.

- **Performance issues**: If your experiment slows down, consider preloading stimuli and minimizing rebuilding operations.

- **YAML parsing errors**: Verify your YAML syntax, especially indentation and special characters.

## Next Steps

Now that you understand how to use `StimBank`, you can:

- Explore the [StimUnit tutorial](build_trialunit.md) to learn how to create trial sequences
- Check out the [BlockUnit tutorial](build_blocks.md) to organize trials into blocks
- Learn about [trigger sending](send_trigger.md) for EEG/MEG experiments

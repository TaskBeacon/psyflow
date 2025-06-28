# BlockUnit: Organizing Trials into Experimental Blocks

## Overview

The `BlockUnit` class is a powerful tool for organizing trials in psychological experiments. It provides a structured way to manage trial sequences, generate balanced conditions, track results, and summarize performance metrics. This tutorial will guide you through using `BlockUnit` to create well-structured experimental blocks.

`BlockUnit` solves several common challenges in experimental design:

- **Condition balancing**: Generate trial conditions with proper randomization and counterbalancing
- **Trial sequencing**: Manage the flow of trials within a block
- **Data organization**: Automatically track trial-level data and block metadata
- **Block lifecycle**: Execute setup and cleanup operations at block boundaries
- **Result summarization**: Calculate performance metrics across trials and conditions

## Key Features

| Feature | Description |
|---------|-------------|
| Condition generation | Create balanced, randomized trial sequences |
| Block lifecycle hooks | Execute code before/after block execution |
| Result tracking | Automatically collect and organize trial data |
| Summarization | Calculate performance metrics by condition |
| Metadata | Track timing, trial counts, and block information |
| Integration | Works seamlessly with other psyflow components |

## Quick Reference

| Purpose | Method | Example |
|---------|--------|--------|
| Initialize block | `BlockUnit(block_id, block_idx, ...)` | `block = BlockUnit("block1", 0, settings)` |
| Generate conditions | `.generate_conditions(func, labels)` | `block.generate_conditions(generate_func, ["A", "B"])` |
| Add trials manually | `.add_trials(trial_list)` | `block.add_trials(["A", "B", "A"])` |
| Register start hook | `.on_start(func)` | `@block.on_start()` or `block.on_start(func)` |
| Register end hook | `.on_end(func)` | `@block.on_end()` or `block.on_end(func)` |
| Run all trials | `.run_trial(trial_func, **kwargs)` | `block.run_trial(run_trial_function)` |
| Get results | `.to_dict()` | `results = block.to_dict()` |
| Append results | `.to_dict(target_list)` | `block.to_dict(all_results)` |
| Summarize results | `.summarize()` | `summary = block.summarize()` |
| Custom summary | `.summarize(func)` | `summary = block.summarize(custom_func)` |
| Get trial count | `len(block)` | `num_trials = len(block)` |
| Log block info | `.logging_block_info()` | `block.logging_block_info()` |

## Detailed Usage Guide

### 1. Initializing a Block

To create a `BlockUnit`, you need to provide basic information about the block and the experiment settings:

```python
from psyflow import BlockUnit

block = BlockUnit(
    block_id="practice_block",  # Unique identifier string
    block_idx=0,               # Index of this block in the experiment
    settings=settings,         # TaskSettings object with experiment configuration
    window=win,                # PsychoPy window (optional but recommended)
    keyboard=kb                # PsychoPy keyboard (optional but recommended)
)
```

The `settings` parameter should be a `TaskSettings` object or similar that includes:
- `trials_per_block`: Number of trials in each block
- `block_seed`: Seed for random number generation (for reproducibility)

### 2. Generating Trial Conditions

#### Option A: Using a Condition Generation Function

The most flexible way to create trial conditions is with a custom generation function:

```python
def generate_balanced_conditions(n, labels, seed=None):
    """Generate a balanced, randomized sequence of conditions."""
    import numpy as np
    rng = np.random.default_rng(seed)
    
    # Calculate repetitions needed to reach n trials
    reps = int(np.ceil(n / len(labels)))
    
    # Create sequence and shuffle
    conditions = labels * reps  # Repeat labels as needed
    shuffled = rng.permutation(conditions)[:n]  # Shuffle and trim
    
    return np.array(shuffled)

# Generate conditions for the block
block.generate_conditions(
    func=generate_balanced_conditions,
    condition_labels=["congruent", "incongruent", "neutral"]
)
```

This populates `block.trials` with a balanced, randomized sequence of conditions.

#### Option B: Manually Assigning Trials

For full control, you can manually specify the trial sequence:

```python
block.add_trials(["congruent", "incongruent", "neutral", "congruent", "incongruent"])
```

### 3. Registering Block Lifecycle Hooks

You can register functions to be called automatically at the start and end of a block. This is useful for:

- Displaying instructions or break screens
- Sending block-level triggers to recording equipment
- Logging block information
- Calculating block-level metrics

#### Using Decorator Syntax

```python
@block.on_start()
def show_instructions(b):
    # The block object is passed as the first argument
    print(f"Starting block {b.block_id} ({len(b)} trials)")
    
    # Show instructions
    instructions = visual.TextStim(b.window, text="Press left or right arrow")
    instructions.draw()
    b.window.flip()
    b.keyboard.waitForPresses(maxWait=5.0)  # Wait max 5 seconds

@block.on_end()
def show_block_summary(b):
    print(f"Block {b.block_id} completed in {b.meta['duration']:.2f} seconds")
    
    # Calculate and display accuracy
    correct_trials = sum(1 for r in b.results if r.get("correct", False))
    accuracy = correct_trials / len(b) * 100
    
    # Show feedback
    feedback = visual.TextStim(
        b.window, 
        text=f"Accuracy: {accuracy:.1f}%\nPress any key to continue"
    )
    feedback.draw()
    b.window.flip()
    b.keyboard.waitForPresses()
```

#### Using Functional Syntax

```python
# Alternative approach without decorators
block.on_start(lambda b: print(f"Block {b.block_id} starting"))
block.on_end(lambda b: print(f"Block {b.block_id} completed"))
```

### 4. Defining the Trial Function

The trial function defines what happens on each trial. It receives the block's window, keyboard, settings, and the current trial's condition:

```python
def run_trial(win, kb, settings, condition, **kwargs):
    """Run a single trial and return results."""
    # Create stimuli based on condition
    if condition == "congruent":
        text = "RED"
        color = "red"
    elif condition == "incongruent":
        text = "RED"
        color = "blue"
    else:  # neutral
        text = "XXX"
        color = "green"
    
    # Create and display stimulus
    stimulus = visual.TextStim(win, text=text, color=color)
    stimulus.draw()
    win.flip()
    
    # Record onset time
    onset_time = core.getTime()
    
    # Wait for response (max 2 seconds)
    keys = kb.waitForPresses(maxWait=2.0)
    
    # Calculate response time
    if keys:
        rt = keys[0].rt
        response = keys[0].name
        # Determine if response was correct
        correct = (color == "red" and response == "left") or \
                  (color == "blue" and response == "right")
    else:
        rt = None
        response = None
        correct = False
    
    # Return trial results as a dictionary
    return {
        "condition": condition,
        "response": response,
        "rt": rt,
        "correct": correct,
        "onset_time": onset_time
    }
```

### 5. Running the Block

Once you've set up the block, you can run all trials with a single call:

```python
# Run all trials in the block
block.run_trial(run_trial)
```

This will:
1. Call your `on_start` hook(s)
2. Run each trial in sequence, passing the appropriate condition
3. Store each trial's results
4. Call your `on_end` hook(s)

### 6. Accessing and Summarizing Results

#### Getting Raw Results

```python
# Get all trial results as a list of dictionaries
results = block.to_dict()

# First trial result
print(results[0])
# Example output: {'block_id': 'practice_block', 'trial_idx': 0, 'condition': 'congruent', 'response': 'left', 'rt': 0.543, 'correct': True, 'onset_time': 1234.567}
```

#### Appending to an External List

```python
# Useful for collecting results across multiple blocks
all_results = []
block.to_dict(all_results)  # Appends to all_results
```

#### Summarizing Results

```python
# Get default summary (hit_rate and avg_rt by condition)
summary = block.summarize()
print(summary)
# Example output: {'congruent': {'hit_rate': 0.8, 'avg_rt': 0.523}, 'incongruent': {'hit_rate': 0.6, 'avg_rt': 0.678}, 'neutral': {'hit_rate': 0.7, 'avg_rt': 0.601}}
```

#### Custom Summarization

```python
def custom_summary(block):
    """Calculate custom performance metrics."""
    # Group results by condition
    by_condition = {}
    for cond in set(r.get("condition") for r in block.results):
        cond_results = [r for r in block.results if r.get("condition") == cond]
        
        # Calculate metrics
        accuracy = sum(1 for r in cond_results if r.get("correct", False)) / len(cond_results)
        mean_rt = sum(r.get("rt", 0) for r in cond_results if r.get("rt") is not None) / \
                  sum(1 for r in cond_results if r.get("rt") is not None)
        
        by_condition[cond] = {
            "accuracy": accuracy,
            "mean_rt": mean_rt,
            "trial_count": len(cond_results)
        }
    
    # Add overall metrics
    by_condition["overall"] = {
        "accuracy": sum(1 for r in block.results if r.get("correct", False)) / len(block.results),
        "mean_rt": sum(r.get("rt", 0) for r in block.results if r.get("rt") is not None) / \
                   sum(1 for r in block.results if r.get("rt") is not None),
        "trial_count": len(block.results)
    }
    
    return by_condition

# Use custom summary function
detailed_summary = block.summarize(custom_summary)
```

## Complete Example: Stroop Task

Here's a complete example implementing a simple Stroop task with two blocks:

```python
from psychopy import visual, core, event
from psychopy.hardware.keyboard import Keyboard
from psyflow import BlockUnit, TaskSettings, StimUnit
import numpy as np
import pandas as pd

# Setup experiment
settings = TaskSettings(
    exp_name="stroop",
    trials_per_block=20,
    total_blocks=2,
    block_seed=42,
    resp_keys=["left", "right"]
)

# Create PsychoPy window and keyboard
win = visual.Window(size=[800, 600], color="black", units="norm")
kb = Keyboard()

# Condition generation function
def generate_conditions(n, labels, seed=None):
    rng = np.random.default_rng(seed)
    reps = int(np.ceil(n / len(labels)))
    conditions = labels * reps
    return rng.permutation(conditions)[:n]

# Trial function
def run_stroop_trial(win, kb, settings, condition, **kwargs):
    # Set up stimuli based on condition
    if condition == "congruent":
        word = np.random.choice(["RED", "BLUE"])
        color = word.lower()
    elif condition == "incongruent":
        word = np.random.choice(["RED", "BLUE"])
        color = "red" if word == "BLUE" else "blue"
    else:  # neutral
        word = "XXXX"
        color = np.random.choice(["red", "blue"])
    
    # Create stimulus
    stim = visual.TextStim(win, text=word, color=color, height=0.2)
    
    # Show stimulus and wait for response
    stim.draw()
    win.flip()
    onset_time = core.getTime()
    
    # Wait for response with timeout
    keys = kb.waitForPresses(maxWait=2.0)
    
    # Process response
    if keys:
        key = keys[0].name
        rt = keys[0].rt
        # Check if correct (left for red, right for blue)
        correct = (color == "red" and key == "left") or \
                  (color == "blue" and key == "right")
    else:
        key = None
        rt = None
        correct = False
    
    # Clear screen
    win.flip()
    core.wait(0.5)  # Inter-trial interval
    
    # Return trial data
    return {
        "word": word,
        "color": color,
        "response": key,
        "rt": rt,
        "correct": correct,
        "onset_time": onset_time
    }

# Run experiment
all_results = []

# Show welcome screen
welcome = visual.TextStim(
    win, 
    text="Welcome to the Stroop Task\n\nPress any key to begin", 
    height=0.1
)
welcome.draw()
win.flip()
kb.waitForPresses()

# Run blocks
for block_idx in range(settings.total_blocks):
    # Create block
    block = BlockUnit(
        block_id=f"block_{block_idx}",
        block_idx=block_idx,
        settings=settings,
        window=win,
        keyboard=kb
    )
    
    # Generate conditions
    block.generate_conditions(
        func=generate_conditions,
        condition_labels=["congruent", "incongruent", "neutral"]
    )
    
    # Register block hooks
    @block.on_start()
    def show_block_instructions(b):
        instructions = visual.TextStim(
            win,
            text=f"Block {b.block_idx + 1} of {settings.total_blocks}\n\n" +
                 "Press LEFT for RED words\n" +
                 "Press RIGHT for BLUE words\n\n" +
                 "Ignore the word, respond to the color!\n\n" +
                 "Press any key to start",
            height=0.08
        )
        instructions.draw()
        win.flip()
        kb.waitForPresses()
    
    @block.on_end()
    def show_block_feedback(b):
        # Calculate accuracy
        correct_count = sum(1 for r in b.results if r.get("correct", False))
        accuracy = correct_count / len(b.results) * 100
        
        # Show feedback
        feedback = visual.TextStim(
            win,
            text=f"Block complete!\n\n" +
                 f"Accuracy: {accuracy:.1f}%\n\n" +
                 "Press any key to continue",
            height=0.08
        )
        feedback.draw()
        win.flip()
        kb.waitForPresses()
    
    # Run all trials in the block
    block.run_trial(run_stroop_trial)
    
    # Add results to overall results list
    block.to_dict(all_results)

# Show goodbye screen
goodbye = visual.TextStim(
    win,
    text="Experiment complete!\n\nThank you for participating.",
    height=0.1
)
goodbye.draw()
win.flip()
core.wait(3.0)

# Save results
df = pd.DataFrame(all_results)
df.to_csv(settings.res_file, index=False)

# Clean up
win.close()
core.quit()
```

## Advanced Usage

### Multiple Blocks with Different Conditions

You can create multiple blocks with different condition sets:

```python
# Block 1: Standard Stroop
block1 = BlockUnit("standard", 0, settings, win, kb)
block1.generate_conditions(generate_func, ["congruent", "incongruent"])
block1.run_trial(run_trial)

# Block 2: Emotional Stroop
block2 = BlockUnit("emotional", 1, settings, win, kb)
block2.generate_conditions(generate_func, ["neutral", "negative", "positive"])
block2.run_trial(run_emotional_trial)  # Different trial function
```

### Integration with StimBank and TriggerSender

`BlockUnit` works seamlessly with other psyflow components:

```python
from psyflow import StimBank, TriggerSender, BlockUnit
from functools import partial

# Create components
stim_bank = StimBank(win)
stim_bank.add_from_dict({
    "fixation": {"type": "TextStim", "text": "+"},
    "target_a": {"type": "TextStim", "text": "A"},
    "target_b": {"type": "TextStim", "text": "B"},
    "feedback": {"type": "TextStim", "text": "{score} points"}
})

trigger = TriggerSender(mock=True)

# Define trial function using components
def run_trial_with_components(win, kb, settings, condition, stim_bank, trigger, **kwargs):
    # Send block start trigger
    trigger.send(1)
    
    # Show fixation
    fixation = stim_bank.get("fixation")
    fixation.draw()
    win.flip()
    core.wait(0.5)
    
    # Show target based on condition
    target = stim_bank.get(f"target_{condition}")
    target.draw()
    win.flip()
    trigger.send(2)  # Target onset trigger
    
    # Wait for response
    keys = kb.waitForPresses(maxWait=1.0)
    
    # Process response
    if keys:
        trigger.send(3)  # Response trigger
        response = keys[0].name
        rt = keys[0].rt
    else:
        response = None
        rt = None
    
    # Return results
    return {"condition": condition, "response": response, "rt": rt}

# Create and run block with components
block = BlockUnit("block1", 0, settings, win, kb)
block.generate_conditions(generate_func, ["a", "b"])

# Use partial to include additional components
block.run_trial(
    partial(run_trial_with_components, stim_bank=stim_bank, trigger=trigger)
)
```

### Dynamic Trial Generation

You can implement adaptive procedures by generating trials dynamically:

```python
# Staircase procedure example
difficulty = 5  # Starting difficulty (1-10)

def adaptive_trial_generator(n, labels=None, seed=None):
    """Generate trials that adapt based on performance."""
    trials = []
    for i in range(n):
        trials.append({"difficulty": difficulty})
    return trials

block = BlockUnit("adaptive", 0, settings, win, kb)
block.generate_conditions(adaptive_trial_generator)

def run_adaptive_trial(win, kb, settings, condition, **kwargs):
    nonlocal difficulty
    
    # Get current difficulty
    current_difficulty = condition["difficulty"]
    
    # Run trial with current difficulty
    # ...
    
    # Adjust difficulty based on performance
    if correct:
        difficulty = min(10, difficulty + 1)  # Make harder
    else:
        difficulty = max(1, difficulty - 1)  # Make easier
    
    return {"difficulty": current_difficulty, "correct": correct}

block.run_trial(run_adaptive_trial)
```

## Best Practices

1. **Use meaningful block IDs**: Choose descriptive names that reflect the block's purpose (e.g., "practice", "main_task", "memory_test").

2. **Separate condition generation from trial execution**: Keep your condition generation function reusable and independent of the trial function.

3. **Use block hooks for setup/cleanup**: Put instructions, breaks, and other non-trial content in block hooks rather than in the trial function.

4. **Return comprehensive trial data**: Include all relevant information in your trial function's return dictionary.

5. **Use custom summarization for complex metrics**: Implement custom summary functions for specialized analyses.

6. **Save raw trial data**: Always save the complete trial-level data, not just summaries.

7. **Set appropriate seeds**: Use consistent seeds for reproducibility in experiments.

## Troubleshooting

- **Trial conditions not balanced**: Check your condition generation function and ensure it properly handles the requested number of trials.

- **Missing trial data**: Verify that your trial function returns a dictionary for every trial.

- **Block hooks not executing**: Ensure hooks are registered before calling `run_trial()`.

- **Performance issues**: If trials run slowly, optimize your trial function and avoid creating new stimuli on each trial.

## Next Steps

Now that you understand how to use `BlockUnit`, you can:

- Learn about [StimUnit](build_trialunit.md) for more control over individual trials
- Explore [StimBank](build_stimulus.md) for efficient stimulus management
- Check out [TriggerSender](send_trigger.md) for EEG/MEG experiment integration
- See [TaskSettings](getting_started.md) for experiment-wide configuration
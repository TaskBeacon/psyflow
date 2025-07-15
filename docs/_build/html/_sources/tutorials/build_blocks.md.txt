# BlockUnit: Managing Trials

## Overview

The `BlockUnit` class is a powerful tool for organizing trials in psychological experiments. It provides a structured way to manage trial sequences, generate balanced conditions, track results, and summarize performance metrics. This tutorial will guide you through using `BlockUnit` to create well-structured experimental blocks.

`BlockUnit` solves several common challenges in experimental design:

- **Condition balancing:** Generate trial conditions with proper randomization and counterbalancing
- **Trial sequencing:** Manage the flow of trials within a block
- **Data organization:** Automatically track trial-level data and block metadata
- **Block lifecycle:** Execute setup and cleanup operations at block boundaries
- **Result summarization:** Calculate performance metrics across trials and conditions

## Key Features

| Feature               | Description                                       |
| --------------------- | ------------------------------------------------- |
| Condition generation  | Create balanced, randomized trial sequences       |
| Block lifecycle hooks | Execute code before/after block execution         |
| Result tracking       | Automatically collect and organize trial data     |
| Summarization         | Calculate performance metrics by condition        |
| Metadata              | Track timing, trial counts, and block information |
| Integration           | Works seamlessly with other psyflow components    |

## Quick Reference

| Purpose                 | Method                                | Example                                               |
| ----------------------- | ------------------------------------- | ----------------------------------------------------- |
| Initialize block        | `BlockUnit(block_id, block_idx, ...)` | `block = BlockUnit("block1", 0, settings)`            |
| Generate conditions     | `.generate_conditions(func, labels)`  | `block.generate_conditions(generate_func, ["A","B"])` |
| Add conditions manually | `.add_condition(condition_list)`      | `block.add_condition(["A","B","A"])`                  |
| Register start hook     | `.on_start(func)`                     | `@block.on_start()` or `block.on_start(func)`         |
| Register end hook       | `.on_end(func)`                       | `@block.on_end()` or `block.on_end(func)`             |
| Run all trials          | `.run_trial(trial_func, **kwargs)`    | `block.run_trial(run_trial_function)`                 |
| Get results             | `.to_dict()`                          | `results = block.to_dict()`                           |
| Append results          | `.to_dict(target_list)`               | `block.to_dict(all_results)`                          |
| Summarize results       | `.summarize()`                        | `summary = block.summarize()`                         |
| Custom summary          | `.summarize(func)`                    | `summary = block.summarize(custom_func)`              |
| Log block info          | `.logging_block_info()`               | `block.logging_block_info()`                          |

## Detailed Usage Guide

### 1. Initialization

To create a `BlockUnit`, you need to provide basic information about the block and the experiment settings:

```python
from psyflow import BlockUnit

block = BlockUnit(
    block_id='block1',      # unique identifier
    block_idx=0,            # block index (0-based)
    settings=settings,      # TaskSettings instance
    window=win,             # PsychoPy Window
    keyboard=kb             # PsychoPy Keyboard
)
```

The `settings` parameter should be a `TaskSettings` object or similar that includes:

- `trials_per_block`: Number of trials in each block
- `block_seed`: Seed for random number generation (for reproducibility)
- `condition_list`: List of conditions

### 2. Generating Conditions

The `generate_conditions()` method provides a built-in, balanced (or weighted) generator to create a sequence of condition labels of length `n_trials`. Key parameters:

- `condition_labels`: List of labels to use for this block (defaults to `settings.conditions`).
- `weights`: Relative weights for each label (defaults to equal weights).
- `order`: `'random'` or `'sequential'`—controls final sequence arrangement.
- `seed`: Random seed override for reproducible shuffling.

**Weighted Generation Algorithm**

This method first computes each label’s base count as `floor(n_trials * weight / total_weight)`, then distributes any leftover trials randomly according to the given weights. Finally, it constructs the full sequence by either interleaving labels in their specified order or shuffling the complete list, based on the `order` parameter.

**Setting Weights**::

```
# Make 'A' twice as likely as 'B'
block.generate_conditions(
    condition_labels=['A', 'B'],
    weights=[2, 1],
    order='random',
    seed=42
)
```

Expected ratio A\:B ≈ 2:1, subject to rounding and random distribution of remainder.

**Order Modes**:

- **Sequential**: Ensures interleaved, cyclic presentation of conditions in the original label order.\
  *Example*: In a resting-state experiment with two conditions—`ec` (eyes closed) and `eo` (eyes open)—using `order='sequential'` produces `['ec','eo','ec','eo']`, alternating blocks predictably.
- **Random**: Provides a fully shuffled sequence, respecting label weights.\
  *Example*: With the same `ec`/`eo` settings and `order='random'`, the sequence might be `['ec','ec','eo','eo']` or any other random arrangement.

**Examples**:

```python
# Default: use settings.conditions, equal weights, random order
block.generate_conditions()

# Custom labels and sequential order
block.generate_conditions(
    condition_labels=['X', 'Y', 'Z'],
    weights=[1, 1, 2],
    order='sequential'
)
```

**Custom Condition Generator**

For specialized block designs—such as a Stop-Signal Task (SST) where you need specific constraints on stop/go ratios, run lengths, and starting trials—you can supply your own generator function. Your function must have the signature:

```python
def gen_func(n_trials, condition_labels=None, seed=None, **kwargs) -> List[str]:
    ...
```

**Example: SST condition generator**

This custom function generates condition sequences for a Stop-Signal Task (SST), enforcing:

- A fixed stop-to-go trial ratio (`stop_ratio`).
- A maximum run length of consecutive stop trials (`max_stop_run`).
- A minimum number of initial go trials (`min_go_start`).
- Preservation of the global random state via a local RNG.

```python
import random
from typing import List, Optional

def generate_sst_conditions(
    n_trials: int,
    condition_labels: Optional[List[str]] = None,
    stop_ratio: float = 0.25,
    max_stop_run: int = 4,
    min_go_start: int = 3,
    seed: Optional[int] = None
) -> List[str]:
    """
    Generates an SST sequence while preserving global RNG state.
    """
    # 1) Default labels if none provided
    if condition_labels is None:
        condition_labels = ['go_left', 'go_right', 'stop_left', 'stop_right']
    go_labels   = [lbl for lbl in condition_labels if lbl.startswith('go')]
    stop_labels= [lbl for lbl in condition_labels if lbl.startswith('stop')]

    # 2) Compute trial counts
    n_stop = int(round(n_trials * stop_ratio))
    n_go   = n_trials - n_stop
    base_go, rem_go   = divmod(n_go,   len(go_labels))
    base_st, rem_st   = divmod(n_stop, len(stop_labels))

    counts = {}
    for i, lbl in enumerate(go_labels):
        counts[lbl] = base_go + (1 if i < rem_go else 0)
    for i, lbl in enumerate(stop_labels):
        counts[lbl] = base_st + (1 if i < rem_st else 0)

    # 3) Build and shuffle with constraints
    trial_list = [lbl for lbl, cnt in counts.items() for _ in range(cnt)]
    rng = random.Random(seed)

    while True:
        rng.shuffle(trial_list)
        # a) First min_go_start trials must be 'go'
        if any(lbl.startswith('stop') for lbl in trial_list[:min_go_start]):
            continue
        # b) No more than max_stop_run stops in any 5-trial window
        violation = False
        for i in range(n_trials - 4):
            window = trial_list[i:i+5]
            if sum(lbl.startswith('stop') for lbl in window) > max_stop_run:
                violation = True
                break
        if not violation:
            break

    return trial_list

# Use it in BlockUnit:
block.generate_conditions(
    func=generate_sst_conditions,
    condition_labels=['go_left','go_right','stop_left','stop_right'],
    seed=123
)
print(block.conditions)
```

The custom generator is applied by passing it as the `func` argument to `generate_conditions()`. 

For example, to use `generate_sst_conditions` when constructing a block:

```python
block = BlockUnit(
    block_id=f"block_{block_i}",
    block_idx=block_i,
    settings=settings,
    window=win,
    keyboard=kb
).generate_conditions(
    func=generate_sst_conditions
)
```

This single call both creates the block and generates its trial conditions according to the SST constraints, storing the resulting sequence in `block.conditions`.

**Manual Condition Assignment**

If the exact sequence of conditions is predetermined, bypass the generator entirely:

```python
# Predefined block sequence for alternating ec/eo
manual_seq = ['ec','eo','ec','eo']
block.add_condition(manual_seq)
print(block.conditions)
```

### 3. Hooks: on\_start and on\_end

Hooks allow injection of custom logic at the beginning or end of each block, without modifying the core trial loop. Common uses include:

- **Triggering hardware events** (e.g., sending EEG or MRI triggers)
- **Updating GUI elements** (e.g., showing block progress or instructions)
- **Logging or analytics** (e.g., timestamping additional metrics)

Hooks can be registered in two ways:

1. **Decorator style**:
   ```python
   @block.on_start()
   def before_block(b):
       # Custom setup
       print(f"Starting block {b.block_id}")

   @block.on_end()
   def after_block(b):
       # Custom cleanup
       print(f"Ending block {b.block_id}")
   ```
2. **Chaining style**:
   ```python
   block = BlockUnit(...)
   block.on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset")))
        .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end")))
   ```

**Example: sending triggers at block boundaries**

```python
block = BlockUnit(
    block_id=f"block_{block_i}",
    block_idx=block_i,
    settings=settings,
    window=win,
    keyboard=kb
).generate_conditions(func=generate_sst_conditions)
  .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset")))
  .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end")))
```

This setup ensures that a trigger or an external event is sent precisely when the block begins and ends, integrated seamlessly into the block execution flow.

### 4. Running Trials

The `.run_trials()` method drives the execution of every trial in the block by repeatedly calling a user‑defined trial function. The function is typically implemented in the TAPS codebase under `src/run_trial.py` and encapsulates all trial‑level logic (e.g., stimulus presentation, response capture, triggers).

**Signature:**

```python
block.run_trials(
    trial_func,
    **kwargs
)
```

- `trial_func` (callable, required): the trial‑level function. Must accept four mandatory arguments:
  1. `win` (PsychoPy Window)
  2. `kb` (PsychoPy Keyboard)
  3. `settings` (TaskSettings)
  4. `condition` (str or label) Additional parameters (e.g., `stim_bank`, `controller`, `trigger_sender`) can be passed via `kwargs` and are optional—include them only if your `trial_func` uses them.

> **Note:** Register all `on_start` and `on_end` hooks **before** calling `.run_trials()`, as they are invoked inside this method.

**Execution flow:**

1. **Start timestamp**: saves `meta['block_start_time']`.
2. **hooks**: runs block‑start callbacks (e.g., triggers).
3. **Per‑trial loop**:
   ```python
   result = trial_func(
       block.win,
       block.kb,
       block.settings,
       condition,
       **kwargs
   )
   ```
4. **hooks**: runs block‑end callbacks.
5. **End timestamp & duration**: sets `meta['block_end_time']` and `meta['duration']`.

#### **Resting‑state example**

This trial function displays an instruction screen followed by a simple stimulus, without response collection.

```python
from psyflow import StimUnit
from functools import partial

def run_trials(win, kb, settings, condition, stim_bank, trigger_sender):
    data = {'condition': condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)

    # Instruction only
    make_unit('inst') \
        .add_stim(stim_bank.get(f"{condition}_instruction")) \
        .show() \
        .to_dict(data)

    # Stimulus only
    make_unit('stim') \
        .add_stim(stim_bank.get(f"{condition}_stim")) \
        .show(duration=settings.rest_duration) \
        .to_dict(data)

    return data

block.run_trials(run_trials, stim_bank=stim_bank, trigger_sender=trigger_sender)
```
#### **MID task example**
Implements a multi‑phase trial (cue → anticipation → target → feedback), using the `controller` to adapt durations and recording responses.

```python
from psyflow import StimUnit
from functools import partial

def run_trials(win, kb, settings, condition, stim_bank, controller, trigger_sender):
    data = {'condition': condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)

    # Cue phase
    make_unit('cue') \
        .add_stim(stim_bank.get(f"{condition}_cue")) \
        .show(duration=settings.cue_duration) \
        .to_dict(data)

    # (anticipation, target, feedback phases follow similar patterns)

    return data

block.run_trials(run_trials, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender)
```

### 5. Accessing & Filtering Data

To extract and analyze block-level outcomes, use two core methods:

1. **Retrieve all trials** with `.get_all_data()`, which returns an ordered list of all trial dictionaries in the block.
2. **Filter specific trials** with `.get_trial_data(key, pattern, match_type, negate)`, selecting subsets that match given criteria.

#### Example: MID block summary using `.get_all_data()`

In a Monetary Incentive Delay (MID) task, you typically calculate overall performance metrics across all trials of a block:

```python
# Retrieve every trial in order
block_trials = block.get_all_data()

# Compute hit rate: proportion of trials where 'target_hit' is True
total_trials = len(block_trials)
hit_trials = sum(t.get('target_hit', False) for t in block_trials)
hit_rate = hit_trials / total_trials

# Compute total feedback score across trials
total_score = sum(t.get('feedback_delta', 0) for t in block_trials)
```

Here, `.get_all_data()` provides the full trial dataset, and simple list comprehensions produce summary statistics for the block.

#### Example: SST block analysis using `.get_trial_data()`

In a Stop-Signal Task (SST), separate go and stop trials for distinct performance metrics:

```python
# Filter trials by condition prefix
go_trials = block.get_trial_data(
    key='condition',
    pattern='go',
    match_type='startswith'
)
stop_trials = block.get_trial_data(
    key='condition',
    pattern='stop',
    match_type='startswith'
)

# Go-trial hit rate
total_go = len(go_trials)
go_hits = sum(t.get('go_hit', False) for t in go_trials)
go_hit_rate = go_hits / total_go if total_go else 0

# Stop-trial success rate (no key presses)
total_stop = len(stop_trials)
stops_success = sum(
    not t.get('go_ssd_key_press', False) and not t.get('stop_key_press', False)
    for t in stop_trials
)
stop_success_rate = stops_success / total_stop if total_stop else 0
```

`.get_trial_data()` filters by matching the `'condition'` field against a pattern, allowing downstream calculations on each trial subset.

### 6. Summarizing Block Results

For full flexibility, it is often preferable to compute block‑level summaries manually using the data retrieval methods covered above. This ensures that the statistics match exactly the fields produced by your trial logic. Two common patterns are:

#### Manual summarization using `.get_all_data()` (e.g., MID task)

Use `.get_all_data()` to obtain every trial’s result dict in order, then apply simple Python expressions to compute block metrics. In a Monetary Incentive Delay (MID) experiment, you might calculate overall hit rate and total score as follows:

```python
# Fetch all trial data
block_trials = block.get_all_data()

# Hit rate: proportion of trials where the target was hit
total_trials = len(block_trials)
hit_count    = sum(trial.get('target_hit', False) for trial in block_trials)
hit_rate     = hit_count / total_trials

# Total feedback score (delta) across the block
total_score  = sum(trial.get('feedback_delta', 0) for trial in block_trials)
```

This approach works for any field your `run_trials` function stores. Simply adjust the comprehensions to target the relevant keys.

#### Manual summarization using `.get_trial_data()` (e.g., SST task)

When different trial types require separate metrics—as in a Stop‑Signal Task (SST) with go vs. stop trials—use `.get_trial_data()` to filter the block’s trials, then summarize each subset:

```python
# Separate go and stop trials by condition prefix
go_trials   = block.get_trial_data(
    key='condition', pattern='go', match_type='startswith'
)
stop_trials = block.get_trial_data(
    key='condition', pattern='stop', match_type='startswith'
)

# Go-trial hit rate
total_go     = len(go_trials)
go_hits      = sum(trial.get('go_hit', False) for trial in go_trials)
go_hit_rate  = go_hits / total_go if total_go else 0

# Stop-trial success rate (no responses on stop trials)
total_stop        = len(stop_trials)
stop_success_count = sum(
    not trial.get('go_ssd_key_press', False) and not trial.get('stop_key_press', False)
    for trial in stop_trials
)
stop_success_rate = stop_success_count / total_stop if total_stop else 0
```

####  Built‑in `.summarize()` utility

`BlockUnit` also provides a default summarizer that computes hit rate and average reaction time per condition:

```python
summary = block.summarize()
# Example output:
# {
#   'A': {'hit_rate': 0.75, 'avg_rt': 0.48},
#   'B': {'hit_rate': 0.62, 'avg_rt': 0.55}
# }
```

To override this behavior, supply a custom function that accepts the `BlockUnit` and returns a dictionary of summary metrics. Below is an example tailored for an SST block:

```python
import numpy as np

def sst_summary(bu):
    """Compute go hit rate and stop success rate for SST blocks."""
    # Retrieve all trials
    trials = bu.get_all_data()
    # Separate go and stop trials
    go_trials = bu.get_trial_data('condition', 'go', match_type='startswith')
    stop_trials = bu.get_trial_data('condition', 'stop', match_type='startswith')

    # Go-trial hit rate
    total_go = len(go_trials)
    go_hits = sum(t.get('go_hit', False) for t in go_trials)
    go_hit_rate = go_hits / total_go if total_go else 0

    # Stop-trial success rate (no responses)
    total_stop = len(stop_trials)
    stop_success = sum(
        (not t.get('go_ssd_key_press', False)) and not t.get('stop_key_press', False)
        for t in stop_trials
    )
    stop_success_rate = stop_success / total_stop if total_stop else 0

    return {
        'go_hit_rate': go_hit_rate,
        'stop_success_rate': stop_success_rate
    }

# Use the custom summarizer
summary = block.summarize(summary_func=sst_summary)
```

### 7. Storing Block-Level Data

After each block finishes, its trial results (stored in `block.results`) can be merged into a master list for the entire experiment using the `.to_dict()` method. This method supports two modes:

- **Chaining mode**: Calling `.to_dict()` with no argument simply returns the `BlockUnit` instance, allowing you to chain other calls.
- **Append mode**: Passing a list to `.to_dict(target_list)` extends that list with the block’s trial dictionaries.

```python
# Initialize an empty list to collect all trials
all_data = []

for block_i in range(settings.total_blocks):
    # Prepare and run block, then append its results
    BlockUnit(
        block_id=f"block_{block_i}",
        block_idx=block_i,
        settings=settings,
        window=win,
        keyboard=kb
    ).generate_conditions() \
     .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset"))) \
     .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end"))) \
     .run_trials(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender) \
     .to_dict(all_data)

# At this point, all_data contains every trial dict from all blocks

# Convert to DataFrame and save to CSV
import pandas as pd
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)
```

> **Alternative:** you can call `block.get_all_data()` after running a block and extend your list manually:
>
> ```python
> block.run_trials(...)
> block_data = block.get_all_data()
> all_data.extend(block_data)
> ```

### 8. Logging Block Info

`BlockUnit` logs metadata at start and end automatically:

```
[BlockUnit] Blockid: block1
[BlockUnit] Blockidx: 0
[BlockUnit] Blockseed: 12345
[BlockUnit] Blocktrial-N: 40
[BlockUnit] Blockdist: {'A':20,'B':20}
[BlockUnit] Blockconditions: ['A','B',...]
```

## Next Steps

Now that you understand how to use `BlockUnit`, you can:

- **Build Trials**: Learn about [StimUnit](build_stimunit.md) for more control over individual trials
- **Manage Stimuli**: Explore [StimBank](build_stimulus.md) for efficient stimulus management
- **Send Triggers**: Check out [TriggerSender](send_trigger.md) for EEG/MEG experiment integration
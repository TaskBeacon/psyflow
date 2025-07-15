# StimUnit: Modular Stimulus & Response Handler

## Overview

`StimUnit` is a versatile, stimulus-level controller for PsychoPy experiments. It bundles everything you need for one trial into a single, chainable object:

- **Stimulus presentation**: Draw multiple visual or audio stimuli together with sub-frame accuracy.
- **Response collection**: Detect keyboard events and record reaction times effortlessly.
- **Timing control**: Opt for frame-based (refresh-locked) or clock-based timing based on your needs.
- **State management**: Store all trial-related data in a centralized internal dictionary.
- **Event hooks**: Plug in custom callbacks at start, response, timeout, and end stages.

By using `StimUnit`, your trial logic (typically defined in `src/run_trial.py`) becomes more modular, readable, and maintainable.

## Key Features

| Feature                | Description                                                    |
| ---------------------- | -------------------------------------------------------------- |
| **Chainable API**      | Build trials fluently by chaining methods.                     |
| **Frame-based Timing** | High precision  |
| **Event hooks**        | Call custom functions on start, response, timeout, or end.     |
| **Flexible responses** | Specify valid keys and automatic RT handling.                  |
| **State tracking**     | Centralized storage of timestamps, responses, and custom data. |
| **Response highlight** | Visually emphasize selections (static or dynamic).             |
| **Jittered timing**    | Support randomized (min–max) durations for unpredictability.   |

## Quick Reference

| Purpose            | Method                              | Example                                        |
| ------------------ | ----------------------------------- | ---------------------------------------------- |
| Initialize         | `StimUnit(label, win, kb)`          | `unit = StimUnit("cue", win, kb)`              |
| Add stimuli        | `.add_stim(stim1, stim2, ...)`      | `unit.add_stim(fixation, target)`              |
| Start hook         | `.on_start(fn)`                     | `@unit.on_start()`                             |
| Response hook      | `.on_response(keys, fn)`            | `@unit.on_response(['left','right'])`          |
| Timeout hook       | `.on_timeout(sec, fn)`              | `@unit.on_timeout(2.0)`                        |
| End hook           | `.on_end(fn)`                       | `@unit.on_end()`                               |

| Simple display     | `.show(duration)`                   | `unit.show(1.0)`                               |
| Response capture   | `.capture_response(keys, duration)` | `unit.capture_response(['left','right'], 2.0)` |
| Full trial control | `.run()`                            | `unit.run()`                                   |
| Pause & continue   | `.wait_and_continue(keys)`          | `unit.wait_and_continue(['space'])`            |
| Update state       | `.set_state(**kwargs)`              | `unit.set_state(correct=True)`                 |
| Retrieve state     | `.get_state()` or access `.state`     | `data = unit.get_state(key,default)`                        |
| Export state     | `.to_dict()`      | `data = unit.to_dict()`                        |

## Detailed Usage Guide

### 0. Create a StimBank
```python
from psyflow.stim_bank import StimBank
# 1. Define a dictionary of stimulus configurations
stim_config = {
    'fixation': {
        'type': 'text',
        'text': '+',
        'color': 'white',
        'height': 1.0
    },
    'target': {
        'type': 'circle',
        'radius': 0.5,
        'fillColor': 'red'
    },
    'feedback': {
        'type': 'text',
        'text': 'Correct!',
        'pos': [0, -2],
        'color': 'green'
    }
}

# 2. Create your StimBank with window and definitions
stim_bank = StimBank(win, stim_config)
stim_bank.preload_all()  # optional
```


### 1. Initialization

Start by creating your PsychoPy window and keyboard, then instantiate `StimUnit` with a descriptive label.

```python

win = visual.Window([1024,768], color='black')
kb = Keyboard()

# Instantiate StimUnit
fix = StimUnit('fix', win, kb).add_stim(stim_bank.get('fixation'))
tar = StimUnit('tar', win, kb).add_stim(stim_bank.get('target'))
fb = StimUnit('fb', win, kb).add_stim(stim_bank.get('feedback'))
```

Choose descriptive `unit_label`s (e.g., `"fix"`, `"tar"`, `"fb"`). These labels are automatically prefixed to your state keys when you call `set_state()` and accessed by `get_state()`, ensuring your trial data is neatly namespaced and easy to query.

**Pro tip:** When you need to create many similar trial units in the same context, use Python’s `functools.partial` to simplify instantiation:

```python
from functools import partial
# Create a shortcut with common arguments
make_unit = partial(StimUnit, win=win, kb=kb)

# --- Cue phase ---
fix=make_unit('fix').add_stim(stim_bank.get('fixation'))
tar=make_unit('tar').add_stim(stim_bank.get('target'))
fb=make_unit('fb').add_stim(stim_bank.get('feedback'))
```


### 2. Adding Stimuli

Before presenting a trial, attach the stimuli you want to display or play—this defines what participants will see or hear during the unit.

StimUnit accepts instances of `visual.BaseVisualStim` (e.g., `TextStim`, `Circle`) and `sound.Sound`. You can add a single stimulus, multiple stimuli at once, or pass a list of stimuli:

```python
# Add a single stimulus
unit.add_stim(stim_bank.get('fixation'))

# Add multiple stimuli at once
unit.add_stim(
    stim_bank.get('target'),
    stim_bank.get('feedback')
)

# Add a list of stimuli
unit.add_stim([
    stim_bank.get('fixation'),
    stim_bank.get('target'),
    stim_bank.get('feedback')
])

# Chain additions 
unit.add_stim(stim_bank.get('fixation')) \
    .add_stim(stim_bank.get('target')) \
    .add_stim(stim_bank.get('feedback'))

# Clear all stimuli
unit.clear_stimuli()
```

All added stimuli will be drawn or played together when you present the unit. 

Note that `add_stim` also support PsychoPy style definitions of the stimulus. For exmaple:
```python
from psychopy.visual import TextStim, Circle
# Example 1
stim_list = {'fix': TextStim(win, text='+', pos=(0,0)), 
            'tar': Circle(win, radius=0.5, fillColor='red'),
            'fb': TextStim(win, text='Correct!', pos=(0,0))}
unit.add_stim(stim_list['fix']).add_stim(stim_list['tar']).add_stim(stim_list['fb'])

# Example 2
fixation = visual.TextStim(win, text='+', height=0.8)
unit.add_stim(fixation)
unit.show(duration=(0.5, 1.5))
```
In the `psyflow` framework, stimuli are normally retrieved from a `stim_bank` object. 
This lets you quickly retrieve named stimuli from your `stim_bank` and pass them into a `StimUnit`, streamlining stimunit setup. For example:
```python
condition = 'loss'
make_unit(unit_label='cue').add_stim(stim_bank.get(f"{condition}_cue"))
make_unit(unit_label=f"pop")\
    .add_stim(stim_bank.get(f"{condition}_pop"))\
    .add_stim(stim_bank.get("pop_sound"))
```

### 3. Display stimulus with `show()`

The `show()` method is the core display function in `StimUnit`. It handles precise timing, drawing, optional audio playback, and state logging—all in one call. Use it when you want to present stimuli without requiring responses.


**Key Features of `show()`**
- **Frame-based timing**: Locks presentation to monitor refreshes for sub-frame precision.
- **Automatic audio support**: Starts any sound stimuli on the first flip.
- **Flexible duration**: Accepts fixed times, jittered ranges, or automatically uses sound length.
- **State logging**: Records onset/offset timestamps and duration into `unit.state`.


Use this method when you need standalone stimulus presentation without response handling:
- **Feedback Displays**: Show feedback messages or sounds (e.g., "Correct!", error tones) for a short duration.
- **Passive Stimulus Presentation**: Present visual or auditory stimuli (e.g., flicker, tones) in paradigms where responses are recorded separately, such as resting-state EEG or fMRI.
- **Baseline/Rest Periods**: Present fixation crosses or blank screens for jittered durations to serve as inter-trial intervals or baselines.

#### Method Signature

```python
.show(
    duration: float | tuple[float, float] | None = None,
    onset_trigger: int = None,
    offset_trigger: int = None
) -> StimUnit
```

- `duration`:

  - **None**: Uses the longest `getDuration()` of your sound stimuli (0.0 if none).
  - **float**: A fixed presentation time in seconds.
  - **(min, max)**: Uniformly randomize between `min` and `max`.

- `onset_trigger` / `offset_trigger`: *(optional)* placeholder parameters for sending triggers—these are ignored if you manage triggers separately.

#### Behavior Table

| Input Duration          | Behavior                                      |
| ----------------------- | --------------------------------------------- |
| `None`                  | Auto-select from audio (max duration or 0.0). |
| `0.5`                   | Present for exactly 0.5 s.                    |
| `(0.8, 1.2)`            | Sample in [0.8, 1.2] s.                       |
| `1.0` + audio of 2.5 s  | Screen stops at 1.0 s; audio may be cut off.  |
| `None` + audio of 2.5 s | Both screen & audio last full 2.5 s.          |

The following examples demonstrate how to use `.show()` for fixed, jittered, and audio-driven durations. Assume `unit` is an initialized `StimUnit` and `stim_bank` contains your stimuli.

```python
# 1. Fixed duration – shows text for exactly 1.0 second
unit.add_stim(stim_bank.get('fixation'))\
    .show(duration=1.0)

# 2. Jittered duration – shows text for a random time between 1 and 2s
unit.add_stim(stim_bank.get('fixation'))\
    .show(duration=(1,2)) #tuple

unit.add_stim(stim_bank.get('fixation'))\
    .show(duration=[1,2]) #list

# 3. Auto from audio – shows visual and plays audio for the full sound duration
unit.add_stim(stim_bank['pop_sound']).show() # duration=None is default

# 4. Multiple stimuli
unit.add_stim(stim_bank.get('pop_sound'))\
    .add_stim(stim_bank.get('fixation'))\
    .show(duration=None)
```



### 4. Pause & Continue with `wait_and_continue()`

Use `.wait_and_continue()` to display stimuli and wait for participant input before proceeding, ideal for instruction screens, inter-block breaks, and end-of-experiment acknowledgments. It enforces a minimum display time and can optionally terminate the session after the key press.

Use this method when you need participants to confirm or acknowledge before moving on, without capturing a trial response. Common scenarios include:
- **Instruction screens**: e.g., "Press SPACE to start" before an experiment block.
- **Inter-block breaks**: Giving participants a chance to rest and proceed when ready.
- **End-of-experiment messages**: Display a thank‑you note or debrief until key press.
- **Any standalone confirmation**: When you don’t need to record response data but require an explicit continuation.

#### Method Signature

```python
def wait_and_continue(
    keys: list[str] = ["space"],
    min_wait: Optional[float] = None,
    log_message: Optional[str] = None,
    terminate: bool = False
) -> StimUnit
```

- `keys`: List of keys that allow continuation (default `['space']`).
- `min_wait`: Minimum seconds to wait before accepting input. If `None`, and audio stimuli are present, it defaults to the longest sound duration. If only visual stimuli are present, it defaults to infinite until the button preseed.
- `log_message`: Custom message logged to PsychoPy’s log (defaults to:
  - “Continuing after key 'X'” or
  - “Experiment ended by key press.” if `terminate=True`).
- `terminate`: If `True`, closes the PsychoPy window after input.

**Example**
```python
# Instruction screen: wait at least 2s for SPACE
StimUnit('instruction_text', win, kb)\
    .add_stim(stim_bank.get('instruction_text'))\
    .add_stim(stim_bank.get('instruction_text_voice'))\
    .wait_and_continue()

# End screen: immediate termination on key
final_score = sum(trial.get("feedback_delta", 0) for trial in all_data)
StimUnit('goodbye',win,kb)\
    .add_stim(stim_bank.get_and_format('good_bye', total_score=final_score))\
    .wait_and_continue(terminate=True)
```


### 6. Get responses with `capture_response()`

The `capture_response()` method in `StimUnit` integrates stimulus presentation, timing, triggers, and response handling into a single, chainable call. It is ideal for:

- Detecting and logging subject responses within a predefined response window
- Determining correct versus incorrect responses for performance analysis
- Delivering immediate visual feedback by highlighting participant selections

#### Features
- Capturing and logging participant choices within precise time windows
- Sending and receiving hardware triggers (e.g., EEG/fMRI) in sync with stimuli
- Differentiating correct vs. incorrect responses for performance metrics
- Providing both static and dynamic visual feedback based on key presses

#### Method Signature

```python
def capture_response(
    keys: list[str],
    duration: float | tuple[float, float],
    onset_trigger: int = None,
    response_trigger: int | dict[str, int] = None,
    timeout_trigger: int = None,
    terminate_on_response: bool = True,
    correct_keys: list[str] | None = None,
    highlight_stim: visual.BaseVisualStim | dict[str, visual.BaseVisualStim] = None,
    dynamic_highlight: bool = False
) -> StimUnit
```

- `key`: Valid response keys.
- `duration`: Response window (fixed or jittered range).
- `terminate_on_response`: If `True`, stops redrawing after a valid response.
- `correct_keys`: Subset of `keys` to be treated as correct responses (for state logging).
- `highligt_stim`: A stim (or dict mapping keys→stim) to draw around the selected choice.
- `dynamic_highlight`: If `True`, highlights update on every keypress instead of just the first.

Below is the signature and four practical scenarios illustrating its use.

#### Scenario 1: Simple Anticipation Phase (detect early responses without termination)
In an anticipation phase of MID task, we want to monitor for any key presses but continue presenting the fixation cross even if the participant responds early. After the window, we record whether there was an early response.

```python
# --- Anticipation phase ---
anti = make_unit(unit_label='anticipation') \
    .add_stim(stim_bank.get("fixation"))
anti.capture_response(
    keys=settings.key_list,
    duration=settings.anticipation_duration,
    onset_trigger=settings.triggers[f"{condition}_anti_onset"],
    terminate_on_response=False
)

# After capture_response returns, check and store early response
early_response = anti.get_state("response", False)
anti.set_state(early_response=early_response)
anti.to_dict(trial_data)
```

- `terminate_on_response=False` ensures the fixation stays on screen for the full anticipation duration, regardless of key presses.
- After running, `anti.get_state("response")` tells whether any key was pressed.



#### Scenario 2: Target Phase with Required Response
In the target phase of the MID task, we require a response. Here we use default settings where keys in the `keys=settings.key_list` count as potential responses, and no separate `correct_keys` are defined. By default, `correct_keys=None`, so any key in `keys=settings.key_list` is counted as a correct response.

```python
# --- Target phase ---
duration = controller.get_duration(condition)
target = make_unit(unit_label="target") \
    .add_stim(stim_bank.get(f"{condition}_target"))

target.capture_response(
    keys=settings.key_list,
    duration=duration,
    onset_trigger=settings.triggers[f"{condition}_target_onset"],
    response_trigger=settings.triggers[f"{condition}_key_press"],
    timeout_trigger=settings.triggers[f"{condition}_no_response"]
)

target.to_dict(trial_data)
```

- By default, `correct_keys=None`, so any key in `keys` is logged as a response.
- `response_trigger` and `timeout_trigger` send triggers for EEG/behavior marking.



#### Scenario 3: Detecting Correct vs. Incorrect Responses
In tasks where only one key is correct (e.g., left vs. right dot detection), specify `correct_keys` to log hits vs. misses.

```python
# Determine which key is correct based on target position
target_stim = stim_bank.get(f"{trial_info['target_position']}_target")
correct_key = (
    settings.left_key
    if trial_info['target_position'] == 'left'
    else settings.right_key
)

target_unit = make_unit(unit_label="target") \
    .add_stim(target_stim)

target_unit.capture_response(
    keys=settings.key_list,
    correct_keys=[correct_key],
    duration=settings.target_duration,
    onset_trigger=settings.triggers[f"{condition}_target_onset"],
    response_trigger=settings.triggers.get("key_press"),
    timeout_trigger=settings.triggers.get("no_response"),
    terminate_on_response=True
)

target_unit.to_dict(trial_data)
```

- `correct_keys` filters which responses count as hits. The boolean `hit` state is set accordingly.
- `terminate_on_response=True` ends the trial on the first valid key press.


#### Scenario 4: Highlighting Participant Choices
To provide visual feedback, pass a dictionary of highlight stimuli to draw around the chosen option. Use `dynamic_highlight=True` to allow participants to change their selection during the window.

```python
cue = make_unit(unit_label="cue") \
    .add_stim(stim_bank.get('stimA')) \
    .add_stim(stim_bank.get('stimB'))

correct_key = settings.left_key  # for example

cue.capture_response(
    keys=settings.key_list,
    correct_keys=[correct_key],
    duration=settings.cue_duration,
    onset_trigger=settings.triggers['cue_onset'] + marker_pad,
    response_trigger=settings.triggers['key_press'] + marker_pad,
    timeout_trigger=settings.triggers['no_response'] + marker_pad,
    terminate_on_response=False,
    highlight_stim={
        'f': stim_bank.get('highlight_left'),
        'j': stim_bank.get('highlight_right')
    },
    dynamic_highlight=False
)

cue.to_dict(trial_data)
```

- `highlight_stim` maps each key to a visual cue (e.g., a frame or dot).
- If `dynamic_highlight=True`, each new key press updates the highlight until the window ends.

```{Tip}
You can also pass a `dict` to `response_trigger` to send different trigger codes per key.
```


### 7. Lifecycle Hooks

Lifecycle hooks give you maximum flexibility to define custom behaviors at key trial events—complementing built‑in methods like `.capture_response()` or `.show()`. You pick exactly what code runs during **start**, **response**, **timeout**, and **end** phases.

Below is a complete example demonstrating how each hook operates in practice. Watch how state keys are automatically prefixed with your `unit_label` ("demo"):

```
from psychopy import core, visual
from psychopy.hardware.keyboard import Keyboard
from psyflow import StimUnit

# 1. Setup
win = visual.Window([800,600], color='black', units='deg')
kb  = Keyboard()
unit = StimUnit('demo', win, kb)

# 2. Add a stimulus
fix = visual.TextStim(win, text='+', height=1.0)
unit.add_stim(fix)

# 3. Define hooks
@unit.on_start()
def start_hook(u):
    # record the moment the trial begins
    u.set_state(start_time=u.clock.getTime())
    print(f"[start_hook] prefix key 'demo_start_time' = {u.state['demo_start_time']}")

@unit.on_response(['space'])
def response_hook(u, key, rt):
    # capture spacebar presses
    u.set_state(response=key, rt=rt)
    print(f"[response_hook] key={key}, rt={rt:.3f}")

@unit.on_timeout(1.0)
def timeout_hook(u):
    # handle no-response after 1 second
    u.set_state(timeout=True)
    print("[timeout_hook] no response within 1.0s")

@unit.on_end()
def end_hook(u):
    # finalize and inspect full state
    data = u.to_dict()
    print("[end_hook] final state:", data)

# 4. Run the trial
unit.run()
```

**Explanation:**

- **start\_hook**: Fires immediately after the global start time is recorded and before the first screen flip.
- **response\_hook**: Executes on `'space'` press, providing `(unit, key, rt)`.
- **timeout\_hook**: Triggers if no response occurs within 1.0 second.
- **end\_hook**: Runs after the trial finishes but before logging, giving you a final chance to inspect or modify data.

All calls to `u.set_state()` automatically add entries like `demo_start_time`, `demo_response`, and `demo_timeout` into `unit.state`, which you can retrieve with `unit.to_dict()` or view in your PsychoPy logs via `unit.log_unit()`.

Instead of decorators, you can register hooks fluently via chaining for concise code:

```
unit = StimUnit('chain_demo', win, kb)  

# Chain registrations and run in one statement
unit.add_stim(fix)  
    .on_start(lambda u: u.set_state(start=time.time()))  
    .on_response(['space'], lambda u, k, rt: u.set_state(response=k, rt=rt))  
    .on_timeout(1.0, lambda u: u.set_state(timeout=True))  
    .on_end(lambda u: print('Chained final state:', u.to_dict()))  
    .run()
```
While `.show()` and `.capture_response()` bundle common patterns, you can achieve the same behavior using lifecycle hooks for greater customization.

#### Replicating `show()` with Hooks
```python
unit = StimUnit('show_demo', win, kb)
unit.add_stim(my_stim)

# Start: send onset trigger, record time
@unit.on_start()
def start_show(u):
    u.win.callOnFlip(u.send_trigger, trigger_onset)
    u.set_state(onset_time=u.clock.getTime())

# Timeout after desired duration: send offset trigger, record close time
@unit.on_timeout(show_duration)
def end_show(u):
    u.send_trigger(trigger_offset)
    u.set_state(close_time=u.clock.getTime())

# End hook for any cleanup or logging
@unit.on_end()
def finalize_show(u):
    print('Show ended, state:', u.get_dict())

# Run without terminating on response (no responses listened for)
unit.run(terminate_on_response=False)
```
- on_start sets up the flip‑synchronized onset trigger and timestamps.
- on_timeout fires after show_duration, mirroring offset_trigger.
- on_end finalizes the trial.

For a more fluent style, you can register hooks and configure trials in a chainable manner:
```python
make_unit('show_chain', win, kb) \
    .add_stim(my_stim) \
    .on_start(lambda u: (
        u.win.callOnFlip(u.send_trigger, trigger_onset),
        u.set_state(onset_time=u.clock.getTime())
    )) \
    .on_timeout(show_duration, lambda u: (
        u.send_trigger(trigger_offset),
        u.set_state(close_time=u.clock.getTime())
    )) \
    .on_end(lambda u: print('Show ended, state:', u.get_dict())) \
    .run(terminate_on_response=False)
```


#### Replicating `.capture_response()` with Hooks
```python
unit = StimUnit('resp_demo', win, kb)
unit.add_stim(response_stim)

# Start: draw stimuli, flip, send onset trigger, reset clock
@unit.on_start()
def start_resp(u):
    for s in u.stimuli:
        s.draw()
    u.win.callOnFlip(u.send_trigger, onset_trigger)
    u.win.callOnFlip(u.clock.reset)

# Response: for each valid key, send trigger and set state
@unit.on_response(['f','j'])
def on_resp(u, key, rt):
    code = response_triggers[key]
    u.send_trigger(code)
    u.set_state(response=key, rt=rt, hit=(key in correct_keys))

# Timeout: if no response within window
@unit.on_timeout(response_duration)
def on_timeout(u):
    u.send_trigger(timeout_trigger)
    u.set_state(response=None, timeout=True)

# End: log and clean up
@unit.on_end()
def end_resp(u):
    u.log_unit()

# Run the trial (hooks manage drawing and events)
unit.run()
```
Make it in a chainable manner:
```python
make_unit('resp_chain', win, kb) \
    .add_stim(response_stim) \
    .on_start(lambda u: (
        [s.draw() for s in u.stimuli],
        u.win.callOnFlip(u.send_trigger, onset_trigger),
        u.win.callOnFlip(u.clock.reset)
    )) \
    .on_response(['f','j'], lambda u, key, rt: (
        u.send_trigger(response_triggers[key]),
        u.set_state(response=key, rt=rt, hit=(key in correct_keys))
    )) \
    .on_timeout(response_duration, lambda u: (
        u.send_trigger(timeout_trigger),
        u.set_state(response=None, timeout=True)
    )) \
    .on_end(lambda u: u.log_unit()) \
    .run()
```
```{Warning}
In most cases, using `.show()`, `.capture_response()`, and `.wait_and_continue()` covers the vast majority of task requirements and has been extensively tested. Lifecycle hooks offer maximum flexibility, but they are less commonly used and have seen less practical validation. We did not test their usage extensively. Only opt for manual hooks when you need custom behavior beyond the built-in methods—and proceed with caution.
```


### 8. State and Data Management

`StimUnit` keeps all unit-related values in its internal `unit.state` dictionary. Use the following methods to keep your StimUnit data organized, easily retrievable, and ready for analysis or export.

#### Recording or Updating Values with `set_state()`

Use `set_state()` to record key–value data into the unit’s state

**Example**
```python
    # --- Feedback ---
if early_response:
    delta = settings.delta * -1
    hit=False
else:
    hit = target.get_state("hit", False)
    if condition == "win":
        delta = settings.delta if hit else 0
    elif condition == "lose":
        delta = 0 if hit else settings.delta * -1
    else:
        delta = 0

hit_type = "hit" if hit else "miss"
fb_stim = stim_bank.get(f"{condition}_{hit_type}_feedback")
fb = make_unit(unit_label="feedback") \
    .add_stim(fb_stim) \
    .show(duration=settings.feedback_duration, onset_trigger=settings.triggers.get(f"{condition}_{hit_type}_fb_onset"))
fb.set_state(hit=hit, delta=delta).to_dict(trial_data)
```
In this snippet, we:

1. **Create and display** a feedback `StimUnit` labeled "feedback" with the correct stimulus and triggers.
2. **Compute** whether the trial was a hit (`True`/`False`) and determine the `delta` value (+Δ, –Δ, or 0).
3. **Record** these values into the unit’s internal state using `set_state()` (which prefixes keys by default).
4. **Export** all stored state entries into your `trial_data` dict for logging or further analysis.

Note: `set_sate()` uses **prefixing** to control how keys are stored

**Default** (unit label): keys stored as `<unit_label>_<key>`

```python
fb.set_state(hit=True, delta=0.5)
# stores 'feedback_hit' and 'feedback_delta'
```
 
**Raw** (`prefix=''`): keys stored as-is

```python
fb.set_state(prefix='', hit=True, delta=0.5)
# stores 'hit' and 'delta'
```
**Custom** (`prefix='special'`): keys prefixed with 'special\_'

```python
fb.set_state(prefix='special', hit=True)
# stores 'special_hit'
```

**Summary of the prefix behavior**
| Mode    | Prefix       | Stored keys                    |
| ------- | ------------ | ------------------------------ |
| Default | (unit label) | feedback\_hit, feedback\_delta |
| Raw     | ''           | hit, delta                     |
| Custom  | 'special'    | special\_hit                   |


```{Tip}
`set_state` is **Chaining**: it returns the same `StimUnit`, so you can chain calls:`unit.set_state(block=2, trial=5).set_state(condition='win')`
```



**Summary of Automatic State Entries**

Several `StimUnit` methods populate internal state without explicit `set_state()` calls. Here’s a quick reference:

| Method                 | Keys Set in `.state`                                               | Notes                                      |
|------------------------|--------------------------------------------------------------------|--------------------------------------------|
| `run()`                | `global_time`                                                      | Experiment-wide timestamp before start     |
|                        | `onset_time`, `onset_time_global`, `flip_time`                     | Recorded at first `win.flip()`             |
|                        | `close_time`, `close_time_global`                                  | At end of trial (response or timeout)      |
|                        | `timeout_triggered`, `duration`                                     | If a timeout occurs                        |
| `show()`               | `duration`                                                         | Final chosen duration                      |
|                        | `onset_time`, `onset_time_global`, `onset_trigger`                 | At stimulus onset                          |
|                        | `flip_time`                                                        | Time of flip after onset                   |
|                        | `close_time`, `close_time_global`, `offset_trigger`                | At presentation end                        |
| `capture_response()`   | `duration`, `onset_time`, `onset_time_global`, `flip_time`          | Response window setup                      |
|                        | `hit`, `correct_keys`, `response`, `key_press`, `rt`               | On response                                |
|                        | `response_trigger`, `close_time`, `close_time_global`              | Response trigger and end time              |
|                        | `timeout_trigger`, `hit=False`, `response=None`, `rt=None`         | On timeout                                 |
| `wait_and_continue()`  | `wait_keys`, `onset_time`, `onset_time_global`, `flip_time`         | At display onset                           |
|                        | `response`, `response_time`, `close_time`, `close_time_global`     | When continuation key pressed              |

Use this table to quickly see what state values are filled in automatically, so you know which additional `set_state()` calls you might still need.

```{Note}
For `capture_response()`, the `hit` means the response was a correct key press.
```

#### Retrieving Values with `get_state()`
When you call `get_state()`, it first looks for the exact key, then for the prefixed form (using your unit_label or a supplied prefix), and if neither is found it returns the default value.

  ```python
  # Reads either 'response' or 'cue_response' if the unit_label is 'cue'
  resp = unit.get_state('response', default=None)
  # Force a different prefix lookup, it reads 'custom_response'
  resp = unit.get_state('response', default=0, prefix='custom')
  ```

#### Exporting All State with `.to_dict()` 

**`to_dict(target=None)`**
  - If no `target` is given, returns the `StimUnit` instance (for chaining) and leaves you to inspect `unit.state`.
  - If you pass in a dict, it merges `unit.state` into that dict and returns the `StimUnit`. 
  
  ```python
    # After an anticipation phase:
    anti = make_unit('anticipation')\
        .add_stim(stim_bank.get('fixation'))\
        .capture_response(keys=settings.keys, duration=settings.anticipation_duration)
    # Check if participant responded early
    early = anti.get_state('response', default=None)
    # Record this custom flag and merge into main trial_data
    anti.set_state(early_response=early)\
        .to_dict(trial_data)

    # In the target phase:
    target = make_unit('target')\
        .add_stim(stim_bank.get(f"{condition}_target"))\
        .capture_response(keys=settings.keys, duration=duration)
    # Export results
    target.to_dict(trial_data)
  ```

#### Logging State Internally with `.log_unit()`

`log_unit()` writes every key–value pair in `unit.state` to the log score in `data/*.log`.   It uses PsychoPy’s `logging.data()`, which by default appends timestamped entries to the experiment log file or console.
  It's automatically invoked within the `StimUnit` class, so you usually don’t need to call it manually.


**What gets logged?**  All entries currently in `unit.state`, including:

| State key examples            | Description                                  |
|-------------------------------|----------------------------------------------|
| `trial_block`, `trial_trial`  | Pre-trial identifiers                        |
| `onset_time`, `flip_time`     | Timestamps from `.show()` or `.run()`        |
| `hit`, `response`, `rt`       | Response metrics from `capture_response()`   |
| `feedback_hit`, `feedback_delta` | Custom values from your `set_state()` calls |

If you need a separate log for debugging at other points, you can call `unit.log_unit()` manually to snapshot current state.



## Next Steps

Now that you understand how to use `StimUnit`, you can:

- **Organize Blocks**: Explore the [BlockUnit tutorial](build_blocks.md) to organize trials into blocks
- **Manage Stimuli**: Learn about [StimBank](build_stimulus.md) for flexible stimulus management
- **Send Triggers**: Check out [trigger sending](send_trigger.md) for EEG/MEG experiments

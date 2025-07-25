# StimBank: Flexible Stimulus Management

## Overview

`StimBank` is a powerful stimulus management system for PsychoPy experiments that solves several common challenges:

- **Centralized stimulus management**: Define all visual and auditory stimuli in one place.
- **Multiple definition methods**: Register stimuli via Python decorators or configuration files (YAML/dictionaries).
- **Lazy loading**: Instantiate stimuli only when first accessed to reduce initial load time.
- **Dynamic formatting**: Insert runtime values into text stimuli without redefining them.
- **Batch operations**: Preview, export, validate, and group stimuli efficiently.

Whether you are running a simple behavioral task or a complex multi-modal protocol, `StimBank` helps you keep stimulus-related code and configuration clean, consistent, and maintainable.

## Key Features

| Feature               | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| Dual registration     | Define stimuli via decorators or declaratively via YAML/dictionaries |
| Lazy instantiation    | Delay object creation until needed                                   |
| Grouping              | Retrieve related stimuli by prefix or explicit list                  |
| Text formatting       | Use Python-style placeholders and `get_and_format()`                 |
| Stimulus rebuilding   | Override properties on-the-fly with `rebuild()`                      |
| Preview functionality | Visually inspect or play stimuli in batch                            |

## Quick Reference

| Purpose              | Method                            | Example                                    |
| -------------------- | --------------------------------- | ------------------------------------------ |
| Initialize           | `StimBank(win)`                   | `bank = StimBank(win)`                     |
| Register (decorator) | `@bank.define(name)`              | `@bank.define("fixation")`                 |
| Register (dict/YAML) | `bank.add_from_dict(dict)`        | `bank.add_from_dict(config)`               |
| Get stimulus         | `bank.get(name)`                  | `stim = bank.get("target")`                |
| Get multiple         | `bank.get_selected(list)`         | `stims = bank.get_selected(["fix","cue"])` |
| Get by prefix        | `bank.get_group(prefix)`          | `cues = bank.get_group("cue_")`            |
| Format text          | `bank.get_and_format(name, **kw)` | `bank.get_and_format("msg", name="John")`  |
| Modify stimulus      | `bank.rebuild(name, **kw)`        | `bank.rebuild("target", fillColor="blue")` |
| Preview all          | `bank.preview_all()`              | `bank.preview_all()`                       |
| Export config        | `bank.export_to_yaml(file_path)`  | `bank.export_to_yaml("stimuli.yaml")`      |

## Detailed Usage Guide

### 1. Initialization

Create a `StimBank` instance with your PsychoPy window:

```python
from psychopy.visual import Window
from psyflow import StimBank

win = Window(size=[1024, 768], color="black", units="deg")
stim_bank = StimBank(win)
```

Optionally, pass an initial configuration dictionary or load from YAML:

```python
stim_config = {
    "instructions": {
        "type": "text",
        "text": "Press SPACE to begin",
        "height": 0.7,
        "color": "white",
        "pos": [0, 3]
    },
    "left_target": {"type": "circle", "radius": 0.8, "pos": [-5, 0], "fillColor": "blue"},
    "image_stimulus": {"type": "image", "image": "images/stimulus.png", "size": [4, 3]}
}
stim_bank = StimBank(win, config=stim_config)
```

### 2. Supported Stimuli

`StimBank` currently supports the following stimulus types. In dict/YAML definitions, use these keys in the `type` field to select the appropriate class:

| Key     | Class     | Description                           |
| ------- | --------- | ------------------------------------- |
| text    | TextStim  | Single-line text                      |
| textbox | TextBox2  | Multi-line, wrapped text box          |
| circle  | Circle    | Filled or outlined circle             |
| rect    | Rect      | Rectangle                             |
| polygon | Polygon   | Arbitrary polygon defined by vertices |
| image   | ImageStim | Static bitmap image                   |
| shape   | ShapeStim | Custom shapes via vertex lists        |
| movie   | MovieStim | Video playback                        |
| sound   | Sound     | Audio playback using PsychoPy Sound   |

```{note}
A good place to learn about stimulus parameters is the PsychoPy Visual API page (https://www.psychopy.org/api/visual/). We will add support for additional stimulus types as we encounter them during the development of new tasks.
```

#### Parameter Validation

When loading definitions via `add_from_dict`, you can validate specs against the constructor signatures:

```python
# Validate without raising errors (prints warnings)
stim_bank.validate_dict(config, strict=False)

# Validate and raise on any issue
stim_bank.validate_dict(config, strict=True)
```

This checks for:

- **Missing required arguments** (parameters with no default)
- **Unknown arguments** (typos or unsupported fields)

#### Inspecting Available Parameters

To see exactly which keyword arguments each stimulus class accepts (and their defaults), use:

```python
stim_bank.describe("fixation")
```

Example output:

```
Description of 'fixation' (TextStim)
  - text: required
  - pos: default=(0, 0)
  - color: default='white'
  - height: default=1.0
  - bold: default=False
  ...
```

This built‑in helper lets you discover all supported parameters and their default values when writing dict/YAML specs or calling `rebuild()`.

### 3. Registering Stimuli

#### Method 1: Using Decorators

Programmatic registration via a factory function decorator:

```python
from psychopy.visual import TextStim, Circle

@stim_bank.define("fixation")
def make_fixation(win):
    return TextStim(win, text="+", color="white", height=1.0)

@stim_bank.define("target")
def make_target(win):
    return Circle(win, radius=0.5, fillColor="red", lineColor="white", lineWidth=2)
```

You can also build compound stimuli by assembling child elements and overriding methods.

#### Method 2: Using Dictionaries, YAML, or `load_config`

You have two main options for declarative stimulus definitions:

**1. Manual dict/YAML loading**

Use Python’s `yaml` library or plain dicts:

```python
import yaml
# a) Load YAML file
yaml_config = yaml.safe_load(open("config.yaml"))
# b) Extract nested 'stimuli' section if present
stim_config = yaml_config.get('stimuli', yaml_config)
# c) Register definitions
stim_bank.add_from_dict(stim_config)
```

Or define directly using dict in code:

```python
stim_config = {
    "instructions": {
        "type": "text",
        "text": "Press SPACE to begin",
        "height": 0.7,
        "color": "white",
        "pos": [0, 3]
    },
    "left_target": {"type": "circle", "radius": 0.8, "pos": [-5, 0], "fillColor": "blue"}
}
stim_bank.add_from_dict(stim_config)
```

**2. Using the built‑in **`load_config`** helper**

The `config.yaml` normally contains multiple sections (e.g., `settings`, `triggers`, `stimuli`), `load_config()` automatically reads `config.yaml` and returns a dict with a key `stim_config` holding only the relevant stimulus definitions.

```python
from psyflow.config import load_config
# Load all config sections
cfg = load_config()
# Extract only stimulus definitions
stim_config = cfg['stim_config']

# Initialize bank with preloaded definitions and chain further setup\ nstim_bank = (
    StimBank(win, stim_config)
    .convert_to_voice('instruction_text')
    .preload_all()
```

### 4. Retrieving and Previewing Stimuli

Once stimuli are registered, you can fetch and inspect them on demand.

**Single retrieval**: Fetch a single stimulus by name (instantiates on first use).

  ```python
  fixation = stim_bank.get("fixation")
  ```

**Selective retrieval**: Get a specific subset by listing names.

  ```python
  choices = stim_bank.get_selected(["left_target", "right_target"])
  ```

**Grouped retrieval**: Fetch all stimuli whose keys share a common prefix.

  ```python
  cues = stim_bank.get_group("cue_")
  ```

All retrieval methods cache instances after creation, so repeated calls are fast.

#### Previewing stimuli

Before embedding stimuli into trial code, it is often useful to preview their appearance or audio to verify positions, colors, sizes, or playback behavior:

```python
stim_bank.preview_all()                    # display or play every registered stimulus
stim_bank.preview_selected(["fixation"])   # only the specified stimuli
stim_bank.preview_group("feedback_")       # all stimuli with the "feedback_" prefix
```
```{tip}
Use previews to catch layout or styling issues early, rather than during live trials.
```

#### Listing and describing stimuli

**List all keys**: See which stimuli are registered.
  ```python
  print(stim_bank.keys())
  ```

**Check existence**: Test whether a name is registered.
  ```python
  if stim_bank.has("target"):
      # proceed
  ```

**Describe parameters**: Inspect constructor arguments and default values for any stimulus.
  ````python
  stim_bank.describe("fixation")
  # prints each keyword arg, its default (or "required" if none)
  ````


### 5. Dynamic Text Formatting

`get_and_format()` supports only `TextStim` and `TextBox2` stimuli. It returns a fresh instance with the same properties except for the formatted `text` field. Applying it to other stimulus types will raise a `TypeError`.

You just need to define text with Python-style placeholders in your configuration (dict or YAML) and inject runtime values.

For example, when you need to display a summary screen after each block, with dynamic values and a user prompt. Here’s how to configure and render a multi-line break message.

You can define the `block_break` stimulus either in a YAML file or directly in Python as a dict:

```yaml
# config.yaml
stimuli:
  block_break:
    type: text
    text: |
      {block_num}/{total_blocks} Done
      Score: {score}
      Press Enter to proceed
    color: white
    height: 0.78
```

```python
# In code, using a dict
stim_bank.add_from_dict({
    "block_break": {
        "type": "text",
        "text": (
            "{block_num}/{total_blocks} Done
"
            "Score: {score}
"
            "Press Enter to proceed"
        ),
        "color": "white",
        "height": 0.78
    }
})
```

**Runtime example**:

```python
# At end of block:
block_trials = block.get_all_data()
score = sum(t.get('cue_delta', 0) for t in block_trials)

# Format and display break screen
StimUnit('block',win,kb).add_stim(stim_bank.get_and_format('block_break', 
                                                                block_num=block_i+1, 
                                                                total_blocks=settings.total_blocks,
                                                                score=score)).wait_and_continue()
```

In this pattern, placeholders `{block_num}`, `{total_blocks}`, and `{score}` are replaced at runtime, and the resulting `TextStim` is passed to a `StimUnit` for display and input handling.

Note: `get_and_format()` works by manually reconstructing a new text stimulus rather than attempting a deep copy of the original. Internally, it inspects the constructor signature of `TextStim` or `TextBox2`, pulls out all of the original instance’s stored keyword arguments (from its __dict__), replaces the text field with your formatted string, and then calls the class constructor with that argument set. This approach avoids mutating the version cached in StimBank, but because PsychoPy objects don’t support true deep copying, some complex properties—especially in TextBox2 (e.g. wrapping behavior or anchor points)—may not carry over exactly as in the original. If you hit unexpected layout or formatting issues using `TextBox2`, consider using `TextStim`type or `rebuild()` with a new `text` override instead.


### 6. Rebuilding and Modifying Stimuli

`StimBank.rebuild()` lets you override stimulus parameters on-the-fly without mutating the original definition. Pass keyword arguments matching the stimulus constructor to create a fresh instance. Use `update_cache=True` if you want to overwrite the cached version.

**Basic example**:

```python
# Create a blue variant of "target" without altering original
blue_target = stim_bank.rebuild("target", fillColor="blue", radius=0.7)
# Original remains unchanged
red_target = stim_bank.get("target")  # still red, radius=0.5
```

Below is a realistic example from a probabilistic reversal learning (PRL) task showing how and when stimuli are rebuilt within a `run_trial` function. In each trial, the two choice stimuli swap positions depending on the `condition` and participant history:

```python
from functools import partial

def run_trial(win, kb, settings, condition, stim_bank, controller, trigger_sender=None):
    """
    Single PRL trial sequence:
      1. fixation
      2. cue display + response collection
      3. stochastic feedback
      4. inter-trial interval
    """
    trial_data = {"condition": condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)
    marker_pad = controller.reversal_count * 10

    # 1) Fixation
    make_unit(unit_label="fixation") \
        .add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.fixation_duration,
              onset_trigger=settings.triggers.get("fixation_onset") + marker_pad) \
        .to_dict(trial_data)

    # 2) Cue + response collection
    # Rebuild left/right stimuli positions based on condition
    if condition == "AB":
        stima = stim_bank.rebuild("stima", pos=(-4, 0))
        stimb = stim_bank.rebuild("stimb", pos=(4, 0))
    else:  # "BA"
        stimb = stim_bank.rebuild("stimb", pos=(-4, 0))
        stima = stim_bank.rebuild("stima", pos=(4, 0))

    # Determine correct response key
    correct_label = controller.current_correct
    correct_side = "left" if correct_label == "stima" else "right"
    correct_key = settings.left_key if correct_side == "left" else settings.right_key

    # Build and show cue unit
    cue_unit = make_unit(unit_label="cue")
    cue_unit.add_stim(stima).add_stim(stimb)
    cue_unit.capture_response(
        key_list=[settings.left_key, settings.right_key],
        correct_key=correct_key,
        duration=settings.cue_duration,
        onset_trigger=settings.triggers.get("cue_onset") + marker_pad
    ).to_dict(trial_data)

    # 3) Feedback and ITI omitted for brevity...

    return trial_data
```
In this example, using `rebuild()` lets you start from a single base definition and adjust only the parameters that need to change—such as swapping left/right positions—without creating entirely new stimulus entries. By passing constructor overrides (for example, `pos`, `fillColor`, `size`, or `opacity`), you retain full runtime flexibility to customize stimuli based on the current condition or participant data. Because `rebuild()` doesn’t overwrite the cached instance by default, the original definition remains untouched; if you do want to persist your changes across subsequent trials, simply include `update_cache=True`. This pattern keeps your stimulus bank compact and avoids proliferating nearly identical definitions for every possible variant.


#### `get_and_format()` vs `rebuild()`
| Feature               | `get_and_format()`                                   | `rebuild()`                                                   |
|-----------------------|------------------------------------------------------|---------------------------------------------------------------|
| **Purpose**           | Update only the **text** content                     | Create a new instance with any overridden properties          |
| **Supported Stimuli** | `TextStim`, `TextBox2` only                          | All stimulus types via registered factory                    |
| **Modifiable Props**  | Text content only                                    | Any constructor argument (`pos`, `fillColor`, `size`, etc.)  |
| **Mechanism**         | Copies stored kwargs from original, replaces `text`, then calls constructor | Calls registered factory with base kwargs + overrides       |
| **Cache Behavior**    | Never overwrites the cache                           | Does **not** overwrite by default; use `update_cache=True` to replace |
| **Best For**          | Simple label or score updates where visual layout stays constant | Complex or multi-property overrides; when TextBox2 formatting is unreliable |
| **Limitations**       | Cannot change non-text properties; deep-copy issues with wrapping/anchoring | Requires valid factory definition; always instantiates a fresh object |


### 7. Text-to-Voice Conversion

`StimBank` supports **text-to-speech (TTS)** conversion to enhance accessibility and standardize instruction delivery across different languages.

**Why it matters**: Using text-to-speech improves accessibility—especially for children, elderly participants, or those with low literacy. It ensures consistent voice delivery across different language versions and eliminates the need to record human voiceovers for each translation. By using standardized synthetic voices, you reduce variability introduced by different experimenters, maintaining consistency across sessions and sites.

**How it works**: `StimBank` uses Microsoft's `edge-tts`, a cloud-based TTS API that converts text to MP3 audio. Generated files are saved under the `assets/` folder and skipped if they already exist (unless `overwrite=True`), then automatically registered as new `Sound` stimuli.

```note
An internet connection is required for TTS generation. Offline tools exist but generally produce lower-quality audio.
```

#### Convert Existing Text Stimuli to Voice

```python
win, kb = initialize_exp(settings)
Setup stimulus bank
stim_bank = StimBank(win,cfg['stim_config'])\
    .convert_to_voice('instruction_text')\
    .preload_all()
```

This creates `instruction_text_voice.mp3` and `good_bye_voice.mp3` in `assets/`, and registers stimuli named `instruction_text_voice` and `good_bye_voice`.

 If you plan to regenerate voices, delete previously generated files in `assets/` first. Choose a TTS voice matching the text language to ensure natural pronunciation. The default is `zh-CN-XiaoxiaoNeural`.

#### Add Voice from Custom Text

```python
stim_bank.add_voice(
    stim_label="welcome_voice",
    text="ようこそ。タスクを開始します。",
    voice="ja-JP-NanamiNeural"
)
```

Registers `welcome_voice` and saves `assets/welcome_voice.mp3` for playback.

#### Voice Selection

Use the helper to list supported voices:

```python
from psyflow.tts_utils import list_supported_voices

# All voices
tsv = list_supported_voices(human_readable=True)
# Filter by language code
ts_jp = list_supported_voices(filter_lang="ja", human_readable=True)
```

Sample output:

| ShortName          | Locale | Gender | Personalities      | FriendlyName                                                 |
| ------------------ | ------ | ------ | ------------------ | ------------------------------------------------------------ |
| af-ZA-AdriNeural   | af-ZA  | Female | Friendly, Positive | Microsoft Adri Online (Natural) - Afrikaans (South Africa)   |
| af-ZA-WillemNeural | af-ZA  | Male   | Friendly, Positive | Microsoft Willem Online (Natural) - Afrikaans (South Africa) |

Alternatively, view the full list in this [Gist of supported voices](https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462).

#### Tips and Caveats

- **Placeholder limitation**: TTS does not support dynamic placeholders (e.g., `{duration}`). Use static text only.
- **Internet connection required**: Generation relies on Microsoft’s cloud service—ensure network access.
- **Overwrite**: Pass `overwrite=True` to force regeneration, but use sparingly.
- **Voice–language match**: Always match voice locale to text language for natural output.
- **Preview audio**: Verify MP3 files in `assets/` before full experiments. If a file is empty or corrupted, delete and regenerate.


## Next Steps

Now that you understand how to use `StimBank`, you can:

- **Build Trials**: Explore the [StimUnit tutorial](build_stimunit.md) to learn how to create trial sequences
- **Organize Blocks**: Check out the [BlockUnit tutorial](build_blocks.md) to organize trials into blocks
- **Send Triggers**: Learn about [trigger sending](send_trigger.md) for EEG/MEG experiments

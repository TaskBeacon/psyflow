## 🎨 StimBank: Flexible Stimulus Management for PsychoPy

`StimBank` is a hybrid registry system that allows you to manage PsychoPy stimuli using both decorators and YAML/dictionary specifications. It supports dynamic construction, formatting, lazy loading, previewing, and exporting of stimuli.

`StimBank` offers a declarative and reusable way to manage visual components in your PsychoPy experiments. Whether you're defining stimuli programmatically or loading them from config files, `StimBank` gives you the tools to keep things modular, inspectable, and flexible.

### 🧵 Summary of Key Methods

| Purpose                    | Method                        |
|-------------------------------------|--------------------------------------|
| Register (decorator)      | `@stim_bank.define(name)`     |
| Register (dict)           | `.add_from_dict()`            |
| Get one stimulus          | `.get(name)`                  |
| Get many (selected/group) | `.get_selected(keys)` / `.get_group(prefix)` |
| Preview stimuli           | `.preview_all()` etc.         |
| Format `TextStim`         | `.get_and_format(name, **kwargs)` |
| Override stimulus         | `.rebuild(name, **kwargs)`    |
| YAML export/import        | `.export_to_yaml()` / `add_from_dict()` |
| Validate config           | `.validate_dict()`            |




### 1. Initialization

To begin, create a `StimBank` instance with your PsychoPy window:

    from your_package import StimBank

    stim_bank = StimBank(win)



### 2. Registering Stimuli (Two Ways)

#### Option A: Register via Decorator

Use `@stim_bank.define("name")` to register a stimulus-generating function:

    @stim_bank.define("fixation")
    def make_fix(win):
        return TextStim(win, text="+")

    @stim_bank.define("cue_circle")
    def make_cue(win):
        return Circle(win, radius=1.0, fillColor='blue')

#### Option B: Register via Dictionary

You can also register multiple stimuli using `.add_from_dict()`:

    stim_bank.add_from_dict({
        "my_text": {
            "type": "text",
            "text": "Hello!",
            "pos": [0, 0],
            "color": "white"
        },
        "left_target": {
            "type": "circle",
            "radius": 2,
            "pos": [-4, 0],
            "fillColor": "red"
        }
    })



### 3. Retrieving Stimuli

Get a single stimulus (instantiated lazily):

    stim = stim_bank.get("my_text")
    stim.draw()

Get a group of stimuli by name or prefix:

    stim_bank.get_selected(["my_text", "left_target"])
    stim_bank.get_group("cue_")  # e.g., all keys like "cue_circle", "cue_square"

List all available keys:

    stim_bank.keys()

Check if a stimulus exists:

    stim_bank.has("fixation")  # returns True or False



### 4. Dynamic Text Formatting

If you registered a `TextStim`, you can format its contents dynamically,
for example you used {username} as placeholder when defining the text:

    stim = stim_bank.get_and_format("my_text", username="Zhang")
    stim.draw()  # will show "Hello, Zhang!" if the text was "Hello, {username}!"


### 5. Rebuilding or Overriding Stimuli

For other stimulus, you can rebuild them with new parameters, a good way to get rid of the `clone` or `deepcopy` that does not work for visual stimuli.

Important note: 
1. The rebuilding process will not update the original stimulus in the bank. It creates a new instance with the same properties, but you can specify new ones.
2. It works for the class but not for the visual stimuli per se. stim_bank.get('some_stim").rebuild() will give an error that `rebuild` is not a method of the visual stimuli.

To get a fresh instance of a stimulus with new properties:

    new_stim = stim_bank.rebuild("left_target", radius=4, fillColor="green")

Optionally, update the internal cache: (This will update the one saved in stim_bank)

    stim_bank.rebuild("left_target", update_cache=True, fillColor="green")



### 6. Previewing Stimuli

You can preview stimuli one by one:

    stim_bank.preview_all()

Preview a specific group by name prefix:

    stim_bank.preview_group("cue_")

Preview a selected list of keys:

    stim_bank.preview_selected(["my_text", "left_target"])




### 7. Describing Parameters

Use `describe(name)` to print all valid parameters for the stimulus type:

    stim_bank.describe("left_target")

Output example:

    🧾 Description of 'left_target' (Circle)
      - radius: required
      - pos: default=(0, 0)
      - fillColor: default='white'



### 8. YAML Export and Import

Export all dictionary-based stimuli to YAML:

    stim_bank.export_to_yaml("my_stimuli.yaml")

This includes only stimuli added via `add_from_dict()` or YAML — not decorators.

You can later reload these using:

    import yaml

    with open("my_stimuli.yaml", "r") as f:
        stim_dict = yaml.safe_load(f)

    stim_bank.add_from_dict(stim_dict)



### 9. Validating Definitions

Use `.validate_dict()` to check your dictionary for mistakes:

    stim_bank.validate_dict(stim_dict, strict=False)

This prints warnings for unknown or missing arguments. Set `strict=True` to raise exceptions instead. When using add_from_dict() or YAML, it will validate the dictionary before adding it to the bank.

### 10. Realistic Examples
#### 10.1. Monetary Incentive Delay Task (MID) example.

```yaml
# === Stimuli (for MID task) ===
stimuli:
  fixation:
    type: text
    text: "+"
    color: white

  win_cue:
    type: circle
    radius: 3
    fillColor: magenta
    lineColor: black

  lose_cue:
    type: rect
    width: 6
    height: 6
    fillColor: yellow
    lineColor: black

  neut_cue:
    type: polygon
    edges: 3
    size: 6
    fillColor: cyan
    lineColor: black

  win_target:
    type: circle
    radius: 3
    fillColor: black
    lineColor: black

  lose_target:
    type: rect
    width: 6
    height: 6
    fillColor: black
    lineColor: black

  neut_target:
    type: polygon
    edges: 3
    size: 6
    fillColor: black
    lineColor: black

  win_hit_feedback:
    type: text
    text: "You earned 10 points!"
    color: white

  win_miss_feedback:
    type: text
    text: "You earned 0 points."
    color: white

  lose_hit_feedback:
    type: text
    text: "You earned 0 points."
    color: white

  lose_miss_feedback:
    type: text
    text: "You earned -10 points."
    color: white

  neut_hit_feedback:
    type: text
    text: "You earned 0 points."
    color: white

  neut_miss_feedback:
    type: text
    text: "You earned 0 points."
    color: white

  
  block_break:
    type: text
    text: |
      Take a break! 
      When you are ready, press space to continue.
    color: white

  block_feedback:
    type: text
    text: |
      Block {block_num} of {total_blocks} completed. 
      Accuaracy: {accuracy:.2f}
      Reward: {reward:.2f}
      Press space to continue.
    color: white

  instruction_text:
    type: text
    text: |
      In this task, you will see a series of cues and targets. 
      Your task is to respond to the cues as quickly as possible. 
      If you respond to a cue, you will earn 10 points. 
      If you do not respond to a cue, you will earn 0 points. 
      Press space to continue.
    color: white

  instruction_image1:
    type: image
    image: ./assets/instruction_iamge1.bmp

  instruction_image2:
    type: image
    image: ./assets/instruction_image2.bmp

  good_bye:
    type: text
    text: |
      Thank you for participating!
      Your final reward is {reward:.2f}.
      Press space to exit.
    color: white
```

As everything is almost static, we just need to load them to stim_bank.

```python
# 5. Setup stimulus bank
stim_bank = StimBank(win)
# Preload all for safety

stim_config={
    **config.get('stimuli', {})
}
stim_bank.add_from_dict(stim_config)
stim_bank.preload_all()
```

#### 10.2. Probabilistic reversal learning (PRL) task example.

```yaml
stimuli:
  fixation:
    type: text
    text: "+"
    color: white
  
  win_feedback:
    type: text
    text: "You won!"
    color: green

  lose_feedback:
    type: text
    text: "You lost!"
    color: red
  
  no_response_feedback:
    type: text
    text: "No response!"
    color: yellow

  stima:
    type: image
    size: [5, 5]
  
  stimb:
    type: image
    size: [5, 5]

  highlight_left:
    type: rect
    lineColor: 'white'
    lineWidth: 3
    pos: [-4, -0.3]
    width: 3
    height: 4

  highlight_right:
    type: rect
    lineColor: 'white'
    lineWidth: 3
    pos: [4, -0.3]
    width: 3
    height: 4
```

Each block we use a pair of images, so we need to load them in the loop. 

```python

files = sorted(glob.glob("assets/*.png"))
pairs = list(zip(files[::2], files[1::2]))

stim_config={
    **config.get('stimuli', {})
}
all_data = []
for block_i in range(settings.total_blocks):
    stim_bank=StimBank(win)
    stima_img, stimb_img = pairs[block_i]
    cfg = stim_config.copy()
    cfg['stima']['image'] = stima_img
    cfg['stimb']['image'] = stimb_img
    stim_bank.add_from_dict(cfg)
    stim_bank.preload_all()
```
Then we will rebuild them based on the condition (this is in the `run_trial` function)

```python
    if condition == "AB":
        stima = stim_bank.rebuild('stima',pos=(-4,0))
        stimb = stim_bank.rebuild('stimb',pos=(4,0))
    elif condition == "BA":
        stimb = stim_bank.rebuild('stimb',pos=(-4,0))
        stima = stim_bank.rebuild('stima',pos=(4,0))

    make_unit(unit_label="cue") \
        .add_stim(stima) \
        .add_stim(stimb)
```

#### 10.3. Dealing with complicated conditions and stimulus 😱
In the emotional dot probe tasks, we need to take the emotion, gender, location and probe location into account when setup the conditions. In the task, we have defined 20 conditons, and assigned relevant stimuli to them.

```python
def assign_stim_from_condition(condition: str, asset_pool: AssetPool) -> dict:
    """
    Assigns left/right faces to a given condition label using the AssetPool.

    Parameters:
    -----------
    condition : str
        A condition label, e.g., 'PN_F_L', 'SN_M_R', etc.
    asset_pool : AssetPool
        An instance of the AssetPool class with loaded stimuli.

    Returns:
    --------
    dict with keys: condition, left_stim, right_stim, target_position
    """
    emotion, gender, target = condition.split('_')

    # Map emotion code to left/right stimulus categories
    if emotion == 'PN':
        left_key, right_key = 'P_' + gender, 'N_' + gender
    elif emotion == 'NP':
        left_key, right_key = 'N_' + gender, 'P_' + gender
    elif emotion == 'SN':
        left_key, right_key = 'S_' + gender, 'N_' + gender
    elif emotion == 'NS':
        left_key, right_key = 'N_' + gender, 'S_' + gender
    elif emotion == 'NN':
        left_key = right_key = 'N_' + gender
    else:
        raise ValueError(f"Unknown emotion code: {emotion}")

    # Draw from pool
    left_stim = asset_pool.draw(left_key)
    right_stim = asset_pool.draw(right_key)

    return {
        'condition': condition,
        'left_stim': left_stim,
        'right_stim': right_stim,
        'target_position': 'left' if target == 'L' else 'right'
    }

class AssetPool:
    def __init__(self, stim_list: Dict[str, List[str]], seed: int = 42):
        self.rng = random.Random(seed)
        self.original = stim_list
        self.pool = {k: [] for k in stim_list}  # working pools start empty

    def draw(self, key: str) -> str:
        """Draw one stimulus from the specified key pool."""
        if not self.pool[key]:
            self.pool[key] = self.original[key][:]
            self.rng.shuffle(self.pool[key])
        return self.pool[key].pop()

import os
from collections import defaultdict
def get_stim_list_from_assets(asset_dir: str = './assets') -> dict:
    stim_list = defaultdict(list)
    for file in os.listdir(asset_dir):
        if file.lower().endswith('.bmp'):
            name = file.upper()
            if name.startswith('HF'):
                stim_list['P_F'].append(file)
            elif name.startswith('HM'):
                stim_list['P_M'].append(file)
            elif name.startswith('NEF'):
                stim_list['N_F'].append(file)
            elif name.startswith('NEM'):
                stim_list['N_M'].append(file)
            elif name.startswith('SAF'):
                stim_list['S_F'].append(file)
            elif name.startswith('SAM'):
                stim_list['S_M'].append(file)
    return dict(stim_list)
# Example usage:

stim_list = get_stim_list_from_assets('./assets')
stim_pool = StimPool(stim_list, seed=123)

trial = assign_stim_from_condition('PN_F_L', stim_pool)
print(trial)
# {
#   'condition': 'PN_F_L',
#   'left_face': 'HF1.BMP',
#   'right_face': 'NEF3.BMP',
#   'probe_position': 'left'
# }
```

For use the of stim_bank, we can define include a placeholder stim in the stim_bank.
```yaml
stimuli:  
  left_stim:
    type: image
    pos: [-4.5, 0]
    size: [4.5, 5]
  
  right_stim:
    type: image
    pos: [4.5, 0]
    size: [4.5, 5]
```

Then find out the left and right stimuli based on the condition and rebuild them.

```python
trial_info = assign_stim_from_condition(condition, asset_pool)
    left_stim = stim_bank.rebuild('left_stim', image=os.path.join('assets', trial_info['left_stim']))
    right_stim = stim_bank.rebuild('right_stim', image=os.path.join('assets', trial_info['right_stim']))
```
So in this case, the stim_bank is more of the container for the placeholder stimuli.
The way to assign stimuli and generate conditions is a core part of the experiment design.
### 11. Converting Text to Speech

`convert_to_voice` allows you to synthesize existing text stimuli into spoken audio using [edge-tts](https://github.com/rany2/edge-tts). It creates a new `Sound` entry with the suffix `_voice`.

```python
# Convert two registered TextStim objects to speech
stim_bank.convert_to_voice(["instruction_text", "block_feedback"],
                           voice="en-US-AriaNeural")
# Afterwards you can access them as Sound stimuli
sound = stim_bank.get("instruction_text_voice")
```

If you just want to generate speech from arbitrary text, use `add_voice` which registers a new entry directly:

```python
# Create and register a custom voice clip
stim_bank.add_voice("intro_voice",
                   "Welcome to the experiment!",
                   voice="en-GB-RyanNeural")
intro = stim_bank.get("intro_voice")
intro.play()
```

# content to be added


# 3. setup stimuli
```
# 3. setup stimuli
from psychopy.visual import Circle, Rect, Polygon
from psyflow.StimBank import StimBank

# Assuming 
stim_bank = StimBank(win)
# --- Cue Stimuli ---
@stim_bank.define("cue_win")
def _cue_circle(win):
    return Circle(win, radius=4, fillColor="magenta", lineColor=None)

@stim_bank.define("cue_lose")
def _cue_square(win):
    return Rect(win, width=8, height=8, fillColor="yellow", lineColor=None)

@stim_bank.define("cue_neut")
def _cue_triangle(win):
    return Polygon(win, edges=3, size=8, fillColor="cyan", lineColor=None)

# --- Target Stimuli (Black) ---
@stim_bank.define("target_win")
def _target_circle(win):
    return Circle(win, radius=4, fillColor="black", lineColor=None)

@stim_bank.define("target_lose")
def _target_square(win):
    return Rect(win, width=8, height=8, fillColor="black", lineColor=None)

@stim_bank.define("target_neut")
def _target_triangle(win):
    return Polygon(win, edges=3, size=8, fillColor="black", lineColor=None)

# Preload all for safety

stim_bank.add_from_dict(
    fixation={"type": "text", "text": "+"},
    cue_win={"type": "circle", "radius": 4, "fillColor": "magenta","lineColor": ""},
    cue_lose={"type": "rect", "width": 8, "height": 8, "fillColor": "yellow","lineColor": ""},
    cue_neut={"type": "polygon", "edges": 3, "size": 8, "fillColor": "cyan","lineColor": ""},
    target_win={"type": "circle", "radius": 4, "fillColor": "black","lineColor": ""},
    target_lose={"type": "rect", "width": 8, "height": 8, "fillColor": "black","lineColor": ""},
    target_neut={"type": "polygon", "edges": 3, "size": 8, "fillColor": "black","lineColor": ""}
)


stim_bank.describe("cue_neut")
stim_bank.preload_all()
stim_bank.preview_all()
stim_bank.preview_selected(['cue_neut'])
stim_bank.rebuild('cue_neut', fillColor='red')
stim_bank.preview_selected(['cue_neut']) # not change?
```
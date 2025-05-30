## 🎯 StimUnit: Modular Trial Controller for PsychoPy

`StimUnit` wraps all the pieces of a single trial—stimulus presentation, response collection, triggers, timeouts, logging—into one reusable, chainable object. Below is a complete step‑by‑step guide on how to set it up and use it.


### 🧵 Summary of Key Methods

| Purpose                         | Method                                         |
|---|---|
| Add stimuli                     | `.add_stim(...)`                               |
| Clear stimuli                   | `.clear_stimuli()`                             |
| Update internal state           | `.set_state(prefix, **kwargs)`                 |
| Register start hook             | `.on_start(fn)`                                |
| Register response hook          | `.on_response(keys, fn)`                       |
| Register timeout hook           | `.on_timeout(sec, fn)`                         |
| Register end hook               | `.on_end(fn)`                                  |
| Auto-close after duration       | `.duration(t)`                                 |
| Auto-close on key               | `.close_on('key')`                             |
| Simple display                  | `.show(duration, onset_trigger, frame_based)`  |
| Stimulus + response window      | `.capture_response(...)`                       |
| Full trial control              | `.run(frame_based, terminate_on_response)`     |
| Pause & continue                | `.wait_and_continue(keys, terminate)`          |
| Inspect state                   | `trial.state` or `.to_dict()`                  |
| Log state                       | `.log_unit()`                                  |



### 1. Initialization

Create a new `StimUnit` by passing your window, a label, and (optionally) a `TriggerSender`:

    from psyflow import StimUnit, TriggerSender

    # Real trigger on a serial port:
    sender = TriggerSender(lambda code: port.write(bytes([code])))

    # Or mock mode for local testing:
    sender = TriggerSender(mock=True)

    trial = StimUnit(
        win=win,
        unit_label="trial_01",
        triggersender=sender
    )

- **win**: a `visual.Window` instance  
- **unit_label**: short string to prefix state keys  
- **triggersender**: optional, defaults to a no‑op print  



### 2. Adding Stimuli

Attach your visual components. You can pass one stim, several, or a list:

    trial.add_stim(text_stim)
    trial.add_stim(circle_stim, image_stim)
    trial.add_stim([stimA, stimB, stimC])
    trial.add_stim(stimA).add_stim(stimB).add_stim(stimC)

All added stimuli will be drawn together in every presentation call.



### 3. Lifecycle Hooks

Define callbacks at key stages:

- **on_start**: before first flip  
- **on_response**: when a valid key is pressed  
- **on_timeout**: when time runs out  
- **on_end**: after the trial completes  

Example:

    @trial.on_start()
    def prep(unit):
        print("Starting", unit.label)

    @trial.on_response(['left','right'])
    def record(unit, key, rt):
        unit.set_state(response=key, rt=rt)

    @trial.on_timeout(2.0)
    def timeout(unit):
        unit.set_state(hit=False)

    @trial.on_end()
    def wrap(unit):
        print("Finished:", unit.state)



### 4. Auto‑Closing

#### Fixed or Jittered Duration

    trial.duration(1.5)         # close after 1.5 s
    trial.duration((1.0,2.0))   # random between 1.0–2.0 s

#### Close on Key Press

    trial.close_on('space', 'escape')

Automatically records the key, RT, and close times into state.



### 5. Simple Display with `show()`

Present stimuli for a duration, send an onset trigger, and log:

    trial \
      .add_stim(my_stim) \
      .show(
          duration=1.0,
          onset_trigger=32,
          frame_based=True
      )

- **duration**: seconds or `[min,max]` jitter  
- **onset_trigger**: code sent at the flip  
- **frame_based**: `True` for frame‑loop timing  



### 6. Stimulus + Response Window with `capture_response()`

One‑stop call for show + response + triggers + highlight:

    trial \
      .add_stim(cue) \
      .capture_response(
          keys=['left','right'],
          duration=1.5,
          onset_trigger=32,
          response_trigger={'left':33,'right':34},
          timeout_trigger=35,
          correct_keys=['left'],
          highlight_stim=highlight_map,
          dynamic_highlight=False
      )

- **keys**: valid keys  
- **response_trigger**: int or `{key:code}`  
- **timeout_trigger**: code on timeout  
- **correct_keys**: keys counted as hits  
- **highlight_stim**: stim or `{key:stim}`  
- **dynamic_highlight**: redraw on repeated presses  

State fields like `hit`, `response`, `rt`, and trigger codes are all managed automatically.



### 7. Full Trial Loop with `run()`

Assemble hooks, then call `.run()` for maximum flexibility:

    trial \
      .add_stim(stimA, stimB) \
      .on_start(start_fn) \
      .on_response(['a','l'], resp_fn) \
      .on_timeout(2.0, timeout_fn) \
      .on_end(end_fn) \
      .run(frame_based=False, terminate_on_response=True)

- **frame_based**: `True` counts frames; `False` uses clock time  
- **terminate_on_response**: stop drawing after first response  

After `.run()`, inspect `trial.state` for all recorded timings, triggers, and custom data.



### 8. Pause & Continue with `wait_and_continue()`

Show stimuli, then block until a keypress:

    trial \
      .add_stim(instr_text) \
      .wait_and_continue(
          keys=['space'],
          log_message="Instructions done",
          terminate=False
      )

Pass `terminate=True` to close the window when done.



### 9. Chainable API Showcase

You can define and execute an entire trial in one fluid chain:

    trial = StimUnit( "T1",win, kb, TriggerSender(mock=True))

    trial \
      .add_stim(stimA, stimB) \
      .on_start(lambda u: print("Start", u.label)) \
      .on_response(
          ['x','z'],
          lambda u, k, rt: u.set_state(response=k, rt=rt)
      ) \
      .on_end(lambda u: print("State:", u.state)) \
      .run(frame_based=True)


### 10. Realistic Example
#### 10.1. Monetary Incentive Delay Task (MID) example.

```python
to be added
```


With `StimUnit` you get a concise, expressive, and chainable API for building every aspect of your trial—visuals, inputs, timing, triggers, and data logging—without boilerplate. Happy experimenting!

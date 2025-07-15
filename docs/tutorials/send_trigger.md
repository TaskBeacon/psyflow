## Overview

The `TriggerSender` class provides a flexible, device-independent way to send event codes (triggers) to external recording equipment (e.g., EEG, MEG, eye‐trackers). By wrapping your device-specific send function, it keeps experiment code clean, adds optional pre- and post-hooks, enforces precise timing delays, and even supports a mock mode for development without hardware.

`TriggerSender` solves several common challenges in neuroscience experiments:

- **Hardware abstraction**: Decouple your experiment logic from device-specific I/O.
- **Mock testing**: Develop and debug on any machine—no data acquisition hardware needed.
- **Precise timing**: Automatically insert configurable delays after each trigger send.
- **Custom hooks**: Run user-provided callbacks immediately before and after each trigger.
- **Robust logging**: Warn on invalid codes, catch errors, and record trigger events in PsychoPy’s log.

## Key Features

| Feature            | Description                                                          |
| ------------------ | -------------------------------------------------------------------- |
| Device-independent | Accepts any Python function to transmit integer codes to your device |
| Mock mode          | Print trigger codes instead of sending, for development/testing      |
| Configurable delay | Wait a specified duration after each send (default 0.001 s)          |
| Pre-/post hooks    | Execute user functions before and/or after sending each trigger      |
| Error handling     | Catch exceptions, log errors, and continue without crashing          |
| Logging support    | Record warnings and trigger events via PsychoPy’s logging system     |

## Quick Reference

| Purpose                 | Method                                           | Example                                          |
| ----------------------- | ------------------------------------------------ | ------------------------------------------------ |
| Initialize in mock mode | `TriggerSender(mock=True)`                       | `sender = TriggerSender(mock=True)`              |
| Initialize for hardware | `TriggerSender(trigger_func=your_send_function)` | `sender = TriggerSender(trigger_func=send_code)` |
| Send a trigger          | `sender.send(code)`                              | `sender.send(32)`                                |

## Detailed Usage Guide

### 1. Getting Started: Mock Mode for Development

Use mock mode to build and test your experiment logic without any hardware:

```python
from psyflow import TriggerSender

# Initialize in mock mode
trigger_sender = TriggerSender(mock=True)

# Console output: "[MockTrigger] Sent code: 1"
trigger_sender.send(1)

# Console output: "[MockTrigger] Sent code: 255"
trigger_sender.send(255)
```

### 2. Connecting to Real Hardware

```{Warning}
 Of the examples below, only the Serial (UART) Port example has been tested by the authors. The EGI, Neuroscan, Brain Products (RDA) and other device snippets were gathered from online sources and have not been validated on actual hardware. If you test these or implement triggers for additional devices (e.g., eye‑trackers), please share your code so we can keep this documentation up to date.
```

When your rig is ready, supply a function to send integer codes to your device via the `trigger_func` argument. You can adapt this pattern for serial ports, USB interfaces, LabJack devices, or any other hardware: just supply a function that takes an integer and transmits it.

#### Example: Serial (UART) Port (tested)

```python
from psyflow import TriggerSender
import serial
#ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
ser = serial.Serial("COM3", baudrate=115200, timeout=1)
if not ser.is_open:
    ser.open()

# Create TriggerSender
trigger_sender = TriggerSender(
    trigger_func=lambda code: ser.write(bytes([1, 225, 1, 0, code])),
    post_delay=0.005
)

# Example usage with psyflow BlockUnit callbacks

trigger_sender.send(settings.triggers.get("exp_onset"))

block = BlockUnit(
    block_id=f"block_{block_i}",
    block_idx=block_i,
    settings=settings,
    window=win,
    keyboard=kb
).generate_conditions() \
    .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset"))) \
    .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end"))) \
    .run_trial(partial(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender)) \
    .to_dict(all_data)

ser.close()
```

#### Example: Parallel (LPT) Port (Not tested yet)

```python
from psychopy import parallel, logging, core
from psyflow import TriggerSender

try:
    # Adjust address to your system (e.g., '0x0378' on Windows)
    port = parallel.ParallelPort(address='/dev/parport0')
    send_code = lambda c: port.setData(c)

    trigger_sender = TriggerSender(trigger_func=send_code)
    trigger_sender.send(128)  # Sends 128 to the parallel port

except Exception as e:
    print(f"Failed to initialize parallel port: {e}\nFalling back to mock mode.")
    trigger_sender = TriggerSender(mock=True)
    trigger_sender.send(128)  # Prints to console instead
```

#### Example: EGI NetStation (Not tested yet)

```python
from egi_pynetstation.NetStation import NetStation
from psyflow import TriggerSender

# Configure IPs and port for your NetStation and amplifier
IP_ns = '10.10.10.42'      # NetStation host IP
IP_amp = '10.10.10.51'     # Amplifier NTP server IP (for 400-series amps)
port_ns = 55513            # Default ECI port

# Initialize EGI NetStation client
eci_client = NetStation(IP_ns, port_ns)
eci_client.connect(ntp_ip=IP_amp)
eci_client.begin_rec()

# Wrap NetStation send_event in TriggerSender
egi_sender = TriggerSender(
    trigger_func=lambda code: eci_client.send_event(
        event_type=str(code)[:4],  # event_type max length 4 chars
        start=0.0,                  # relative timestamp
        label=str(code)
    ),
    post_delay=0.001
)

# Send trigger code 100
egi_sender.send(100)

# At experiment end, stop recording and disconnect
eci_client.end_rec()
eci_client.disconnect()
```

#### Example: Neuroscan via Parallel Port (Not tested yet)

```python
from psychopy import parallel
from psyflow import TriggerSender

# Initialize parallel port (address may vary by system)
port = parallel.ParallelPort(address=0x0378)

# Wrap parallel port setData in TriggerSender
neuroscan_sender = TriggerSender(
    trigger_func=lambda code: [port.setData(code), port.setData(0)],  # reset to 0 after send
    post_delay=0.001
)

# Send code 50 to Neuroscan system
neuroscan_sender.send(50)
```

#### Example: Brain Products via RDA Server (TCP) (Not tested yet)

```python
import socket
from psyflow import TriggerSender

# Connect to BrainVision Recorder's RDA interface
HOST, PORT = 'localhost', 51244
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Wrap socket send in TriggerSender
gp_sender = TriggerSender(
    trigger_func=lambda code: sock.sendall(f'{code}
'.encode()),
    post_delay=0.001
)

# Send marker 128 to Brain Products
gp_sender.send(128)

# Close socket when done
sock.close()
```

### 3. Advanced: Timing and Hooks

For finer control, `TriggerSender` lets you:

- `post_delay`: Insert a pause (in seconds) after each send (default `0.001`).
- `on_trigger_start` : Call a function just before sending starts.
- `on_trigger_end` : Call a function after the post-delay.

```python
from psyflow import TriggerSender

def before_hook():
    t0 = core.getTime()
    logging.data(f"Trigger start at {t0:.4f}s")

def after_hook():
    t1 = core.getTime()
    logging.data(f"Trigger end at {t1:.4f}s")

trigger_sender = TriggerSender(
    trigger_func=send_code,
    post_delay=0.01,
    on_trigger_start=before_hook,
    on_trigger_end=after_hook
)

trigger_sender.send(42)
```

Use hooks to timestamp events, synchronize with other systems, or run custom diagnostics around each trigger.

---

## 5. Integration with `StimUnit`

`TriggerSender` can be passed into `StimUnit` to automate sending triggers at key points in a trial with minimal code.

1. **Initialize and inject**:

   ```python
   from psyflow import TriggerSender, StimUnit

   sender = TriggerSender(trigger_func=your_send_func)
   unit = StimUnit(
       unit_label='trial1',
       win=win,
       kb=kb,
       triggersender=sender
   )
   ```

2. **Automatic calls inside methods**:

   - In `.show()`, `StimUnit` calls `sender.send(onset_trigger)` on the first frame (via `win.callOnFlip`) and `sender.send(offset_trigger)` after the visual presentation.
   - In `.capture_response()`, it looks up the code for the pressed key and calls `sender.send(code)` immediately when the response is registered.

3. **Configure trigger codes via dictionaries**:

   ```python
   settings.triggers = {
       'onset': 1,
       'offset': 2,
       'response': {'left': 10, 'right': 20}
   }

   unit.show(
       duration=1.0,
       onset_trigger=settings.triggers['onset'],
       offset_trigger=settings.triggers['offset']
   )
   unit.capture_response(
       keys=['left','right'],
       duration=2.0,
       response_trigger=settings.triggers['response']
   )
   ```

If you omit the `triggersender` or use `mock=True`, `StimUnit` will still run all its hooks and logging, allowing you to develop and test behavioral tasks without hardware.

4. **Example: MID Task Integration**:

Below is a real-world example from a Monetary Incentive Delay (MID) task showing how to use `TriggerSender` and `StimUnit` together. The `make_unit` helper simplifies passing the same `trigger_sender` to each trial phase.

```python
from psyflow import StimUnit
from functools import partial

def run_trial(win, kb, settings, condition, stim_bank, controller, trigger_sender):
    """
    Run a single MID trial sequence (fixation → cue → anticipation → target → feedback).
    """
    trial_data = {"condition": condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)

    # --- Cue Phase ---
    make_unit(unit_label='cue')\
        .add_stim(stim_bank.get(f"{condition}_cue")) \
        .show(
            duration=settings.cue_duration,
            onset_trigger=settings.triggers.get(f"{condition}_cue_onset")
        ) \
        .to_dict(trial_data)

    # --- Anticipation Phase ---
    anti = make_unit(unit_label='anticipation')\
        .add_stim(stim_bank.get("fixation"))
    anti.capture_response(
        keys=settings.key_list,
        duration=settings.anticipation_duration,
        onset_trigger=settings.triggers.get(f"{condition}_anti_onset"),
        terminate_on_response=False
    )
    early_resp = anti.get_state("response", default=None)
    anti.set_state(early_response=bool(early_resp)).to_dict(trial_data)

    # --- Target Phase ---
    duration = controller.get_duration(condition)
    tgt = make_unit(unit_label='target')\
        .add_stim(stim_bank.get(f"{condition}_target"))
    tgt.capture_response(
        keys=settings.key_list,
        duration=duration,
        onset_trigger=settings.triggers.get(f"{condition}_target_onset"),
        response_trigger=settings.triggers.get(f"{condition}_key_press"),
        timeout_trigger=settings.triggers.get(f"{condition}_no_response")
    )\
        .to_dict(trial_data)

    # --- Feedback Phase ---
    feedback_code = settings.triggers.get(
        f"{condition}_{'hit' if tgt.get_state('hit', False) else 'miss'}_fb_onset"
    )
    make_unit(unit_label='feedback')\
        .add_stim(stim_bank.get(f"{condition}_{'hit' if tgt.get_state('hit') else 'miss'}_feedback"))\
        .show(
            duration=settings.feedback_duration,
            onset_trigger=feedback_code
        )\
        .set_state(hit=tgt.get_state('hit', False))\
        .to_dict(trial_data)

    return trial_data
```

This example demonstrates:

- Creating a partial constructor (`make_unit`) that automatically injects `trigger_sender` into each `StimUnit`.
- Scheduling onset and offset triggers for each phase with minimal boilerplate.
- Seamlessly capturing responses and mapping them to trigger codes via `settings.triggers`.

If you choose not to pass a `triggersender`, the exact same code will run as a behavioral-only task, emitting logs but without hardware triggers.

## Next Steps

Now that you know how to send triggers, you can explore other parts of PsyFlow:

- **Getting Started**: If you're new to PsyFlow, check out the [Getting Started tutorial](getting_started.md).
- **Building Trials**: Learn how to build complex trials in the [StimUnit tutorial](build_stimunit.md).
- **Organizing Blocks**: See the [BlockUnit tutorial](build_blocks.md) to learn how to organize trials into blocks.


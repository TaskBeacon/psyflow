# ⏱ Trigger System for EEG/MEG: Trigger Dictionary + `TriggerSender`

Store your event codes in a plain dictionary and let `TriggerSender` handle the dispatch. This keeps your configuration centralized and your send logic simple.

### 🧵 Summary of Key Methods 

#### `TriggerSender`

| Purpose                    | Method                   |
|-|-|
| Send a trigger             | `.send(code)`            |
| Use mock/debug mode        | `TriggerSender(mock=True)` |
| Add hooks (start/end)      | `on_trigger_start/on_end` |
| Control post-delay         | `post_delay=0.001`       |


### 🗂 1. Prepare a Trigger Dictionary

Store event labels (e.g., "cue_onset", "response") as keys in a dictionary with integer codes as values.

#### A. Define manually

    triggers = {
        "cue_onset": 32,
        "key_press": 33,
    }

#### B. Load from YAML

YAML format:

    triggers:
      cue_onset: 32
      key_press: 33

Code:

    import yaml
    with open("trigger_config.yaml") as f:
        triggers = yaml.safe_load(f)["triggers"]

#### C. Get a code

    code = triggers["key_press"]  # returns 33



###  2. Sending Triggers with `TriggerSender`

TriggerSender handles the dispatch logic. It wraps your actual send function (e.g., serial port) and can also run in mock/debug mode.

#### A. Real device example

    def send_to_port(code):
        serial_port.write(bytes([code]))

    sender = TriggerSender(send_to_port)

#### B. Mock mode for testing

    sender = TriggerSender(mock=True)

#### C. Sending a trigger

    sender.send(triggers["cue_onset"])

This prints:

    [MockTrigger] Sent code: 32
    [Trigger] Trigger sent: 32



### 3. Optional Hooks and Delays

You can register actions before/after sending triggers (e.g., opening and closing ports):

    sender = TriggerSender(
        trigger_func=send_to_port,
        on_trigger_start=lambda: print("Opening port..."),
        on_trigger_end=lambda: print("Closing port..."),
        post_delay=0.005  # Wait 5ms after sending
    )


### 4. Realistic Example
Here we used mock mode for testing and a serial port for real device communication.
```python
trigger_config = {
    **config.get('triggers', {})
}
ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
triggersender = TriggerSender(
    trigger_func=lambda code: ser.write([1, 225, 1, 0, (code)]),
    post_delay=0.005,
    on_trigger_start=lambda: ser.open() if not ser.is_open else None,
    on_trigger_end=lambda: ser.close()
)
```

Using a trigger dictionary with `TriggerSender` keeps configuration and logic separated, making your experiment easier to debug, replicate, and maintain.

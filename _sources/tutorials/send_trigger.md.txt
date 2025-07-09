# Sending Hardware Triggers

In many psychology and neuroscience experiments, it's crucial to send precise time markers (triggers) to external recording equipment like EEG, MEG, or eye-trackers. `psyflow` provides a flexible and hardware-agnostic `TriggerSender` class to handle this.

The `TriggerSender` is designed to be a wrapper around the actual hardware communication logic, making your experiment code cleaner and easier to test.

## Getting Started: Mock Mode for Development

You don't need any hardware to start developing your experiment. The `TriggerSender` can be initialized in a `mock` mode, which simply prints the trigger codes to the console instead of sending them to a real device. This is extremely useful for testing and debugging.

```python
from psyflow.TriggerSender import TriggerSender

# Initialize in mock mode
trigger_sender = TriggerSender(mock=True)

# This will print "[MockTrigger] Sent code: 1" to the console
trigger_sender.send(1)

# This will print "[MockTrigger] Sent code: 255"
trigger_sender.send(255)
```

By using `mock=True`, you can develop and test your entire experiment logic on any computer, even without the final data acquisition hardware.

## Connecting to Real Hardware

When you are ready to connect to your actual hardware, you need to provide a function to the `TriggerSender` that knows how to communicate with your specific device. This is done via the `trigger_func` argument.

### Example: Parallel (LPT) Port

A common way to send triggers is through a parallel (LPT) port. PsychoPy's `psychopy.parallel` module can be used for this. Here is how you would configure the `TriggerSender` to use a parallel port:

```python
from psychopy import parallel
from psyflow.TriggerSender import TriggerSender

# Initialize the parallel port
# The address might be different on your system (e.g., 0x0378 on Windows)
try:
    port = parallel.ParallelPort(address='/dev/parport0')
    # The actual function that sends the trigger
    send_code = lambda code: port.setData(code)
    trigger_sender = TriggerSender(trigger_func=send_code)
    
    # Now, this will send the value 128 to the parallel port
    trigger_sender.send(128)

except Exception as e:
    print(f"Failed to initialize parallel port: {e}")
    print("Running in mock mode instead.")
    trigger_sender = TriggerSender(mock=True)
    trigger_sender.send(128) # This will now print to console
```
In this example, we define a `send_code` function that takes a `code` and uses `port.setData()` to send it. This function is then passed to our `TriggerSender`. We also include error handling to fall back to mock mode if the port can't be opened.

### Other Devices

The same principle applies to any other device. As long as you can write a Python function to send a number to it (e.g., via a serial port or a LabJack device), you can integrate it with the `TriggerSender`.

## Advanced: Timing and Hooks

The `TriggerSender` also has optional parameters for more advanced control:
- `post_delay`: A small delay (in seconds) to wait after a trigger is sent.
- `on_trigger_start` and `on_trigger_end`: Custom functions (hooks) that can be executed immediately before and after the trigger is sent, which can be useful for precise timing measurements.
from psyflow import BlockUnit,StimBank, StimUnit,SubInfo,TaskSettings,TriggerSender
from psyflow import load_config,count_down, initialize_exp

import pandas as pd
from psychopy import core
from functools import partial
import serial

# Optional imports — include only if needed
# from src import get_stim_list_from_assets, AssetPool
# from src import generate_valid_conditions
from src import run_trial, Controller

# Load experiment configuration from config.yaml
cfg = load_config()

# Collect subject/session info using SubInfo form
subform = SubInfo(cfg['subform_config'])
subject_data = subform.collect()

# Load task settings and merge with subject info
settings = TaskSettings.from_dict(cfg['task_config'])
settings.add_subinfo(subject_data)

# Initialize trigger sender (can be changed to real serial port)
settings.triggers = cfg['trigger_config']
ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
trigger_sender = TriggerSender(
    trigger_func=lambda code: ser.write([1, 225, 1, 0, code]),
    post_delay=0,
    on_trigger_start=lambda: ser.open() if not ser.is_open else None,
    on_trigger_end=lambda: ser.close()
)

# Initialize PsychoPy window and input devices
win, kb = initialize_exp(settings)

# Load and preload all stimuli
stim_bank = StimBank(win, cfg['stim_config']).preload_all()

# If the task uses an adaptive controller (e.g., SST, MID, PRL), initialize it here
if 'controller_config' in cfg:
    settings.controller = cfg['controller_config']
    controller = Controller.from_dict(settings.controller)
else:
    controller = None

# Optional: set up asset pool for dynamic image assignment (e.g., dot-probe)
# asset_pool = AssetPool(get_stim_list_from_assets()) if use_assets else None
asset_pool = None

# Save settings to file (for logging and reproducibility)
settings.save_to_json()

# Show instruction text and images if available
StimUnit('instruction_text', win, kb).add_stim(stim_bank.get('instruction_text')).wait_and_continue()
for key in ['instruction_image1', 'instruction_image2']:
    if key in stim_bank.bank:
        StimUnit(key, win, kb).add_stim(stim_bank.get(key)).wait_and_continue()

# Run task blocks
all_data = []
for block_i in range(settings.total_blocks):
    count_down(win, 3, color='white')

    block = BlockUnit(
        block_id=f"block_{block_i}",
        block_idx=block_i,
        settings=settings,
        window=win,
        keyboard=kb
    ).generate_conditions() \
     .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset", 100))) \
     .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end", 101))) \
     .run_trial(partial(run_trial,
                        stim_bank=stim_bank,
                        controller=controller,
                        asset_pool=asset_pool,
                        trigger_sender=trigger_sender)) \
     .to_dict(all_data)

    # Customize block-level feedback (hit rate, scores, etc.)
    block_trials = block.get_all_data()
    kwargs = {
        "block_num": block_i + 1,
        "total_blocks": settings.total_blocks
    }

    if any("feedback_delta" in trial for trial in block_trials):
        kwargs["total_score"] = sum(t.get("feedback_delta", 0) for t in block_trials)

    if any("target_hit" in trial for trial in block_trials):
        kwargs["accuracy"] = sum(t.get("target_hit", False) for t in block_trials) / len(block_trials)

    if any("go_hit" in trial for trial in block_trials):
        go_trials = [t for t in block_trials if t["condition"].startswith("go")]
        stop_trials = [t for t in block_trials if t["condition"].startswith("stop")]
        kwargs["go_accuracy"] = sum(t.get("go_hit", False) for t in go_trials) / len(go_trials) if go_trials else 0
        kwargs["stop_accuracy"] = sum(
            not t.get("go_ssd_key_press", False) and not t.get("stop_unit_key_press", False)
            for t in stop_trials
        ) / len(stop_trials) if stop_trials else 0

    StimUnit('block', win, kb).add_stim(stim_bank.get_and_format('block_break', **kwargs)).wait_and_continue()

# Final screen (e.g., goodbye or total score)
final_score = sum(t.get("feedback_delta", 0) for t in all_data)
StimUnit('block', win, kb).add_stim(
    stim_bank.get_and_format('good_bye', total_score=final_score)
).wait_and_continue(terminate=True)

# Save trial data to CSV
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)

# Clean up
core.quit()

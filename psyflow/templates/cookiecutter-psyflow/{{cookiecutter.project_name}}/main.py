import os
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core

from psyflow import BlockUnit, StimBank, StimUnit, SubInfo, TaskSettings, TriggerSender
from psyflow import count_down, initialize_exp, load_config

from src import Controller, run_trial


def _make_qa_trigger_sender():
    # In QA mode we don't want to hit real hardware.
    # Trigger logging (planned/executed) is handled by TriggerRuntime.
    return TriggerSender(trigger_func=lambda code: None, post_delay=0.0)


def run():
    task_root = Path(__file__).resolve().parent
    mode = (os.getenv("PSYFLOW_MODE", "human") or "human").strip().lower()

    if mode in ("qa", "sim"):
        from psyflow.qa.context import context_from_env, qa_context

        ctx = context_from_env(task_dir=task_root)
        with qa_context(ctx):
            _run_impl(mode=mode, qa_output_dir=ctx.output_dir)
    else:
        _run_impl(mode=mode, qa_output_dir=None)


def _run_impl(*, mode: str, qa_output_dir: Path | None):
    # 1. Load config
    cfg = load_config()

    # 2. Collect subject info (skip GUI in QA mode)
    if mode == "qa":
        subject_data = {"subject_id": "qa"}
    else:
        subform = SubInfo(cfg["subform_config"])
        subject_data = subform.collect()

    # 3. Load task settings
    settings = TaskSettings.from_dict(cfg["task_config"])
    if mode == "qa" and qa_output_dir is not None:
        settings.save_path = str(qa_output_dir)

    settings.add_subinfo(subject_data)

    # In QA mode, force deterministic artifact locations.
    if mode == "qa" and qa_output_dir is not None:
        qa_output_dir.mkdir(parents=True, exist_ok=True)
        settings.res_file = str(qa_output_dir / "qa_trace.csv")
        settings.log_file = str(qa_output_dir / "qa_psychopy.log")
        settings.json_file = str(qa_output_dir / "qa_settings.json")

    # 4. Setup triggers (mock in QA)
    settings.triggers = cfg["trigger_config"]
    if mode == "qa":
        trigger_sender = _make_qa_trigger_sender()
        ser = None
    else:
        import serial

        driver_cfg = cfg.get("trigger_driver_config", {})
        timing_cfg = cfg.get("trigger_timing_config", {})
        port = driver_cfg.get("port", "loop://")
        baudrate = driver_cfg.get("baudrate", 115200)
        post_delay_ms = timing_cfg.get("post_delay_ms", 1)
        post_delay_s = float(post_delay_ms) / 1000.0

        ser = serial.serial_for_url(port, baudrate=baudrate, timeout=1)
        # ser = serial.Serial("COM3", baudrate=115200, timeout=1)
        if not ser.is_open:
            ser.open()

        trigger_sender = TriggerSender(
            trigger_func=lambda code: ser.write(bytes([1, 225, 1, 0, code])),
            post_delay=post_delay_s,
        )

    # 5. Set up window & input
    win, kb = initialize_exp(settings)

    # 6. Setup stimulus bank (skip TTS/voice conversion in QA)
    stim_bank = StimBank(win, cfg["stim_config"])
    if mode != "qa":
        stim_bank = stim_bank.convert_to_voice("instruction_text")
    stim_bank = stim_bank.preload_all()

    # 7. Setup controller across blocks
    settings.controller = cfg["controller_config"]
    settings.save_to_json()
    controller = Controller.from_dict(settings.controller)

    trigger_sender.send(settings.triggers.get("exp_onset"))

    # Instruction
    instr = StimUnit("instruction_text", win, kb, triggersender=trigger_sender).add_stim(
        stim_bank.get("instruction_text")
    )
    if mode != "qa":
        instr.add_stim(stim_bank.get("instruction_text_voice"))
    instr.wait_and_continue()

    all_data = []
    for block_i in range(settings.total_blocks):
        # 8. setup block
        if mode != "qa":
            count_down(win, 3, color="black")

        block = (
            BlockUnit(
                block_id=f"block_{block_i}",
                block_idx=block_i,
                settings=settings,
                window=win,
                keyboard=kb,
            )
            .generate_conditions()
            .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset")))
            .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end")))
            .run_trial(partial(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender))
            .to_dict(all_data)
        )

        block_trials = block.get_all_data()

        # Calculate for the block feedback
        hit_rate = sum(trial.get("target_hit", False) for trial in block_trials) / len(block_trials)
        total_score = sum(trial.get("feedback_delta", 0) for trial in block_trials)
        StimUnit("block", win, kb, triggersender=trigger_sender).add_stim(
            stim_bank.get_and_format(
                "block_break",
                block_num=block_i + 1,
                total_blocks=settings.total_blocks,
                accuracy=hit_rate,
                total_score=total_score,
            )
        ).wait_and_continue()

    final_score = sum(trial.get("feedback_delta", 0) for trial in all_data)
    StimUnit("goodbye", win, kb, triggersender=trigger_sender).add_stim(
        stim_bank.get_and_format("good_bye", total_score=final_score)
    ).wait_and_continue(terminate=True)

    trigger_sender.send(settings.triggers.get("exp_end"))

    # 9. Save data
    df = pd.DataFrame(all_data)
    df.to_csv(settings.res_file, index=False)

    # 10. Close everything
    if ser is not None:
        ser.close()
    core.quit()


if __name__ == "__main__":
    run()

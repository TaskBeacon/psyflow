# PsyFlow Task Template

| Field                | Value                        |
|----------------------|------------------------------|
| Name                 | PsyFlow Task Template |
| Version              | main (0.1.0) |
| URL / Repository     | https://github.com/TaskBeacon/{{cookiecutter.project_name}} |
| Short Description    | Paradigm-agnostic scaffold for building a PsyFlow task from literature evidence |
| Created By           | Template Maintainer |
| Date Updated         | 2026-03-02 |
| PsyFlow Version      | 0.1.0 |
| PsychoPy Version     | 2025.1.1 |
| Modality             | Behavior |
| Language             | English |

## 1. Task Overview

This repository is a generic PsyFlow task scaffold. It includes standardized mode wiring (human/qa/sim), config split, trigger plumbing, responder integration, and contract-ready reference artifacts.

The default trial logic is intentionally minimal and non-paradigm-specific. Replace condition generation, timing, scoring, and stimuli with task-specific logic grounded in references under `references/`.

## 2. Task Flow

### Block-Level Flow

| Step | Description |
|---|---|
| Load Config | Load selected mode config (`config.yaml`, `config_qa.yaml`, or sim config). |
| Collect Subject Info | Collect participant info in human mode; inject deterministic IDs in qa/sim mode. |
| Setup Runtime | Initialize triggers, window, keyboard, and stimuli bank. |
| Show Instructions | Present configurable instruction stimuli. |
| Run Blocks | Generate per-block conditions and execute `run_trial(...)` for each trial. |
| Show Block Break | Present summary values from trial outputs (for example, accuracy and mean RT). |
| Save Data | Write trial-level CSV outputs and settings JSON. |
| Finalize | Emit end trigger, close trigger runtime, and quit PsychoPy. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Fixation | Show baseline fixation stimulus. |
| Response Window | Show prompt stimulus, collect key response with timeout handling. |
| Feedback | Show configurable feedback stimulus based on response presence. |
| ITI | Show inter-trial fixation. |

### Controller Logic

| Feature | Description |
|---|---|
| Condition Scheduling | Uses a generic controller to distribute conditions across a block. |
| Determinism | Supports seed-driven scheduling for reproducible QA/sim runs. |
| Extensibility | Replace `src/utils.py` with task-specific planners/adaptive controllers when needed. |

## 3. Configuration Summary

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | Numeric participant ID from subform or qa/sim context. |

### b. Window Settings

| Parameter | Meaning |
|---|---|
| `window.size` | Window resolution in pixels. |
| `window.units` | PsychoPy units used for stimulus placement. |
| `window.bg_color` | Background color. |
| `window.fullscreen` | Fullscreen mode toggle. |

### c. Stimuli

| Stimulus ID | Purpose |
|---|---|
| `instruction_text` | Entry instruction text. |
| `fixation` | Baseline fixation symbol. |
| `trial_prompt` | Response window prompt text. |
| `feedback_hit` / `feedback_miss` | Response-dependent feedback messages. |
| `block_break` | Inter-block summary message. |
| `good_bye` | End-of-task summary message. |

### d. Timing

| Parameter | Meaning |
|---|---|
| `timing.fixation_duration` | Pre-response fixation duration. |
| `timing.response_window_duration` | Response collection window duration. |
| `timing.feedback_duration` | Feedback duration. |
| `timing.iti_duration` | Inter-trial interval duration. |

## 4. Methods (for academic publication)

Participants completed a computerized behavioral paradigm implemented in PsychoPy/PsyFlow. The runtime architecture supports human testing, QA replay, and simulation with shared task code. Trial flow and timing parameters are fully config-defined, and simulation context fields are attached per phase to support reproducible responder behavior and post-hoc auditing.

For publication use, replace this template section with task-specific participant/sample details, condition definitions, timing values, scoring rules, and citation-grounded implementation rationale.

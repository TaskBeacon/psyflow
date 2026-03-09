# Task Logic Audit

## 1. Paradigm Intent

- Template scaffold for documenting paradigm intent and theoretical targets.
- Replace with task-specific cognitive processes and hypotheses.

## 2. Block/Trial Workflow

- Current scaffold flow: fixation -> response_window -> feedback -> iti.
- Replace with task-specific state machine and transition constraints.

## 3. Condition Semantics

- Current scaffold provides generic `baseline` and `variant` labels.
- Replace with literature-defined condition semantics and balancing rules.

## 4. Response and Scoring Rules

- Current scaffold records response presence, key, RT, and correctness against `task.correct_key`.
- Replace with task-specific response validity and scoring contracts.

## 5. Stimulus Layout Plan

- Current scaffold uses config-defined text stimuli (`instruction_text`, `trial_prompt`, `feedback_*`).
- Replace with task-specific stimulus inventory, modality, and positioning rules.

## 6. Trigger Plan

- Current scaffold defines experiment/block/trial phase triggers in `triggers.map`.
- Replace with acquisition-specific trigger taxonomy and hardware timing constraints.

## 7. Architecture Decisions (Auditability)

- `main.py` provides one auditable run flow across human/qa/sim.
- `run_trial.py` sets trial context before every participant-visible phase for simulation and plotting auditability.
- Replace template notes with task-specific design decisions and rationale.

## 8. Inference Log

- Populate this section with explicit assumptions made when source papers omit implementation details.
- Include justification for parameter values, task phase structure, and stimulus choices.

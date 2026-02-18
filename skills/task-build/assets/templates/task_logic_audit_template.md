# Task Logic Audit Template

Use this file as `references/task_logic_audit.md` before coding.

## 1. Paradigm Intent

- Task:
- Primary construct:
- Manipulated factors:
- Dependent measures:
- Key citations:

## 2. Block/Trial Workflow

### Block Structure

- Total blocks:
- Trials per block:
- Randomization/counterbalancing:

### Trial State Machine

List each state in order with entry/exit conditions:

1. State name:
   - Onset trigger:
   - Stimuli shown:
   - Valid keys:
   - Timeout behavior:
   - Next state:

## 3. Condition Semantics

For each condition token in `task.conditions`:

- Condition ID:
- Participant-facing meaning:
- Concrete stimulus realization (visual/audio):
- Outcome rules:

## 4. Response and Scoring Rules

- Response mapping:
- Missing-response policy:
- Correctness logic:
- Reward/penalty updates:
- Running metrics:

## 5. Stimulus Layout Plan

For every screen with multiple simultaneous options/stimuli:

- Screen name:
- Stimulus IDs shown together:
- Layout anchors (`pos`):
- Size/spacing (`height`, width, wrap):
- Readability/overlap checks:
- Rationale:

## 6. Trigger Plan

Map each phase/state to trigger code and semantics.

## 7. Inference Log

List any inferred decisions not directly specified by references:

- Decision:
- Why inference was required:
- Citation-supported rationale:

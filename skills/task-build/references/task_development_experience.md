# Task Development Experience (Generic)

This note captures reusable engineering lessons for building cognitive tasks with PsyFlow/TAPS.

## 1) Two Validation Layers

- Layer A: framework/contract compliance (`main.py` modes, config split, responder plumbing, gates).
- Layer B: paradigm validity (stimulus logic, condition semantics, timing and response meaning).
- Always satisfy both layers; Layer A pass alone does not mean the task is scientifically valid.

## 2) Evidence Before Implementation Details

- Lock core paradigm decisions from references first.
- Maintain explicit mapping files (`parameter_mapping.md`, `stimulus_mapping.md`).
- Treat unresolved decisions as blockers or clearly marked inferences.

## 3) Stimulus Strategy

- Prefer PsychoPy built-ins for robust, auditable baseline implementations.
- Use generated assets only when they are reference-aligned and documented.
- Avoid placeholder/dummy assets; they hide paradigm mistakes and inflate false progress.

## 4) Language and Participant UX Consistency

- Keep all participant-facing text in the configured language.
- Align instruction, cue, feedback, break, and exit texts in the same language style.
- Use a language-appropriate font policy:
  - Chinese: default to `SimHei`.
  - Non-Chinese: select fonts that fully cover the required script.
- Do not expose internal/debug information to participants.
- Do not reveal internal condition labels before response unless the protocol explicitly requires it.

## 5) QA/Sim Design Principles

- QA and sim should be short but cover all mechanisms (conditions, phases, trigger paths).
- Sampler responders should reliably continue non-target screens and only model target behavior.
- Deterministic seeds are required for reproducible debugging.

## 6) Automation Guardrails

- Fail fast on structural or fidelity violations before expensive gate loops.
- Do not auto-generate paradigm logic without evidence.
- Batch automation should be used only after one task is proven end-to-end.

## 7) Iteration Workflow

- Develop one task deeply, validate, then generalize patterns.
- Re-run strict checks after each major stimulus or language change.
- Update docs/changelog with concrete, auditable changes only.
- Keep README structure stable across tasks so humans can audit quickly:
  - task overview
  - block/trial/controller logic
  - config tables
  - publication-style methods

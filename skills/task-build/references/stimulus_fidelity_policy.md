# Stimulus Fidelity Policy

This policy defines the minimum bar for stimulus implementation in `task-build`.

## Core Rule

Implemented stimuli must be traceable to selected references. Placeholder or dummy media is not allowed.

## Allowed Implementation Modes

- PsychoPy primitives (`text`, `circle`, `rect`, `polygon`, `shape`, etc.) with parameter values extracted from references.
- Generated assets that replicate the referenced paradigm structure (timing, category logic, perceptual properties) and are documented in evidence files.
- Licensed external media only when required by paradigm and legally usable.

## Required Evidence

- `references/parameter_mapping.md`: parameter-level mapping.
- `references/stimulus_mapping.md`: condition/stimulus-level citation mapping.

## Hard Fail Conditions

- Any config or asset path containing `placeholder`, `dummy`, or `todo`.
- Missing asset files referenced by config.
- Unresolved entries in `references/stimulus_mapping.md`.

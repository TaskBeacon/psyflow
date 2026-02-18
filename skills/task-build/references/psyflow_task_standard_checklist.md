# PsyFlow Task Standard Checklist

Use this checklist before running final gates.

## Required Files

- `main.py`
- `src/run_trial.py`
- `config/config.yaml`
- `config/config_qa.yaml`
- `config/config_scripted_sim.yaml`
- `config/config_sampler_sim.yaml`
- `responders/__init__.py`
- `responders/task_sampler.py`
- `README.md`
- `CHANGELOG.md`
- `taskbeacon.yaml`
- `.gitignore`
- `references/references.yaml`
- `references/references.md`
- `references/parameter_mapping.md`
- `references/stimulus_mapping.md`

## Runtime Pattern

- `main.py` supports modes: `human`, `qa`, `sim`
- `main.py` uses `parse_task_run_options(...)`
- `run_trial.py` uses `set_trial_context(...)`
- trigger schema is structured (`map/driver/policy/timing`)

## Config Separation Rules

- `config.yaml`: no `qa`, no `sim`
- `config_qa.yaml`: contains `qa`, no `sim`
- `config_scripted_sim.yaml`: contains `sim`, no `qa`
- `config_sampler_sim.yaml`: contains `sim`, no `qa`

## Stimulus Fidelity Rules

- Placeholder/dummy stimuli are forbidden.
- Configs must not reference files containing tokens like `placeholder`, `dummy`, `todo`.
- Asset-backed stimuli (`image`, `movie`, `sound`) must point to existing files.
- `references/stimulus_mapping.md` must be fully resolved (no `UNSET`, `TODO`, or review markers).
- Every base-config condition must appear in `references/stimulus_mapping.md`.
- Internal condition/debug labels must not be shown to participants unless references require them.

## Metadata Rules

- `taskbeacon.yaml` includes `contracts.psyflow_taps`
- README metadata reflects current version/date
- CHANGELOG includes current implementation summary
- Participant-facing text is language-consistent with task config (for example, `task.language`).
- Participant-facing text uses script-appropriate fonts:
  - Chinese text defaults to `font: SimHei`.
  - Other languages use fonts with full script coverage.
- README includes all reproducibility sections:
  - `## 1. Task Overview`
  - `## 2. Task Flow`
  - `## 3. Configuration Summary`
  - `## 4. Methods (for academic publication)`
- README task flow includes block-level, trial-level, controller logic, and other logic (if applicable).
- README configuration summary includes subject info, window, stimuli, timing, triggers (if present), and adaptive controller (if present).

## Required Gates

- `check_task_standard.py` pass
- validate pass
- qa pass
- scripted sim pass
- sampler sim pass

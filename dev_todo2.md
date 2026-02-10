# psyflow dev TODO 2 (Additional Critical + High-Impact)

Last updated: 2026-02-10

Scope: This file lists *additional* issues/enhancements beyond the timing-focused items already tracked in `dev_todo.md`.

## Critical Issues (Must Fix)

- [ ] `StimUnit.run()` crashes due to undefined `frame_i` (`psyflow/StimUnit.py:404-421`).
  Reason: the loop is `for _ in range(...)` but later checks `if frame_i == ...`, causing `NameError` at runtime.
  Proposed fix: change the loop to `for frame_i in range(n_frames - 1):` and keep the "final frame close stamp" logic on `frame_i == n_frames - 2`.

- [ ] `BlockUnit.summarize()` is broken because `to_dict()` returns `self` (`psyflow/BlockUnit.py:269-318`).
  Reason: default summarize does `results = self.to_dict()` then iterates `results`, but `to_dict()` returns a `BlockUnit` instance.
  Proposed fix (minimal): change `results = self.to_dict()` to `results = self.results` (or `self.get_all_data()`).
  Proposed fix (cleanup): rename `to_dict()` to something like `append_to(target)` and add a real `to_list()` that returns `self.results`.

- [ ] `LLMClient` advertises `provider="moonshot"` but it is not supported in `generate()` / `list_models()` (`psyflow/LLM.py:32-83`, `psyflow/LLM.py:137-186`).
  Reason: `__init__` accepts `"moonshot"` and creates an OpenAI-compatible client, but `generate()`/`list_models()` only handle `"openai"` and `"deepseek"` and otherwise raise "No handler".
  Proposed fix: treat `"moonshot"` exactly like `"deepseek"` in `generate()` and `list_models()` (same SDK, different `base_url`).

- [ ] `LLMClient.generate()` can raise `TypeError` when caller passes `stream=...` (`psyflow/LLM.py:141-146`, `psyflow/LLM.py:252-261`).
  Reason: `_filter_openai_kwargs()` allows `"stream"`, but `generate()` hard-codes `stream=False` and then expands `**params`, producing duplicate keyword arguments.
  Proposed fix: remove `"stream"` from the allowed kwargs OR remove the explicit `stream=False` and use `stream = params.pop("stream", False)`.

- [ ] `utils.taps()` likely points at a non-existent template directory (`psyflow/utils.py:41-68`).
  Reason: the template lives under `psyflow/templates/cookiecutter-psyflow`, but `taps()` uses `pkg_res.files("psyflow") / template` (missing the `templates/` layer).
  Proposed fix: align with `psyflow/cli.py` and use `pkg_res.files("psyflow.templates") / "cookiecutter-psyflow"` (or `pkg_res.files("psyflow") / "templates" / template`).

- [ ] Packaging does not declare a minimum Python version, but code requires Python >= 3.10 (PEP 604 `|` unions) (`pyproject.toml:1-29`, e.g. `psyflow/StimUnit.py`).
  Reason: pip can install on older Python and then fail at import with `SyntaxError`.
  Proposed fix: add `requires-python = \">=3.10\"` to `pyproject.toml` and `python_requires=\">=3.10\"` to `setup.py` (if `setup.py` is kept).

## High-Impact Enhancements (Recommended, Minimal Design)

- [ ] Make `import psyflow` cheap and low-side-effect (`psyflow/__init__.py:3-12`).
  Reason: `psyflow/__init__.py` imports PsychoPy-facing modules, CLI, and LLM utilities eagerly; this slows startup and makes importing the package do much more than "define symbols".
  Proposed fix: keep `__init__.py` minimal (version + lightweight re-exports), and avoid importing CLI/LLM by default. If you want convenience imports, do them lazily (inside functions) or document explicit imports (`from psyflow.StimUnit import StimUnit`, etc.).

- [ ] Replace intra-package imports like `from psyflow import TriggerSender/load_config` with relative imports (`psyflow/StimUnit.py:5`, `psyflow/LLM.py:10`).
  Reason: importing the package from inside the package is fragile (order-dependent) and increases import-time coupling.
  Proposed fix: use `from .TriggerSender import TriggerSender` and `from .utils import load_config`.

- [ ] Move LLM/TTS dependencies behind optional extras (installation footprint + failure surface).
  Reason: core experiment users may not want `openai`, `google-generativeai`, `tiktoken`, `edge-tts`, `requests` installed and imported as part of the base package.
  Proposed fix: split dependencies into extras, e.g. `psyflow[llm]`, `psyflow[tts]`, and import those modules only when used (raise a clear error if optional deps are missing).

- [ ] Add minimal config validation (fail fast on typos/missing keys).
  Reason: YAML/config mistakes often become late `KeyError`/`None` values during a run, which is expensive to debug in lab time.
  Proposed fix: add a lightweight `validate_config(raw_cfg)` that checks the existence/types of the top-level sections you rely on (window/task/timing/stimuli/triggers), and run it once at experiment start.

- [ ] Standardize on `psychopy.logging` instead of `print()` for library code (opt-in verbosity).
  Reason: `print()` is noisy and hard to control; it can also show up in contexts where you want clean console output.
  Proposed fix: replace most prints with `logging.info`/`logging.data` (and allow a `verbose`/`enable_logging` flag to turn them on/off).

- [ ] Add a small smoke test + CI workflow (compile + a couple pure-Python tests).
  Reason: regressions like the `frame_i`/`summarize()` bugs are easy to reintroduce and expensive to catch manually.
  Proposed fix: add a GitHub Actions workflow that runs `python -m py_compile` and a tiny `pytest` suite for pure functions (`load_config`, `TaskSettings.from_dict`, etc.). Keep PsychoPy window creation out of CI by default.

- [ ] Clean up encoding mojibake in user-facing strings/docs (e.g. weird arrows/dashes).
  Reason: console output and docs currently contain corrupted characters (likely from mixed encodings), which looks unprofessional and can confuse users.
  Proposed fix: replace non-essential fancy punctuation with ASCII (`->`, `...`, `-`) and ensure files are saved as UTF-8 consistently.

# Using `LLMClient` for AI-Driven Helpers

## Overview

`LLMClient` provides a unified interface for interacting with several large language model (LLM) providers and includes helpers for converting tasks to documentation, reconstructing tasks from documentation, and translating experiment resources.

It supports:

- **Google Gemini** via the GenAI SDK (`provider="gemini"`)
- **OpenAI** models (`provider="openai"`)
- **Deepseek** models using the OpenAI API format (`provider="deepseek"`)

Custom providers can also be registered programmatically.

## Initialization

Create an instance by specifying the provider, API key, and model name:

```python
from psyflow import LLMClient

client = LLMClient(
    provider="openai",
    api_key="YOUR_API_KEY",
    model="gpt-3.5-turbo"
)
```

The client wraps the underlying SDK and exposes common methods regardless of provider.

## Generating Text

Use `generate(prompt, **kwargs)` to obtain a completion from the configured model. Optional keyword arguments are passed to the underlying provider. Setting `deterministic=True` disables sampling randomness.

```python
reply = client.generate(
    "Summarise the Stroop task in one sentence",
    deterministic=True,
    max_tokens=50
)
print(reply)
```

## Converting Tasks to Documentation

`task2doc()` summarises an existing task into a README. The function loads your task logic and configuration, optionally uses few‑shot examples from `add_knowledge()`, and returns the generated Markdown text. If `output_path` is provided the README is also written to disk.

```python
readme_text = client.task2doc(
    logic_paths=["./src/run_trial.py", "./main.py"],
    config_paths=["./config/config.yaml"],
    deterministic=True,
    output_path="./README.md"
)
```

## Recreating Tasks from Documentation

`doc2task()` performs the reverse operation. Given a README or raw description it regenerates the key source files. Provide a directory for outputs via `taps_root` and optionally customise the list of expected file names.

```python
files = client.doc2task(
    doc_text="./README.md",
    taps_root="./recreated_task",
    deterministic=True
)
# files is a dict mapping each file name to its saved path
```

## Translation Utilities

Several helper methods assist with localisation. The base `translate(text, target_language)` function translates arbitrary text while keeping formatting intact. `translate_config()` applies translation to relevant fields in a psyflow YAML configuration and can write the translated file to disk.

```python
translated = client.translate(
    "Press the space bar when you see the target word",
    target_language="German"
)

new_cfg = client.translate_config(
    target_language="German",
    config="./config/config.yaml",
    output_dir="./i18n"
)
```

These utilities store the last prompt and response for inspection (`last_prompt`, `last_response`) and automatically count tokens for the active model.

## Further Reading

See the API reference for a full description of all attributes and methods provided by [`psyflow.LLMClient`](../api/psyflow#psyflow.LLMClient).


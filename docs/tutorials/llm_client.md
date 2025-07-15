# LLMClient: Using Large Language Models

## Overview

The `LLMClient` class in `psyflow` offers a lightweight, unified interface for interacting with various Large Language Model (LLM) backends, including Google Gemini, OpenAI, Deepseek, and Moonshot. Instead of relying on heavy frameworks like LangChain, we built a minimal wrapper to keep things simple: no extra dependencies beyond provider SDKs, a clean API (e.g., `generate()`, `translate()`, `count_tokens()`), and fast, low-overhead execution.

## Supported Providers

Our library supports flexible, cost-effective access across multiple providers:

- **Gemini** (Google GenAI): Free-tier access to powerful models—ideal for getting started at no cost.
- **OpenAI**: Official OpenAI SDK support for GPT‑series models and fine-tuned endpoints.
- **Deepseek**: A cost-effective alternative via the OpenAI-compatible SDK for users without Gemini access.
- **Moonshot**: A cost-effective alternative via the OpenAI-compatible SDK for users without Gemini access.

## Key Features

| Feature                | Description                                                          |
| ---------------------- | -------------------------------------------------------------------- |
| Multi-provider support | Out-of-the-box: Gemini, OpenAI, Deepseek, Moonshot                   |
| Text generation        | `generate()` with sampling and deterministic options                 |
| Model discovery        | `list_models()` lists IDs from each provider                         |
| Task documentation     | `task2doc()` auto-creates a structured `README.md`                   |
| Translation            | `translate()` for strings, `translate_config()` for YAML             |
| Knowledge management   | `add_knowledge()` & `save_knowledge()` manage few-shot examples      |
| Error handling         | Raises `LLMAPIError` for failures, missing models, or token overflow |

## Quick Reference

| Purpose               | Method                                                  | Example                                                                  |
| --------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------ |
| Initialize client     | `LLMClient(provider, api_key, model)`                   | `client = LLMClient("openai", os.getenv("OPENAI_KEY"), "gpt-4o-mini")`   |
| Generate text         | `generate(prompt, deterministic=False, **kwargs)`       | `resp = client.generate("Hello world", temperature=0.5)`                 |
| List models           | `list_models()`                                         | `models = client.list_models()`                                          |
| Smoke-test connection | `test(ping, max_tokens)`                                | `client.test("Hi", max_tokens=5)`                                        |
| Auto-generate README  | `task2doc(logic_paths, config_paths, output_path)`      | `client.task2doc(["src/run_trial.py"], ["config/config.yaml"], "./")`    |
| Translate string      | `translate(text, target_language)`                      | `client.translate("Welcome", "Japanese")`                                |
| Translate config YAML | `translate_config(target_language, config, output_dir)` | `client.translate_config("Spanish", "./config/config.yaml", "./config")` |

## Detailed Usage Guide

### 1. Verify Native SDKs

#### 1.1 Google-GenAI (Gemini)

```python
from google import genai
# Initialize the Gemini client
genai.configure(api_key="…your Gemini API key…")
client = genai.Client()

# List available models
models = client.models.list()
model_ids = [m.name.split('/')[-1] for m in models]
print("Available models:", model_ids)

# Quick echo test
resp = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="Hello, how are you?"
)
print(resp.text)
# -> I am doing well... How are you today?
```

#### 1.2 OpenAI / Deepseek

```python
from openai import OpenAI
client = OpenAI(api_key="…your key…", base_url="https://api.deepseek.com")

# List models from Deepseek
resp = client.models.list()
ids = [m.id for m in resp.data]
print("Available models:", ids)

# Quick echo test
echo = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Hello"}],
    stream=False
)
print(echo.choices[0].message.content)
# -> Hello! How can I assist you today?
```

### 2. Use Psyflow `LLMClient` Wrapper

```python
from psyflow import LLMClient
import os

# Instantiate wrappers for each provider
gemini = LLMClient("gemini", os.getenv("GEMINI_KEY"), "gemini-2.0-flash")
deep   = LLMClient("deepseek", os.getenv("DEESEEK_KEY"), "deepseek-chat")

# List models via wrapper
print("Gemini sees:", gemini.list_models())
print("Deepseek sees:", deep.list_models())

# Echo test via wrapper
gemini_echo = gemini.test(max_tokens=5)
print("Gemini echo:", gemini_echo)
deepseal_echo = deep.test(max_tokens=5)
print("Deepseek echo:", deepseal_echo)
```

### 3. LLMs-Powered Task Documentation

Use `task2doc()` to generate a complete `README.md` for your PsyFlow task:

```python
client = LLMClient("gemini", os.getenv("GEMINI_KEY"), "gemini-2.5-flash")
readme = client.task2doc(
    logic_paths=["main.py", "src/run_trial.py"],
    config_paths=["config/config.yaml"],
    output_path="./"
)
print("Generated README content:")
print(readme)
```

This reads your code and config, sends them to the LLM, and writes a structured markdown document with:

- **Meta Information**: version, author, requirements
- **Task Overview** and **Flow Tables**
- **Configuration Summaries**: stimuli, timing, triggers
- **Methods** section ready for manuscripts

### 4. LLMs-Powered Localization

#### 4.1 In-Memory Translation

```python
client = LLMClient("deepseek", os.getenv("DEESEEK_KEY"), "deepseek-chat")
translated = client.translate_config(
    target_language="Japanese"
)
print(translated)
```

#### 4.2 Translate and Save

```python
translated = client.translate_config(
    target_language="Spanish",
    config="./config/config.yaml",
    output_dir="./config",
    output_name="config.es.yaml"
)
print("Saved to ./config/config.es.yaml")
```

This updates your YAML fields (labels, stimuli text) and writes a `.translated.yaml` file.

## Next Steps

Now that you've seen how to use LLMs with PsyFlow, you might be interested in:

- **Getting Started**: If you're new to PsyFlow, check out the [Getting Started tutorial](getting_started.md).
- **Sending Triggers**: Learn how to send hardware triggers in the [TriggerSender tutorial](send_trigger.md).
- **Building Trials**: Understand how to build complex trials in the [StimUnit tutorial](build_stimunit.md).
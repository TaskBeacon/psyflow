# Interacting with Large Language Models (LLMs)

`psyflow` provides a powerful and unified `LLMClient` to connect your experiments with various Large Language Models (LLMs). This client can be used for a variety of tasks, including generating text, creating documentation for your task, and even translating content.

The `LLMClient` supports multiple providers out-of-the-box:
- `gemini` (Google)
- `openai` (OpenAI)
- `deepseek` (DeepSeek)

## Getting Started: Initializing the Client

First, you need to import the `LLMClient` and initialize it with your provider details. You will need an API key from your chosen provider.

```python
from psyflow.LLM import LLMClient
import os

# Make sure to set your API key securely
# For example, load it from an environment variable
# api_key = os.environ.get("OPENAI_API_KEY")

llm_client = LLMClient(
    provider="openai",
    api_key="YOUR_API_KEY",  # Replace with your actual key
    model="gpt-3.5-turbo"
)
```

When you create an `LLMClient` instance, you specify the `provider`, your `api_key`, and the `model` you wish to use.

## Basic Text Generation

The most fundamental use of the client is to generate text from a prompt using the `generate()` method.

```python
prompt = "Explain the Stroop effect in one sentence."
response = llm_client.generate(prompt)
print(response)
```

You can also control the creativity of the response. For a more predictable, less random output, set `deterministic=True`.

```python
response = llm_client.generate(prompt, deterministic=True)
print(response)
```

## Listing Available Models

If you are not sure which model identifier to use, you can list all available models for your configured provider.

```python
available_models = llm_client.list_models()
print(available_models)
```
This is a great way to explore and find the perfect model for your needs.

## Advanced Usage: Auto-generating Task Documentation

One of the powerful features of the `LLMClient` is its ability to automatically generate a `README.md` file for your task based on your source code and configuration. This is done with the `task2doc()` method.

```python
# This assumes you are running from the root of a psyflow project
readme_content = llm_client.task2doc(
    logic_paths=["./src/run_trial.py", "./main.py"],
    config_paths=["./config/config.yaml"],
    output_path="./"  # Save the README.md in the current directory
)

print("README.md has been generated!")
```
This method reads your task logic and configuration, sends it to the LLM with a carefully crafted prompt, and saves the generated documentation.

## Advanced Usage: Translating Content

The `LLMClient` can also be used to translate text, which is incredibly useful for creating multilingual experiments.

### Translating a simple string
You can translate any string to a target language using the `translate()` method.
```python
english_text = "Welcome to the experiment."
german_text = llm_client.translate(english_text, target_language="German")
print(german_text)
# Expected output: Willkommen zum Experiment.
```

### Translating a configuration file
You can even translate a whole configuration file using the `translate_config()` method. This is useful for localizing instructions or stimuli defined in your `config.yaml`.
```python
# This will translate relevant fields in the config file
# and save a new file (e.g., config.translated.yaml)
translated_config = llm_client.translate_config(
    target_language="Spanish",
    config="./config/config.yaml",
    output_dir="./config"
)
print("Translated config has been saved!")
```
This will automatically find text-based stimuli and other translatable fields in your configuration and translate them.
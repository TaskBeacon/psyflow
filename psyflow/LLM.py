import os
import json
import re
import tempfile
import requests
from typing import Any, Dict, List, Union, Optional, Callable, Tuple
from urllib.parse import urlparse
import tiktoken
# --- Custom Exception for LLM API Errors ---
class LLMAPIError(Exception):
    """
    Exception raised for errors returned by LLM providers.

    :param message: Human-readable description of the error.
    :param status_code: HTTP status code if applicable.
    :param api_response: Raw response from the provider or SDK error details.
    """
    def __init__(self, message: str, status_code: Optional[int] = None, api_response: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.api_response = api_response

# --- Type for custom-provider handlers ---
ProviderHandler = Callable[[str, Dict[str, Any]], str]

class LLMClient:
    """
    Unified client for multiple LLM backends, plus utilities for task-document conversion and translation.

    Supported providers:
      - ``gemini``  : Google GenAI SDK
      - ``openai``  : Official OpenAI SDK
      - ``deepseek``: OpenAI SDK with custom base_url

    Attributes:
        provider:        Lowercase provider name.
        api_key:         API key for authentication.
        model:           Model identifier to use.
        _sdk_client:     Underlying SDK client instance.
        knowledge_base:  Few-shot examples for generation context.
    """

    _custom_handlers: Dict[str, ProviderHandler] = {}

    def __init__(self, provider: str, api_key: str, model: str):
        """
        Initialize the LLMClient.

        :param provider:  Name of the LLM provider (gemini, openai, deepseek).
        :param api_key:   Authentication key for the provider.
        :param model:     Default model identifier.
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self._sdk_client: Any = None
        self.knowledge_base: List[Tuple[List[str], List[str], str]] = []
        self.last_prompt: Optional[str] = None
        self.last_prompt_token_count: Optional[int] = None
        self.prompt_token_limit: int = 10000  # Default token limit for prompts

        if self.provider == "gemini":
            from google import genai  # noqa: F401
            from google.genai.types import GenerateContentConfig  # noqa: F401
            self._sdk_client = genai.Client(api_key=self.api_key)
            self._GenerateContentConfig = GenerateContentConfig

        elif self.provider in ("openai", "deepseek"):
            from openai import OpenAI  # noqa: F401
            base_url = "https://api.deepseek.com/v1" if self.provider == "deepseek" else None
            self._sdk_client = OpenAI(api_key=self.api_key, base_url=base_url)

        else:
            raise ValueError(f"Unsupported provider '{provider}'")

    @classmethod
    def register_provider(cls, name: str, handler: ProviderHandler):
        """
        Register a custom provider handler.

        :param name:    Identifier for the custom provider.
        :param handler: Callable that takes (prompt, kwargs) and returns response string.
        """
        cls._custom_handlers[name.lower()] = handler

    def generate(self, prompt: str, *, deterministic: bool = False, **kwargs) -> str:
        """
        Generate text completion from the configured model.

        :param prompt:       Input prompt for the LLM.
        :param deterministic: If True, zero out sampling randomness.
        :param kwargs:       Additional generation parameters (e.g., temperature, stop).
        :return:             Generated text response.
        :raises LLMAPIError: If the provider returns an error.
        """
        # Apply deterministic settings
        if deterministic:
            kwargs.update({
                "temperature": 0.0,
                "top_p": 1.0,
                "top_k": 1,
                "candidate_count": 1,
            })
        p = self.provider

        # --- Gemini ---
        if p == "gemini":
            params = self._filter_genai_kwargs(kwargs)
            config = self._GenerateContentConfig(**params) if params else None
            try:
                if config:
                    resp = self._sdk_client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=config
                    )
                else:
                    resp = self._sdk_client.models.generate_content(
                        model=self.model,
                        contents=prompt
                    )
                return resp.text
            except Exception as e:
                raise LLMAPIError(f"Gemini API error: {e}")

        # --- OpenAI / Deepseek ---
        if p in ("openai", "deepseek"):
            params = self._filter_openai_kwargs(kwargs)
            try:
                resp = self._sdk_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False,
                    **params
                )
                choice = resp.choices[0].message.content if resp.choices else None
                if choice is None:
                    raise LLMAPIError("No content in response", api_response=resp)
                return choice
            except Exception as e:
                raise LLMAPIError(f"{p.capitalize()} API error: {e}")

        # --- Custom handler ---
        handler = self._custom_handlers.get(p)
        if handler:
            try:
                return handler(prompt, {"model": self.model, **kwargs})
            except Exception as e:
                raise LLMAPIError(f"Handler '{p}' error: {e}")

        raise ValueError(f"No handler for provider '{p}'")

    def list_models(self) -> List[str]:
        """
        Retrieve a list of available model IDs for the current provider.

        :return:             List of model identifiers.
        :raises LLMAPIError: If no models are returned or listing fails.
        """
        p = self.provider
        if p == "gemini":
            raw = self._sdk_client.models.list()
            names = [m.name.split("/",1)[-1] for m in raw]
        elif p in ("openai", "deepseek"):
            resp = self._sdk_client.models.list()
            data = getattr(resp, "data", None)
            if not data:
                raise LLMAPIError(f"No models from {p}")
            names = [m.id for m in data]
        else:
            raise ValueError(f"Provider '{p}' does not support model listing")

        if not names:
            raise LLMAPIError(f"Empty model list for {p}")
        return names

    def test(self, ping: str = "Hello", max_tokens: int = 1) -> Optional[str]:
        """
        Smoke test connection and small completion.

        1. Ensures the configured model exists.
        2. Sends a small ping and returns its response.

        :param ping:       Prompt to send for testing.
        :param max_tokens: Maximum tokens to request.
        :return:           Ping response string.
        :raises LLMAPIError: On model not found or generation failure.
        """
        available = self.list_models()
        if self.model not in available:
            raise LLMAPIError(f"Model '{self.model}' not in {available}")
        return self.generate(
            prompt=ping,
            deterministic=True,
            temperature=0.0,
            max_tokens=max_tokens
        )
    
    def _count_tokens(self, text: str) -> int:
        """
        Return the token count for `text` under the currently-configured model.
        Requires `tiktoken`.
        """
        try:
            enc = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # fallback to default encoding
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    @staticmethod
    def _filter_genai_kwargs(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter and rename kwargs for Google GenAI.

        :param params: Raw generation parameters.
        :return:       Filtered and mapped parameters.
        """
        allowed = {"temperature","max_tokens","top_p","top_k","stop","candidate_count","system_instruction"}
        mapped: Dict[str, Any] = {}
        for k, v in params.items():
            if k not in allowed:
                continue
            if k == "max_tokens":
                mapped["max_output_tokens"] = v
            elif k == "stop":
                mapped["stop_sequences"] = v
            else:
                mapped[k] = v
        return mapped

    @staticmethod
    def _filter_openai_kwargs(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter kwargs for OpenAI-style chat completions.

        :param params: Raw generation parameters.
        :return:       Filtered parameters for OpenAI SDK.
        """
        valid = {"temperature","max_tokens","top_p","stop","presence_penalty","frequency_penalty","n","logit_bias","stream"}
        return {k: v for k, v in params.items() if k in valid}


    @staticmethod
    def _parse_entry(
        entry: Dict[str, Union[str, List[str]]]
    ) -> Dict[str, str]:
        """
        Parse one dict of {key → file(s)/URL(s)/text} into {key → combined text}.

        :param entry:  
          A mapping where each value is either:
            - a list of local file paths or HTTP URLs
            - a raw text string
        :return:  
          A dict mapping each key to the concatenated text contents.
        """
        out: Dict[str, str] = {}
        def _load(loc: str) -> Optional[str]:
            # Local file?
            if os.path.isfile(loc):
                with open(loc, 'r', encoding='utf-8') as f:
                    return f.read()
            # URL?
            parsed = urlparse(loc)
            if parsed.scheme in ("http", "https"):
                resp = requests.get(loc, timeout=10)
                resp.raise_for_status()
                return resp.text
            return None

        for key, val in entry.items():
            if isinstance(val, list):
                chunks = []
                for loc in val:
                    txt = _load(loc)
                    if txt:
                        chunks.append(txt)
                if chunks:
                    out[key] = "\n\n".join(chunks)

            elif isinstance(val, str):
                if val.startswith(("http://", "https://")):
                    txt = _load(val)
                    if txt:
                        out[key] = txt
                else:
                    out[key] = val.strip()

        return out
    
    
    def add_knowledge(
            self,
            source: Union[
                str,                                  # path to JSON file
                List[Dict[str, Union[str, List[str]]]]  # in-memory entries
            ]
        ) -> None:
        """
        Bulk-load few-shot examples into memory from either:
        
        1. A JSON file path containing a list of example-dicts, or
        2. A list of example-dicts directly.
        
        Each example-dict maps keys to either:
          • List[str] of file paths or URLs → will be parsed via `_parse_entry()`
          • Raw text (str)                 → will be stripped and stored as-is
        
        :param source:
          - If `str`, treated as path to a JSON file containing List[Dict[...]].
          - If `list`, treated as in-memory list of example dicts.
        :raises ValueError: on invalid JSON structure or unsupported source type.
        """
        if isinstance(source, str):
            # load from JSON file
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Expected a JSON file containing a list of examples")
            for ex in data:
                if isinstance(ex, dict):
                    # assume already parsed JSON examples
                    self.knowledge_base.append(ex)
        elif isinstance(source, list):
            # parse each entry (files/URLs/raw text) into text blobs
            for ex in source:
                if not isinstance(ex, dict):
                    continue
                parsed = self._parse_entry(ex)
                if parsed:
                    self.knowledge_base.append(parsed)
        else:
            raise ValueError(
                "add_knowledge() requires a JSON file path or a list of example-dicts"
            )

    def save_knowledge(self, json_path: str) -> None:
        """
        Write current knowledge_base (a list of dicts) to a JSON file.
        """
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)



    def task2doc(
        self,
        logic_paths: Optional[List[str]] = None,
        config_paths: Optional[List[str]] = None,
        prompt: Optional[str] = None,
        deterministic: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 1500,
        output_path: Optional[str] = None
    ) -> str:
        """
        Summarize a task into README.md.

        1. Renders few-shot examples from `knowledge_base`.  
        2. Inserts your instruction.  
        3. Renders the one-off task context.  
        4. Sends the combined JSON payload to the LLM.  
        5. Optionally writes the result to `output_path`.

        :param logic_paths:   Python file paths for this task context.
        :param config_paths:  YAML config paths for this task context.
        :param prompt:        Custom instruction (defaults provided).
        :param deterministic: Force deterministic decoding.
        :param temperature:   Sampling temperature (ignored if deterministic).
        :param max_tokens:    Maximum tokens to generate.
        :param output_path:
          - If a directory, writes “README.md” inside it.
          - If a path ending in “.md”, writes to that file.
          - If omitted, no file is written.
        :return:              The generated README content.
        """
        # ── 1) Resolve defaults ─────────────────────────────────────
        logic  = logic_paths  or ["./src/run_trial.py", "./src/utils.py", "./main.py"]
        config = config_paths or ["./config/config.yaml"]

        # ── 2) Build one-off context dict (no side-effects) ─────────
        task_context = self._parse_entry({
            "task_logic":  logic,
            "task_config": config
        })

        # ── 3) Build prompt payload in three parts ─────────────────
        instr = prompt or (
            "You are a documentation assistant. Using the examples above, produce a concise README.md"
            " for the following task that:\n"
            "1) Summarize the core task logic.\n"
            "2) Explain the configuration options.\n"
            ""
        )

        if self.knowledge_base:
            payload = {
                "examples":   self.knowledge_base,  # few-shot KB
                "instruction": instr,               # your request
                "context":    task_context               # this task’s code + config
            }
        else:
            payload = {
                "instruction": instr,               # your request
                "context":    task_context               # this task’s code + config
            }
        full_prompt = json.dumps(payload, indent=2, ensure_ascii=False)

        # ── 4) Store & enforce token limits ─────────────────────────
        self.last_prompt = full_prompt
        self.last_prompt_token_count = self._count_tokens(full_prompt)
        if self.last_prompt_token_count > self.prompt_token_limit:
            raise LLMAPIError(
                f"Prompt too large ({self.last_prompt_token_count} tokens). "
                f"Limit is {self.prompt_token_limit}."
                "Try to reduce the number of instructions or the number of examples."
                "Or increase the prompt_token_limit in the LLMClient instance."
            )

        # ── 5) Call the LLM ────────────────────────────────────────
        result = self.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # ── 6) Optionally write out to a README.md file ───────────
        if output_path:
            # If a directory, create it (if needed) and write README.md inside
            if os.path.isdir(output_path):
                out_file = os.path.join(output_path, "README.md")
            else:
                # Not a dir: if endswith .md and parent dir exists, use it
                _, ext = os.path.splitext(output_path)
                if ext.lower() == ".md":
                    parent = os.path.dirname(output_path)
                    if parent and not os.path.isdir(parent):
                        os.makedirs(parent, exist_ok=True)
                    out_file = output_path
                else:
                    # Treat as a directory
                    os.makedirs(output_path, exist_ok=True)
                    out_file = os.path.join(output_path, "README.md")
            with open(out_file, "w", encoding="utf-8") as fw:
                fw.write(result)

        return result
            
    def doc2task(
        self,
        doc_text: str,
        taps_root: str = ".",
        prompt: Optional[str] = None,
        deterministic: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 10000,
        file_names: Optional[List[str]] = None,
        return_raw: bool = False
    ) -> Union[str, Dict[str,str]]:
        """
        Reconstruct multiple interdependent source files from a task description,
        with utils.py treated as optional.

        :param doc_text:    Directory, README path, or raw description string.
        :param taps_root:   Root folder to write outputs under `<task_name>/`.
        :param prompt:      Custom instruction prompt (defaults shown below).
        :param deterministic: Force deterministic sampling.
        :param temperature: Sampling temperature.
        :param max_tokens:  Max tokens to generate.
        :param file_names:  List of filenames to request. Defaults to
                            ["run_trial.py","utils.py","main.py","config.yaml"].
        :param return_raw:  If True, return raw LLM markdown; no files written.
        :return:
        - If return_raw: the raw markdown string from the LLM.
        - Otherwise: a dict mapping each filename → its saved path (excluding any empty utils.py).
        :raises ValueError: if any **required** section is missing (all except utils.py).
        """
        # 1) Load doc_text into `desc`
        if os.path.isdir(doc_text):
            md = os.path.join(doc_text, "README.md")
            with open(md, 'r', encoding='utf-8') as f: desc = f.read()
        elif os.path.isfile(doc_text) and doc_text.lower().endswith((".md", ".txt")):
            with open(doc_text, 'r', encoding='utf-8') as f: desc = f.read()
        else:
            desc = doc_text

        # 2) Determine files (utils.py is optional)
        fnames = file_names or ["run_trial.py", "utils.py", "main.py", "config.yaml"]
        required = {"run_trial.py", "main.py", "config.yaml"}

        # 3) Build instruction
        instr = prompt or (
            "You are a code-generation assistant. Given the examples below and the task description, "
            "output markdown sections for each file. Use headers ### <filename> followed by a fenced block:\n\n" +
            "\n".join(f"### {fn}" for fn in fnames) +
            "\n\nUse ```python for .py files and ```yaml for .yaml. Omit utils.py if unused."
        )

        # 4) Build payload
        if self.knowledge_base:
            payload = {
                "examples":   self.knowledge_base,  # few-shot KB
                "instruction": instr,               # your request
                "context":    desc               # this task’s code + config
            }
        else:
            payload = {
                "instruction": instr,               # your request
                "context":    desc               # this task’s code + config
            }

        full_prompt = json.dumps(payload, indent=2, ensure_ascii=False)

        # 5) Token check
        self.last_prompt = full_prompt
        self.last_prompt_token_count = self._count_tokens(full_prompt)
        if self.last_prompt_token_count > self.prompt_token_limit:
            raise LLMAPIError(f"Prompt too large ({self.last_prompt_token_count} tokens).")

        # 6) Call LLM
        raw = self.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        )
        # 7) Extract sections
        out_paths: Dict[str, str] = {}
        tm = re.search(r'^#\s*(.+)', desc, re.M)
        title = tm.group(1).strip() if tm else "task"
        task_name = re.sub(r'\W+','_', title.lower()).strip('_')
        task_dir = os.path.join(taps_root, task_name)
        os.makedirs(task_dir, exist_ok=True)

        for fn in fnames:
            lang = "yaml" if fn.endswith(".yaml") else "python"
            pattern = rf"###\s*{re.escape(fn)}\s*```{lang}\n(.*?)```"
            m = re.search(pattern, raw, re.S)
            if not m or not m.group(1).strip():
                if fn in required:
                    raise ValueError(f"Required section for `{fn}` not found or empty.")
                else:
                    # skip optional utils.py
                    continue
            content = m.group(1).strip()
            path = os.path.join(task_dir, fn)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            out_paths[fn] = path
        if return_raw:
            return raw
        else:
            return out_paths


    def translate(
        self,
        text: str,
        target_language: str,
        prompt: Optional[str] = None,
        deterministic: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 800
    ) -> str:
        """
        Translate text, capturing raw prompt and token count before sending.

        :param text:             Input text to translate.
        :param target_language:  Target language name.
        :param prompt:           Optional custom instruction prompt.
        :param deterministic:    Force deterministic output.
        :param temperature:      Sampling temperature.
        :param max_tokens:       Max tokens to generate.
        :return:                 Translated text.
        """
        instr = prompt or f"Translate the following text into {target_language}, preserving formatting."

        payload = {
            "examples": self.build_examples_json(),
            "instruction": instr,
            "text": text
        }
        full_prompt = json.dumps(payload, indent=2, ensure_ascii=False)

        self.last_prompt = full_prompt
        self.last_prompt_token_count = self._count_tokens(full_prompt)

        return self.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        )
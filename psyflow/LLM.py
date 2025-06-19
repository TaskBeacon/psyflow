import os
import json
import re
import requests
from typing import Any, Dict, List, Union, Optional, Callable, Tuple
from urllib.parse import urlparse
import tiktoken
from importlib import resources
import yaml
from psyflow import load_config
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
        self.last_response: Optional[str] = None
        self.last_response_token_count: Optional[int] = None

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
        """Count tokens for the active model.

        Parameters
        ----------
        text : str
            Text to be encoded.

        Returns
        -------
        int
            Number of tokens consumed by ``text`` under the current model's
            tokenizer.
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

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """
        Remove a leading ```…\n and a trailing \n``` fence if present.
        """
        # remove leading fence
        text = re.sub(r'^\s*```[^\n]*\n', '', text)
        # remove trailing fence
        text = re.sub(r'\n```$', '', text)
        return text
    
    @staticmethod
    def _save_readme(content: str, output_path: str) -> None:
        """
        Write `content` to `output_path`, handling directories and file extensions.
        """
        if os.path.isdir(output_path):
            out_file = os.path.join(output_path, "README.md")
        else:
            base, ext = os.path.splitext(output_path)
            if ext.lower() == ".md":
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                out_file = output_path
            else:
                os.makedirs(output_path, exist_ok=True)
                out_file = os.path.join(output_path, "README.md")

        cleaned = LLMClient._strip_code_fences(content)
        with open(out_file, "w", encoding="utf-8") as fw:
            fw.write(cleaned)

    def save_readme(self, *args) -> None:
        """
        Save a README to disk. Call as either:
          save_readme(output_path)
          save_readme(content, output_path)

        If only output_path is provided, uses self.last_response.
        """
        if len(args) == 1:
            content = self.last_response
            output_path = args[0]
        elif len(args) == 2:
            content, output_path = args
        else:
            raise ValueError("save_readme() expects save_readme(path) or save_readme(content, path)")

        if not content:
            raise ValueError("No content available to save. Have you called task2doc() yet?")
        try:
            self._save_readme(content, output_path)
        except Exception as e:
            print(f"Warning: failed to write README to {output_path}: {e}")
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
        Summarize a task into README.md. If `prompt` is None, loads the
        instruction template from `psyflow/templates/task2doc_prompt.txt`.
        """
        # ── 1) Resolve defaults and validate existence ────────────────────
        # Required logic files
        default_logic = ["./src/run_trial.py", "./main.py"]
        # Optional helper
        optional_utils = "./src/utils.py"

        # Use user-specified logic_paths if given, else defaults
        if logic_paths:
            logic = logic_paths
        else:
            logic = default_logic.copy()
            if os.path.exists(optional_utils):
                logic.append(optional_utils)

        # Ensure each logic file exists
        missing_logic = [p for p in logic if not os.path.exists(p)]
        if missing_logic:
            raise FileNotFoundError(
                f"The following logic files were not found: {missing_logic}"
            )

        # Config file(s)
        default_config = ["./config/config.yaml"]
        config = config_paths if config_paths else default_config

        # Ensure each config file exists
        missing_cfg = [p for p in config if not os.path.exists(p)]
        if missing_cfg:
            raise FileNotFoundError(
                f"The following config files were not found: {missing_cfg}"
            )

        # 2) Build one-off context
        task_context = self._parse_entry({
            "task_logic":  logic,
            "task_config": config
        })

        # 3) Determine instruction text
        instr_text = prompt or resources.read_text(
            "psyflow.templates", "task2doc_prompt.txt"
        )

        # 4) Build payload
        payload: Dict[str, Any] = {
            "task_context": task_context,
            "instruction":  instr_text,
        }
        if self.knowledge_base:
            payload["examples"] = self.knowledge_base
        full_prompt = json.dumps(payload, indent=2, ensure_ascii=False)

        # 5) Store & enforce token limits for prompt
        self.last_prompt = full_prompt
        self.last_prompt_token_count = self._count_tokens(full_prompt)
        if self.last_prompt_token_count > self.prompt_token_limit:
            raise LLMAPIError(
                f"Prompt too large ({self.last_prompt_token_count} tokens), "
                f"limit is {self.prompt_token_limit}."
            )

        # 6) Call LLM
        result = self.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # store response and its token count
        self.last_response = result
        self.last_response_token_count = self._count_tokens(result)

        # 7) Optionally write to disk (uses save_readme)
        if output_path:
            self.save_readme(output_path)

        return result

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
        Translate arbitrary text into the target language, preserving formatting
        and placeholders. Returns only the translated text—no explanations.
        """
        # 1) Build a strict instruction
        instr = prompt or (
            f"Translate the following text into {target_language}. "
            "Output ONLY the translated text, preserving orignal formatting, "
            "indentation, and placeholder tokens (e.g. {field}). "
            "Do NOT include any explanations or comments."
        )

        # 2) Combine instruction and text
        full_prompt = instr + "\n\n" + text

        # 3) Record prompt & token count
        self.last_prompt = full_prompt
        self.last_prompt_token_count = self._count_tokens(full_prompt)

        # 4) Call the LLM
        result = self.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        ) or ""

        # 5) Record response & its token count
        self.last_response = result
        self.last_response_token_count = self._count_tokens(result)

        return result

    def _str_presenter(dumper, data):
        # if the string has a newline, use block style;
        # otherwise fall back to the default
        style = '|' if '\n' in data else None
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)

    def translate_config(
        self,
        target_language: str,
        config: Optional[Union[str, Dict[str, Any]]] = None,
        output_dir: Optional[str] = None,
        output_name: Optional[str] = None,
        prompt: Optional[str] = None,
        deterministic: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Translate selected fields of a YAML config:
          - subinfo_mapping values
          - any stimuli entries where type is 'text' or 'textbox'

        If `config` is:
          • a file path (str) → loaded via load_config()
          • a dict returned from load_config()
          • None → defaults to "./config/config.yaml"

        If `output_dir` is provided, writes out a translated YAML:
          filename is `output_name` if given, else original basename + ".translated.yaml".

        Returns the updated raw YAML dict.
        """
        # 1) Determine config source
        if config is None:
            default_path = os.path.join(os.getcwd(), "config", "config.yaml")
            if not os.path.exists(default_path):
                raise FileNotFoundError(f"No config found at {default_path}")
            config = default_path

        # 2) Load or unwrap structured config
        if isinstance(config, str):
            structured = load_config(config)
            raw_yaml = structured['raw']
            original_name = os.path.splitext(os.path.basename(config))[0]
        elif isinstance(config, dict) and 'raw' in config:
            structured = config
            raw_yaml = structured['raw']
            original_name = "config"
        else:
            raise ValueError("`config` must be None, a path, or a dict from load_config()")

        # 3) Translate subinfo_mapping
        mapping = structured['subform_config']['subinfo_mapping']
        for key, val in mapping.items():
            if isinstance(val, str) and val.strip():
                mapping[key] = self.translate(
                    text=val,
                    target_language=target_language,
                    prompt=prompt or (
                        f"Translate this label into {target_language}. "
                         "Output ONLY the translated text, preserving original format. No trailing newline"
                    ),
                    deterministic=deterministic,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

        # 4) Translate stimuli text fields
        stim_config = structured['stim_config']
        for name, spec in stim_config.items():
            if spec.get('type') in ('text', 'textbox') and 'text' in spec:
                original = spec['text']
                if isinstance(original, str) and original.strip():
                    raw_yaml['stimuli'][name]['text'] = self.translate(
                        text=original,
                        target_language=target_language,
                        prompt=prompt or (
                            f"Translate this stimulus text into {target_language}. "
                            "Output ONLY the translated text, preserving original format. No trailing newline"
                        ),
                        deterministic=deterministic,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

        # 5) Optionally write translated YAML to disk
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = output_name or f"{original_name}.translated.yaml"
            out_path = os.path.join(output_dir, filename)
            
            LLMDumper = type("LLMDumper", (yaml.SafeDumper,), {})
            def _str_presenter(dumper, data):
                style = '|' if '\n' in data else None
                return dumper.represent_scalar(
                    'tag:yaml.org,2002:str',
                    data,
                    style=style
                )
            LLMDumper.add_representer(str, _str_presenter)
            def _list_presenter(dumper, data):
            # inline only for lists of scalars length ≤ 10
                if (
                    len(data) <= 10 and
                    all(not isinstance(x, (dict, list)) for x in data)
                ):
                    flow = True
                else:
                    flow = False
                return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)
            LLMDumper.add_representer(list, _list_presenter)

            # Monkey‐patch it onto SafeDumper:
            yaml.SafeDumper.add_representer(str, _str_presenter)
            with open(out_path, 'w', encoding='utf-8') as f:
                yaml.dump(raw_yaml, f, allow_unicode=True,sort_keys=False, Dumper=LLMDumper)
        
        task_keys = ['window', 'task', 'timing']
        structured_config = {
            'raw': raw_yaml,
            'task_config': {k: v for key in task_keys for k, v in raw_yaml.get(key, {}).items()},
            'stim_config': raw_yaml.get('stimuli', {}),
            'subform_config': {
                'subinfo_fields': raw_yaml.get('subinfo_fields', []),
                'subinfo_mapping': raw_yaml.get('subinfo_mapping', {}),
            },
            'trigger_config': raw_yaml.get('triggers', {}),
            'controller_config': raw_yaml.get('controller', {}),
        }

        return structured_config


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



import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

# --- Custom Exception for LLM API Errors ---
class LLMAPIError(Exception):
    """
    Custom exception for unifying LLM API errors across different providers.

    Attributes:
        message (str): A human-readable error message.
        status_code (Optional[int]]): The HTTP status code, if available.
        api_response (Optional[Any]): Raw API response or SDK error details.
    """
    def __init__(self, message: str, status_code: Optional[int] = None, api_response: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.api_response = api_response


class LLMAPIError(Exception):
    """Unified exception for LLM API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, api_response: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.api_response = api_response


# Type for custom‐provider handlers
ProviderHandler = Callable[[str, Dict[str, Any]], str]

class LLMClient:
    """
    Unified interface to multiple LLM backends with optional deterministic mode.

    Providers:
      - "gemini"   → google-genai SDK
      - "openai"   → OpenAI SDK
      - "deepseek" → OpenAI SDK with custom base_url
    """

    _custom_handlers: Dict[str, ProviderHandler] = {}

    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self._sdk_client: Any = None

        if self.provider == "gemini":
            try:
                from google import genai
                from google.genai.types import GenerateContentConfig, SafetySetting
                self._sdk_client = genai.Client(api_key=self.api_key)
                self._GenerateContentConfig = GenerateContentConfig
                self._SafetySetting = SafetySetting
            except ImportError as e:
                raise ImportError("Install google-genai: pip install google-genai") from e
        elif self.provider in ("openai", "deepseek"):
            try:
                import openai
                from openai import OpenAI
                base = "https://api.deepseek.com/v1" if self.provider == "deepseek" else None
                self._sdk_client = OpenAI(api_key=self.api_key, base_url=base)
            except ImportError as e:
                raise ImportError("Install openai: pip install openai") from e

    @classmethod
    def register_provider(cls, name: str, handler: ProviderHandler):
        cls._custom_handlers[name.lower()] = handler

    def generate(self, prompt: str, *, deterministic: bool = False, **kwargs) -> str:
        """
        Generate text. If deterministic=True, forces a deterministic decode by
        zeroing out sampling parameters.
        """
        if deterministic:
            kwargs["temperature"]     = 0.0
            kwargs["top_p"]           = 1.0
            kwargs["top_k"]           = 1
            kwargs["candidate_count"] = 1  # for Gemini only

        p = self.provider

        if p == "gemini":
            if not self._sdk_client:
                raise ValueError("Gemini client not initialized.")
            try:
                params = self._filter_genai_kwargs(kwargs.copy())
                safety = params.pop("safety_settings", None)
                config = self._GenerateContentConfig(**params) if params else None
                safety_list = [self._SafetySetting(**s) for s in safety] if safety else None

                resp = self._sdk_client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                    safety_settings=safety_list
                )
                return resp.text
            except Exception as e:
                raise LLMAPIError(f"Gemini API error: {e}")

        if p in ("openai", "deepseek"):
            if not self._sdk_client:
                raise ValueError(f"{p.capitalize()} client not initialized.")
            try:
                params = self._filter_openai_kwargs(kwargs.copy())
                resp = self._sdk_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False,
                    **params
                )
                choice = resp.choices[0].message.content if resp.choices else None
                if choice is None:
                    raise LLMAPIError("No content in response", api_response=resp.model_dump())
                return choice
            except Exception as e:
                raise LLMAPIError(f"{p.capitalize()} API error: {e}")

        handler = self._custom_handlers.get(p)
        if handler:
            try:
                return handler(prompt, {"model": self.model, **kwargs})
            except Exception as e:
                raise LLMAPIError(f"Custom handler '{p}' error: {e}")

        raise ValueError(f"No handler for provider '{self.provider}'")

    def test_connection(self, timeout: float = 5.0) -> bool:
        p = self.provider
        if p == "gemini":
            models = self._sdk_client.models.list(timeout=timeout)
            if not models:
                raise LLMAPIError("No models returned from Gemini")
            return True
        if p in ("openai", "deepseek"):
            models = self._sdk_client.models.list(request_timeout=timeout)
            if not getattr(models, "data", None):
                raise LLMAPIError(f"No models returned from {p.capitalize()}")
            return True
        handler = self._custom_handlers.get(p)
        if handler:
            handler("", {"model": self.model, "max_tokens": 1})
            return True
        raise ValueError(f"No connection test for provider '{p}'")

    @staticmethod
    def _filter_genai_kwargs(params: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {
            "temperature", "max_tokens", "top_p", "top_k",
            "stop", "candidate_count", "system_instruction"
        }
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
        if "safety_settings" in params:
            mapped["safety_settings"] = params["safety_settings"]
        return mapped

    @staticmethod
    def _filter_openai_kwargs(params: Dict[str, Any]) -> Dict[str, Any]:
        valid = {
            "temperature", "max_tokens", "top_p", "stop",
            "presence_penalty", "frequency_penalty",
            "n", "logit_bias", "stream"
        }
        return {k: v for k, v in params.items() if k in valid}


class TaskMapper:
    """
    Bidirectional converter between task code/config and README text,
    with support for translation and few-shot examples from a curated knowledge base.

    Methods:
      - task2doc: Summarize Python task code and YAML configs into a README.md narrative.
      - doc2task: Reconstruct task code and config from a README.md and save under a TAPS folder.
      - translate: Translate text, preserving formatting and code fences.
      - add_example: Add a new few-shot example to the knowledge base.

    Attributes:
        llm: The LLMClient instance for text generation.
        examples: List of examples, each as (logic_paths, config_paths, readme_text).
    """

    def __init__(
        self,
        llm_client: LLMClient,
        examples: Optional[List[Tuple[List[str], List[str], str]]] = None
    ):
        """
        Args:
            llm_client: Initialized LLMClient for text generation.
            examples:   Optional list of examples, each a tuple
                        (logic_paths, config_paths, readme_text) for few-shot prompting.
        """
        self.llm = llm_client
        self.examples = examples or []

    def add_example(
        self,
        logic_paths: List[str],
        config_paths: List[str],
        readme_text: str
    ) -> None:
        """
        Add a few-shot example by specifying code and config file paths, plus the README narrative.
        """
        self.examples.append((logic_paths, config_paths, readme_text))

    @staticmethod
    def _read_file(path: str) -> Optional[str]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception:
            return None

    def _build_sections(
        self,
        logic_paths: List[str],
        config_paths: List[str]
    ) -> str:
        """
        Create fenced code blocks for logic and config file contents.
        """
        parts: List[str] = []
        for p in logic_paths:
            content = self._read_file(p)
            if content:
                parts.append(f"```python\n{content}\n```")
        for p in config_paths:
            content = self._read_file(p)
            if content:
                parts.append(f"```yaml\n{content}\n```")
        return "\n\n".join(parts)

    def _build_examples(self) -> str:
        """
        Construct few-shot example blocks with separate Code, Config, and README sections.
        """
        if not self.examples:
            return ""
        blocks: List[str] = []
        for idx, (logic_paths, config_paths, readme) in enumerate(self.examples, start=1):
            # Code section
            code_blocks = []
            for p in logic_paths:
                content = self._read_file(p)
                if content:
                    code_blocks.append(f"```python\n{content}\n```")
            # Config section
            cfg_blocks = []
            for p in config_paths:
                content = self._read_file(p)
                if content:
                    cfg_blocks.append(f"```yaml\n{content}\n```")
            blocks.append(f"### Example {idx} Code\n" + "\n\n".join(code_blocks))
            blocks.append(f"### Example {idx} Config\n" + "\n\n".join(cfg_blocks))
            blocks.append(f"### Example {idx} README\n```markdown\n{readme}\n```")
        return "\n\n".join(blocks)

    def task2doc(
        self,
        logic_paths: List[str],
        config_paths: Optional[List[str]] = None,
        prompt: Optional[str] = None,
        deterministic: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        """
        Summarize code + config files into a structured README.md narrative.

        Args:
            logic_paths: List of paths to .py files.
            config_paths: Optional list of paths to .yaml files.
            prompt: Optional custom instruction prompt.
            deterministic: If True, forces deterministic decoding.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.

        Returns:
            Generated README.md content.
        """
        default_prompt = (
            "You are a documentation assistant. Produce a concise, well-structured README.md:\n"
            "1. Summarize purpose and key functions of the Python code.\n"
            "2. Explain each top-level configuration option."
        )
        instruction = prompt if prompt is not None else default_prompt
        parts: List[str] = []
        ex = self._build_examples()
        if ex:
            parts.append(ex)
        parts.append(instruction)
        body = self._build_sections(logic_paths, config_paths or [])
        parts.append(body)
        full_prompt = "\n\n".join(parts)

        return self.llm.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def doc2task(
        self,
        readme_text: str,
        taps_root: str = ".",
        prompt: Optional[str] = None,
        deterministic: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> Tuple[str, str]:
        """
        Reconstruct task code and config from a README.md narrative,
        save under `taps_root/<task_name>/` and return (code_path, config_path).

        Args:
            readme_text: The README.md content to parse.
            taps_root: Root directory for saving the task.
            prompt: Optional custom instruction prompt.
            deterministic: If True, forces deterministic decoding.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.

        Returns:
            Tuple of (path_to_python_file, path_to_yaml_file).
        """
        default_prompt = (
            "You are a task-generation assistant. Given this README.md, reconstruct "
            "the task's code and YAML config. Provide two fenced blocks: python and yaml."
        )
        instruction = prompt if prompt is not None else default_prompt
        parts: List[str] = []
        ex = self._build_examples()
        if ex:
            parts.append(ex)
        parts.append(instruction)
        parts.append(readme_text)
        full_prompt = "\n\n".join(parts)

        raw = self.llm.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        )
        code_match = re.search(r'```python\n(.*?)```', raw, re.S)
        yaml_match = re.search(r'```yaml\n(.*?)```', raw, re.S)
        if not code_match or not yaml_match:
            raise ValueError("Missing code or config blocks in output.")

        code = code_match.group(1).strip()
        config = yaml_match.group(1).strip()
        m = re.search(r'^#\s*(.+)', readme_text, re.M)
        name = m.group(1).strip() if m else 'generated_task'
        task_name = re.sub(r'\W+', '_', name.lower()).strip('_')
        task_dir = os.path.join(taps_root, task_name)
        os.makedirs(task_dir, exist_ok=True)

        code_path = os.path.join(task_dir, f"{task_name}.py")
        cfg_path = os.path.join(task_dir, f"{task_name}.yaml")
        with open(code_path, 'w', encoding='utf-8') as fc:
            fc.write(code)
        with open(cfg_path, 'w', encoding='utf-8') as fy:
            fy.write(config)

        return code_path, cfg_path

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
        Translate text into a target language, preserving formatting and code fences.

        Args:
            text: The text to translate.
            target_language: e.g. "Japanese", "French".
            prompt: Optional custom instruction prompt.
            deterministic: If True, forces deterministic decoding.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.

        Returns:
            Translated text.
        """
        default_prompt = (
            f"Translate the following text into {target_language}, preserving formatting and code fences."
        )
        instruction = prompt if prompt is not None else default_prompt
        parts: List[str] = []
        ex = self._build_examples()
        if ex:
            parts.append(ex)
        parts.append(instruction)
        parts.append(text)
        full_prompt = "\n\n".join(parts)

        return self.llm.generate(
            prompt=full_prompt,
            deterministic=deterministic,
            temperature=temperature,
            max_tokens=max_tokens
        )
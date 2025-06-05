from __future__ import annotations
from pathlib import Path
import re


def read_version() -> str:
    """Return project version from pyproject.toml."""
    root = Path(__file__).resolve().parent.parent
    pyproject = root / "pyproject.toml"
    text = pyproject.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        raise RuntimeError("Version not found in pyproject.toml")
    return match.group(1)


__version__ = read_version()

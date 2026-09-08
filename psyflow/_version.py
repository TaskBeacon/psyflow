from __future__ import annotations
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import re


def read_version() -> str:
    """Read installed metadata, with a fallback for an uninstalled checkout."""
    try:
        return version("psyflow")
    except PackageNotFoundError:
        pass

    root = Path(__file__).resolve().parent.parent
    pyproject = root / "pyproject.toml"
    try:
        text = pyproject.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "0+unknown"
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "0+unknown"


__version__ = read_version()

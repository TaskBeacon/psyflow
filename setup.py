from pathlib import Path
import re
from setuptools import setup, find_packages


def read_version() -> str:
    text = Path(__file__).with_name("pyproject.toml").read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        raise RuntimeError("Version not found in pyproject.toml")
    return match.group(1)

setup(
    name="psyflow",
    version=read_version(),
    description="A utility package for building modular PsychoPy experiments.",
    author="Zhipeng Cao",
    author_email="zhipeng30@foxmail.com",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "psychopy",
        "numpy",
        "pandas",
        "click",           # for CLI support
        "cookiecutter",    # for template-based scaffolding
        "pyyaml",          # for YAML configuration parsing
        "pyserial",        # for serial port communication
        "edge-tts",        # for text-to-speech support
    ],
    entry_points={
        "console_scripts": [
            "psyflow = psyflow.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "psyflow": ["templates/cookiecutter-psyflow/**/*"],
    },
    zip_safe=False
)

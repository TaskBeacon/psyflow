from setuptools import setup, find_packages

setup(
    name="psyflow",
    version="0.1.0",
    description="A utility package for building modular PsychoPy experiments.",
    author="Zhipeng Cao",
    author_email="zhipeng30@foxmail.com",
    packages=find_packages(),
    install_requires=[
        "psychopy",
        "numpy",
        "pandas",
        "click",           # for CLI support
        "cookiecutter",    # for template-based scaffolding
    ],
    entry_points={
        "console_scripts": [
            "psyflow-init = psyflow.cli:climain"],
    },
    include_package_data=True,
    package_data={
        "psyflow": ["templates/cookiecutter-psyflow/**/*"],
    },
    zip_safe=False
)

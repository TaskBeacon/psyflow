from setuptools import setup, find_packages

setup(
    name="psyflow",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "psychopy",
        "numpy",
        "pandas"
    ],
)

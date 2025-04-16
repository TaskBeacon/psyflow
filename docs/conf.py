# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'psyflow'
copyright = '2025, Zhipeng Cao'
author = 'Zhipeng Cao'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


import os
import sys
sys.path.insert(0, os.path.abspath(".."))  # so Sphinx can find your package

# Enable extensions
extensions = [
    "myst_parser",                      # Markdown support
    "sphinx.ext.autodoc",              # Auto pull docstrings
    "sphinx.ext.napoleon",             # Google/Numpy style docstrings
    "sphinx_autodoc_typehints",        # Type hints in docs
]

# Allow both .rst and .md files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

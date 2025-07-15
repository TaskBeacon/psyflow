# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'psyflow'
copyright = '2025, Zhipeng Cao'
author = 'Zhipeng Cao'
import os
import sys
sys.path.insert(0, os.path.abspath(".."))  # so Sphinx can find your package
from psyflow._version import read_version
release = read_version()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']
html_sidebars = {
    "**": [
        "sidebar/brand.html",        # pinned
        "sidebar/search.html",       # pinned
        "sidebar/scroll-start.html", # begin scrollable
        "sidebar/entries.html",      # now scrolls
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",   # end scrollable
    ]
}

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Enable extensions
extensions = [
    "myst_parser",                      # Markdown support
    "sphinx.ext.autodoc",              # Auto pull docstrings
    "sphinx.ext.napoleon",             # Google/Numpy style docstrings
    "sphinx_autodoc_typehints",        # Type hints in docs
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

# Allow both .rst and .md files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

html_theme = "furo"
html_static_path = ["_static"]
# html_logo = "_static/logo.png"
# html_js_files = [
#     "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit",
#     "translate-float.js"
# ]


html_theme_options = {
    "sidebar_hide_name": False,
    "light_logo": "logo_white-removebg.png",  # used on white background
    "dark_logo": "logo_black-removebg.png",   # used on dark background
    "source_repository": "https://github.com/TaskBeacon/psyflow/",
    "source_branch": "main",
    "source_directory": "source/",
}

def setup(app):
    app.add_css_file("logo_settings.css")

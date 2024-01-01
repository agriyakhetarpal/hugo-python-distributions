from __future__ import annotations

import importlib.metadata

project = "python-hugo"
copyright = "2023, Agriya Khetarpal"
author = "Agriya Khetarpal"
version = release = importlib.metadata.version("python-hugo")

extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "furo"

myst_enable_extensions = [
    "colon_fence",
]

always_document_param_types = True

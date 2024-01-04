"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

python-hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

from python_hugo.cli import __call

# Hugo binary entry point caller
if __name__ == "__main__":
    __call()

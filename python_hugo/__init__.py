"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

python-hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

import os
import sys

import importlib.metadata

HUGO_VERSION = importlib.metadata.version("python-hugo")
FILE_EXT = ".exe" if sys.platform == "win32" else ""

# On editable and source installs, we keep binaries in the package directory
# for ease of use. On wheel installs, we keep them in the venv/binaries directory.
# On installing from a wheel, the binary is in the venv/binaries, but the package
# is in venv/lib/python3.X/site-packages, so we need to go up two directories and
# then down into binaries
try:
    hugo_executable = os.path.join(
        os.path.dirname(__file__),
        "binaries",
        f"hugo-{HUGO_VERSION}" + FILE_EXT,
    )
    if not os.path.exists(hugo_executable):
        raise FileNotFoundError
except FileNotFoundError:
    hugo_executable = os.path.join(
        # Go up into the venv directory and down into the data files
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
                    )
                )
            )
        ),
        "binaries",
        f"hugo-{HUGO_VERSION}" + FILE_EXT,
    )
    if not os.path.exists(hugo_executable):
        raise FileNotFoundError
except Exception as e:
    print(f"Error: {e}")

def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    os.execvp(hugo_executable, ["hugo", *sys.argv[1:]])

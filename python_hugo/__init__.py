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
# Note: on Windows, this is venv\Lib\site-packages (instead of venv/lib/python3.X/site-packages)
# therefore we need to go up to the venv directory and then down into the data files
try:
    hugo_executable = os.path.join(
        os.path.dirname(__file__),
        "binaries",
        f"hugo-{HUGO_VERSION}" + FILE_EXT,
    )
    if not os.path.exists(hugo_executable):
        raise FileNotFoundError
except FileNotFoundError:
    if sys.platform == "win32":
        PATH_TO_SEARCH = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(__file__)
                    )
                )
            ),
            "binaries"
            ) # four times instead of five
    else:
        # five times instead of four
        PATH_TO_SEARCH = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(__file__)
                        )
                    )
                )
            ),
            "binaries"
            )

    # Go up into the venv directory and down into the data files
    hugo_executable = os.path.join(PATH_TO_SEARCH, f"hugo-{HUGO_VERSION}" + FILE_EXT)
    if not os.path.exists(hugo_executable):
        raise FileNotFoundError from None
except Exception as e:
    sys.exit(f"Error: {e}")

def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    os.execvp(hugo_executable, ["hugo", *sys.argv[1:]])

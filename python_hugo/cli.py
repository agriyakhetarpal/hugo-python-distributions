"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

python-hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from functools import lru_cache

HUGO_VERSION = "0.121.1"

FILE_EXT = ".exe" if sys.platform == "win32" else ""
HUGO_PLATFORM = {
    "darwin": "darwin",
    "linux": "linux",
    "win32": "windows",
}[sys.platform]
HUGO_ARCH = {
    "x86_64": "amd64",
    "arm64": "arm64",
    "AMD64": "amd64",
    "aarch64": "arm64",
}[platform.machine()]

@lru_cache(maxsize=1)
def hugo_executable():
    """
    Returns the path to the Hugo executable.
    """
    return os.path.join(
        os.path.dirname(__file__),
        "binaries",
        f"hugo-{HUGO_VERSION}-{HUGO_PLATFORM}-{HUGO_ARCH}" + FILE_EXT,
    )

MESSAGE = f"Running Hugo {HUGO_VERSION} via python-hugo at {hugo_executable()}"

def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    # send to stdout a message that we are using the python-hugo wrapper
    print(MESSAGE)
    os.execvp(hugo_executable(), ["hugo", *sys.argv[1:]])

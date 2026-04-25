"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

import os
from pathlib import Path
from sys import platform as sysplatform

from hugo._version import HUGO_VERSION

HUGO_EXECUTABLE = "hugo.exe" if sysplatform == "win32" else "hugo"
HUGO_EXECUTABLE_PATH = Path(__file__).with_name("binaries") / HUGO_EXECUTABLE


def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    hugo_executable_str = os.fspath(HUGO_EXECUTABLE_PATH)

    print(
        f"\033[95mRunning Hugo {HUGO_VERSION} via hugo-python-distributions at {hugo_executable_str}\033[0m"
    )

    from sys import argv as sysargv

    if sysplatform == "win32":
        from subprocess import check_call

        check_call([hugo_executable_str, *sysargv[1:]])
    else:
        os.execv(hugo_executable_str, ["hugo", *sysargv[1:]])


if __name__ == "__main__":
    __call()

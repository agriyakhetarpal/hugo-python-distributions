"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

# Reduce expenses for various imports
from functools import lru_cache
from os import execvp, path
from platform import machine
from subprocess import check_call
from sys import argv
from sys import platform as sysplatform

HUGO_VERSION = "0.124.1"

FILE_EXT = ".exe" if sysplatform == "win32" else ""

HUGO_PLATFORM = {
    "darwin": "darwin",
    "linux": "linux",
    "win32": "windows",
}[sysplatform]

HUGO_ARCH = {
    "x86_64": "amd64",
    "arm64": "arm64",
    "AMD64": "amd64",
    "aarch64": "arm64",
}[machine()]


@lru_cache(maxsize=1)
def hugo_executable():
    """
    Returns the path to the Hugo executable.
    """
    return path.join(  # noqa: PTH118
        path.dirname(__file__),  # noqa: PTH120
        "binaries",
        f"hugo-{HUGO_VERSION}-{HUGO_PLATFORM}-{HUGO_ARCH}" + FILE_EXT,
    )


MESSAGE = (
    f"Running Hugo {HUGO_VERSION} via hugo-python-distributions at {hugo_executable()}"
)


def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    if sysplatform == "win32":
        # execvp broken on Windows, use subprocess instead to not launch a new shell
        print(f"\033[95m{MESSAGE}\033[0m")
        check_call([hugo_executable(), *argv[1:]])
    else:
        print(f"\033[95m{MESSAGE}\033[0m")
        execvp(hugo_executable(), ["hugo", *argv[1:]])

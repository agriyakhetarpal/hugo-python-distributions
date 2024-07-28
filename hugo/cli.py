"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

# Reduce expenses for various imports
from functools import lru_cache
from os import execv, path
from platform import machine
from subprocess import check_call
from sys import argv, maxsize
from sys import platform as sysplatform

with open(path.join(path.dirname(__file__), "VERSION")) as f:  # noqa: PTH123, PTH120, PTH118
    HUGO_VERSION = f.read().strip()

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
    "x86": "386",
    "s390x": "s390x",
    "ppc64le": "ppc64le",
}[machine()]

# platform.machine returns AMD64 on Windows because the architecture is
# 64-bit (even if one is running a 32-bit Python interpreter). Therefore
# we use sys. maxsize to handle this special case on Windows

if not (maxsize > 2**32) and sysplatform == "win32":
    HUGO_ARCH = "386"


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
        execv(hugo_executable(), ["hugo", *argv[1:]])

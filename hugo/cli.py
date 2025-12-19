"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

import os
from pathlib import Path
from sys import platform as sysplatform

HUGO_VERSION = "0.153.0"
FILE_EXT = ".exe" if sysplatform == "win32" else ""
HUGO_PLATFORM = {"darwin": "darwin", "linux": "linux", "win32": "windows"}[sysplatform]


def get_hugo_arch():
    from platform import machine
    from sys import maxsize as sysmaxsize

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

    if not (sysmaxsize > 2**32) and sysplatform == "win32":
        HUGO_ARCH = "386"

    return HUGO_ARCH


HUGO_ARCH = get_hugo_arch()

DIR = Path(__file__).parent.resolve()

HUGO_EXECUTABLE = Path(
    DIR / "binaries" / f"hugo-{HUGO_VERSION}-{HUGO_PLATFORM}-{HUGO_ARCH}{FILE_EXT}",
).resolve()

MESSAGE = (
    f"Running Hugo {HUGO_VERSION} via hugo-python-distributions at {HUGO_EXECUTABLE}"
)


def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    print(f"\033[95m{MESSAGE}\033[0m")

    from sys import argv as sysargv

    if sysplatform == "win32":
        from subprocess import check_call

        check_call([HUGO_EXECUTABLE, *sysargv[1:]])
    else:
        os.execv(HUGO_EXECUTABLE, ["hugo", *sysargv[1:]])


if __name__ == "__main__":
    __call()

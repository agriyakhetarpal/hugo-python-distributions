"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

import os
import sysconfig
from sys import platform as sysplatform

from hugo._version import HUGO_VERSION

FILE_EXT = ".exe" if sysplatform == "win32" else ""

HUGO_EXECUTABLE = os.path.join(  # noqa: PTH118
    sysconfig.get_path("scripts"), "_hugo_bin" + FILE_EXT
)


def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    print(
        f"\033[95mRunning Hugo {HUGO_VERSION} via hugo-python-distributions at {HUGO_EXECUTABLE}\033[0m"
    )

    from sys import argv as sysargv

    if sysplatform == "win32":
        from subprocess import check_call

        check_call([HUGO_EXECUTABLE, *sysargv[1:]])
    else:
        os.execv(HUGO_EXECUTABLE, ["hugo", *sysargv[1:]])


if __name__ == "__main__":
    __call()

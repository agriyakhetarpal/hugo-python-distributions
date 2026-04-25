"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

import os
import sys
from contextlib import nullcontext
from importlib import resources
from pathlib import Path
from sys import platform as sysplatform

from hugo._version import HUGO_VERSION

HUGO_EXECUTABLE = "hugo.exe" if sysplatform == "win32" else "hugo"


def _editable_hugo_executable() -> Path | None:
    """Resolve the bundled binary from meson-python's editable install tree."""
    for finder in sys.meta_path:
        if type(finder).__name__ != "MesonpyMetaFinder":
            continue
        if getattr(finder, "_name", None) != "hugo":
            continue

        tree = finder._rebuild()
        binary = tree.get(("hugo", "binaries", HUGO_EXECUTABLE))
        if isinstance(binary, str):
            return Path(binary)

    return None


def _hugo_executable():
    try:
        binary = resources.files("hugo").joinpath("binaries", HUGO_EXECUTABLE)
        return resources.as_file(binary)
    except ValueError:
        editable_binary = _editable_hugo_executable()
        if editable_binary is not None:
            return nullcontext(editable_binary)
        raise


def __call():
    """
    Hugo binary entry point. Passes all command-line arguments to Hugo.
    """
    with _hugo_executable() as hugo_executable:
        hugo_executable_str = os.fspath(hugo_executable)

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

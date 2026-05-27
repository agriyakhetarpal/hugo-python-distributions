"""
Copyright (c) 2023 Agriya Khetarpal. All rights reserved.

hugo: Binaries for the Hugo static site generator, installable with pip
"""

from __future__ import annotations

import json
import os
import sys
import sysconfig
from contextlib import nullcontext
from pathlib import Path, PurePosixPath
from sys import platform as sysplatform

from hugo._version import HUGO_VERSION

HUGO_EXECUTABLE = "hugo.exe" if sysplatform == "win32" else "hugo"
HUGO_BINARY_PATH = Path("hugo", "binaries", HUGO_EXECUTABLE)


def _editable_hugo_executable() -> Path | None:
    """Resolve the bundled binary from meson-python's editable install tree."""
    for finder in sys.meta_path:
        if type(finder).__name__ != "MesonpyMetaFinder":
            continue
        if getattr(finder, "_name", None) != "hugo":
            continue

        finder._rebuild()

        install_plan = Path(finder._build_path, "meson-info", "intro-install_plan.json")
        if not install_plan.is_file():
            continue

        with install_plan.open(encoding="utf-8") as file:
            plan = json.load(file)

        for targets in plan.values():
            for source, target in targets.items():
                destination = PurePosixPath(target["destination"].replace("\\", "/"))
                if destination.parts[-3:] == ("hugo", "binaries", HUGO_EXECUTABLE):
                    return Path(source)

    return None


def _hugo_executable():
    data_path = Path(sysconfig.get_path("data"))
    binary = data_path / HUGO_BINARY_PATH
    if binary.is_file():
        return nullcontext(binary)

    editable_binary = _editable_hugo_executable()
    if editable_binary is not None:
        return nullcontext(editable_binary)

    raise FileNotFoundError(binary)


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

"""
Build the Hugo binary from the vendored submodule.

Invoked by meson.build's custom_target. All inputs come via CLI flags, so we
can also run this script standalone for debugging.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

HUGO_VENDOR_NAME = "hugo-python-distributions"

HOST_GOOS = {
    "darwin": "darwin",
    "linux": "linux",
    "win32": "windows",
}.get(sys.platform, sys.platform)

HOST_GOARCH = {
    "x86_64": "amd64",
    "arm64": "arm64",
    "AMD64": "amd64",
    "aarch64": "arm64",
    "x86": "386",
    "i686": "386",
    "i386": "386",
    "s390x": "s390x",
    "ppc64le": "ppc64le",
    "armv7l": "arm",
    "armv6l": "arm",
    "riscv64": "riscv64",
}.get(platform.machine(), platform.machine())

ZIG_TARGET_MAP = {
    ("darwin", "amd64"): "x86_64-macos-none",
    ("darwin", "arm64"): "aarch64-macos-none",
    ("linux", "amd64"): "x86_64-linux-gnu",
    ("linux", "arm64"): "aarch64-linux-gnu",
    ("linux", "arm"): "arm-linux-gnueabihf",
    ("linux", "386"): "x86-linux-gnu",
    ("linux", "ppc64le"): "powerpc64le-linux-gnu",
    ("linux", "s390x"): "s390x-linux-gnu",
    ("linux", "riscv64"): "riscv64-linux-gnu",
    ("windows", "386"): "x86-windows-gnu",
    ("windows", "amd64"): "x86_64-windows-gnu",
    ("windows", "arm64"): "aarch64-windows-gnu",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--hugo-src", required=True, type=Path)
    p.add_argument("--cache", required=True, type=Path)
    p.add_argument("--version", required=True)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--use-zig", default="false")
    p.add_argument("--goos", default="")
    p.add_argument("--goarch", default="")
    return p.parse_args()


def check_dependencies(use_zig: bool) -> None:
    try:
        subprocess.check_call(
            ["go", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except OSError as err:
        msg = "Go toolchain not found. Install Go from https://go.dev/dl/."
        raise OSError(msg) from err

    try:
        subprocess.check_call(
            ["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except OSError as err:
        msg = "Git not found. Please install Git from https://git-scm.com/downloads or your package manager."
        raise OSError(msg) from err

    if use_zig:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "ziglang", "version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as err:
            msg = "Zig compiler not found. Please install Zig from https://ziglang.org/download/, from PyPI as ziglang, or your package manager."
            raise OSError(msg) from err
        return

    for cc in ("gcc", "clang"):
        try:
            subprocess.check_call(
                [cc, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return
        except OSError:
            continue
    msg = "GCC/Clang not found. Please install GCC or Clang via your package manager."
    raise OSError(msg)



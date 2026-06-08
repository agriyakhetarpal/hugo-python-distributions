"""
Shared helpers for obtaining a Go toolchain on 32-bit ARM Linux
on piwheels.

The go-bin PyPI package that we use as a build-time dependency does
not publish wheels or an sdist for armv6l/armv7l (piwheels), and thus
breaks builds on that platform. On that one platform, we can bypass
and download the official go.dev toolchain archive directly instead.
"""

from __future__ import annotations

import hashlib
import platform
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

# Keep in sync with the go-bin pins in hugo_meson_python_wrapper.py
GO_VERSION = "1.26.3"
GO_LINUX_ARM_SHA256 = "d44133d4c66b1451a1e247da26db7716f76a081c0169a75e6c84e1871e394320"

GO_LINUX_ARM_FILENAME = f"go{GO_VERSION}.linux-armv6l.tar.gz"
GO_LINUX_ARM_URL = f"https://go.dev/dl/{GO_LINUX_ARM_FILENAME}"


def is_32bit_arm_linux() -> bool:
    return sys.platform == "linux" and platform.machine() in ("armv6l", "armv7l")


def download_go_toolchain(dest_dir: Path) -> tuple[str, str]:
    """Download and extract the official Go toolchain for 32-bit ARM Linux on piwheels."""
    goroot = dest_dir / "go"
    shutil.rmtree(goroot, ignore_errors=True)

    archive_path = dest_dir / GO_LINUX_ARM_FILENAME
    urllib.request.urlretrieve(GO_LINUX_ARM_URL, archive_path)

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if digest != GO_LINUX_ARM_SHA256:
        msg = (
            f"checksum mismatch for {GO_LINUX_ARM_FILENAME}: "
            f"expected {GO_LINUX_ARM_SHA256}, got {digest}"
        )
        raise RuntimeError(msg)

    with tarfile.open(archive_path) as tar:
        tar.extractall(dest_dir, filter="data")
    archive_path.unlink()

    return str(goroot / "bin" / "go"), str(goroot)

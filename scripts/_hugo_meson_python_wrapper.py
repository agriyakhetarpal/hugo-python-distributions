"""
This is a thin PEP 517 wrapper around meson-python's PEP 517 support.
Its primary purpose is to set the _PYTHON_HOST_PLATFORM env var for
cross-compilation without requiring users to set it by hand, based on
requirements passed via the --cross-file=... flag in config_settings.

It looks for `--cross-file=...` in the wheel build's `config_settings`
(`-Csetup-args=--cross-file=foo.ini`), parses the cross file, and sets
the `_PYTHON_HOST_PLATFORM` environment variable, so that meson-python
will tag the wheel for the cross without needing users to set it by hand.

Native builds (without a cross file) are no-ops here, i.e., this wrapper
does nothing in that case and just passes through to meson-python. Cross
builds with an unsupported (host_machine.system, host_machine.cpu_family)
tuple will likely produce an incorrectly tagged wheel that will need to
be manually renamed.
"""

from __future__ import annotations

import configparser
import os
import re
from pathlib import Path
from typing import Any

import mesonpy

# (host_machine.system, host_machine.cpu_family) -> _PYTHON_HOST_PLATFORM
PLATFORM_TAGS_MAP: dict[tuple[str, str], str] = {
    ("linux", "x86_64"): "linux_x86_64",
    ("linux", "aarch64"): "linux_aarch64",
    ("linux", "arm"): "linux_armv7l",
    ("linux", "x86"): "linux_i686",
    ("linux", "ppc64"): "linux_ppc64le",
    ("linux", "s390x"): "linux_s390x",
    ("linux", "riscv64"): "linux_riscv64",
    ("windows", "x86_64"): "win_amd64",
    ("windows", "aarch64"): "win_arm64",
    ("windows", "x86"): "win32",
    (
        "darwin",
        "x86_64",
    ): "macosx_10_13_x86_64",  # TODO: figure out what to do about MACOSX_DEPLOYMENT_TARGET
    (
        "darwin",
        "aarch64",
    ): "macosx_11_0_arm64",  # TODO: figure out what to do about MACOSX_DEPLOYMENT_TARGET
}


def _flatten(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _strip_quotes(string: str) -> str:
    return string.strip().strip("'\"")


def _maybe_set_host_platform(config_settings: dict[str, Any] | None) -> None:
    """If config_settings contains a --cross-file=... flag, parse the cross file and set
    _PYTHON_HOST_PLATFORM based on the host_machine config.
    """
    if not config_settings:
        return
    setup_args = _flatten(config_settings.get("setup-args"))
    cross_file: Path | None = None
    for arg in setup_args:
        m = re.match(r"--cross-file[= ](.+)$", arg)
        if m:
            cross_file = Path(m.group(1))
            break
    if cross_file is None or not cross_file.exists():
        return

    cfg = configparser.ConfigParser()
    cfg.read(cross_file)
    if "host_machine" not in cfg:
        return

    system = _strip_quotes(cfg["host_machine"].get("system", ""))
    family = _strip_quotes(cfg["host_machine"].get("cpu_family", ""))
    tag = PLATFORM_TAGS_MAP.get((system, family))
    if tag is None:
        return

    os.environ.setdefault("_PYTHON_HOST_PLATFORM", tag)


# Unchanged meson-python PEP 517 entry points below


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _maybe_set_host_platform(config_settings)
    return mesonpy.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _maybe_set_host_platform(config_settings)
    return mesonpy.build_editable(wheel_directory, config_settings, metadata_directory)


def build_sdist(
    sdist_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    return mesonpy.build_sdist(sdist_directory, config_settings)


def get_requires_for_build_wheel(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    return mesonpy.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_editable(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    return mesonpy.get_requires_for_build_editable(config_settings)


def get_requires_for_build_sdist(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    return mesonpy.get_requires_for_build_sdist(config_settings)


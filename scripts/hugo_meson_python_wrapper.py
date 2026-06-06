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


def _parse_cross_file(config_settings: dict[str, Any] | None) -> tuple[str, str] | None:
    """Return (system, cpu_family) from a Meson cross file in config_settings, or None."""
    if not config_settings:
        return None
    setup_args = _flatten(config_settings.get("setup-args"))
    cross_file: Path | None = None
    for arg in setup_args:
        m = re.match(r"--cross-file[= ](.+)$", arg)
        if m:
            cross_file = Path(m.group(1))
            break
    if cross_file is None or not cross_file.exists():
        return None

    cfg = configparser.ConfigParser()
    cfg.read(cross_file)
    if "host_machine" not in cfg:
        return None

    system = _strip_quotes(cfg["host_machine"].get("system", ""))
    family = _strip_quotes(cfg["host_machine"].get("cpu_family", ""))
    return (system, family) if system and family else None


def _host_platform_tag(config_settings: dict[str, Any] | None) -> str | None:
    """Return the target wheel platform tag from a Meson cross file, if any."""
    host = _parse_cross_file(config_settings)
    return None if host is None else PLATFORM_TAGS_MAP.get(host)


def _needs_zig(config_settings: dict[str, Any] | None) -> bool:
    """Return True if the Zig compiler is needed for this build.

    We do `auto_use_zig = meson.is_cross_build() and host_sys != 'darwin'`.
    It maps here. An explicit -Duse_zig=true/false in setup-args overrides
    the auto logic.
    """
    host = _parse_cross_file(config_settings)
    if host is None:
        return False
    setup_args = _flatten(config_settings.get("setup-args") if config_settings else [])
    for arg in setup_args:
        m = re.match(r"-Duse_zig=(true|false)$", arg)
        if m:
            return m.group(1) == "true"
    system, _ = host
    return system != "darwin"


def _maybe_set_host_platform(config_settings: dict[str, Any] | None) -> None:
    """If config_settings contains a Meson cross file, force meson-python's wheel tag."""
    tag = _host_platform_tag(config_settings)
    if tag is None:
        return

    os.environ["_PYTHON_HOST_PLATFORM"] = tag
    mesonpy._tags.get_platform_tag = lambda: (
        tag
    )  # TODO: drop this hack/use of private API


def _force_py3_none_tag() -> None:
    """Force py3-none-<platform> instead of cp<XY>-cp<XY>-<platform>.

    With pure: false, meson-python assumes every file in {platlib} is a CPython
    extension module and applies a Python-version-specific ABI tag. The Hugo
    binary is a Go executable that runs under any Python version, so we patch
    _has_extension_modules to always return False, and that causes meson-python
    to fall through to the py3-none-<platform> branch in its tag property.
    TODO: drop this hack/use of public API if meson-python someday exposes a way
    to opt out of the CPython ABI tag for non-extension platlib content.
    """
    mesonpy._WheelBuilder._has_extension_modules = property(lambda _: False)


# Unchanged meson-python PEP 517 entry points below


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _maybe_set_host_platform(config_settings)
    _force_py3_none_tag()
    return mesonpy.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _maybe_set_host_platform(config_settings)
    _force_py3_none_tag()
    return mesonpy.build_editable(wheel_directory, config_settings, metadata_directory)


def build_sdist(
    sdist_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    return mesonpy.build_sdist(sdist_directory, config_settings)


def get_requires_for_build_wheel(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    reqs = list(mesonpy.get_requires_for_build_wheel(config_settings))
    reqs.append("go-bin==1.26.3")
    if _needs_zig(config_settings):
        reqs.append("ziglang==0.16.0")
    return reqs


def get_requires_for_build_editable(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    return mesonpy.get_requires_for_build_editable(config_settings)


def get_requires_for_build_sdist(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    return mesonpy.get_requires_for_build_sdist(config_settings)

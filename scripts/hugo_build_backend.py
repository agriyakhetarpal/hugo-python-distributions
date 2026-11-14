"""
A thin PEP 517 wrapper around the Hatchling build backend.

Hatchling does not respect config settings. This build backend turns the
`goos` and `goarch` config settings we use into the GOOS and GOARCH
environment variables for the build hook, thereby allowing the following
invocation, for example:

    python -m build --wheel -Cgoos=linux -Cgoarch=arm64
"""

from __future__ import annotations

import os
from typing import Any

import hatchling.build as _hatchling

CONFIG_SETTINGS = {
    "goos": "GOOS",
    "goarch": "GOARCH",
}


def _apply_config_settings(config_settings: dict[str, Any] | None) -> None:
    if not config_settings:
        return
    for key, env_var in CONFIG_SETTINGS.items():
        if key not in config_settings:
            continue
        value = config_settings[key]
        if isinstance(value, (list, tuple)):  # repeated -C options
            value = value[-1] if value else ""
        value = str(value).strip()
        if not value:
            msg = f"The '{key}' config setting must not be empty"
            raise ValueError(msg)
        os.environ[env_var] = value


def _validate_target() -> None:
    from hatch_build import resolve_target

    resolve_target()


def get_requires_for_build_sdist(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    return _hatchling.get_requires_for_build_sdist(config_settings)


def build_sdist(
    sdist_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    return _hatchling.build_sdist(sdist_directory, config_settings)


def get_requires_for_build_wheel(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    _apply_config_settings(config_settings)
    return _hatchling.get_requires_for_build_wheel(config_settings)


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _apply_config_settings(config_settings)
    _validate_target()
    return _hatchling.build_wheel(wheel_directory, config_settings, metadata_directory)


def get_requires_for_build_editable(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    _apply_config_settings(config_settings)
    return _hatchling.get_requires_for_build_editable(config_settings)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    _apply_config_settings(config_settings)
    _validate_target()
    return _hatchling.build_editable(
        wheel_directory, config_settings, metadata_directory
    )


# hatchling only defines these hooks outside pip builds
if hasattr(_hatchling, "prepare_metadata_for_build_wheel"):

    def prepare_metadata_for_build_wheel(
        metadata_directory: str,
        config_settings: dict[str, Any] | None = None,
    ) -> str:
        _apply_config_settings(config_settings)
        return _hatchling.prepare_metadata_for_build_wheel(
            metadata_directory, config_settings
        )

    def prepare_metadata_for_build_editable(
        metadata_directory: str,
        config_settings: dict[str, Any] | None = None,
    ) -> str:
        _apply_config_settings(config_settings)
        return _hatchling.prepare_metadata_for_build_editable(
            metadata_directory, config_settings
        )

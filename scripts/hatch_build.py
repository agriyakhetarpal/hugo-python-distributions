"""
A Hatchling build hook to compile and add the Hugo binary to the wheel.

The build target comes from the GOOS and GOARCH environment variables, which
are set by our custom build backend, hugo_build_backend.py, which is a thin
wrapper over Hatchling and sets the GOOS and GOARCH environment variables
from the goos and goarch config settings. When neither is set, the wheel is
built for the running interpreter's platform.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

# Hatchling imports this file by path, so we need to make the sibling modules
# importable. too. Otherwise, I found that the ImportError gets swallowed and
# go-bin silently got dropped from the build requirements.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from piwheels_go_toolchain import GO_VERSION, is_32bit_arm_linux

# (GOOS, GOARCH) ➡️ wheel platform tag
PLATFORM_TAGS: dict[tuple[str, str], str] = {
    ("linux", "amd64"): "linux_x86_64",
    ("linux", "arm64"): "linux_aarch64",
    ("linux", "arm"): "linux_armv7l",
    ("linux", "386"): "linux_i686",
    ("linux", "ppc64le"): "linux_ppc64le",
    ("linux", "s390x"): "linux_s390x",
    ("linux", "riscv64"): "linux_riscv64",
    ("windows", "amd64"): "win_amd64",
    ("windows", "arm64"): "win_arm64",
    ("windows", "386"): "win32",
}

GO_TARGETS: dict[str, tuple[str, str]] = {
    tag: target for target, tag in PLATFORM_TAGS.items()
}
GO_TARGETS["linux_armv6l"] = ("linux", "arm")  # piwheels case

# macOS architecture mappings cases
MACOS_ARCHS = {"amd64": "x86_64", "arm64": "arm64"}
MACOS_GOARCHS = {arch: goarch for goarch, arch in MACOS_ARCHS.items()}

_32BIT_INTERPRETER = sys.maxsize <= 2**32


def _macos_platform_tag(arch: str) -> str:
    """macosx_<major>_<minor>_<arch> (ported from meson-python)"""
    version: tuple[int, int] | None = None
    target = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "")
    if target:
        parts = target.split(".")[:2]
        try:
            major, minor = (int(p) for p in [*parts, "0"][:2])
            version = (major, minor)
        except ValueError:
            version = None
    if version is None:
        mac_ver = platform.mac_ver()[0] if sys.platform == "darwin" else ""
        if mac_ver:
            major, minor = (int(p) for p in [*mac_ver.split(".")[:2], "0"][:2])
            version = (major, minor)
        else:
            version = (11, 0) if arch == "arm64" else (10, 13)

    # arm64 starts at 11.0, and from 11 onwards the minor is a patch level
    if arch == "arm64" and version < (11, 0):
        version = (11, 0)
    major, minor = version
    if major >= 11:
        minor = 0
    return f"macosx_{major}_{minor}_{arch}"


def native_platform_tag() -> str:
    """Wheel platform tag for the running interpreter (ported from meson-python)"""
    plat = sysconfig.get_platform()
    if plat.startswith("macosx"):
        arch = platform.mac_ver()[2]
        host_platform = os.environ.get("_PYTHON_HOST_PLATFORM", "").split("-")
        if len(host_platform) >= 3:
            arch = host_platform[2]
        return _macos_platform_tag(arch)
    if _32BIT_INTERPRETER:  # 32-bit interpreter on a 64-bit kernel
        if plat == "linux-x86_64":
            return "linux_i686"
        if plat == "linux-aarch64":
            return "linux_armv7l"
    return plat.replace("-", "_").replace(".", "_").lower()


def go_target_for_tag(tag: str) -> tuple[str, str]:
    if tag.startswith("macosx_"):
        arch = tag.rsplit("_", 1)[1]
        if arch in MACOS_GOARCHS:
            return ("darwin", MACOS_GOARCHS[arch])
    elif tag in GO_TARGETS:
        return GO_TARGETS[tag]
    msg = (
        f"Cannot build Hugo for the platform tag '{tag}'. Set the goos and "
        "goarch config settings (or the GOOS and GOARCH environment "
        "variables) to a supported target."
    )
    raise ValueError(msg)


def tag_for_go_target(goos: str, goarch: str) -> str:
    if goos == "darwin" and goarch in MACOS_ARCHS:
        return _macos_platform_tag(MACOS_ARCHS[goarch])
    if (goos, goarch) in PLATFORM_TAGS:
        return PLATFORM_TAGS[(goos, goarch)]
    supported = sorted(
        f"{os_}/{arch}"
        for os_, arch in [*PLATFORM_TAGS, *(("darwin", a) for a in MACOS_ARCHS)]
    )
    msg = (
        f"Unsupported GOOS/GOARCH combination '{goos}/{goarch}'. "
        f"Supported targets: {', '.join(supported)}"
    )
    raise ValueError(msg)


def resolve_target() -> tuple[str, str, str]:
    """Return (platform tag, GOOS, GOARCH). An unset half defaults to native"""
    goos = os.environ.get("GOOS", "").strip()
    goarch = os.environ.get("GOARCH", "").strip()
    if not goos and not goarch:
        tag = native_platform_tag()
        goos, goarch = go_target_for_tag(tag)
        return tag, goos, goarch
    if not goos or not goarch:
        native_goos, native_goarch = go_target_for_tag(native_platform_tag())
        goos = goos or native_goos
        goarch = goarch or native_goarch
    return tag_for_go_target(goos, goarch), goos, goarch


def check_submodule_tag(hugo_src: Path, version: str) -> None:
    """Fail if hugo-src is not at the tag the version declares (skipped without .git present, such as in sdists)"""
    if not (hugo_src / ".git").exists():
        return
    try:
        result = subprocess.run(
            ["git", "-C", str(hugo_src), "describe", "--tags", "--exact-match", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return
    if result.returncode != 0:
        return
    tag = result.stdout.strip()
    expected = "v" + ".".join(version.split(".")[:3])
    if tag != expected:
        msg = (
            f"the hugo-src submodule is at '{tag}' but pyproject.toml "
            f"declares version {version} (expected tag '{expected}')"
        )
        raise RuntimeError(msg)


def build_binary(hugo_src: Path, output: Path, goos: str, goarch: str) -> None:
    """Compile Hugo into `output` and put the cache in HUGO_BUILD_CACHE if set or a tempdir"""
    command = [
        sys.executable,
        str(SCRIPTS_DIR / "build_hugo.py"),
        "--hugo-src",
        str(hugo_src),
        "--output",
        str(output),
        "--goos",
        goos,
        "--goarch",
        goarch,
    ]
    cache = os.environ.get("HUGO_BUILD_CACHE", "")
    if cache:
        subprocess.run([*command, "--cache", cache], check=True)
        return
    with tempfile.TemporaryDirectory(
        prefix="hugo-build-", ignore_cleanup_errors=True
    ) as tmp:
        subprocess.run([*command, "--cache", tmp], check=True)


class HugoBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    @property
    def _package_dir(self) -> Path:
        return Path(self.root) / "src" / "hugo"

    @property
    def _version_file(self) -> Path:
        return self._package_dir / "_version.py"

    @property
    def _binaries_dir(self) -> Path:
        return self._package_dir / "binaries"

    def dependencies(self) -> list[str]:
        # go-bin has no armv6l/armv7l wheels.
        # see how build_hugo.py downloads Go there
        if is_32bit_arm_linux():
            return []
        return [f"go-bin=={GO_VERSION}"]

    def clean(self, versions: list[str]) -> None:  # noqa: ARG002
        self._version_file.unlink(missing_ok=True)
        for binary in self._binaries_dir.glob("hugo*"):
            binary.unlink()

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        project_version = self.metadata.version
        hugo_src = Path(self.root) / "hugo-src"
        check_submodule_tag(hugo_src, project_version)

        platform_tag, goos, goarch = resolve_target()
        executable = "hugo.exe" if goos == "windows" else "hugo"
        binary = self._binaries_dir / executable

        self._version_file.write_text(
            f'HUGO_VERSION = "{project_version}"\n', encoding="utf-8"
        )
        build_binary(hugo_src, binary, goos, goarch)

        build_data["pure_python"] = False
        if version != "standard":
            # editable installs reach these files through the src/ .pth entry
            return
        build_data["tag"] = f"py3-none-{platform_tag}"
        build_data["force_include"][str(binary)] = f"hugo/binaries/{executable}"
        build_data["force_include"][str(self._version_file)] = "hugo/_version.py"

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
        msg = "Go toolchain not found. Please install Go from https://go.dev/dl/ or your package manager."
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


def setup_zig_compiler(goos: str, goarch: str) -> None:
    target = ZIG_TARGET_MAP.get((goos, goarch))
    if not target:
        print(
            f"Warning: there is no Zig target combination for GOOS={goos} and GOARCH={goarch}",
            file=sys.stderr,
        )
        return
    cc = f"{sys.executable} -m ziglang cc -target {target}"
    cxx = f"{sys.executable} -m ziglang c++ -target {target}"
    if target == "x86-windows-gnu":
        cc += " -w"
        cxx += " -w"
    os.environ["CC"] = cc
    os.environ["CXX"] = cxx
    os.environ["CGO_CFLAGS"] = "-g0 -O3 -ffunction-sections -fdata-sections"
    os.environ["CGO_LDFLAGS"] = "-s -w -Wl,--gc-sections"


class SubmoduleVcsSwap:
    """Replace the submodule .git file with a .git directory such that Go's
    VCS stamping reads the Hugo submodule's HEAD, not that of the parent
    repository.

    Submodules store a `.git` file that points into the parent repository's
    `.git/modules` directory. Go's VCS detection follows that link into the
    parent repo and produces wrong metadata. We copy the actual git directory
    into the submodule worktree temporarily and rewrite the worktree config
    entry. This is restored on exit.
    """

    def __init__(self, hugo_src: Path) -> None:
        self.hugo_git = hugo_src / ".git"
        self._saved: str | None = None

    def __enter__(self) -> SubmoduleVcsSwap:
        if not self.hugo_git.is_file():
            return self
        content = self.hugo_git.read_text()
        self._saved = content
        gitdir = content.strip().split("gitdir: ", 1)[1]
        gitdir_abs = (self.hugo_git.parent / gitdir).resolve()
        self.hugo_git.unlink()
        shutil.copytree(str(gitdir_abs), str(self.hugo_git))
        if sys.platform == "win32":
            for p in self.hugo_git.rglob("*"):
                if p.is_file():
                    p.chmod(p.stat().st_mode | stat.S_IWRITE)
        config_file = self.hugo_git / "config"
        if config_file.exists():
            cfg = config_file.read_text()
            cfg = re.sub(r"worktree\s*=\s*[^\n]+", "worktree = ..", cfg)
            config_file.write_text(cfg)
        return self

    def __exit__(self, *exc: object) -> None:
        if self._saved is None:
            return
        if self.hugo_git.is_dir() and not self.hugo_git.is_symlink():
            shutil.rmtree(self.hugo_git)
        elif self.hugo_git.exists() or self.hugo_git.is_symlink():
            self.hugo_git.unlink()
        self.hugo_git.write_text(self._saved)


def get_hugo_commit_date(hugo_src: Path) -> str:
    """Return the Hugo submodule's HEAD commit date (ISO 8601).

    Falls back to a stamp file (`<hugo-src>/.hugo_commit_date`) when
    `.git` is absent, which is the case for sdist builds.
    """
    stamp = hugo_src / ".hugo_commit_date"
    try:
        date = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI"],
            cwd=hugo_src,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if date:
            stamp.write_text(date)
            return date
    except (subprocess.CalledProcessError, OSError):
        pass
    if stamp.exists():
        return stamp.read_text().strip()
    return ""


def locate_built_binary(gopath: Path, goos: str, goarch: str, exe_ext: str) -> Path:
    """Find the binary that ``go install`` produced.

    Go places it at ``$GOPATH/bin/hugo`` for native builds, or
    ``$GOPATH/bin/$GOOS_$GOARCH/hugo`` when cross-compiling.
    """
    cross = goos != HOST_GOOS or goarch != HOST_GOARCH
    if cross:
        candidate = gopath / "bin" / f"{goos}_{goarch}" / ("hugo" + exe_ext)
        if candidate.exists():
            return candidate
    return gopath / "bin" / ("hugo" + exe_ext)


def main() -> int:
    args = parse_args()
    use_zig = args.use_zig.lower() == "true"
    goos = args.goos or HOST_GOOS
    goarch = args.goarch or HOST_GOARCH
    cache = args.cache.resolve()
    hugo_src = args.hugo_src.resolve()
    output = args.output.resolve()

    cache.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(cache / "bin", ignore_errors=True)

    check_dependencies(use_zig)

    os.environ["CGO_ENABLED"] = "1"
    os.environ["GO111MODULE"] = "on"
    os.environ["GOPATH"] = str(cache)
    os.environ["GOCACHE"] = str(cache)
    os.environ["GOOS"] = goos
    os.environ["GOARCH"] = goarch

    if goarch == "arm" and goos == "linux":
        default_goarm = "6" if platform.machine() == "armv6l" else "7"
        os.environ.setdefault("GOARM", default_goarm)

    if use_zig:
        setup_zig_compiler(goos, goarch)

    ldflags = [
        f"-s -w -X github.com/gohugoio/hugo/common/hugo.vendorInfo={HUGO_VENDOR_NAME}",
    ]
    commit_date = get_hugo_commit_date(hugo_src)
    if commit_date:
        ldflags.append(
            f"-X github.com/gohugoio/hugo/common/hugo.buildDate={commit_date}",
        )
    if goos == "windows":
        ldflags.append("-extldflags '-static'")

    with SubmoduleVcsSwap(hugo_src):
        subprocess.check_call(
            [
                "go",
                "install",
                "-trimpath",
                "-v",
                "-ldflags",
                " ".join(ldflags),
                "-tags",
                "extended,withdeploy",
            ],
            cwd=hugo_src,
        )

    exe_ext = ".exe" if goos == "windows" else ""
    built = locate_built_binary(cache, goos, goarch, exe_ext)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    shutil.copy2(built, output)
    output.chmod(output.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return 0


if __name__ == "__main__":
    sys.exit(main())

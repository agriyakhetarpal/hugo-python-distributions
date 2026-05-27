"""
Emits a Meson cross file for a given GOOS and GOARCH combination, to derive
the wheel platform tag from `[host_machine]` for cross-compilation builds.
These are used for Zig-based cross-compilation in CI, but can also be used
for any general cross-compiler (say, Clang, or a custom-built GCC toolchain).

Usage:
    python scripts/generate_meson_cross_file.py --goos OS --goarch ARCH --output PATH.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# This is (goos, goarch), mapping to (system, cpu_family, cpu, endian)
HOST_MACHINE_MAP: dict[tuple[str, str], tuple[str, str, str, str]] = {
    ("linux", "amd64"): ("linux", "x86_64", "x86_64", "little"),
    ("linux", "arm64"): ("linux", "aarch64", "aarch64", "little"),
    ("linux", "arm"): ("linux", "arm", "armv7l", "little"),
    ("linux", "386"): ("linux", "x86", "i686", "little"),
    ("linux", "ppc64le"): ("linux", "ppc64", "ppc64le", "little"),
    ("linux", "s390x"): ("linux", "s390x", "s390x", "big"),
    ("linux", "riscv64"): ("linux", "riscv64", "riscv64", "little"),
    ("windows", "amd64"): ("windows", "x86_64", "x86_64", "little"),
    ("windows", "arm64"): ("windows", "aarch64", "aarch64", "little"),
    ("windows", "386"): ("windows", "x86", "i686", "little"),
    ("darwin", "amd64"): ("darwin", "x86_64", "x86_64", "little"),
    ("darwin", "arm64"): ("darwin", "aarch64", "aarch64", "little"),
}


def render(goos: str, goarch: str) -> str:
    key = (goos, goarch)
    if key not in HOST_MACHINE_MAP:
        sys.exit(f"This is an unsupported GOOS/GOARCH combination: {goos}/{goarch}")

    system, family, cpu, endian = HOST_MACHINE_MAP[key]
    return (
        "[host_machine]\n"
        f"system     = '{system}'\n"
        f"cpu_family = '{family}'\n"
        f"cpu        = '{cpu}'\n"
        f"endian     = '{endian}'\n"
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--goos", required=True)
    p.add_argument("--goarch", required=True)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args.goos, args.goarch))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

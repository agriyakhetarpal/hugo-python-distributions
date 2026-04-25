"""Prunes a lot of large/irrelevant trees from the sdist, mainly from the
Hugo submodule, which is not needed for users building from sdist and would
just artificially inflate the distributions' size. This is invoked by the
`meson dist` command.

TODO: figure out a better, more declarative way to do this, because I can't
find a meson-python sdist include/exclude mechanism. There's only one for
wheels right now.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

EXCLUDED_DIRS = (
    "hugo-src/docs",
    "hugo-src/testscripts",
    "docs",
    "src/hugo/binaries",
    "hugo_cache",
    "build",
)


def main() -> int:
    root = Path(os.environ["MESON_DIST_ROOT"])
    for rel in EXCLUDED_DIRS:
        target = root / rel
        if target.exists():
            shutil.rmtree(target)
            print(f"pruned {rel}")

    for testdata in root.glob("hugo-src/**/testdata"):
        if testdata.is_dir():
            shutil.rmtree(testdata)
            print(f"pruned {testdata.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

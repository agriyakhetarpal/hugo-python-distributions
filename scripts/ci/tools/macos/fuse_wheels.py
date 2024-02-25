#!/usr/bin/env python3
#
#                            ,---.           ,---.
#                           / /"`.\.--"""--./,'"\ \
#                           \ \    _       _    / /
#                            `./  / __   __ \  \,'
#                             /    /_O)_(_O\    \
#                             |  .-'  ___  `-.  |
#                          .--|       \_/       |--.
#                        ,'    \   \   |   /   /    `.
#                       /       `.  `--^--'  ,'       \
#                    .-"""""-.    `--.___.--'     .-"""""-.
#       .-----------/         \------------------/         \--------------.
#       | .---------\         /----------------- \         /------------. |
#       | |          `-`--`--'                    `--'--'-'             | |
#       | |                                                             | |
#       | |                                                             | |
#       | |    This script is currently not in use. It is kept for      | |
#       | |    future reference in case we need to ship universal       | |
#       | |    binaries that target both macOS Intel and macOS ARM      | |
#       | |    architectures again.                                     | |
#       | |                                                             | |
#       | |    It is to be noted that the issue with universal2         | |
#       | |    wheels up to Hugo v0.123.3 is not only their size,       | |
#       | |    i.e., 90+ MB owing to ZIP compression rather than        | |
#       | |    TGZ, but also that they contain executables for          | |
#       | |    both architectures rather than a single binary that      | |
#       | |    has been merged with tools like LIPO.                    | |
#       | |                                                             | |
#       | |_____________________________________________________________| |
#       |_________________________________________________________________|
#                          )__________|__|__________(
#                         |            ||            |
#                         |____________||____________|
#                           ),-----.(      ),-----.(
#                         ,'   ==.   \    /  .==    `.
#                        /            )  (            \
#                        `==========='    `==========='  hjw
#
#
#   A wrapper script over delocate-fuse for creating universal2 wheels
#   from x86_64 and arm64 wheels, with basic command-line argument parsing
#
#   Usage: fuse_wheels.py <x86_64_wheels_dir> <arm64_wheels_dir> <output_dir>
#   Note: these directories must be created beforehand before running this script.

import os
import shutil
import subprocess
import sys
from pathlib import Path

in_dir1 = sys.argv[1]
in_dir2 = sys.argv[2]
out_dir = sys.argv[3]


def search_wheel_in_dir(package, dir):
    for i in os.listdir(dir):
        if i.startswith(package):
            return i
    return None


def copy_if_universal(wheel_name, in_dir, out_dir):
    if wheel_name.endswith(("universal2.whl", "any.whl")):
        src_path = Path(in_dir) / wheel_name
        dst_path = Path(out_dir) / wheel_name.replace("x86_64", "universal2").replace(
            "arm64", "universal2"
        )

        shutil.copy(src_path, dst_path)
        return True
    return False


for wheel_name_1 in os.listdir(in_dir1):
    package = wheel_name_1.split("-")[0]
    wheel_name_2 = search_wheel_in_dir(package, in_dir2)
    if copy_if_universal(wheel_name_1, in_dir1, out_dir):
        continue
    if copy_if_universal(wheel_name_2, in_dir2, out_dir):
        continue

    wheel_path_1 = Path(in_dir1) / wheel_name_1
    wheel_path_2 = Path(in_dir2) / wheel_name_2
    subprocess.run(
        ["delocate-fuse", wheel_path_1, wheel_path_2, "-w", out_dir], check=True
    )

for wheel_name in os.listdir(out_dir):
    wheel_name_new = wheel_name.replace("x86_64", "universal2").replace(
        "arm64", "universal2"
    )

    src_path = Path(out_dir) / wheel_name
    dest_path = Path(out_dir) / wheel_name_new

    wheel_name_string = f"\033[33m{wheel_name}\033[0m"
    wheel_name_new_string = f"\033[33m{wheel_name_new}\033[0m"
    print(f"✨ Renamed wheel {wheel_name_string} to {wheel_name_new_string} 🎉")
    Path(src_path).rename(dest_path)

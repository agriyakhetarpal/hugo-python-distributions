#!/usr/bin/env python3

# The auditwheel tool might mess up the platform tags for the wheel, but this
# peculiarity comes from the Hugo binaries inside the wheel, not from auditwheel
# itself: the Hugo binaries have been referencing various shared libraries with
# different versioned symbols from GLIBC, restricting the wheel to a single
# platform tag.

# Therefore, we will manually fix the platform tags for the wheel as a workaround.
# Please note that this is not a fix, it is not guaranteed to make reproducible wheels
# and could be dangerous if the Hugo binaries are not compatible with the GLIBC version
# of the target platform. This script should be used with due cognizance of such risks
# involved in the distribution of such wheels.

# Usage:
# python repair_wheels.py <dir_containing_wheels> <output_dir>

import glob
import os
import sys

IN_DIR = sys.argv[1]
OUT_DIR = sys.argv[2]

# We will do this for each wheel in IN_DIR and move the repaired wheels to OUT_DIR.

for wheel_path in glob.glob(os.path.join(IN_DIR, "*.whl")):
    wheel_name = os.path.basename(wheel_path)

    if "x86_64" in wheel_name:
        new_platform_tag = "manylinux_2_17_x86_64.manylinux2014_x86_64"
    elif "aarch64" in wheel_name:
        new_platform_tag = "manylinux_2_17_aarch64.manylinux2014_aarch64"
    else:
        print(
            f"Skipping wheel '{wheel_name}', does not contain 'x86_64' or 'aarch64'"
        )
        continue

    new_wheel_name = wheel_name.replace("linux_x86_64", new_platform_tag).replace(
        "linux_aarch64", new_platform_tag
    )

    # Construct the full paths for the original and new wheel
    original_wheel_path = os.path.join(IN_DIR, wheel_name)
    new_wheel_path = os.path.join(OUT_DIR, new_wheel_name)

    os.link(original_wheel_path, new_wheel_path)
    print(f"✨ Repaired wheel '{wheel_name}' to '{new_wheel_name}' ✅")

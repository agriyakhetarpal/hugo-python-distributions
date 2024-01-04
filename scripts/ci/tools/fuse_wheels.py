#!/usr/bin/env python3
# A wrapper script over delocate-fuse for creating universal2 wheels
# from x86_64 and arm64 wheels, with basic command-line argument parsing

# Usage: fuse_wheels.py <x86_64_wheels_dir> <arm64_wheels_dir> <output_dir>
# Note: these directories must be created beforehand before running this script.

import sys
import os
import shutil
import subprocess

in_dir1 = sys.argv[1]
in_dir2 = sys.argv[2]
out_dir = sys.argv[3]

def search_wheel_in_dir(package, dir):
    for i in os.listdir(dir):
        if i.startswith(package):
            return i

def copy_if_universal(wheel_name, in_dir, out_dir):
    if wheel_name.endswith('universal2.whl') or wheel_name.endswith('any.whl'):
        src_path = os.path.join(in_dir, wheel_name)
        dst_path = os.path.join(
            out_dir, 
            wheel_name
            .replace('x86_64', 'universal2')
            .replace('arm64', 'universal2')
            )

        shutil.copy(src_path, dst_path)
        return True
    else:
        return False

for wheel_name_1 in os.listdir(in_dir1):
    package = wheel_name_1.split('-')[0]
    wheel_name_2 = search_wheel_in_dir(package, in_dir2)
    if copy_if_universal(wheel_name_1, in_dir1, out_dir):
        continue
    if copy_if_universal(wheel_name_2, in_dir2, out_dir):
        continue

    wheel_path_1 = os.path.join(in_dir1, wheel_name_1)
    wheel_path_2 = os.path.join(in_dir2, wheel_name_2)
    subprocess.run(['delocate-fuse', wheel_path_1, wheel_path_2, '-w', out_dir])

for wheel_name in os.listdir(out_dir):
    wheel_name_new = wheel_name.replace('x86_64', 'universal2').replace('arm64', 'universal2')

    src_path = os.path.join(out_dir, wheel_name)
    dst_path = os.path.join(out_dir, wheel_name_new)

    os.rename(src_path, dst_path)
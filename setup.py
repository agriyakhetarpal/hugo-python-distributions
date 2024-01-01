import os
# TODO: add support for Windows
# import sys
# import platform
import subprocess
import tarfile

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

import pooch

# Keep in sync with pyproject.toml and update SHA-256 hashes accordingly
HUGO_VERSION = "0.120.4"
HUGO_RELEASE = (
    f"https://github.com/gohugoio/hugo/archive/refs/tags/v{HUGO_VERSION}.tar.gz"
)

# Pooch will download the tarball into the OS cache directory.
# We will point the build command to that location to build Hugo from source
HUGO_CACHE_DIR = pooch.os_cache(".python_hugo")
HUGO_SHA256 = "e374effe369c340d8085060e6bb45337eabf64cfe075295432ecafd6d033eb8b"
# Path where the Hugo binary will be placed and copied from
HUGO_BIN = os.path.join(os.environ.get("HOME"), "go")


class HugoBuilder(build_ext):
    """
    Custom build_ext command that builds Hugo from source
    """

    def initialize_options(self):
        super().initialize_options()
        self.hugo_version = None

    def finalize_options(self):
        super().finalize_options()
        self.hugo_version = HUGO_VERSION

    def run(self):
        """
        Build Hugo from source and place the binary in the package directory, mangling
        # the name so that it is unique to the verion of Hugo being built.
        """

        # Download Hugo source tarball, place into OS cache directory
        hugo_targz = pooch.retrieve(
            url=HUGO_RELEASE,
            known_hash=HUGO_SHA256,
            path=HUGO_CACHE_DIR,
            progressbar=True,
        )

        # Extract Hugo source tarball into a folder of the same name in the OS cache directory
        with tarfile.open(hugo_targz) as tar:
            tar.extractall(path=HUGO_CACHE_DIR)

        os.environ["CGO_ENABLED"] = "1"
        os.environ["GOPATH"] = os.path.join(os.environ.get("HOME"), "go")
        # The binary is put into GOBIN, which is set to the package directory (src/python_hugo/binaries)
        # for use in editable mode. The binary is copied into the wheel afterwards
        os.environ["GOBIN"] = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "python_hugo", "binaries"
        )

        # Build Hugo from source using the Go toolchain, place it into GOBIN
        # Requires the following dependencies:
        #
        # 1. Go
        # 2. GCC/Clang
        # 3. Git
        #
        # Once built this the files are cached into GOPATH for future use
        subprocess.check_call(
            [
                "go",
                "install",
                "-tags",
                "extended",
            ],
            cwd=os.path.join(HUGO_CACHE_DIR, f"hugo-{HUGO_VERSION}"),
        )
        # TODO: introduce some error handling here to detect compilers, etc.

        # Mangle the name of the compiled executable to include the version
        # of Hugo being built
        original_name = os.path.join(os.environ.get("GOBIN"), "hugo")
        new_name = os.path.join(os.environ.get("GOBIN"), f"hugo-{HUGO_VERSION}")
        os.rename(original_name, new_name)


setup(
    ext_modules=[
        Extension(
            name="hugo.build",
            sources=[
                "setup.py"
            ]
        )
    ],
    cmdclass={
        "build_ext": HugoBuilder
    },
    packages=[
        "python_hugo",
        "python_hugo.binaries"
    ]
    if os.path.exists("python_hugo/binaries")
    else ["python_hugo"],
    # Include binary named hugo-HUGO_VERSION in the wheel, which is presently stored
    # in python_hugo/binaries (i.e., in a folder binaries/ inside the package directory)
    package_data={"python_hugo": ["binaries/*"]},
    # include_package_data=True,
    # TODO: data_files is deprecated for wheels, so we need to find a better way to
    # include the binary in the wheel
    data_files=[("binaries", [f"python_hugo/binaries/hugo-{HUGO_VERSION}"])],
    # Add Hugo binary as a dynamic console script entry point but with its version
    # number. This is done so that users can run, say, `hugo_0.X.Y` to run
    # Hugo 0.X.Y, even if they have multiple versions of Hugo installed.
    entry_points={
        "console_scripts": [rf"hugo_{HUGO_VERSION}=python_hugo.__init__:__call"]
    },
    version=HUGO_VERSION,
)

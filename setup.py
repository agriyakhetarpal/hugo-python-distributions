import glob
import os
import platform
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pooch
from setuptools import Command, Extension, setup
from setuptools.command.build_ext import build_ext
from wheel.bdist_wheel import bdist_wheel, get_platform

# Has to be kept in sync with the version in hugo/cli.py and incantation of setup()
HUGO_VERSION = "0.123.0"
HUGO_RELEASE = (
    f"https://github.com/gohugoio/hugo/archive/refs/tags/v{HUGO_VERSION}.tar.gz"
)
# Commit hash for current HUGO_VERSION, needs to be updated when HUGO_VERSION is updated
# Tip: git ls-remote --tags https://github.com/gohugoio/hugo v<HUGO_VERSION>
HUGO_RElEASE_COMMIT_HASH = "3c8a4713908e48e6523f058ca126710397aa4ed5"
# The pooch tool will download the tarball into the hugo_cache/ directory.
# We will point the build command to that location to build Hugo from source
HUGO_CACHE_DIR = "hugo_cache"
HUGO_SHA256 = "877f4d8246053d6e577fc57d85291c8b1e88635e2711d00ba5708c3782cef89e"
FILE_EXT = ".exe" if sys.platform == "win32" else ""

# The vendor name is used to set the vendorInfo variable in the Hugo binary
HUGO_VENDOR_NAME = "hugo-python-distributions"

# Normalise platform strings to match the Go toolchain
HUGO_PLATFORM = {
    "darwin": "darwin",
    "linux": "linux",
    "win32": "windows",
}[sys.platform]

# Normalise architecture strings to match the Go toolchain
HUGO_ARCH = {
    "x86_64": "amd64",
    "arm64": "arm64",
    "AMD64": "amd64",
    "aarch64": "arm64",
}[platform.machine()]

# Name of the Hugo binary that will be built
HUGO_BINARY_NAME = (
    f"hugo-{HUGO_VERSION}-{HUGO_PLATFORM}-{os.environ.get('GOARCH', HUGO_ARCH)}"
    + FILE_EXT
)


class HugoBuilder(build_ext):
    """
    Custom extension command that builds Hugo from source, placing the binary into
    the package directory for further use.
    """

    def initialize_options(self):
        super().initialize_options()
        self.hugo_version = None
        self.hugo_platform = None
        self.hugo_arch = None

    def finalize_options(self):
        # Platforms and architectures that we will build Hugo for are:
        # i.e., a subset of "go tool dist list":
        # 1. darwin/amd64
        # 2. darwin/arm64
        # 3. linux/amd64
        # 4. linux/arm64
        # 5. windows/amd64
        # The platform is the first part of the string, the architecture is the second.
        # We will mangle the hugo binary name to include the platform and architecture
        # so that we can build Hugo for multiple platforms and architectures.
        # The platform is used to set the GOOS environment variable, the architecture
        # is used to set the GOARCH environment variable, and they must be exactly these
        # strings for the Go toolchain to work.
        super().finalize_options()
        self.hugo_version = HUGO_VERSION
        self.hugo_platform = HUGO_PLATFORM
        self.hugo_arch = HUGO_ARCH

    def run(self):
        """
        Build Hugo from source and place the binary in the package directory, mangling
        # the name so that it is unique to the version of Hugo being built.
        """

        # Download Hugo source tarball, place into hugo_cache/ directory
        hugo_targz = pooch.retrieve(
            url=HUGO_RELEASE,
            known_hash=HUGO_SHA256,
            path=HUGO_CACHE_DIR,
            progressbar=True,
        )

        # Extract Hugo source tarball into a folder hugo-HUGO_VERSION/
        # inside hugo_cache/
        with tarfile.open(hugo_targz) as tar:
            tar.extractall(path=HUGO_CACHE_DIR)

        # The binary is put into GOBIN, which is set to the package directory
        # (hugo/binaries/) for use in editable mode. The binary is copied
        # into the wheel afterwards
        # Error: GOBIN cannot be set if GOPATH is set when compiling for different
        # architectures, so we use the default GOPATH/bin as the place to copy
        # binaries from
        # os.environ["GOBIN"] = os.path.join(
        #     os.path.dirname(os.path.abspath(__file__)), "hugo", "binaries"
        # )
        os.environ["CGO_ENABLED"] = "1"
        os.environ["GOPATH"] = os.path.abspath(HUGO_CACHE_DIR)  # noqa: PTH100
        # it must be absolute (Go requirement)

        # Set GOCACHE to the hugo_cache/ directory so that the Go toolchain
        # caches the build artifacts there for future use.
        os.environ["GOCACHE"] = os.path.abspath(HUGO_CACHE_DIR)  # noqa: PTH100

        os.environ["GOOS"] = self.hugo_platform
        os.environ["GOARCH"] = os.environ.get("GOARCH", self.hugo_arch)
        # i.e., allow override if GOARCH is set!

        # Build Hugo from source using the Go toolchain, place it into GOBIN
        # Requires the following dependencies:
        #
        # 1. Go
        # 2. GCC/Clang
        # 3. Git
        #
        # Once built this the files are cached into GOPATH for future use

        # Delete hugo_cache/bin/ + files inside, it left over from a previous build
        shutil.rmtree(Path(HUGO_CACHE_DIR).resolve() / "bin", ignore_errors=True)

        # ldflags are passed to the go linker to set variables at runtime
        # Note: the Homebrew version of Hugo sets extra ldflags such as the build
        # date. We do not set that here, we only set the vendorInfo variable.
        ldflags = [
            f"-X github.com/gohugoio/hugo/common/hugo.vendorInfo={HUGO_VENDOR_NAME}",
        ]

        # Check for compilers, toolchains, etc. and raise helpful errors if they
        # are not found.
        try:
            subprocess.check_call(["go", "version"])
        except OSError as err:
            error_message = "Go toolchain not found. Please install Go from https://go.dev/dl/ or your package manager."
            raise OSError(error_message) from err

        try:
            subprocess.check_call(["gcc", "--version"])
        except OSError:
            try:
                subprocess.check_call(["clang", "--version"])
            except OSError as err:
                error_message = "GCC/Clang not found. Please install GCC or Clang via your package manager."
                raise OSError(error_message) from err
        try:
            subprocess.check_call(["git", "--version"])
        except OSError as err:
            error_message = "Git not found. Please install Git from https://git-scm.com/downloads or your package manager."
            raise OSError(error_message) from err

        subprocess.check_call(
            [
                "go",
                "install",
                "-ldflags",
                *ldflags,
                "-tags",
                "extended",
            ],
            cwd=os.path.abspath(os.path.join(HUGO_CACHE_DIR, f"hugo-{HUGO_VERSION}")),  # noqa: PTH118, PTH100
        )
        # TODO: introduce some error handling here to detect compilers, etc.

        # Mangle the name of the compiled executable to include the version, the
        # platform, and the architecture of Hugo being built.
        # The binary is present in GOPATH (i.e, either at hugo_cache/bin/ or at
        # hugo_cache/bin/$GOOS_$GOARCH/bin) and now GOBIN is not set, so we need
        # to copy it from there.

        # If the GOARCH is not the same as self.hugo_arch, we are cross-compiling, so
        # we need to go into the GOOS_GOARCH/bin folder to find the binary rather than
        # the GOPATH/bin folder.

        if os.environ.get("GOARCH") != self.hugo_arch:
            original_name = (
                Path(os.environ.get("GOPATH"))
                / "bin"
                / f"{self.hugo_platform}_{os.environ.get('GOARCH')}"
                / ("hugo" + FILE_EXT)
            )
        else:
            original_name = Path(os.environ.get("GOPATH")) / "bin" / ("hugo" + FILE_EXT)

        new_name = (
            Path(os.environ.get("GOPATH"))
            / "bin"
            / (
                f"hugo-{HUGO_VERSION}-{self.hugo_platform}-{os.environ.get('GOARCH', self.hugo_arch)}"
                + FILE_EXT
            )
        )
        original_name.rename(new_name)

        # Copy the new_name file into a folder binaries/ inside hugo/
        # so that it is included in the wheel.
        # basically we are copying hugo-HUGO_VERSION-PLATFORM-ARCH into
        # hugo/binaries/ and creating the folder if it does not exist.

        binaries_dir = Path(__file__).parent / "hugo" / "binaries"
        if not binaries_dir.exists():
            binaries_dir.mkdir()

        # if the binary already exists, delete it, and then copy the new binary
        # to ensure that the binary is always the newest rendition
        new_binary_path = binaries_dir / new_name.name
        if new_binary_path.exists():
            new_binary_path.unlink()
        new_name.rename(new_binary_path)


# https://github.com/pypa/setuptools/issues/1347: setuptools does not support
# the clean command from distutils yet. so we need to use a workaround that gets
# called inside bdist_wheel invocation.
class Cleaner(Command):
    """
    Custom command that cleans the build directory of the package at the project root.
    """

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Clean ancillary files at runtime."""

        here = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))  # noqa: PTH100, PTH120
        files_to_clean = "./build ./*.pyc ./*.egg-info ./__pycache__".split(" ")

        for path_spec in files_to_clean:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(os.path.join(here, path_spec)))  # noqa: PTH207, PTH118
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(str(here)):
                    # raise error if path in files_to_clean is absolute + outside
                    # this directory
                    msg = f"{path} is not a path around {here}"
                    raise ValueError(msg)
                shutil.rmtree(path)


# Mock setuptools into thinking that we are building a target binary on a host machine
# so that the wheel gets tagged correctly. We can fuse the arm64 and amd64 wheels
# together later using delocate.
class HugoWheel(bdist_wheel):
    """
    A customised wheel build command that sets the platform tags to accommodate
    the varieties of the GOARCH and GOOS environment variables when cross-compiling
    the Hugo binary. Currently used for macOS arm64 and macOS x86_64.
    """

    def initialize_options(self):
        super().initialize_options()

    def finalize_options(self):
        # plat_name is essentially the {platform tag} at the end of the wheel name.
        # Note to self: the wheel name will look like this:
        # {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
        # # on macOS, if GOARCH is set to arm64 on an x86_64 machine, or if GOARCH is set to
        # amd64 on an arm64 machine, we need to set the platform tag to macosx_X_Y_arm64 or
        # macosx_X_Y_x86_64 respectively.
        #
        # TODO: FIXME: look at how Linux and Windows tags are set later

        if sys.platform == "darwin":
            platform_tag = get_platform("_")
            # ensure correct platform tag for macOS arm64 and macOS x86_64
            # macOS 3.12 Python runners are mislabelling the platform tag to be
            # universal2
            # see: https://github.com/pypa/wheel/issues/573. we will explicitly rename
            # the universal2 tag to macosx_X_Y_arm64 or macosx_X_Y_x86_64 respectively,
            # since we fuse the wheels together later anyway.
            if (("arm64" in platform_tag) or ("univeral2" in platform_tag)) and (
                os.environ.get("GOARCH") == "amd64"
            ):
                self.plat_name = platform_tag.replace("arm64", "x86_64").replace(
                    "universal2", "x86_64"
                )
            if (("x86_64" in platform_tag) or ("universal2" in platform_tag)) and (
                os.environ.get("GOARCH") == "arm64"
            ):
                self.plat_name = platform_tag.replace("x86_64", "arm64").replace(
                    "universal2", "arm64"
                )
        super().finalize_options()

    def run(self):
        self.root_is_pure = False  # ensure that the wheel is tagged as a binary wheel

        self.run_command("clean")  # clean the build directory before building the wheel

        # ensure that the binary is copied into the binaries/ folder and then
        # into the wheel.
        hugo_binary = Path(__file__).parent / "hugo" / "binaries" / HUGO_BINARY_NAME

        # if the binary does not exist, then we need to build it, so invoke
        # the build_ext command again and proceed to build the binary
        if not Path(hugo_binary).exists():
            self.run_command("build_ext")

        # now that the binary exists, we have ensured its presence in the wheel
        super().run()


setup(
    ext_modules=[
        Extension(
            name="hugo.build",
            sources=[
                f"hugo/binaries/{HUGO_BINARY_NAME}",
            ],
        )
    ],
    cmdclass={
        "build_ext": HugoBuilder,
        "clean": Cleaner,
        "bdist_wheel": HugoWheel,
    },
    package_data={
        "hugo": [
            f"binaries/{HUGO_BINARY_NAME}",
        ],
    },
    # has to be kept in sync with the version in hugo/cli.py
    version=HUGO_VERSION,
)

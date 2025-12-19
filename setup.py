import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import Command, Extension, setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py

# ------ Hugo build configuration and constants ------------------------------------

# Also update hugo/cli.py
HUGO_VERSION = "0.153.0"

# The Go toolchain will download the tarball into the hugo_cache/ directory.
# We will point the build command to that location to build Hugo from source
HUGO_CACHE_DIR = "hugo_cache"
FILE_EXT = (
    ".exe" if (sys.platform == "win32" or os.environ.get("GOOS") == "windows") else ""
)
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
    "x86": "386",
    "s390x": "s390x",
    "ppc64le": "ppc64le",
    "armv7l": "arm",
}[platform.machine()]

# Name of the Hugo binary that will be built
HUGO_BINARY_NAME = (
    f"hugo-{HUGO_VERSION}-{os.environ.get('GOOS', HUGO_PLATFORM)}-{os.environ.get('GOARCH', HUGO_ARCH)}"
    + FILE_EXT
)

# ----------------------------------------------------------------------------------


class HugoWriter(build_py):
    """
    A custom pre-installation command that writes the version of Hugo being built
    directly to hugo/cli.py so that the version is available at runtime.
    """

    def initialize_options(self) -> None:
        return super().initialize_options()

    def finalize_options(self) -> None:
        return super().finalize_options()

    def run(self) -> None:
        cli_file_path = Path(__file__).parent / "hugo" / "cli.py"
        content = cli_file_path.read_text()
        version = re.sub(
            r'HUGO_VERSION = "[0-9.]+"', f'HUGO_VERSION = "{HUGO_VERSION}"', content
        )
        with open(cli_file_path, "w") as cli_file:  # noqa: PTH123
            cli_file.write(version)

        super().run()


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
        # Platforms and architectures that we will build Hugo natively for are:
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
        # Note to self: go tool dist list -json | jq -r "map(select(.CgoSupported)) | .[] | .GOOS + \"/\" + .GOARCH"
        super().finalize_options()
        self.hugo_version = HUGO_VERSION
        self.hugo_platform = HUGO_PLATFORM
        self.hugo_arch = HUGO_ARCH

    def run(self):
        """
        Build Hugo from source and place the binary in the package directory, mangling
        # the name so that it is unique to the version of Hugo being built.
        """

        # If Hugo cache does not exist, create it
        if not Path(HUGO_CACHE_DIR).exists():
            Path(HUGO_CACHE_DIR).mkdir(parents=True)

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
        os.environ["GO111MODULE"] = "on"
        os.environ["GOPATH"] = str(Path(HUGO_CACHE_DIR).resolve())
        # it must be absolute (Go requirement)

        # Set GOCACHE to the hugo_cache/ directory so that the Go toolchain
        # caches the build artifacts there for future use.
        os.environ["GOCACHE"] = str(Path(HUGO_CACHE_DIR).resolve())

        os.environ["GOOS"] = os.environ.get("GOOS", self.hugo_platform)
        os.environ["GOARCH"] = os.environ.get("GOARCH", self.hugo_arch)
        # i.e., allow override if GOARCH is set!

        if os.environ.get("GOARCH") == "arm" and os.environ.get("GOOS") == "linux":
            os.environ["GOARM"] = os.environ.get("GOARM", "7")

        # New: Setup Zig compiler if USE_ZIG is set
        if os.environ.get("USE_ZIG"):
            self._setup_zig_compiler()

        # Build Hugo from source using the Go toolchain, place it into GOBIN
        # Requires the following dependencies:
        #
        # 1. Go
        # 2. GCC/Clang
        # 3. Git
        #
        # Once built this the files are cached into GOPATH for future use

        # Delete hugo_cache/bin/ + files inside, if left over from a previous build
        shutil.rmtree(Path(HUGO_CACHE_DIR).resolve() / "bin", ignore_errors=True)
        # shutil.rmtree(
        #     Path(HUGO_CACHE_DIR).resolve() / f"hugo-{HUGO_VERSION}", ignore_errors=True
        # )

        # Check for compilers, toolchains, etc. and raise helpful errors if they
        # are not found. These are essentially smoke tests to ensure that the
        # build environment is set up correctly.
        self._check_build_dependencies()

        # These ldflags are passed to the Go linker to set variables at runtime
        ldflags = [
            f"-s -w -X github.com/gohugoio/hugo/common/hugo.vendorInfo={HUGO_VENDOR_NAME}"
        ]

        # Build a static binary on Windows to avoid missing DLLs from MinGW,
        # i.e., libgcc_s_seh-1.dll, libstdc++-6.dll, etc.
        BUILDING_FOR_WINDOWS = (
            os.environ.get("GOOS") == "windows" or sys.platform == "win32"
        )

        if BUILDING_FOR_WINDOWS:
            ldflags.append("-extldflags '-static'")

        self._clone_hugo_source()
        self._build_hugo(ldflags)
        self._rename_and_move_binary()

    def _setup_zig_compiler(self):
        goos = os.environ.get("GOOS", self.hugo_platform)
        goarch = os.environ.get("GOARCH", self.hugo_arch)

        zig_target_map = {
            ("darwin", "amd64"): "x86_64-macos-none",
            ("darwin", "arm64"): "aarch64-macos-none",
            ("linux", "amd64"): "x86_64-linux-gnu",
            ("linux", "arm64"): "aarch64-linux-gnu",
            ("linux", "ppc64le"): "powerpc64le-linux-gnu",
            ("linux", "s390x"): "s390x-linux-gnu",
            ("windows", "386"): "x86-windows-gnu",
            ("windows", "amd64"): "x86_64-windows-gnu",
            ("windows", "arm64"): "aarch64-windows-gnu",
        }

        zig_target = zig_target_map.get((goos, goarch))
        if zig_target:
            os.environ["CC"] = f"{sys.executable} -m ziglang cc -target {zig_target}"
            os.environ["CXX"] = f"{sys.executable} -m ziglang c++ -target {zig_target}"
            if zig_target == "x86-windows-gnu":
                os.environ["CC"] += " -w"
                os.environ["CXX"] += " -w"
            # Add additional flags to the linker to ensure that the binary is
            # stripped of debug information and is as small as possible for release
            os.environ["CGO_CFLAGS"] = "-g0 -O3 -ffunction-sections -fdata-sections"
            os.environ["CGO_LDFLAGS"] = "-s -w -Wl,--gc-sections"
        else:
            print(f"Warning: No Zig target found for GOOS={goos} and GOARCH={goarch}")

    def _check_build_dependencies(self):
        # Go toolchain is required for building Hugo
        try:
            subprocess.check_call(
                ["go", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except OSError as err:
            error_message = "Go toolchain not found. Please install Go from https://go.dev/dl/ or your package manager."
            raise OSError(error_message) from err

        # Check for Zig compiler only if USE_ZIG is set
        if os.environ.get("USE_ZIG"):
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "ziglang", "version"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError as err:
                error_message = "Zig compiler not found. Please install Zig from https://ziglang.org/download/ or your package manager."
                raise OSError(error_message) from err
        else:
            # GCC/Clang is required for building Hugo because CGO is enabled
            try:
                subprocess.check_call(
                    ["gcc", "--version"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError:
                try:
                    subprocess.check_call(
                        ["clang", "--version"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except OSError as err:
                    error_message = "GCC/Clang not found. Please install GCC or Clang via your package manager."
                    raise OSError(error_message) from err

        # Git is required for building Hugo to fetch dependencies from various Git repositories
        try:
            subprocess.check_call(
                ["git", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as err:
            error_message = "Git not found. Please install Git from https://git-scm.com/downloads or your package manager."
            raise OSError(error_message) from err

    def _clone_hugo_source(self):
        if not (Path(HUGO_CACHE_DIR).resolve() / f"hugo-{HUGO_VERSION}").exists():
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    "https://github.com/gohugoio/hugo.git",
                    "--depth=1",
                    "--single-branch",
                    "--branch",
                    f"v{HUGO_VERSION}",
                    Path(HUGO_CACHE_DIR) / f"hugo-{HUGO_VERSION}",
                    # disable warning about detached HEAD
                    "-c",
                    "advice.detachedHead=false",
                ]
            )

    def _build_hugo(self, ldflags):
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
            cwd=(Path(HUGO_CACHE_DIR) / f"hugo-{HUGO_VERSION}").resolve(),
        )
        # TODO: introduce some error handling here to detect compilers, etc.

    def _rename_and_move_binary(self):
        # Mangle the name of the compiled executable to include the version, the
        # platform, and the architecture of Hugo being built.
        # The binary is present in GOPATH (i.e, either at hugo_cache/bin/ or at
        # hugo_cache/bin/$GOOS_$GOARCH/bin) and now GOBIN is not set, so we need
        # to copy it from there.

        # If the GOARCH is not the same as self.hugo_arch, we are cross-compiling, so
        # we need to go into the GOOS_GOARCH/bin folder to find the binary rather than
        # the GOPATH/bin folder.

        # four scenarios:
        # 1 cross compiling: GOARCH != self.hugo_arch
        # 2 cross compiling: GOOS != self.hugo_platform
        # 3 cross compiling: GOARCH != self.hugo_arch and GOOS != self.hugo_platform
        # 4 not cross compiling: GOARCH == self.hugo_arch and GOOS == self.hugo_platform

        # scenario 3, it checks for both GOARCH and GOOS, and if both are different
        if (os.environ.get("GOARCH") != self.hugo_arch) and (
            os.environ.get("GOOS") != self.hugo_platform
        ):
            original_name = (
                Path(os.environ.get("GOPATH"))
                / "bin"
                / f"{os.environ.get('GOOS')}_{os.environ.get('GOARCH')}"
                / ("hugo" + FILE_EXT)
            )
        # scenario 1, here GOARCH is different
        elif os.environ.get("GOARCH") != self.hugo_arch:
            original_name = (
                Path(os.environ.get("GOPATH"))
                / "bin"
                / (f"{self.hugo_platform}_{os.environ.get('GOARCH')}")
                / ("hugo" + FILE_EXT)
            )
        # scenario 2, here GOOS is different
        elif os.environ.get("GOOS") != self.hugo_platform:
            original_name = (
                Path(os.environ.get("GOPATH"))
                / "bin"
                / (f"{os.environ.get('GOOS')}_{self.hugo_arch}")
                / ("hugo" + FILE_EXT)
            )
        # scenario 4, here GOARCH and GOOS both are the same
        else:
            original_name = Path(os.environ.get("GOPATH")) / "bin" / ("hugo" + FILE_EXT)

        new_name = (
            Path(os.environ.get("GOPATH"))
            / "bin"
            / (
                f"hugo-{HUGO_VERSION}-{os.environ.get('GOOS', self.hugo_platform)}-{os.environ.get('GOARCH', self.hugo_arch)}"
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

        here = os.path.normpath(Path(__file__).parent.resolve())
        files_to_clean = ["./build", "./*.pyc", "./*.egg-info", "./__pycache__"]

        for path_spec in files_to_clean:
            # Make paths absolute and relative to this path
            abs_paths = Path(here).glob(path_spec)
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(str(here)):
                    # raise error if path in files_to_clean is absolute + outside
                    # this directory
                    msg = f"{path} is not a path around {here}"
                    raise ValueError(msg)
                shutil.rmtree(path)


# Mock setuptools into thinking that we are building a target binary on a host machine
# so that the wheel gets tagged correctly when building or cross-compiling.
class HugoWheel(bdist_wheel):
    """
    A customised wheel build command that sets the platform tags to accommodate
    the varieties of the GOARCH and GOOS environment variables when cross-compiling
    the Hugo binary with any available cross-compilation toolchain.
    """

    def initialize_options(self):
        super().initialize_options()

    def finalize_options(self):
        super().finalize_options()

    def get_tag(self):
        python_tag, abi_tag, platform_tag = bdist_wheel.get_tag(self)
        # Build for all Python versions and set ABI tag to "none" because
        # the Hugo binary is not a CPython extension, it is a self-contained
        # non-Pythonic binary.
        python_tag, abi_tag = "py3", "none"

        # Handle platform tags during cross-compilation from one platform to another
        # ==========================================================================
        # Here we will check for the GOOS environment variable and if it doesn't match
        # HUGO_PLATFORM: if it doesn't match, we are cross-compiling, so we need to set
        # the platform tag to the correct value.
        #
        # We have the following scenarios:
        #
        # 1. Cross-compiling from macOS arm64/x86_64 to Linux arm64/x86_64
        # 2. Cross-compiling from macOS arm64/x86_64 to Windows arm64/x86_64/x86
        # 3. Cross-compiling from Linux arm64/x86_64 to macOS arm64/x86_64
        # 4. Cross-compiling from Linux arm64/x86_64 to Windows arm64/x86_64/x86
        # 5. Cross-compiling from Windows arm64/x86_64/x86 to macOS arm64/x86_64
        # 6. Cross-compiling from Windows arm64/x86_64/x86 to Linux arm64/x86_64
        #
        # These checks will be activated only when GOOS is set. If GOOS is not set,
        # we will use the platform tag as is based on the above checks.

        # Handle cross-compilation on Linux via the Zig compiler
        # ======================================================
        if os.environ.get("GOOS") == "linux":
            if os.environ.get("GOARCH") == "arm64":
                platform_tag = "linux_aarch64"
            elif os.environ.get("GOARCH") == "amd64":
                platform_tag = "linux_x86_64"
            elif os.environ.get("GOARCH") == "ppc64le":
                platform_tag = "linux_ppc64le"

        # Handle cross-compilation on/to Windows via the Zig compiler
        # ===========================================================
        elif os.environ.get("GOOS") == "windows":
            if os.environ.get("GOARCH") == "arm64":
                platform_tag = "win_arm64"
            elif os.environ.get("GOARCH") == "amd64":
                platform_tag = "win_amd64"
            elif os.environ.get("GOARCH") == "386":
                platform_tag = "win32"

        # Cross-compiling to macOS or on macOS via the Zig or Xcode toolchains
        # ====================================================================
        # Also, ensure correct platform tags for macOS arm64 and macOS x86_64
        # since macOS 3.12 Python GH Actions runners are mislabelling the platform
        # tag to be universal2, see: https://github.com/pypa/wheel/issues/573
        # Also, let cibuildwheel handle the platform tags if it is being used,
        # since that is where we won't cross-compile at all but use the native
        # GitHub Actions runners.
        elif (os.environ.get("GOOS") == "darwin") and (
            os.environ.get("CIBUILDWHEEL") != "1"
        ):
            if os.environ.get("GOARCH") == "arm64":
                platform_tag = "macosx_11_0_arm64"
            elif os.environ.get("GOARCH") == "amd64":
                platform_tag = "macosx_10_13_x86_64"

        return python_tag, abi_tag, platform_tag

    def run(self):
        self.root_is_pure = False  # ensure that the wheel is tagged as a binary wheel

        self.run_command("clean")  # clean the build directory before building the wheel

        # ensure that the binary is copied into the binaries/ folder and then
        # into the wheel.
        hugo_binary = (
            Path(__file__).parent
            / "hugo"
            / "binaries"
            / f"hugo-{HUGO_VERSION}-{os.environ.get('GOOS', HUGO_PLATFORM)}-{os.environ.get('GOARCH', HUGO_ARCH)}{FILE_EXT}"
        )

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
        "build_py": HugoWriter,
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

+++
title = 'Building from sources'
date = 2024-04-06T23:28:15+05:30
draft = false
toc = true
+++

The build is driven by [Meson](https://mesonbuild.com/) and [meson-python](https://meson-python.readthedocs.io/). Building the extended + withdeploy edition of Hugo from source requires the following dependencies:

1. The [Go](https://go.dev/doc/install) toolchain
2. The [Git](https://git-scm.com/downloads) version control system
3. A C/C++ compiler, such as [GCC](https://gcc.gnu.org/) or [Clang](https://clang.llvm.org/). You may also use [Zig](https://ziglang.org/) as a C compiler. On Windows, the [MinGW](https://www.mingw-w64.org/) toolchain is supported, and [MSVC](https://visualstudio.microsoft.com/visual-cpp-build-tools/) is untested.
   3a. For cross-compilation to non-macOS targets, [Zig](https://ziglang.org/) is pulled in from PyPI and auto-selected as the C compiler. For cross-compilation from macOS hosts to macOS targets, AppleClang is used with `-arch <target>`.
4. [Python](https://www.python.org/downloads/) ≥ 3.10

`meson-python`, `meson`, `ninja`, and `ziglang` are all pulled in as build-time dependencies by the build backend, so you don't have to install them yourself.

Windows users can use the [Chocolatey package manager](https://chocolatey.org/) in order to use the [MinGW compiler](https://chocolatey.org/packages/mingw). After installing Chocolatey, run the following command in an elevated terminal prompt:

```bash
choco install mingw
```

Then, clone the repository and install the package:

{{< tabs >}}

{{< tab name="Linux/macOS" >}}

```bash
git clone --recurse-submodules https://github.com/agriyakhetarpal/hugo-python-distributions
cd hugo-python-distributions
python -m venv venv
source venv/bin/activate
pip install .
```

{{< /tab >}}

{{< tab name="Windows" >}}

```cmd
git clone --recurse-submodules https://github.com/agriyakhetarpal/hugo-python-distributions
cd hugo-python-distributions
py -m venv venv
venv\Scripts\activate.bat
pip install .
```

{{< /tab >}}

{{< /tabs >}}

For an editable install:

```bash
pip install -e .
```

## Cross-compiling for different architectures

{{< callout type="warning" >}}
Cross-compilation is experimental and may not be stable or reliable for all use cases. If you encounter any issues, please feel free to [open an issue](https://github.com/agriyakhetarpal/hugo-python-distributions/issues/new).
{{</ callout >}}

Cross-compilation is indicated by and happens entirely via a [Meson cross file](https://mesonbuild.com/Cross-compilation.html). This cross-build definition file has a `[host_machine]` section that describes the target platform, and Meson and meson-python both consume it:

- `meson` gets to know what the target is,
- `meson.build` gets to know what `GOOS`/`GOARCH` combination is to be passed on to the Go build, and whether to use the Zig compiler for cross-compilation or not, based on said combination.
- There is an in-tree PEP 517 build backend wrapper around `meson-python` at [`scripts/hugo_meson_python_wrapper.py`](https://github.com/agriyakhetarpal/hugo-python-distributions/blob/main/scripts/hugo_meson_python_wrapper.py), that sets `_PYTHON_HOST_PLATFORM` to tag the wheel correctly for cross-compilation scenarios, both
  across platforms or across architectures on the same platform.

### 1. Generate a cross file

There is a helper that ships with the project:

```bash
python scripts/generate_meson_cross.py --goos linux --goarch arm64 --output cross-linux-arm64.ini
```

The output is a small `[host_machine]` description that meson-python and Meson both consume. You can also write one by hand if you'd like – see the [Meson cross file documentation](https://mesonbuild.com/Cross-compilation.html#cross-file).

Some cross files are already checked into the repository for convenience, in the `meson_cross_files` directory. You can use those directly, or as a reference for writing your own.

Cross-compilation for Hugo binaries is provided for the following platforms and architectures, based on `GOOS`/`GOARCH` combinations that the Go toolchain supports, and that Zig can target for C code generation:

- macOS: `darwin/arm64` and `darwin/amd64`
- Linux: `linux/amd64`, `linux/arm64`, `linux/arm`, `linux/386`, `linux/ppc64le`, `linux/s390x`, and `linux/riscv64`
- Windows: `windows/amd64`, `windows/arm64`, and `windows/386`

For a list of supported distributions for Go, please run the `go tool dist list` command on your system. For a list of supported targets for Zig, please refer to the [Zig documentation](https://ziglang.org/documentation/) for more information or run the `zig targets` command on your system.


### 2. Build the wheel

```bash
python -m build --wheel -Csetup-args=--cross-file=cross-linux-arm64.ini
```

Some examples are showcased below.

{{< tabs >}}

{{< tab name="Linux arm64" >}}

```bash
python scripts/generate_meson_cross.py --goos linux --goarch arm64 --output cross.ini
python -m build --wheel -Csetup-args=--cross-file=cross.ini
# builds into dist/hugo-<ver>-py3-none-linux_aarch64.whl
```

{{< /tab >}}

{{< tab name="Windows arm64" >}}

```bash
python scripts/generate_meson_cross.py --goos windows --goarch arm64 --output cross.ini
python -m build --wheel -Csetup-args=--cross-file=cross.ini
# builds into dist/hugo-<ver>-py3-none-win_arm64.whl
```

{{< /tab >}}

{{< tab name="macOS arm64 to macOS x86_64" >}}

```bash
python scripts/generate_meson_cross.py --goos darwin --goarch amd64 --output cross.ini
python -m build --wheel -Csetup-args=--cross-file=cross.ini
# builds into dist/hugo-<ver>-py3-none-macosx_26_0_x86_64.whl
```

For darwin to darwin cross-builds, you may use AppleClang `-arch <target>`.

{{< /tab >}}

{{< /tabs >}}

### Use a custom toolchain (such as, for MUSL on Linux)

To override the auto-selected compiler, say, to link against MUSL instead of GLIBC on Linux, you can set `CC`/`CXX` manually and disable the Zig target auto-selection by the build backend:

```bash
export CC="$(python -m ziglang) cc -target x86_64-linux-musl"
export CXX="$(python -m ziglang) c++ -target x86_64-linux-musl"
python -m build --wheel \
  -Csetup-args=--cross-file=cross-linux-amd64.ini \
  -Csetup-args=-Duse_zig=disabled
```

Linkage against MUSL is not tested in CI at this time, but it should work in theory. The official Hugo binaries do not link against MUSL for a variety of reasons including the size of the binary and the prevalence of the GLIBC C standard library.

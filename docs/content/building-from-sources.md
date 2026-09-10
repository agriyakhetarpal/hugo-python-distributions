+++
title = 'Building from sources'
date = 2024-04-06T23:28:15+05:30
draft = false
toc = true
+++

The build is driven by [Meson](https://mesonbuild.com/) and [meson-python](https://meson-python.readthedocs.io/). Building the standard + withdeploy edition of Hugo from source requires the following dependencies:

1. The [Git](https://git-scm.com/downloads) version control system
2. [Python](https://www.python.org/downloads/) ≥ 3.10

The Hugo binary is pure Go and is compiled with `CGO_ENABLED=0`, so no C or C++ compiler is needed on any platform, including for cross-compilation.

`meson-python`, `meson`, `ninja`, and `go-bin` (the Go compiler toolchain) are all pulled in as build-time dependencies automatically by the build backend, so you do not need to install them yourself.

Clone the repository and install the package:

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

Cross-compilation is indicated by and happens entirely via a [Meson cross file](https://mesonbuild.com/Cross-compilation.html). This cross-build definition file has a `[host_machine]` section that describes the target platform, and Meson and meson-python both consume it:

- `meson` gets to know what the target is,
- `meson.build` gets to know what `GOOS`/`GOARCH` combination is to be passed on to the Go build, based on said combination. Since the binary is pure Go, the Go toolchain handles the cross-compilation on its own and no cross-compilers are involved.
- There is an in-tree PEP 517 build backend wrapper around `meson-python` at [`scripts/hugo_meson_python_wrapper.py`](https://github.com/agriyakhetarpal/hugo-python-distributions/blob/main/scripts/hugo_meson_python_wrapper.py), that sets `_PYTHON_HOST_PLATFORM` to tag the wheel correctly for cross-compilation scenarios, both
  across platforms or across architectures on the same platform.

### 1. Generate a cross file

There is a helper that ships with the project:

```bash
python scripts/generate_meson_cross_file.py --goos linux --goarch arm64 --output cross-linux-arm64.ini
```

The output is a small `[host_machine]` description that meson-python and Meson both consume. You can also write one by hand if you'd like – see the [Meson cross file documentation](https://mesonbuild.com/Cross-compilation.html#cross-file).

Some cross files are already checked into the repository for convenience, in the `meson_cross_files` directory. You can use those directly, or as a reference for writing your own.

Cross-compilation for Hugo binaries is provided for the following platforms and architectures, based on `GOOS`/`GOARCH` combinations that the Go toolchain supports:

- macOS: `darwin/arm64` and `darwin/amd64`
- Linux: `linux/amd64`, `linux/arm64`, `linux/arm`, `linux/386`, `linux/ppc64le`, `linux/s390x`, and `linux/riscv64`
- Windows: `windows/amd64`, `windows/arm64`, and `windows/386`

For a list of supported distributions for Go, please run the `go tool dist list` command on your system.

### 2. Build the wheel

```bash
python -m build --wheel -Csetup-args=--cross-file=cross-linux-arm64.ini
```

Some examples are showcased below.

{{< tabs >}}

{{< tab name="Linux arm64" >}}

```bash
python scripts/generate_meson_cross_file.py --goos linux --goarch arm64 --output cross.ini
python -m build --wheel -Csetup-args=--cross-file=cross.ini
# builds into dist/hugo-<ver>-py3-none-linux_aarch64.whl
```

{{< /tab >}}

{{< tab name="Windows arm64" >}}

```bash
python scripts/generate_meson_cross_file.py --goos windows --goarch arm64 --output cross.ini
python -m build --wheel -Csetup-args=--cross-file=cross.ini
# builds into dist/hugo-<ver>-py3-none-win_arm64.whl
```

{{< /tab >}}

{{< tab name="macOS arm64 to macOS x86_64" >}}

```bash
python scripts/generate_meson_cross_file.py --goos darwin --goarch amd64 --output cross.ini
python -m build --wheel -Csetup-args=--cross-file=cross.ini
# builds into dist/hugo-<ver>-py3-none-macosx_26_0_x86_64.whl
```

{{< /tab >}}

{{< /tabs >}}

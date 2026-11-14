+++
title = 'Building from sources'
date = 2024-04-06T23:28:15+05:30
draft = false
toc = true
+++

The build is driven by [hatchling](https://hatch.pypa.io/latest/) and a small custom build hook at [`scripts/hatch_build.py`](https://github.com/agriyakhetarpal/hugo-python-distributions/blob/main/scripts/hatch_build.py), which compiles Hugo with the Go toolchain and places the binary inside the wheel. Building the deploy edition of Hugo (the `withdeploy` build tag) from source requires the following dependencies:

1. The [Git](https://git-scm.com/downloads) version control system
2. [Python](https://www.python.org/downloads/) ≥ 3.10

The Hugo binary is pure Go and is compiled with `CGO_ENABLED=0`, so no C or C++ compiler is needed on any platform, including for cross-compilation.

`hatchling` and `go-bin` (the Go compiler toolchain) are pulled in as build-time dependencies automatically by the build backend, so you do not need to install them yourself. On 32-bit ARM Linux, where `go-bin` has no wheels, the official Go toolchain is downloaded directly instead. This is what makes the [piwheels](https://www.piwheels.org/project/hugo/) builds work.

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

The Go build and module caches are kept in a temporary directory and removed after each build. To reuse them across builds, point the `HUGO_BUILD_CACHE` environment variable at a directory of your choice.

## Cross-compiling for different architectures

Since the binary is purely in Go, the Go toolchain handles cross-compilation on its own. No cross-compiler toolchains are involved. The target is selected with the `goos` and `goarch` [config settings](https://peps.python.org/pep-0517/#config-settings), which an in-tree build backend wrapper at [`scripts/hugo_build_backend.py`](https://github.com/agriyakhetarpal/hugo-python-distributions/blob/main/scripts/hugo_build_backend.py) translates into the `GOOS` and `GOARCH` environment variables for the Go build. The build hook then tags the wheel for the target platform, both across platforms and across architectures on the same platform.

Cross-compilation for Hugo binaries is provided for the following platforms and architectures, based on `GOOS`/`GOARCH` combinations that the Go toolchain supports:

- macOS: `darwin/arm64` and `darwin/amd64`
- Linux: `linux/amd64`, `linux/arm64`, `linux/arm`, `linux/386`, `linux/ppc64le`, `linux/s390x`, and `linux/riscv64`
- Windows: `windows/amd64`, `windows/arm64`, and `windows/386`

For a list of supported distributions for Go, please run the `go tool dist list` command on your system.

### Build the wheel

```bash
python -m build --wheel -Cgoos=linux -Cgoarch=arm64
```

Setting `GOOS` and `GOARCH` in the environment works as well, if you have a tool that does not work with config settings. If only one of the two is given, the other defaults to the platform of the running interpreter.

Some examples are showcased below.

{{< tabs >}}

{{< tab name="Linux arm64" >}}

```bash
python -m build --wheel -Cgoos=linux -Cgoarch=arm64
# builds into dist/hugo-<ver>-py3-none-linux_aarch64.whl
```

{{< /tab >}}

{{< tab name="Windows arm64" >}}

```bash
python -m build --wheel -Cgoos=windows -Cgoarch=arm64
# builds into dist/hugo-<ver>-py3-none-win_arm64.whl
```

{{< /tab >}}

{{< tab name="macOS arm64 to macOS x86_64" >}}

```bash
python -m build --wheel -Cgoos=darwin -Cgoarch=amd64
# builds into dist/hugo-<ver>-py3-none-macosx_<deployment target>_x86_64.whl
```

The macOS deployment target in the tag comes from the `MACOSX_DEPLOYMENT_TARGET` environment variable if set. Otherwise, it comes from the running macOS version.

{{< /tab >}}

{{< /tabs >}}

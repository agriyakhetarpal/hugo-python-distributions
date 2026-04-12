+++
title = 'Building from sources'
date = 2024-04-06T23:28:15+05:30
draft = false
toc = true
+++

Building the extended + withdeploy edition of Hugo from source requires the following dependencies:

1. The [Go](https://go.dev/doc/install) toolchain
2. The [Git](https://git-scm.com/downloads) version control system
3. A C/C++ compiler, such as [GCC](https://gcc.gnu.org/) or [Clang](https://clang.llvm.org/)

Windows users can use the [Chocolatey package manager](https://chocolatey.org/) in order to use the [MinGW compiler](https://chocolatey.org/packages/mingw). After installing Chocolatey, run the following command in an elevated terminal prompt:

```bash
choco install mingw
```

Then, clone the repository and run the build script:

{{< tabs >}}

{{< tab name="Linux/macOS" >}}

```bash
git clone --recurse-submodules https://github.com/agriyakhetarpal/hugo-python-distributions@main
python -m venv venv
source venv/bin/activate
```

{{< /tab >}}

{{< tab name="Windows" >}}

```cmd
git clone --recurse-submodules https://github.com/agriyakhetarpal/hugo-python-distributions@main
py -m venv venv
venv\Scripts\activate.bat
```

{{< /tab >}}

{{< /tabs >}}

and then install the package in the current directory:

```bash
pip install .
```

or perform an editable installation via the following command:

```bash
pip install -e .
```

## Cross-compiling for different architectures

{{< callout type="warning" >}}
Cross-compilation is experimental and may not be stable or reliable for all use cases. If you encounter any issues, please feel free to [open an issue](https://github.com/agriyakhetarpal/hugo-python-distributions/issues/new).
{{</ callout >}}

This project is capable of cross-compiling Hugo binaries for various platforms and architectures. Cross-compilation is provided for the following platforms:

1. macOS; for the `arm64` and `amd64` architectures via the Xcode toolchain,
2. Linux; for the `arm64`, `amd64`, `s390x`, and `ppc64le` architectures via the Zig toolchain, and
3. Windows; for the `amd64`, `arm64`, and `x86` architectures via the Zig toolchain.

{{< tabs >}}

{{< tab name="macOS" >}}
Say, on an Intel-based (x86_64) macOS machine:

```bash
export GOARCH="arm64"
pip install .  # or pip install -e .
```

This will build a macOS `arm64` binary distribution of Hugo that can be used on Apple Silicon-based (`arm64`) macOS machines. To build a binary distribution for the _target_ Intel-based (`x86_64`) macOS platform on the _host_ Apple Silicon-based (`arm64`) macOS machine, you can use the following command:

```bash
export GOARCH="amd64"
pip install .  # or pip install -e .
```

{{< /tab >}}

{{< tab name="Linux" >}}
Set the `USE_ZIG`, `GOOS`, and `GOARCH` environment variables prior to installing the package:

Say, on an `amd64` Linux machine:

```bash
export USE_ZIG="1"
export GOOS="linux"
export GOARCH="arm64"
pip install .  # or pip install -e .
```

will cross-compile a Linux arm64 binary distribution of Hugo that can be used on the targeted arm64 Linux machines. To build a binary distribution for the _target_ `amd64` Linux platform on the _host_ `arm64` Linux machine, set the targets differently:

```bash
export USE_ZIG="1"
export GOOS="linux"
export GOARCH="amd64"
pip install .  # or pip install -e .
```

This creates dynamic linkage for the built Hugo binary with a system-provided GLIBC. If you wish to statically link the binary with MUSL, change the `CC` and `CXX` environment variables as follows:

```bash
export CC="zig cc -target x86_64-linux-musl"
export CXX="zig c++ -target x86_64-linux-musl"
```

Linkage against MUSL is not tested in CI at this time, but it should work in theory. The official Hugo binaries do not link against MUSL for a variety of reasons including the size of the binary and the prevalence of the GLIBC C standard library.
{{< /tab >}}

{{< tab name="Windows" >}}
Set these environment variables prior to installing the package (note the use of `set` instead of `export` on Windows):

Say, on an `amd64` Windows machine:

```cmd
set USE_ZIG="1"
set GOOS="windows"
set GOARCH="arm64"
pip install .  # or pip install -e .
```

will cross-compile a Windows `arm64` binary distribution of Hugo that can be used on the targeted `arm64` Windows machines, and so on for the `x86` architecture:

```cmd
set USE_ZIG="1"
set GOOS="windows"
set GOARCH="386"
pip install .  # or pip install -e .
```

{{< /tab >}}

{{< /tabs >}}

For a list of supported distributions for Go, please run the `go tool dist list` command on your system. For a list of supported targets for Zig, please refer to the [Zig documentation](https://ziglang.org/documentation/) for more information or run the `zig targets` command on your system.

{{< callout type="info" >}}
Cross-compilation for a target platform and architecture from a different host platform and architecture is also possible, but it remains largely untested at this time. Currently, the [Zig compiler toolchain](https://ziglang.org/) is known to work for cross-platform, cross-architecture compilation.
{{</ callout >}}

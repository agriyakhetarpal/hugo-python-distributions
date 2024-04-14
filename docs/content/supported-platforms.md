+++
title = 'Supported platforms'
date = 2024-04-06T23:27:31+05:30
draft = false
toc = true
+++

A subset of the platforms supported by Hugo itself are supported by these wheels for `hugo` via `hugo-python-distributions`. The plan is to support as many platforms as possible with Python wheels and platform tags. Please refer to the following table for a list of supported platforms and architectures:

| Platform | Architecture    | Support                         |
| -------- | --------------- | ------------------------------- |
| macOS    | x86_64 (Intel)  | ✅                              |
| macOS    | arm64 (Silicon) | ✅                              |
| Linux    | amd64           | ✅                              |
| Linux    | arm64           | ✅                              |
| Windows  | x86_64          | ✅                              |
| Windows  | arm64           | 💡 Experimental support [^1]    |
| Windows  | x86             | 💡 Experimental support [^1]    |
| DragonFlyBSD | amd64       | ❌ Will not receive support[^2] |
| FreeBSD  | amd64           | ❌ Will not receive support[^2] |
| OpenBSD  | amd64           | ❌ Will not receive support[^2] |
| NetBSD   | amd64           | ❌ Will not receive support[^2] |
| Solaris  | amd64           | ❌ Will not receive support[^2] |

[^1]: Support for 32-bit (i686) and arm64 architectures on Windows is made possible through the use of the [Zig compiler toolchain](https://ziglang.org/) that uses the LLVM ecosystem. These wheels are experimental owing to the use of `cibuildwheel` and cross-compilation and may not be stable or reliable for all use cases, and are not officially supported by the Hugo project at this time. Please refer to the [Building from source](#building-from-source) section for more information on how to build Hugo for these platforms and architectures, since these wheels are not currently pushed to PyPI for general availability – however, they are tested regularly in CI. If you need support for these platforms, please consider building from source or through a CI provider.

[^2]: Support for these platforms is not possible to include because of i. the lack of resources to test and build for them and ii. the lack of support for these platform specifications in Python packaging standards and tooling. If you need support for these platforms, please consider downloading the [official Hugo binaries](https://github.com/gohugoio/hugo/releases).

#### Cross-compiling for different architectures

{{< callout type="warning" >}}
Cross-compilation is experimental and may not be stable or reliable for all use cases. If you encounter any issues with cross-compilation, please feel free to [open an issue](https://github.com/agriyakhetarpal/hugo-python-distributions/issues/new).
{{</ callout >}}

This project is capable of cross-compiling Hugo binaries for various platforms and architectures and it can be used as follows. Cross-compilation is provided for the following platforms:

1. macOS for the `arm64` and `amd64` architectures via the Xcode toolchain,
2. Linux for the `arm64` and `amd64` architectures via the Zig toolchain, and
3. Windows for the `arm64`, and `x86` architectures via the Zig toolchain.

Please refer to the examples below for more information on how to cross-compile Hugo for different architectures:

##### macOS

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

##### Linux

First, install [Zig](https://ziglang.org/download/) on your Linux machine, and set these environment variables prior to installing the package:

Say, on an `amd64` Linux machine:

```bash
export CC="zig cc -target aarch64-linux-gnu"
export CXX="zig c++ -target aarch64-linux-gnu"
export GOARCH="arm64"
pip install .  # or pip install -e .
```

will cross-compile a Linux arm64 binary distribution of Hugo that can be used on the targeted arm64 Linux machines. To build a binary distribution for the _target_ `amd64` Linux platform on the _host_ `arm64` Linux machine, set the targets differently:

```bash
export CC="zig cc -target x86_64-linux-gnu"
export CXX="zig c++ -target x86_64-linux-gnu"
export GOARCH="amd64"
pip install .  # or pip install -e .
```

This creates dynamic linkage for the built Hugo binary with a system-provided GLIBC. If you wish to statically link the binary with MUSL, change the `CC` and `CXX` environment variables as follows:

```bash
export CC="zig cc -target x86_64-linux-musl"
export CXX="zig c++ -target x86_64-linux-musl"
```

Linkage against MUSL is not tested in CI at this time, but it should work in theory. The official Hugo binaries do not link against MUSL for a variety of reasons including but not limited to the size of the binary and the popularity of the GLIBC C standard library and its conventions.

##### Windows

First, install [Zig](https://ziglang.org/download/) on your Windows machine, and set these environment variables prior to installing the package:

Say, on an `amd64` Windows machine:

```bash
set CC="zig cc -target aarch64-windows-gnu"
set CXX="zig c++ -target aarch64-windows-gnu"
set GOARCH="arm64"
pip install .  # or pip install -e .
```

will cross-compile a Windows `arm64` binary distribution of Hugo that can be used on the targeted `arm64` Windows machines (note the use of `set` instead of `export` on Windows), and so on for the `x86` architecture:

```bash
set CC="zig cc -target x86-windows-gnu"
set CXX="zig c++ -target x86-windows-gnu"
set GOARCH="386"
pip install .  # or pip install -e .
```

For a list of supported distributions for Go, please run the `go tool dist list` command on your system. For a list of supported targets for Zig, please refer to the [Zig documentation](https://ziglang.org/documentation/) for more information or run the `zig targets` command on your system.

> [!TIP]
> Cross-compilation for a target platform and architecture from a different host platform and architecture is also possible, but it remains largely untested at this time. Currently, the [Zig compiler toolchain](https://ziglang.org/) is known to work for cross-platform, cross-architecture compilation.

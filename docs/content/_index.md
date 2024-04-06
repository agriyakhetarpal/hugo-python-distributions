+++
title = ''
date = 2024-04-06T22:34:36+05:30
draft = false
toc = true
[cascade]
    type = 'docs'
+++

# Documentation for `hugo-python-distributions`

This webpage is meant to serve the documentation for the `hugo-python-distributions` project, which aims to provide a distribution
channel for the extended version of the Hugo static site generator through `pip`-installable binaries (wheels) hosted on the [Python Package Index (PyPI)](https://pypi.org/).

## Table of contents

- [Quickstart](#quickstart)
- [Supported platforms](#supported-platforms)
- [Building from sources](building-from-sources/)
  - [Cross-compiling for different architectures](#cross-compiling-for-different-architectures)
    - [macOS](#macos)
    - [Linux](#linux)
    - [Windows](#windows)


### Quickstart

Create a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) and install the package (or install it globally on your system):

{{< tabs items="Linux/macOS,Windows" >}}

  {{< tab >}}
    ```bash
    python -m virtualenv venv
    source venv/bin/activate
    python -m pip install hugo
    ```
  {{< /tab >}}

  {{< tab >}}
    ```powershell
    py -m virtualenv venv
    venv\Scripts\activate.bat
    py -m pip install hugo
    ```
  {{< /tab >}}

{{< /tabs >}}

This example is using [`virtualenv`](https://virtualenv.pypa.io/en/latest/) to create a virtual environment, however, you can use any virtual environment manager of your choice. Some popular ones are the built-in [`venv`](https://docs.python.org/3/library/venv.html) module, [`virtualenvwrapper`](https://virtualenvwrapper.readthedocs.io/en/latest/), [`pipenv`](https://pipenv.pypa.io/en/latest/), [`conda`](https://docs.conda.io/en/latest/), [`poetry`](https://python-poetry.org/), [`pyenv`](https://github.com/pyenv/pyenv), [`uv`](https://github.com/astral-sh/uv), and so on.

This places a `hugo` installation with an executable in your virtual environment and adds an [entry point](https://packaging.python.org/en/latest/specifications/entry-points/) to it in your virtual environment's `bin` directory.

Then, you can use the `hugo` CLI commands as you would normally:

```bash
hugo version
hugo env --logLevel info
hugo new site my-new-site
hugo mod <...>
hugo --printI18nWarnings --buildDrafts server
```

and more!

Alternatively, you can install the package globally on your system:

{{< tabs items="Linux/macOS,Windows" >}}

  {{< tab >}}
    ```bash
    python3.X -m pip install hugo
    ```
  {{< /tab >}}

  {{< tab >}}
    ```powershell
    py -m pip install hugo
    ```
  {{< /tab >}}

{{< /tabs >}}

{{< callout emoji=✨ >}}

It is a great idea to use [`pipx`](https://github.com/pypa/pipx) to install or use Hugo in an isolated location without having to create a virtual environment, which will allow you to run Hugo as a command-line tool without having to install it globally on your system.

{{</ callout >}}


{{< tabs items="Install it as an app globally, Run it" >}}

  {{< tab >}}
    ```bash
    pipx install hugo
    ```
    This installs Hugo in a separate location on your system that is isolated from your global Python environment(s).
  {{< /tab >}}

  {{< tab >}}
    ```bash
    pipx run hugo version
    pipx run hugo env --logLevel info
    ```
    This runs the latest version of Hugo available on PyPI and installed through `pipx`. You can also run a specific version of Hugo through `pipx`, even if a different version is installed in whatever environment you are in:
    ```bash
    pipx run hugo==0.124.1 version
    pipx run hugo==0.124.1 env --logLevel info
    ```
  {{< /tab >}}

{{< /tabs >}}

Please refer to the [`pipx` documentation](https://pipx.pypa.io/stable/) for more information.

For more information on using Hugo and its command-line interface, please refer to the [Hugo documentation](https://gohugo.io/documentation/) and the [Hugo CLI documentation](https://gohugo.io/commands/).

### Supported platforms

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

# hugo-python-distributions

[![Actions Status][actions-badge]][actions-link]

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

<!-- SPHINX-START -->

Binaries for the extended version of the Hugo static site generator, installable via `pip`

This package provides wheels for [Hugo](https://gohugo.io/) to be used with `pip` on macOS, Linux, and Windows; for Python versions 3.8–3.12.

## What is Hugo?

[Hugo](https://gohugo.io/) is a static site generator written in [Go](https://golang.org/). It is designed to be fast and flexible, and it is used by many people and organizations for their websites, documentation, personal blogs, and so on.

## What version of `python-hugo` do I install?

This package, `python-hugo` is versioned separately and will adhere to an [amalgamation](https://jacobtomlinson.dev/posts/2023/sometimes-i-regret-using-calver/) of [CalVer](https://calver.org/) (calendar versioning) and [SemVer](https://semver.org/) (semantic versioning) software standards, which is subject to change if deemed absolutely necessary. A release for `python-hugo` will be versioned as `YY.M.PATCH` where `YY` is the year, `M` is the month, and `PATCH` is the patch number of the release. For example, `31.8.2` shall be the release for `python-hugo` on August 2031, patch number 2. This is done to avoid confusion with the versioning of Hugo itself, which uses `SemVer` – but is likely versioned according to [`0ver](https://0ver.org/) software standards based on their [versioning history](https://github.com/gohugoio/hugo/releases). A bump in the `python-hugo` version does not necessarily mean a bump in the Hugo version, and vice versa, but it is likely that a bump in the PATCH number of `python-hugo` will correspond to a new release of Hugo, as mentioned in the table below.

The version of `python-hugo` you install will correspond to a particular version of Hugo as listed in the following table in ascending order of `python-hugo` version.

<!-- NOTE: add versions to this table as we go along with releases. -->

| `python-hugo` version | Hugo (extended) version                                             |
| --------------------- | ------------------------------------------------------------------- |
| `24.1.0`              | [`0.121.1`](https://github.com/gohugoio/hugo/releases/tag/v0.121.1) |
<!-- | `24.1.1`              | [`0.121.2`](https://github.com/gohugoio/hugo/releases/tag/v0.121.2) | -->

<!-- NOTE: add versions to this table as we go along with releases. -->

If you would like to use any available version of Hugo, you don't need to worry about this and you can just install the latest version of `python-hugo` on PyPI.

If you would like to use a specific version of Hugo, you can install the corresponding version of `python-hugo` as listed in the table above.

Please refer to the section on [Supported platforms](#supported-platforms) for a list of `python-hugo`'s supported platforms and architectures. If it does, jump to the [Quickstart](#quickstart) section to get started.

## Documentation

### Quickstart

Create a virtual environment and install the package (or install it globally on your system):

```bash
python -m virtualenv venv  # (or your preferred method of creating virtual environments)
pip install hugo-python
```

This places a `hugo` executable in a `binaries` directory in your virtual environment and adds an entry point to it.

Alternatively, you can install the package globally on your system:

```bash
python3.X -m pip install hugo-python  # Unix
py -m pip install hugo-python         # Windows
```

> [!TIP]
> It is a great idea to use [`pipx`](https://github.com/pypa/pipx) to install Hugo in an isolated location without having to create a virtual environment, which will allow you to use Hugo as a command-line tool without having to install it globally on your system. Please refer to the [`pipx` documentation](https://pipx.pypa.io/stable/) for more information.

Then, you can use the `hugo` commands as you would normally:

```bash
hugo version
hugo env --logLevel info
```

```bash
hugo new site mysite
hugo --printI18nWarnings server
# and so on
...
```

Virtual environments allow multiple versions of Hugo to be installed and used side-by-side. To use a specific version of Hugo, you can specify the version when installing the package (please refer to [What version of `python-hugo` do I install?](#what-version-of-python-hugo-do-i-install) for more information):

```bash
pip install "hugo-python==24.1.0"
```

For more information on using Hugo and its command-line interface, please refer to the [Hugo documentation](https://gohugo.io/documentation/) and [Hugo CLI documentation](https://gohugo.io/commands/).

### Supported platforms

A subset of the platforms supported by Hugo itself are supported by `python-hugo`. The plan is to support as many platforms as possible with Python wheels and platform tags. Please refer to the following table for a list of supported platforms and architectures:

| Platform | Architecture    | Supported                       |
| -------- | --------------- | ------------------------------- |
| macOS    | x86_64 (Intel)  | ✅                              |
| macOS    | arm64 (Silicon) | ✅                              |
| Linux    | amd64           | ✅                              |
| Linux    | arm64           | ✅                              |
| Windows  | x86_64          | ✅                              |
| Windows  | i686            | ❌ Will not receive support[^1] |
| Windows  | arm64           | 💡 Probable[^3]                 |
| DragonFlyBSD | amd64       | ❌ Will not receive support[^2] |
| FreeBSD  | amd64           | ❌ Will not receive support[^2] |
| OpenBSD  | amd64           | ❌ Will not receive support[^2] |
| NetBSD   | amd64           | ❌ Will not receive support[^2] |
| Solaris  | amd64           | ❌ Will not receive support[^2] |

[^1]: Windows 32-bit support is possible to include, but hasn't been included due to the diminishing popularity of i686 instruction set-based systems and the lack of resources to test and build for it. If you need support for Windows 32-bit, please consider either using the official Hugo binaries or compiling from [HugoReleaser](https://github.com/gohugoio/hugoreleaser).
[^2]: Support for these platforms is not possible to include because of i. the lack of resources to test and build for them and ii. the lack of support for these platform specifications in Python packaging standards and tooling. If you need support for these platforms, please consider downloading the [official Hugo binaries](https://github.com/gohugoio/hugo/releases)
[^3]: Support for Windows ARM64 is possible to include, but `cibuildwheel` support for it is currently experimental. Hugo does not officially support Windows ARM64 at the moment, but it should be possible to build from source for it and can receive support in the future through this package.

### Building from source

Building the extended version of Hugo from source requires the following dependencies:

- [Go](https://go.dev/doc/install) toolchain
- [Git](https://git-scm.com/downloads)
- A C/C++ compiler, such as [GCC](https://gcc.gnu.org/) or [Clang](https://clang.llvm.org/)

Windows users can use the [Chocolatey package manager](https://chocolatey.org/) and use the [MinGW compiler](https://chocolatey.org/packages/mingw). After installing Chocolatey, run the following command in an elevated terminal prompt:

```bash
choco install mingw
```

Then, clone the repository and run the build script:

```bash
git clone https://github.com/agriyakhetarpal/hugo-python-distributions@main
python -m venv venv
source venv/bin/activate      # on Unix-based systems
venv\Scripts\activate.bat     # on Windows
pip install -e .              # editable installation
pip install .                 # regular installation
```

#### Cross-compiling for different architectures

> [!NOTE]
> This functionality is implemented just for macOS at the moment, but it can be extended to other platforms as well in the near future.

This package is capable of cross-compiling Hugo binaries for the same platform but different architectures and it can be used as follows.

Say, on an Intel-based (x86_64) macOS machine:

```bash
export GOARCH="arm64"
pip install .  # or pip install -e .
```

This will build a macOS arm64 binary distribution of Hugo that can be used on Apple Silicon-based (arm64) macOS machines. To build a binary distribution for the _target_ Intel-based (x86_64) macOS platform on the _host_ Apple Silicon-based (arm64) macOS machine, you can use the following command:

```bash
export GOARCH="amd64"
pip install .  # or pip install -e .
```

### Background

Binaries for the Hugo static site generator are available for download from the [Hugo releases page](https://github.com/gohugoio/hugo/releases). These binaries have to be downloaded and placed in an appropriate location on the system manually and the PATH environment variable has to be updated to include said location.

This package provides wheels for Hugo to be used with `pip` on macOS, Linux, and Windows. This allows Hugo to be installed and used in a virtual environment, which allows multiple versions of Hugo to be installed and used side-by-side in different virtual environments, where Hugo can be used as a command-line tool (a Python API is not provided at this time given the lack of such a demand for it).

#### Use cases

This package is designed to be used in the following scenarios:

- You want to use Hugo as a command-line tool, but you don't want it to be installed globally on your system or do not have the necessary permissions to do so.
- You cannot or do not want to use the official Hugo binaries
- You want to use Hugo in a virtual environment that is isolated from the rest of your system – this also allows you to install and use multiple versions of Hugo side-by-side if needed for any reason
- You want to use Hugo in a Python-based project, such as a static site generator that uses Hugo as a backend?
- You want to test a new version of Hugo without having to install it globally on your system or affecting your existing Hugo installation
- Python wheels allow for incredibly fast installation, in comparison to using other methods of installing Hugo such as system package managers
- Easier updates to the latest version of Hugo through the use of the `pip install --upgrade hugo-python` command, and automatic updates if you use a package manager such as [Poetry](https://python-poetry.org/) or [PDM](https://pdm.fming.dev/) to manage your Python dependencies or a tool such as [pipx](https://pipxproject.github.io/pipx/) to manage your command-line tools
- ...and so on

#### (Known) limitations

- It is difficult to provide wheels for all platforms and architectures (see [Supported platforms](#supported-platforms)), so this package only provides wheels for the most common ones—those supported by Python platform tags, packaging standards and tooling—it is not reasonable to do so and provide releases for other platforms owing to the limited resources available on CI systems, in this case, GitHub Actions runners. For extra platforms and architectures, please refer to the [Building from source](#building-from-source) section or consider using the [official Hugo binaries](https://github.com/gohugoio/hugo/releases) for your purpose.
- This package does not provide a Python API for Hugo, it just wraps its own command-line interface. The packaging infrastructure for this Python package is not designed to provide a Python API for Hugo, and it is not the goal of this package to provide one. If you need a Python API for Hugo, please refer to the [Hugo documentation](https://gohugo.io/documentation/) for further resources on how to use Hugo programmatically as needed.

### Licensing

This project is licensed under the terms of the [Apache 2.0 license](LICENSE). Hugo is available under Apache 2.0 (see [the Hugo license](licenses/LICENSE-hugo.txt)) as well.

<!-- Badges -->

[actions-badge]:            https://github.com/agriyakhetarpal/hugo-python-distributions/workflows/CI/badge.svg
[actions-link]:             https://github.com/agriyakhetarpal/hugo-python-distributions/actions
[pypi-link]:                https://pypi.org/project/hugo-python/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/hugo-python/
[pypi-version]:             https://img.shields.io/pypi/v/hugo-python/

# hugo-python-distributions

[actions-badge]:            https://github.com/agriyakhetarpal/hugo-python-distributions/workflows/CI/badge.svg
[cd-badge]:                 https://github.com/agriyakhetarpal/hugo-python-distributions/workflows/CD/badge.svg
[actions-link]:             https://github.com/agriyakhetarpal/hugo-python-distributions/actions
[pypi-link]:                https://pypi.org/project/hugo/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/hugo/
[pypi-version]:             https://img.shields.io/pypi/v/hugo/
[pypi-downloads-total]:     https://static.pepy.tech/badge/hugo/
[pypi-downloads-monthly]:   https://static.pepy.tech/badge/hugo/month/
[license-badge]:            https://img.shields.io/pypi/l/hugo?color=lavender
[license-link]:             https://apache.org/licenses/LICENSE-2.0
[hugo-badge]:               https://img.shields.io/badge/hugo-extended-pink.svg?style=flat&logo=hugo
[hugo-link]:                https://gohugo.io/
[docs-link]:                https://github.com/agriyakhetarpal/hugo-python-distributions/
[docs-badge]:               https://img.shields.io/badge/docs-read%20on%20GitHub-blue.svg?style=flat&logo=github

<div align="center">

| Classifiers | Description |
| ------ | ---------------- |
| Builds | [![Actions Status for CI][actions-badge]][actions-link] [![Actions status for CD][cd-badge]][actions-link] [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/agriyakhetarpal/hugo-python-distributions/main.svg)](https://results.pre-commit.ci/latest/github/agriyakhetarpal/hugo-python-distributions/main) |
| Package | [![PyPI version](https://badge.fury.io/py/hugo.svg)](https://badge.fury.io/py/hugo) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hugo) [![Downloads](https://static.pepy.tech/badge/hugo)](https://pepy.tech/project/hugo) [![Downloads per month](https://static.pepy.tech/badge/hugo/month)](https://pepy.tech/project/hugo) [![Downloads](https://static.pepy.tech/badge/hugo/week)](https://pepy.tech/project/hugo) |
| Meta | [![License][license-badge]][license-link] [![Hugo version][hugo-badge]][hugo-link] [![Documentation][docs-badge]][docs-link] [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) |

</div>

Binaries for the **extended version** of the Hugo static site generator, installable via `pip`

This project provides wheels for [Hugo](https://gohugo.io/) so that it can be used with `pip` on macOS, Linux, and Windows; for Python 3.8 and later.

> [!NOTE]
> Only the latest, stable, and to-be EOL Python versions are tested regularly. If you encounter any issues with the package on a specific Python version, please feel free to [open an issue](https://github.com/agriyakhetarpal/hugo-python-distributions/issues/new).

## What is Hugo?

[Hugo](https://gohugo.io/) is a static site generator written in [Go](https://golang.org/). It is designed to be fast and flexible, and it is used by many people and organizations for their websites, documentation, and personal blogs.

> [!NOTE]
> This distribution of `Hugo` is currently not affiliated with the official `Hugo` project. Please refer to the [Hugo documentation](https://gohugo.io/documentation/) for more information on Hugo.

## What version of `hugo` do I install?

This project, `hugo` is versioned alongside the Hugo releases and is aligned with the versioning of Hugo itself, which uses `SemVer` – but is likely versioned according to [0ver](https://0ver.org/) software standards based on their [versioning history](https://github.com/gohugoio/hugo/releases).

Binaries for `hugo` through these wheels are available for Hugo versions **0.121.2** and above, through PyPI or through releases on GitHub. If you need an older version of `hugo` that is not available through this package, please consider using the [official Hugo binaries](https://github.com/gohugoio/hugo/releases).

Please refer to the section on [Supported platforms](#supported-platforms) for a list of wheels available for supported platforms and architectures. If it does, jump to the [Quickstart](#quickstart) section to get started.

> [!WARNING]
> Owing to the limitations of overall sizing available on [PyPI](https://pypi.org/project/hugo/#history) for `hugo`, only the most recent versions of Hugo are available for download through `pip`, and older versions of these wheels will be deleted to make space for newer releases. If you need an older version of Hugo, please consider using the wheels that have been uploaded to the [GitHub releases](https://github.com/agriyakhetarpal/hugo-python-distributions/releases) page or the [official Hugo binaries](https://github.com/gohugoio/hugo/releases). The former can be done via `pip` by downloading the `.whl` file, or through `pipx` using the URL directly (recommended). For example, if you need Hugo 0.122.0, you can run `pipx install "https://github.com/agriyakhetarpal/hugo-python-distributions/releases/download/v0.122.0/hugo-0.122.0-cp311-cp311-win_amd64.whl"` to download and install the wheel for Hugo 0.122.0 on Windows for Python 3.11.

## Documentation

The documentation for this project is available at [https://agriyakhetarpal.github.io/hugo-python-distributions/](https://agriyakhetarpal.github.io/hugo-python-distributions/)

### Background

Binaries for the Hugo static site generator are available for download from the [Hugo releases page](https://github.com/gohugoio/hugo/releases). These binaries have to be downloaded and placed in an appropriate location on the system manually and the PATH environment variable has to be updated to include said location.

This project provides wheels for Hugo to be used with `pip` on macOS, Linux, and Windows. This allows Hugo to be installed and used in a virtual environment, which allows multiple versions of Hugo to be installed and used side-by-side in different virtual environments, where Hugo can be used as a command-line tool (a Python API is not provided at this time given the lack of such a demand for it).

#### Use cases

This project is designed to be used in the following scenarios:

- You want to use Hugo as a command-line tool, but you don't want it to be installed globally on your system or do not have the necessary permissions to do so.
- You cannot or do not want to use the official Hugo binaries
- You want to use Hugo in a virtual environment that is isolated from the rest of your system – this also allows you to install and use multiple versions of Hugo side-by-side if needed for any reason
- You want to use Hugo in a Python-based project, such as a static site generator that uses Hugo as a backend?
- You want to test a new version of Hugo without having to install it globally on your system or affecting your existing Hugo installation
- Python wheels allow for incredibly fast installation, in comparison to using other methods of installing Hugo such as system package managers
- Easy updates to the latest version of Hugo through the use of the `pip install --upgrade hugo` command, and automatic updates possible too if you use a package manager such as [Poetry](https://python-poetry.org/) or [PDM](https://pdm.fming.dev/) to manage your Python dependencies or a tool such as [pipx](https://pipxproject.github.io/pipx/) to manage your command-line tools
- ...and more!

#### (Known) limitations

- It is difficult to provide wheels for all platforms and architectures (see [Supported platforms](#supported-platforms)), so this project only provides wheels for the most common ones—those supported by Python platform tags, packaging standards and tooling—it is not reasonable to do so and provide releases for other platforms owing to the limited resources available on CI systems, in this case, GitHub Actions runners. For extra platforms and architectures, please refer to the [Building from source](#building-from-source) section or consider using the [official Hugo binaries](https://github.com/gohugoio/hugo/releases) for your purpose.
- This project does not provide a Python API for Hugo, it just wraps its own command-line interface. The packaging infrastructure for this Python package is not designed to provide a Python API for Hugo, and it is not the goal of this project to provide one. If you need a Python API for Hugo, please refer to the [Hugo documentation](https://gohugo.io/documentation/) for further resources on how to use Hugo programmatically as needed.

### Licensing

This project is licensed under the terms of the [Apache 2.0 license](LICENSE). Hugo is available under Apache 2.0 (see [the Hugo license](LICENSE-hugo.txt)) as well.

## Security

Please refer to the [Security policy](SECURITY.md) for this project for more information.

## Code of Conduct

This repository aims to follow the Hugo project in striving to provide a welcoming and inclusive environment for all contributors, regardless of their background and identity. Please refer to the [Code of Conduct](CODE_OF_CONDUCT.md) for more information that applies to all interactions in this repository and its associated spaces. It is reliant on the [Contributor Covenant](https://www.contributor-covenant.org/) for its guidelines and conforms to version 2.1.

For requesting help, reporting bugs, or requesting features that are specific to Hugo's functionalities, please refer to the [Hugo Discourse forum](https://discourse.gohugo.io/t/requesting-help/9132). For requesting help for `hugo-python-distributions`, please feel free to [open an issue](https://github.com/agriyakhetarpal/hugo-python-distributions/issues/new) in this repository.

### Footnotes

- This project is currently not affiliated with the official Hugo project. Please refer to the [Hugo documentation](https://gohugo.io/documentation/) for more information on Hugo.
- The author of this project: @agriyakhetarpal, would like to express a token of gratitude to the owner of the `Hugo` package on PyPI (@nariman) for their kind gesture of granting access to take over the package name with the underlying provisions of PEP 541. This way, it allows users to install the package using the same name as the official Hugo project, which undoubtedly provides for a better user experience and convenience to users of this package when compared to the previous package name, `python-hugo`.

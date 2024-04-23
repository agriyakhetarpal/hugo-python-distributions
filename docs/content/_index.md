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
- [Supported platforms](supported-platforms/)
- [Building from sources](building-from-sources/)
  - [Cross-compiling for different architectures](supported-platforms/#cross-compiling-for-different-architectures)
    - [macOS](supported-platforms/#macos)
    - [Linux](supported-platforms/#linux)
    - [Windows](supported-platforms/#windows)


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

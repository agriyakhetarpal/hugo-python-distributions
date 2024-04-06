+++
title = 'Building from sources'
date = 2024-04-06T23:28:15+05:30
draft = false
toc = true
+++

Building the extended version of Hugo from source requires the following dependencies:

1. The [Go](https://go.dev/doc/install) toolchain
2. The [Git](https://git-scm.com/downloads) version control system
3. A C/C++ compiler, such as [GCC](https://gcc.gnu.org/) or [Clang](https://clang.llvm.org/)

Windows users can use the [Chocolatey package manager](https://chocolatey.org/) in order to use the [MinGW compiler](https://chocolatey.org/packages/mingw). After installing Chocolatey, run the following command in an elevated terminal prompt:

```bash
choco install mingw
```

Then, clone the repository and run the build script:

{{< tabs items="Linux/macOS,Windows" >}}

    {{< tab >}}

    ```bash
    git clone https://github.com/agriyakhetarpal/hugo-python-distributions@main
    python -m venv venv
    source venv/bin/activate
    ```

    {{< /tab >}}

    {{< tab >}}

    ```cmd
    git clone https://github.com/agriyakhetarpal/hugo-python-distributions@main
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

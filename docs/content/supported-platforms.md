+++
title = 'Supported platforms'
date = 2024-04-06T23:27:31+05:30
draft = false
toc = true
+++

A subset of the platforms supported by Hugo itself are supported by these wheels for `hugo` via `hugo-python-distributions`. The plan is to support as many platforms as possible with Python wheels and platform tags. Please refer to the following table for a list of supported platforms and architectures:

| Platform     | Architecture    | Support                                |
| ------------ | --------------- | -------------------------------------- |
| macOS        | x86_64 (Intel)  | ✅ macOS 10.13 (High Sierra) and later |
| macOS        | arm64 (Silicon) | ✅ macOS 11.0 (Big Sur) and later      |
| Linux        | amd64           | ✅ glibc 2.17 and later                |
| Linux        | arm64           | ✅ glibc 2.17 and later                |
| Linux        | s390x           | ✅ glibc 2.17 and later                |
| Linux        | ppc64le         | ✅ glibc 2.17 and later                |
| Windows      | x86_64          | ✅                                     |
| Windows      | arm64           | ✅💡 Experimental support [^1]         |
| Windows      | x86             | ✅💡 Experimental support [^1]         |
| DragonFlyBSD | amd64           | ❌ Will not receive support[^2]        |
| FreeBSD      | amd64           | ❌ Will not receive support[^2]        |
| OpenBSD      | amd64           | ❌ Will not receive support[^2]        |
| NetBSD       | amd64           | ❌ Will not receive support[^2]        |
| Solaris      | amd64           | ❌ Will not receive support[^2]        |

[^1]: Support for 32-bit (i686) and arm64 architectures on Windows is made possible through the use of the [Zig compiler toolchain](https://ziglang.org/) that uses the LLVM ecosystem. These wheels are experimental owing to the use of cross-compilation and may not be stable or reliable for all use cases, and are not officially supported by the Hugo project at this time. Hence, while these are published to PyPI for general availability, they are considered experimental. Please refer to the [Building from source](building-from-sources/) section for more information on how to build Hugo for these platforms and architectures locally. If you need official support for these platforms or face any bugs, please consider contacting the Hugo authors by [opening an issue](https://github.com/gohugoio/hugo/issues/new).

[^2]: Support for these platforms is not possible to include because of i. the lack of resources to test and build for them and ii. the lack of support for these platform specifications in Python packaging standards and tooling. If you need support for these platforms, please consider downloading the [official Hugo binaries](https://github.com/gohugoio/hugo/releases) for their non-extended editions.

For instructions on building Hugo for a specific platform or architecture, including cross-compilation, see [Building from sources](../building-from-sources/).

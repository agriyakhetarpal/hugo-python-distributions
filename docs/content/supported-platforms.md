+++
title = 'Supported platforms'
date = 2024-04-06T23:27:31+05:30
draft = false
toc = true
+++

A subset of the platforms supported by Hugo itself are supported by these wheels for `hugo` via `hugo-python-distributions`. The plan is to support as many platforms as possible with Python wheels and platform tags. Please refer to the following table for a list of supported platforms and architectures:

| Platform     | Architecture    | Support                           |
| ------------ | --------------- | --------------------------------- |
| macOS        | x86_64 (Intel)  | ✅ macOS 13.0 (Ventura) and later |
| macOS        | arm64 (Silicon) | ✅ macOS 13.0 (Ventura) and later |
| Linux        | amd64           | ✅ glibc 2.17 and later           |
| Linux        | arm64           | ✅ glibc 2.17 and later           |
| Linux        | s390x           | ✅ glibc 2.17 and later           |
| Linux        | ppc64le         | ✅ glibc 2.17 and later           |
| Linux        | armv6l          | ✅ via piwheels [^3]              |
| Linux        | armv7l          | ✅ via piwheels [^3]              |
| Windows      | x86_64          | ✅                                |
| Windows      | arm64           | ✅                                |
| Windows      | x86             | ✅ [^1]                           |
| DragonFlyBSD | amd64           | ❌ Will not receive support[^2]   |
| FreeBSD      | amd64           | ❌ Will not receive support[^2]   |
| OpenBSD      | amd64           | ❌ Will not receive support[^2]   |
| NetBSD       | amd64           | ❌ Will not receive support[^2]   |
| Solaris      | amd64           | ❌ Will not receive support[^2]   |

[^1]: The 32-bit (i686) wheels for Windows are cross-compiled with the Go toolchain from 64-bit runners, and the resulting binaries are tested in CI through the WoW64 compatibility layer. This target is not officially supported by the Hugo project, which does not publish 32-bit Windows binaries. Please refer to the [Building from source](building-from-sources/) section for more information on how to build Hugo for other platforms and architectures locally. If you need official support for a platform or face any bugs, please consider contacting the Hugo authors by [opening an issue](https://github.com/gohugoio/hugo/issues/new).

[^3]: Wheels for Raspberry Pi (ARMv6l and ARMv7l) are built and distributed by [piwheels](https://www.piwheels.org/project/hugo/), a community service that provides pre-compiled Python wheels for Raspberry Pi devices. These are not published to PyPI and are only available via the piwheels index. To install, add `--extra-index-url https://www.piwheels.org/simple` to your `pip install` command, or configure it permanently in your `pip.conf`. Raspberry Pi OS includes this index by default.

[^2]: Support for these platforms is not possible to include because of i. the lack of resources to test and build for them and ii. the lack of support for these platform specifications in Python packaging standards and tooling. If you need support for these platforms, please consider downloading the [official Hugo binaries](https://github.com/gohugoio/hugo/releases) for these platforms.

For instructions on building Hugo for a specific platform or architecture, including cross-compilation, see [Building from sources](../building-from-sources/).

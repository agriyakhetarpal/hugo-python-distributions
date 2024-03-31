## A security policy for `hugo-python-distributions`

This project has a security policy that aims to cover various potential attack vectors. It is important to note that it is a downstream distribution of Hugo, and as such, it inherits the security policy of the upstream project. This document aims to provide a concise overview of the security policy for this project and some privacy considerations.

It is to be noted that:

1. The PyPI releases as well as GitHub Releases artifacts are signed with Sigstore via GitHub Actions prior to uploads. To verify the authenticity of the release, please refer to the [Sigstore documentation](https://github.com/sigstore/sigstore-python#verifying-signatures-from-github-actions).
2. All releases are built from the upstream Hugo source code, and the build process is automated via GitHub Actions. The build process is reproducible, and the source code is fetched from the upstream repository.
3. Interactions with this project do not collect any user data, and the only data that is collected is by GitHub and PyPI for the purposes of maintaining the project and based on their terms of service and privacy policies.
4. The project does not contain any telemetry or tracking code, and no data is sent to any third-party servers upon usage of the project.
5. The project's distribution does not, and does not plan to, contain any third-party dependencies, and the only dependencies required are the ones that are required to build the project from source. These are not downloaded when the project is installed via wheels from PyPI, which are signed as mentioned in point 1.
6. The project does not contain any code through dependencies or vendors that is executed at runtime. The Hugo binary that is built from the upstream source code upon usage after the project is installed is the only binary that is possible to be executed.
7. The project uses [Dependabot](https://github.com/dependabot) to keep dependencies such as GitHub Actions up-to-date on a daily basis, and utilises commit hashes to pin dependencies to specific versions to mitigate risks, such as those that can arise from dependency confusion and software supply chain attacks, in an approach that bears similarities to that of the upstream Hugo project.

### Reporting a vulnerability

Please read through [Hugo's security policy](https://github.com/gohugoio/hugo/blob/master/SECURITY.md) for more information and please report Hugo-specific issues through this communication channel.

### Plan of action

This project shall strive to make an accompanying downstream release to address any security issues that are reported and confirmed upstream within 48 hours of the upstream release that addresses the issue.

### Disclosure policy

In case this project in specific is affected by a security issue, please open an issue to discuss ways to coordinate the disclosure process with the maintainer, which shall preferably rely over a secure communication channel to ensure the confidentiality of the information. Reporting issues publicly is discouraged until a fix is available – therefore, please prefer to report issues privately through a security advisory on GitHub.

### History

No security issues have been reported so far, and no security advisories have been issued. Shall any security issue be reported, it will be documented here on grounds of fairness and transparency.

### Support and suggestions

Suggestions and feedback on this approach are welcome. If you have any suggestions or need support, please feel free to [open an issue](https://github.com/agriyakhetarpal/hugo-python-distributions/issues/new).

### Acknowledgements

This security policy is inspired by the security policy of the upstream Hugo project, and the author would like to thank the maintainers of the Hugo project for their efforts in maintaining a secure project and for conforming to best practices for the security of the project and the safety of its users.

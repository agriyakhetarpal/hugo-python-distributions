## hugo-python-distributions (`Hugo`) v${VERSION}

This v${VERSION} release is a packaging-side patch over [Hugo v${HUGO_VERSION}](https://github.com/gohugoio/hugo/releases/tag/v${HUGO_VERSION}) and does not include any changes to Hugo itself. For the changes incorporated into Hugo, please refer to the [release notes for Hugo v${HUGO_VERSION}](https://github.com/gohugoio/hugo/releases/tag/v${HUGO_VERSION}).

The release can be installed and used with any of the following commands:

```bash
# either install it
pip install hugo
pipx install hugo
uv pip install hugo
uv tool install hugo

# or run it directly
pipx run hugo
uv run hugo
uvx hugo
```

on Linux (amd64, aarch64, s390x, ppc64le), macOS (amd64, arm64), and Windows (amd64, arm64, i686).
${CHANGES_SECTION}
**Full range of commits**: https://github.com/agriyakhetarpal/hugo-python-distributions/compare/${PREVIOUS_TAG}...v${VERSION}

## Update Hugo to v${LATEST_VERSION}

This is an automated PR to update Hugo from v${CURRENT_VERSION} to v${LATEST_VERSION} (${RELEASE_TYPE} release).

### Changes

- Hugo version updated from v${CURRENT_VERSION} to v${LATEST_VERSION}

### Hugo v${LATEST_VERSION} release notes

https://github.com/gohugoio/hugo/releases/tag/v${LATEST_VERSION}

### Release checklist

- [ ] Check the release notes for any interesting changes, and if the Go version has been updated (if so, update the Go version in `ci.yml` and `cd.yml` manually)
- [ ] Merge this PR
- [ ] Run `nox -s tag -- v${LATEST_VERSION}` locally to create a signed tag
- [ ] Push the tag: `git push origin v${LATEST_VERSION}` — the CD workflow will build and publish the release automatically

## Update Hugo to v${LATEST_VERSION}

This is an automated PR to update Hugo from v${CURRENT_VERSION} to v${LATEST_VERSION} (${RELEASE_TYPE} release).

### Changes

- Hugo version updated from ${CURRENT_VERSION} to ${LATEST_VERSION}
${GO_UPDATE_NOTE}

### Hugo release notes

https://github.com/gohugoio/hugo/releases/tag/v${LATEST_VERSION}

### Release checklist

- [ ] Merge this PR
- [ ] Run `nox -s tag -- ${LATEST_VERSION}` locally to create a signed tag
- [ ] Push the tag: `git push origin v${LATEST_VERSION}`
- [ ] Run `nox -s release -- ${LATEST_VERSION}` to create the GitHub release (or create it manually)

from __future__ import annotations

import re
import string
import subprocess
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()
REPO = "agriyakhetarpal/hugo-python-distributions"

nox.options.sessions = ["lint", "tests"]


@nox.session
def lint(session: nox.Session) -> None:
    """
    Run the linter.
    """
    session.install("pre-commit")
    session.run(
        "pre-commit", "run", "--all-files", "--show-diff-on-failure", *session.posargs
    )


@nox.session(name="venv", reuse_venv=True)
def venv(session: nox.Session) -> None:
    """Create a virtual environment and install wheels from a specified folder into it."""
    folder = "dist" if session.interactive else "wheelhouse"
    session.log(f"Installing wheels from {folder}")
    for file in DIR.joinpath(folder).glob("*.whl"):
        session.install(file)
        session.run("hugo", "version")
        session.run("hugo", "env", "--logLevel", "debug")


def _get_version(session: nox.Session) -> str:
    """Extract version from session posargs or setup.py."""
    if session.posargs:
        return session.posargs[0].lstrip("v")
    content = (DIR / "setup.py").read_text()
    match = re.search(r'HUGO_VERSION = "([0-9.]+)"', content)
    if not match:
        session.error("Could not determine version. Pass it as: nox -s tag -- 0.157.0")
    return match.group(1)


def _get_previous_tag(current_tag: str) -> str:
    result = subprocess.run(
        ["git", "tag", "--sort=-v:refname"],
        capture_output=True,
        text=True,
        check=True,
    )
    tags = result.stdout.strip().splitlines()
    for i, t in enumerate(tags):
        if t == current_tag and i + 1 < len(tags):
            return tags[i + 1]
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", f"{current_tag}^"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@nox.session(default=False)
def tag(session: nox.Session) -> None:
    """Create a signed, annotated tag for a release.

    Usage: nox -s tag -- 0.157.0
    """
    version = _get_version(session)
    tag_name = f"v{version}"
    tag_message = f"hugo-python-distributions, version {version}"

    result = subprocess.run(
        ["git", "tag", "-l", tag_name], capture_output=True, text=True, check=False
    )
    if tag_name in result.stdout:
        session.error(f"Tag {tag_name} already exists")

    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if branch != "main":
        session.warn(f"You are on branch '{branch}', not 'main'. Proceed with caution.")

    session.log(f"Creating signed tag {tag_name}: {tag_message}")
    session.run(
        "git",
        "tag",
        "-s",
        "-a",
        tag_name,
        "-m",
        tag_message,
        external=True,
    )
    session.log(f"Tag {tag_name} created. Push it with: git push origin {tag_name}")


@nox.session(default=False)
def release(session: nox.Session) -> None:
    """Create a GitHub release with formatted release notes.

    Usage: nox -s release -- 0.157.0
    """
    version = _get_version(session)
    tag_name = f"v{version}"

    previous_tag = _get_previous_tag(tag_name)
    is_patch = int(version.split(".")[2]) > 0
    template_name = "patch.md" if is_patch else "stable.md"
    template_path = DIR / "release_notes" / template_name
    template = string.Template(template_path.read_text())

    commit_log = subprocess.run(
        [
            "git",
            "log",
            f"{previous_tag}...HEAD",
            "--pretty=format:- %s by @%an in %H",
            "--no-merges",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if commit_log:
        changes_section = f"\n## Changes that made it to this release\n\n{commit_log}\n"
    else:
        changes_section = ""

    substitutions = {
        "VERSION": version,
        "PREVIOUS_TAG": previous_tag,
        "CHANGES_SECTION": changes_section,
    }

    body = template.substitute(substitutions)

    session.log(f"Creating GitHub release for {tag_name}")
    session.run(
        "gh",
        "release",
        "create",
        tag_name,
        "--title",
        tag_name,
        "--notes",
        body,
        external=True,
    )
    session.log(f"Release {tag_name} created!")

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()
REPO = "agriyakhetarpal/hugo-python-distributions"
DOCS_DIR = DIR / "docs"

nox.options.sessions = ["lint"]
nox.options.verbose = True
nox.options.default_venv_backend = "uv|virtualenv"


@nox.session
def lint(session: nox.Session) -> None:
    """
    Run the linter.
    """
    session.install("prek")
    session.run("prek", "-a", *session.posargs)


@nox.session(default=False, reuse_venv=True)
def editable(session: nox.Session) -> None:
    """Smoke test console and module entry points from an editable install."""
    build_deps = nox.project.load_toml("pyproject.toml")["build-system"]["requires"]
    session.install(*build_deps)
    session.install("--no-build-isolation", "-ve", ".")
    session.run("python", "-m", "hugo", "version")
    session.run("hugo", "version")


@nox.session(default=False, reuse_venv=True)
def docs(session: nox.Session) -> None:
    """Build the documentation website.

    Pass -- serve to start a live-reloading development server instead.
    """
    session.install(".")

    if session.posargs == ["serve"]:
        session.run("hugo", "server", "--source", str(DOCS_DIR))
    else:
        session.run("hugo", "--minify", "--source", str(DOCS_DIR))


def _get_version(session: nox.Session) -> str:
    """Extract version from session posargs or meson.build."""
    if session.posargs:
        return session.posargs[0].lstrip("v")
    content = (DIR / "meson.build").read_text()
    match = re.search(r"version\s*:\s*'([0-9.]+)'", content)
    if not match:
        session.error("Could not determine version. Pass it as: nox -s tag -- 0.157.0")
    return match.group(1)


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

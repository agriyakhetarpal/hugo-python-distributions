from __future__ import annotations

from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()

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

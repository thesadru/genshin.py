"""Nox file."""

from __future__ import annotations

import logging
import pathlib
import typing

import nox

nox.options.sessions = ["reformat", "lint", "type-check", "verify-types", "test"]
nox.options.reuse_existing_virtualenvs = True
PACKAGE = "genshin"
GENERAL_TARGETS = ["./noxfile.py", "./genshin", "./tests"]
PYRIGHT_ENV = {"PYRIGHT_PYTHON_FORCE_VERSION": "latest"}
UV_RUN_EXTRA = ("uv", "run", "--isolated", "--no-dev", "--extra")
UV_RUN_NO_ISOLATE = ("uv", "run", "--no-dev", "--extra")

LOGGER = logging.getLogger("nox")


def isverbose() -> bool:
    """Whether the verbose flag is set."""
    return LOGGER.getEffectiveLevel() == logging.DEBUG - 1


def verbose_args() -> typing.Sequence[str]:
    """Return --verbose if the verbose flag is set."""
    return ["--verbose"] if isverbose() else []


@nox.session()
def docs(session: nox.Session) -> None:
    """Generate docs for this project using Pdoc."""
    output_directory = pathlib.Path("./docs/pdoc/")
    session.log("Building docs into %s", output_directory)

    session.run(*UV_RUN_NO_ISOLATE, "docs", "pdoc3", "--html", PACKAGE, "-o", str(output_directory), "--force")
    session.log("Docs generated: %s", output_directory / "index.html")


@nox.session()
def lint(session: nox.Session) -> None:
    """Run this project's modules against the pre-defined flake8 linters."""
    session.run(*UV_RUN_EXTRA, "lint", "ruff", "check", *GENERAL_TARGETS, *verbose_args())


@nox.session()
def reformat(session: nox.Session) -> None:
    """Reformat this project's modules to fit the standard style."""
    session.run(*UV_RUN_EXTRA, "reformat", "black", *GENERAL_TARGETS, *verbose_args())
    # sort __all__ and format imports
    session.run(
        *UV_RUN_EXTRA,
        "reformat",
        "ruff",
        "check",
        "--select",
        "RUF022,I",
        "--fix",
        "--preview",
        *GENERAL_TARGETS,
        *verbose_args(),
    )
    # fix all fixable linting errors
    session.run(*UV_RUN_EXTRA, "reformat", "ruff", "check", "--fix", *GENERAL_TARGETS, *verbose_args())


@nox.session(name="test")
def test(session: nox.Session) -> None:
    """Run this project's tests using pytest."""
    session.run(
        *UV_RUN_EXTRA,
        "pytest",
        "--extra",
        "all",
        "pytest",
        "--asyncio-mode=auto",
        "-r",
        "sfE",
        *verbose_args(),
        "--cov",
        PACKAGE,
        "--cov-report",
        "term",
        *session.posargs,
    )


@nox.session(name="type-check")
def type_check(session: nox.Session) -> None:
    """Statically analyse and veirfy this project using pyright and mypy."""
    session.run(*UV_RUN_EXTRA, "typecheck", "--extra", "all", "pyright", PACKAGE, *verbose_args(), env=PYRIGHT_ENV)
    session.run(*UV_RUN_EXTRA, "typecheck", "--extra", "all", "mypy", PACKAGE, *verbose_args())


@nox.session(name="verify-types")
def verify_types(session: nox.Session) -> None:
    """Verify the "type completeness" of types exported by the library using pyright."""
    session.run(
        *UV_RUN_EXTRA,
        "typecheck",
        "--extra",
        "all",
        "pyright",
        "--verifytypes",
        PACKAGE,
        "--ignoreexternal",
        *verbose_args(),
        env=PYRIGHT_ENV,
    )


@nox.session(python=False)
def prettier(session: nox.Session) -> None:
    """Run prettier on markdown files."""
    session.run("prettier", "-w", "*.md", "docs/*.md", "*.yml")

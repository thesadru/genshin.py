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

LOGGER = logging.getLogger("nox")


def isverbose() -> bool:
    """Whether the verbose flag is set."""
    return LOGGER.getEffectiveLevel() == logging.DEBUG - 1


def verbose_args() -> typing.Sequence[str]:
    """Return --verbose if the verbose flag is set."""
    return ["--verbose"] if isverbose() else []


def install_requirements(session: nox.Session, *requirements: str, literal: bool = False) -> None:
    """Install requirements."""
    if not literal and all(requirement.isalpha() for requirement in requirements):
        files = ["requirements.txt"] + [f"./genshin-dev/{requirement}-requirements.txt" for requirement in requirements]
        requirements = ("pip", *tuple(arg for file in files for arg in ("-r", file)))

    session.install("--upgrade", *requirements, silent=not isverbose())


@nox.session()
def docs(session: nox.Session) -> None:
    """Generate docs for this project using Pdoc."""
    install_requirements(session, "docs")

    output_directory = pathlib.Path("./docs/pdoc/")
    session.log("Building docs into %s", output_directory)

    session.run("pdoc3", "--html", PACKAGE, "-o", str(output_directory), "--force")
    session.log("Docs generated: %s", output_directory / "index.html")


@nox.session()
def lint(session: nox.Session) -> None:
    """Run this project's modules against the pre-defined flake8 linters."""
    install_requirements(session, "lint")
    session.run("ruff", "check", *GENERAL_TARGETS, *verbose_args())


@nox.session()
def reformat(session: nox.Session) -> None:
    """Reformat this project's modules to fit the standard style."""
    install_requirements(session, "reformat")
    session.run("python", "-m", "black", *GENERAL_TARGETS, *verbose_args())
    # sort __all__ and format imports
    session.run(
        "python",
        "-m",
        "ruff",
        "check",
        "--preview",
        "--select",
        "RUF022,I",
        "--fix",
        *GENERAL_TARGETS,
        *verbose_args(),
    )
    # fix all fixable linting errors
    session.run("ruff", "check", "--fix", *GENERAL_TARGETS, *verbose_args())


@nox.session(name="test")
def test(session: nox.Session) -> None:
    """Run this project's tests using pytest."""
    install_requirements(session, "pytest")

    session.run(
        "pytest",
        "--asyncio-mode=auto",
        "-r",
        "sfE",
        *verbose_args(),
        "--cov",
        PACKAGE,
        "--cov-report",
        "term",
        "--cov-report",
        "html:coverage_html",
        "--cov-report",
        "xml",
        *session.posargs,
    )


@nox.session(name="type-check")
def type_check(session: nox.Session) -> None:
    """Statically analyse and veirfy this project using pyright and mypy."""
    install_requirements(session, "typecheck")
    session.run("pyright", PACKAGE, *verbose_args(), env=PYRIGHT_ENV)
    session.run("mypy", PACKAGE, *verbose_args())


@nox.session(name="verify-types")
def verify_types(session: nox.Session) -> None:
    """Verify the "type completeness" of types exported by the library using pyright."""
    install_requirements(session, ".", "--force-reinstall", "--no-deps")
    install_requirements(session, "typecheck")

    session.run("pyright", "--verifytypes", PACKAGE, "--ignoreexternal", *verbose_args(), env=PYRIGHT_ENV)


@nox.session(python=False)
def prettier(session: nox.Session) -> None:
    """Run prettier on markdown files."""
    session.run("prettier", "-w", "*.md", "docs/*.md", "*.yml")

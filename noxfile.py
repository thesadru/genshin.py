"""Nox file."""
from __future__ import annotations

import logging
import pathlib
import typing

import nox

nox.options.sessions = ["reformat", "lint", "type-check", "test", "verify-types"]
nox.options.reuse_existing_virtualenvs = True
PACKAGE = "genshin"
GENERAL_TARGETS = ["./noxfile.py", "./genshin", "./tests"]
PYRIGHT_ENV = {"PYRIGHT_PYTHON_FORCE_VERSION": "latest"}

LOGGER = logging.getLogger("nox")


def _try_find_option(session: nox.Session, *names: str) -> typing.Optional[str]:
    args_iter = iter(session.posargs)

    for arg in args_iter:
        if arg in names:
            return next(args_iter)

    return None


def install_requirements(session: nox.Session, *requirements: str, literal: bool = False) -> None:
    """Install requirements."""
    if not literal and all(requirement.isalpha() for requirement in requirements):
        files = ["requirements.txt"] + [f"./genshin-dev/{requirement}-requirements.txt" for requirement in requirements]
        requirements = tuple(arg for file in files for arg in ("-r", file))

    verbose = LOGGER.getEffectiveLevel() == logging.DEBUG - 1  # OUTPUT

    session.install("--upgrade", *requirements, silent=not verbose)


@nox.session()
def docs(session: nox.Session) -> None:
    """Generate docs for this project using Pdoc."""
    install_requirements(session, "docs")

    output_directory = pathlib.Path(_try_find_option(session, "-o", "--output") or "./docs/pdoc/")
    session.log("Building docs into %s", output_directory)

    session.run("pdoc3", "--html", PACKAGE, "-o", str(output_directory), "--force")
    session.log("Docs generated: %s", output_directory / "index.html")


@nox.session()
def lint(session: nox.Session) -> None:
    """Run this project's modules against the pre-defined flake8 linters."""
    install_requirements(session, "lint")
    session.run("flake8", *GENERAL_TARGETS)


@nox.session()
def reformat(session: nox.Session) -> None:
    """Reformat this project's modules to fit the standard style."""
    install_requirements(session, "reformat")
    session.run("black", *GENERAL_TARGETS)
    session.run("isort", *GENERAL_TARGETS)

    session.log("sort-all")
    LOGGER.disabled = True
    session.run("sort-all", *map(str, pathlib.Path(PACKAGE).glob("**/*.py")), success_codes=[0, 1])
    LOGGER.disabled = False


@nox.session(name="test")
def test(session: nox.Session) -> None:
    """Run this project's tests using pytest."""
    install_requirements(session, "pytest")

    args: typing.List[str] = session.posargs.copy()
    if "--cooperative" in args:
        args += ["-p", "no:asyncio"]
    else:
        args += ["--asyncio-mode=auto"]

    session.run(
        "pytest",
        "--cov=" + PACKAGE,
        "--cov-report",
        "html:coverage_html",
        "--cov-report",
        "xml:coverage.xml",
        *args,
    )


@nox.session(name="type-check")
def type_check(session: nox.Session) -> None:
    """Statically analyse and veirfy this project using pyright and mypy."""
    install_requirements(session, "typecheck")
    session.run("python", "-m", "pyright", PACKAGE, env=PYRIGHT_ENV)
    session.run("python", "-m", "mypy", PACKAGE)


@nox.session(name="verify-types")
def verify_types(session: nox.Session) -> None:
    """Verify the "type completeness" of types exported by the library using pyright."""
    install_requirements(session, ".", "--force-reinstall", "--no-deps")
    install_requirements(session, "typecheck")
    session.run("python", "-m", "pyright", "--verifytypes", PACKAGE, "--ignoreexternal", env=PYRIGHT_ENV)


@nox.session(python=False)
def prettier(session: nox.Session) -> None:
    """Run prettier on markdown files."""
    session.run("prettier", "-w", "*.md", "docs/*.md", "*.yml")

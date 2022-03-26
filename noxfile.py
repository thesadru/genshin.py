"""Nox file."""
from __future__ import annotations

import logging
import pathlib
import typing

import nox

nox.options.sessions = ["reformat", "lint", "type-check", "test"]
nox.options.reuse_existing_virtualenvs = True
PACKAGE = "genshin"
GENERAL_TARGETS = ["./noxfile.py", "./genshin", "./tests"]

nox_logger = logging.getLogger(nox.__name__)


def _try_find_option(session: nox.Session, *names: str) -> typing.Optional[str]:
    args_iter = iter(session.posargs)

    for arg in args_iter:
        if arg in names:
            return next(args_iter)

    return None


def install_requirements(session: nox.Session, *requirements: str, literal: bool = False) -> None:
    """Install requirements."""
    # --no-install --no-venv leads to it trying to install in the global venv
    # as --no-install only skips "reused" venvs and global is not considered reused.
    if "--skip-install" in session.posargs:
        return

    if not literal:
        requirements = (f"./genshin-dev[{', '.join(requirements)}]",)

    session.install("--upgrade", *requirements)


@nox.session()
def docs(session: nox.Session) -> None:
    """Generate docs for this project using Pdoc."""
    install_requirements(session, "docs")

    output_directory = pathlib.Path(_try_find_option(session, "-o", "--output") or "./docs/pdoc/")
    session.log("Building docs into %s", output_directory)

    session.run(
        "pdoc3",
        "--html",
        PACKAGE,
        "--output-dir",
        str(output_directory),
        "--template-dir",
        "./docs/pdoc",
        "--force",
    )
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
    nox_logger.disabled = True
    session.run("sort-all", *map(str, pathlib.Path(PACKAGE).glob("**/*.py")), success_codes=[0, 1])
    nox_logger.disabled = False


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
    session.run("python", "-m", "pyright", PACKAGE, env={"PYRIGHT_PYTHON_FORCE_VERSION": "latest"})
    session.run("python", "-m", "mypy", PACKAGE)


@nox.session(name="verify-types")
def verify_types(session: nox.Session) -> None:
    """Verify the "type completeness" of types exported by the library using pyright."""
    install_requirements(session, "typecheck")
    session.run("python", "-m", "pyright", "--verifytypes", PACKAGE, "--ignoreexternal")


@nox.session()
def prettier(session: nox.Session) -> None:
    """Run prettier on markdown files."""
    session.run("prettier", "-w", "*.md")

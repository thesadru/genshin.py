"""Mock package to install the dev requirements."""

import pathlib
import typing

import setuptools


def parse_requirements_file(path: pathlib.Path) -> typing.List[str]:
    """Parse a requirements file into a list of requirements."""
    with open(path) as fp:
        raw_dependencies = fp.readlines()

    dependencies: typing.List[str] = []
    for dependency in raw_dependencies:
        comment_index = dependency.find("#")
        if comment_index == 0:
            continue

        if comment_index != -1:  # Remove any comments after the requirement
            dependency = dependency[:comment_index]

        if d := dependency.strip():
            dependencies.append(d)

    return dependencies


dev_directory = pathlib.Path(__file__).parent

normal_requirements = parse_requirements_file(dev_directory / ".." / "requirements.txt")

all_extras: typing.Set[str] = set()
extras: typing.Dict[str, typing.Sequence[str]] = {}

for path in dev_directory.glob("*-requirements.txt"):
    name = path.name.split("-")[0]

    requirements = parse_requirements_file(path)

    all_extras = all_extras.union(requirements)
    extras[name] = requirements

extras["all"] = list(all_extras)


setuptools.setup(name="genshin-dev", install_requires=normal_requirements, extras_require=extras)

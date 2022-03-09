"""Mock package to install the dev requirements."""
import pathlib
import typing

import setuptools


def parse_requirements_file(path: pathlib.Path) -> typing.Sequence[str]:
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


all_extras: typing.Set[str] = set()
extras: typing.Dict[str, typing.Sequence[str]] = {}

for path in pathlib.Path(".").glob("*-requirements.txt"):
    name = str(path)[: -len("-requirements.txt")]

    requirements = parse_requirements_file(path)
    all_extras = all_extras.union(requirements)

    extras[name] = requirements

extras["all"] = list(all_extras)

setuptools.setup(name="genshin-dev", extras_require=extras)

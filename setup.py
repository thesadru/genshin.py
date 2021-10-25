from setuptools import setup, find_packages

setup(
    name="genshin",
    version="0.0.2",
    author="thesadru",
    author_email="thesadru@gmail.com",
    description="An API wrapper for Genshin Impact.",
    keywords="api wrapper mihoyo genshin genshin-impact".split(),
    url="https://github.com/thesadru/genshin.py",
    project_urls={
        "Documentation": "https://thesadru.github.io/genshin.py",
        "Issue tracker": "https://github.com/thesadru/genshin.py/issues",
    },
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    install_requires=["aiohttp", "pydantic", "yarl", "typing-extensions"],
    extras_require={
        "all": ["cachetools", "aioredis", "browser-cookie3", "typer"],
        "cookies": ["browser-cookie3"],
        "cache": ["cachetools", "aioredis"],
        "cli": ["typer", "browser-cookie3"],
        "test": ["pytest", "pytest-asyncio", "cachetools"],
        "doc": ["mkdocs-material", "pdoc"],
    },
    include_package_data=True,
    package_data={"genshin": ["py.typed"]},
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    entry_points="""
        [console_scripts]
        genshin=genshin.__main__:app[cli]
    """,
)

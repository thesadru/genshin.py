"""Run setuptools."""

from setuptools import find_packages, setup

setup(
    name="genshin",
    version="1.7.1",
    author="thesadru",
    author_email="thesadru@gmail.com",
    description="An API wrapper for Genshin Impact.",
    keywords="hoyoverse mihoyo genshin genshin-impact honkai".split(),
    url="https://github.com/thesadru/genshin.py",
    project_urls={
        "Documentation": "https://thesadru.github.io/genshin.py",
        "Issue tracker": "https://github.com/thesadru/genshin.py/issues",
    },
    packages=find_packages(exclude=["tests.*"]),
    python_requires=">=3.8",
    install_requires=["aiohttp", "pydantic"],
    extras_require={
        "all": ["browser-cookie3", "rsa", "click", "qrcode[pil]"],
        "cookies": ["browser-cookie3"],
        "auth": ["rsa", "qrcode[pil]"],
        "cli": ["click"],
    },
    include_package_data=True,
    package_data={"genshin": ["py.typed"]},
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)

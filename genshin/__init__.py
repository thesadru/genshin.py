"""Modern API wrapper for Genshin Impact built on asyncio and pydantic.

Documentation: https://thesadru.github.io/genshin.py

Source Code: https://github.com/thesadru/genshin.py
"""
from . import models  # type: ignore
from .client import *
from .constants import *
from .errors import *
from .types import *

__version__ = "1.0.0"

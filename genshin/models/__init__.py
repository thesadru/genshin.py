"""Pydantic models used by genshin.py"""

# base must be loaded first due to circular imports
import typing

from .base import *

del typing  # TODO: Fix dummy

from . import genshin, honkai
from .daily import *
from .hoyolab import *

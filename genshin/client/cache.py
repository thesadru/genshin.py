from __future__ import annotations

import json as json_
import os
from typing import *

from genshin import utils


class Cache:
    def __init__(self, static: bool = True) -> None:
        self.static = static

    @property
    def static_filename(self) -> str:
        return os.path.join(utils.get_tempdir(), "static_cache.json")

    def _get_static_cache(self) -> Dict[str, Any]:
        if not os.path.isfile(self.static_filename):
            return {}

        with open(self.static_filename, "r", encoding="utf-8") as file:
            try:
                return json_.load(file)
            except json_.JSONDecodeError:
                with open(self.static_filename, "w") as file:
                    json_.dump({}, file)

                return {}

    def get_from_static_cache(self, url: str) -> Optional[Any]:
        if not self.static:
            return None

        data = self._get_static_cache()
        return data.get(url)

    def save_to_static_cache(self, url: str, x: Any) -> None:
        if not self.static:
            return

        data = self._get_static_cache()
        data[url] = x

        with open(self.static_filename, "w", encoding="utf-8") as file:
            json_.dump(data, file, ensure_ascii=False, separators=(",", ":"))

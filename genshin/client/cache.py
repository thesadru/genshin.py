"""Cache for client."""
from __future__ import annotations

import abc
import dataclasses
import enum
import json
import time
import typing

if typing.TYPE_CHECKING:
    import aioredis

__all__ = ["BaseCache", "Cache", "RedisCache"]

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7


def _separate(values: typing.Iterable[typing.Any], sep: str = ":") -> str:
    """Separate a sequence by a separator into a single string."""
    parts: typing.List[str] = []
    for value in values:
        if value is None:
            parts.append("null")
        elif isinstance(value, enum.Enum):
            parts.append(str(value.value))
        elif isinstance(value, tuple):
            if value:
                parts.append(_separate(value))  # pyright: ignore[reportUnknownArgumentType]
        else:
            parts.append(str(value))

    return sep.join(parts)


@dataclasses.dataclass(unsafe_hash=True)
class CacheKey:
    def __str__(self) -> str:
        values = [getattr(self, field.name) for field in dataclasses.fields(self)]
        return _separate(values)


def cache_key(key: str, **kwargs: typing.Any) -> CacheKey:
    name = key.capitalize() + "CacheKey"
    fields = ["key"] + list(kwargs.keys())
    cls = dataclasses.make_dataclass(name, fields, bases=(CacheKey,), unsafe_hash=True)
    return typing.cast("CacheKey", cls(key, **kwargs))


class BaseCache(abc.ABC):
    """Base cache for the client."""

    @abc.abstractmethod
    async def get(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Get an object with a key."""

    @abc.abstractmethod
    async def set(self, key: typing.Any, value: typing.Any) -> None:
        """Save an object with a key."""

    @abc.abstractmethod
    async def get_static(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Get a static object with a key."""

    @abc.abstractmethod
    async def set_static(self, key: typing.Any, value: typing.Any) -> None:
        """Save a static object with a key."""


class NOOPCache(BaseCache):
    """NO-OP cache."""

    async def get(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Do nothing."""

    async def set(self, key: typing.Any, value: typing.Any) -> None:
        """Do nothing."""

    async def get_static(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Do nothing."""

    async def set_static(self, key: typing.Any, value: typing.Any) -> None:
        """Do nothing."""


class Cache(BaseCache):
    """Standard implementation of the cache."""

    cache: typing.Dict[typing.Any, typing.Tuple[float, typing.Any]]
    maxsize: int
    ttl: float
    static_ttl: float

    def __init__(self, maxsize: int = 1024, *, ttl: float = HOUR, static_ttl: float = DAY) -> None:
        self.cache = {}
        self.maxsize = maxsize

        self.ttl = ttl
        self.static_ttl = static_ttl

    def __len__(self) -> int:
        self._clear_cache()
        return len(self.cache)

    def _clear_cache(self) -> None:
        """Clear timed-out items."""
        # since this is always called from an async function we don't need locks
        now = time.time()

        for key, value in self.cache.copy().items():
            if value[0] < now:
                del self.cache[key]

        if len(self.cache) > self.maxsize:
            overflow = len(self.cache) - self.maxsize
            keys = list(self.cache.keys())[:overflow]

            for key in keys:
                del self.cache[key]

    async def get(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Get an object with a key."""
        self._clear_cache()

        if key not in self.cache:
            return None

        return self.cache[key][1]

    async def set(self, key: typing.Any, value: typing.Any) -> None:
        """Save an object with a key."""
        self.cache[key] = (time.time() + self.ttl, value)

        self._clear_cache()

    async def get_static(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Get a static object with a key."""
        return await self.get(key)

    async def set_static(self, key: typing.Any, value: typing.Any) -> None:
        """Save a static object with a key."""
        self.cache[key] = (time.time() + self.static_ttl, value)

        self._clear_cache()


class RedisCache(BaseCache):
    """Redis implementation of the cache."""

    redis: aioredis.Redis
    ttl: int
    static_ttl: int

    def __init__(self, redis: aioredis.Redis, *, ttl: int = HOUR, static_ttl: int = DAY) -> None:
        self.redis = redis
        self.ttl = ttl
        self.static_ttl = static_ttl

    def serialize_key(self, key: typing.Any) -> str:
        """Serialize a key by turning it into a string."""
        return str(key)

    def serialize_value(self, value: typing.Any) -> typing.Union[str, bytes]:
        """Serialize a value by turning it into bytes."""
        return json.dumps(value)

    def deserialize_value(self, value: bytes) -> typing.Any:
        """Deserialize a value back into data."""
        return json.loads(value)

    async def get(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Get an object with a key."""
        value: typing.Optional[bytes] = await self.redis.get(self.serialize_key(key))  # pyright: ignore
        if value is None:
            return None

        return self.deserialize_value(value)

    async def set(self, key: typing.Any, value: typing.Any) -> None:
        """Save an object with a key."""
        await self.redis.set(  # pyright: ignore
            self.serialize_key(key),
            self.serialize_value(value),
            ex=self.ttl,
        )

    async def get_static(self, key: typing.Any) -> typing.Optional[typing.Any]:
        """Get a static object with a key."""
        return await self.get(key)

    async def set_static(self, key: typing.Any, value: typing.Any) -> None:
        """Save a static object with a key."""
        await self.redis.set(  # pyright: ignore
            self.serialize_key(key),
            self.serialize_value(value),
            ex=self.static_ttl,
        )

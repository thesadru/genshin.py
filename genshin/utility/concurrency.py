"""Utilities for concurrency optimizations."""

from __future__ import annotations

import asyncio
import functools
import typing

__all__ = ["prevent_concurrency"]

T = typing.TypeVar("T")
AnyCallable = typing.Callable[..., typing.Any]
CallableT = typing.TypeVar("CallableT", bound=AnyCallable)


def prevent_concurrency(func: CallableT) -> CallableT:
    """Prevent function from running concurrently.

    This should be done exclusively for functions that cache their result.
    """

    def wrapper(func: AnyCallable) -> AnyCallable:
        lock: typing.Optional[asyncio.Lock] = None

        @functools.wraps(func)
        async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            nonlocal lock
            if lock is None:
                lock = asyncio.Lock()

            async with lock:
                return await func(*args, **kwargs)

        return inner

    return typing.cast("CallableT", MethodDecorator(func, wrapper))


class MethodDecorator:
    """Descriptor which applies decorators per-instance."""

    method: AnyCallable
    decorator: typing.Callable[[AnyCallable], AnyCallable]
    name: str

    def __init__(
        self,
        method: AnyCallable,
        decorator: typing.Callable[[AnyCallable], AnyCallable],
        *,
        name: typing.Optional[str] = None,
    ) -> None:
        self.method = method  # type: ignore # mypy doesn't understand methods
        self.decorator = decorator  # type: ignore # mypy doesn't understand methods
        self.name = name or self.method.__name__

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: typing.Optional[T], owner: type[T]) -> AnyCallable:
        if instance is None:
            return self.method

        func = self.decorator(self.method).__get__(instance, type(instance))  # type: ignore # mypy doesn't understand methods
        setattr(instance, self.name, func)
        return func

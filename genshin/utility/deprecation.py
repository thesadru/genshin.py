"""Deprecation decorator."""

import functools
import inspect
import typing
import warnings

__all__ = ["deprecated", "warn_deprecated"]

CallableT = typing.TypeVar("CallableT", bound=typing.Callable[..., typing.Any])


def warn_deprecated(
    obj: typing.Any,
    *,
    alternative: typing.Optional[str] = None,
    stack_level: int = 3,
) -> None:
    """Raise a deprecated warning."""
    if inspect.isclass(obj) or inspect.isfunction(obj):
        obj = f"{obj.__qualname__}"

    message = f"{obj} is deprecated and will be removed in the following version."

    if alternative is not None:
        message += f" You can use '{alternative}' instead."

    warnings.warn(message, category=DeprecationWarning, stacklevel=stack_level)


def deprecated(alternative: typing.Optional[str] = None) -> typing.Callable[[CallableT], CallableT]:
    """Mark a function as deprecated."""

    def decorator(obj: CallableT) -> CallableT:
        alternative_str = f"You can use `{alternative}` instead." if alternative else ""

        doc = inspect.getdoc(obj) or ""
        doc += (
            "\n\n"
            "!!! warning\n"
            f"    This function is deprecated and will be removed in the following version.\n"
            f"    {alternative_str}\n"
        )
        obj.__doc__ = doc

        @functools.wraps(obj)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            warn_deprecated(obj, alternative=alternative, stack_level=3)
            return obj(*args, **kwargs)

        return typing.cast("CallableT", wrapper)

    return decorator

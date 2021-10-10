from __future__ import annotations

from copy import deepcopy
from typing import *

import pydantic.fields
from pydantic.main import BaseModel, create_model, inherit_config

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

TypeT = TypeVar("TypeT", bound=Type[Any])
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)

__all__ = ["FastApiFields"]

def _issubclass(tp: Any, cls: TypeT) -> TypeGuard[TypeT]:
    if isinstance(tp, type):
        return issubclass(tp, cls)

    origin = get_origin(tp)
    return origin is not None and issubclass(origin, cls)


def fastapi_model(model: Type[BaseModelT]) -> Type[BaseModelT]:
    config: Type[Any] = type("", (), {"response_model_by_alias": False})
    config = inherit_config(config, model.Config)

    fields = {}

    for old_field in model.__fields__.values():
        t = old_field.type_

        if _issubclass(t, BaseModel):
            t = fastapi_model(t)
            if old_field.shape != pydantic.fields.SHAPE_SINGLETON:
                t = List[t]

        field = deepcopy(old_field.field_info)
        field.alias = old_field.name

        fields[old_field.name] = (t, field)

    return create_model(
        model.__name__ + '.__fastapi__',
        __config__=config,
        __module__=model.__module__,
        **fields,
    )  # type: ignore


class FastApiFields:
    @overload
    def __get__(self, obj: BaseModelT, objtype: Type[BaseModelT] = ...) -> BaseModelT:
        ...

    @overload
    def __get__(self, obj: None, objtype: Type[BaseModelT]) -> Type[BaseModelT]:
        ...

    def __get__(self, obj: Optional[BaseModelT], objtype: Type[BaseModelT] = None):
        if obj is None:
            if objtype is None:
                raise NotImplementedError("I have no idea when descriptor type is None")

            return fastapi_model(objtype)

        return fastapi_model(objtype or type(obj))(**obj.dict())

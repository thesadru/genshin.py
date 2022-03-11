import typing

import genshin

all_models: typing.Dict[typing.Type[genshin.models.APIModel], genshin.models.APIModel] = {}


def APIModel___new__(cls: typing.Type[genshin.models.APIModel], *args: typing.Any, **kwargs: typing.Any):
    self = object.__new__(cls)
    all_models[cls] = self
    return self


genshin.models.APIModel.__new__ = APIModel___new__


def test_model_reserialization():
    for cls, model in sorted(all_models.items(), key=lambda pair: pair[0].__name__):
        cls(**model.dict())

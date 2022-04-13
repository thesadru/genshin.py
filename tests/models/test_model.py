import os
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

        if hasattr(model, "as_dict"):
            getattr(model, "as_dict")()

    # dump all parsed models
    data = ",\n".join(
        f'"{cls.__name__}": {model.json(indent=4, ensure_ascii=False, models_as_dict=True)}'
        for cls, model in all_models.items()
    )
    data = "{" + data + "}"
    os.makedirs(".pytest_cache", exist_ok=True)
    with open(".pytest_cache/hoyo_parsed.json", "w", encoding="utf-8") as file:
        file.write(data)

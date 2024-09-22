# Genshin.py contributing guidelines

Contributions are always welcome and any amount of time spent on this project is greatly appreciated.

But before you get started contributing, it's recommended that you read through the following guide in-order to ensure that any pull-requests you open can be at their best from the start.

### Pipelines

The most important thing to consider while contributing towards Genshin.py is the checks the library's run against.
While these are run against all PRs by Github Actions, you can run these locally before any PR is opened using Nox.

To run the tests and checks locally you'll have to go through the following steps.

1. Ensure your current working directory is Genshin.py's top-level directory.
2. `pip install nox` to install Nox.
3. Use `nox -s` to run the default tasks.

A list of all the available tasks can be found by running `nox -l` with blue names being the tasks which are run by default when `nox -s` is called alone.
To call specific tasks you just call `nox -s name1 name2` where any number of tasks can be called at once by specifying their name after `-s`.

It's worth noting that the reformat nox task (which is run by default) will reformat additions to the project in-order to make them match the expected style and that nox will generate virtual environments for each task instead of pollution the environment it was installed into.

You may use `nox --no-install` to avoid updating dependencies every run.

### Tests

All changes contributed to this project should be tested. This repository uses pytest and `nox -s test` for an easier and less likely to be problematic way to run the tests.

If the tests are way too slow on your machine you may want to filter them using `nox -s test -- -k "foo"`. (For example `nox -s test -- -k "wish"` for only wish-related tests)

### Type checking

All contributions to this project will have to be "type-complete" and, while [the nox tasks](###Pipelines) let you check that the type hints you've added/changed are type safe,
[pyright's type-completness guidelines](https://github.com/microsoft/pyright/blob/main/docs/typed-libraries.md) and
[standard typing library's type-completness guidelines](https://github.com/python/typing/blob/master/docs/libraries.md) are
good references for how projects should be type-hinted to be type-complete.

---

**NOTES**

- This project deviates from the common convention of importing types from the typing module and instead
  imports the typing module itself to use generics and types in it like `typing.Union` and `typing.Optional`.
- Since this project supports python 3.9+, the `typing` module takes priority over `collections.abc`.
- All exported symbols should have docstrings.

---

### General enforced style

- All modules should start with imports followed by declaration of `__all__`.
- [pep8](https://www.python.org/dev/peps/pep-0008/) should be followed as much as possible with notable cases where its ignored being that [black](https://github.com/psf/black) style may override this.
- The maximum character count for a line is 120 characters.
- Only entire modules may be imported with the exception of `Aliased` and constants.
- All public modules should be explicitly imported into its packages' `__init__.py` except for utilities and individual components which should only be exposed as an entire module.
- Features should be split by API endpoint in components and by game and category in models.
- Only abstract methods may be overwritten.

### Project structure

```
genshin
│
│   constants.py    = global constants like supported languages
│   errors.py       = all errors raised in the library
│   types.py        = enums required in some endpoint parameters
│
├───client          = client used for requests
│   │   client.py       = final client made from
│   │   cache.py        = client cache
│   │   compat.py       = reverse-compatibility layer
│   │   manager.py      = cookie and auth managers
│   │   ratelimit.py    = ratelimit handler
│   │   routes.py       = routes for various endpoints
│   │
│   └───components      = separate client components separated by category
│       │   base.py         = base client without any specific routes
│       └   anything        = file or module that exports a single component
│
├───paginators      = paginators used in the library
│
├───models          = models used in the library
│   │   model.py        = base model and helper fields
│   │
│   └───any dir         = separate module for each game or category
│
└───utility         = utilities for the library
```

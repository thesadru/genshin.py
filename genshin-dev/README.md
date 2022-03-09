# genshin-dev

This is a mock package to install development dependencies for `genshin`. The aim of this package is to provide specific versions for the development utilities to ensure cross-compatibility on all machines as well as in CI.

### How to install

The general syntax is:

```bash
pip install ./genshin-dev[<options>]
```

Where `<options>` is a comma-separated list of what dependencies to install, which are automatically collected from the requirement files in this directory. Below you can find the list of available options.

### Available options

- `all`: all development dependencies
- `docs`: documentation generator dependencies
- `flake8`: flake8 and its plugins
- `pytest`: pytest and its plugins
- `reformat`: formatting tools
- `typecheck`: mypy and pyright

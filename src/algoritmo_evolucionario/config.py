"""Runtime-selectable configuration.

Call load(name) before starting the EA to switch to a different scenario.
Config files live in the configs/ sub-package; each file defines uppercase
constants. load() copies those constants into this module's namespace so
that `from . import config; config.X` always sees the current values.
"""
import importlib
from pathlib import Path

_name: str = ""


def load(name: str = "default") -> None:
    """Load a named config file from the configs/ sub-package."""
    global _name
    try:
        mod = importlib.import_module(f".configs.{name}", package=__package__)
    except ModuleNotFoundError:
        available = _list_available()
        raise SystemExit(
            f"Configuração '{name}' não encontrada. "
            f"Disponíveis: {', '.join(available) or '(nenhuma)'}"
        )
    g = globals()
    for k, v in vars(mod).items():
        if k.isupper():
            g[k] = v
    _name = name


def _list_available() -> list[str]:
    configs_dir = Path(__file__).parent / "configs"
    return sorted(
        p.stem for p in configs_dir.glob("*.py") if p.stem != "__init__"
    )


# Populate with defaults at import time so the module is always fully
# initialised, even if load() is never called explicitly.
load("default")

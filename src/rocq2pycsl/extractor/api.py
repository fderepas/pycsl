"""Backend-agnostic entry point.

`extract(path, backend=...)` returns a `GallinaModule`. The default
backend is the hand-rolled Lark parser; `backend=Backend.SERAPI` opts
into the sertop subprocess implementation (when available).
"""

from __future__ import annotations

import enum
from pathlib import Path

from .gallina import GallinaModule


class Backend(str, enum.Enum):
    LARK = "lark"
    SERAPI = "serapi"


def extract(path: str | Path, *, backend: Backend = Backend.LARK) -> GallinaModule:
    """Parse `path` and return the surface AST.

    Raises FileNotFoundError if `path` does not exist.
    Raises ValueError on parse failure with a path:line:col message.
    Raises NotImplementedError if the SerAPI backend is selected but
    sertop is not installed (with install instructions).
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"no such .v file: {path}")
    text = src.read_text()

    if backend is Backend.LARK:
        # Imported lazily so the SerAPI-only test path doesn't pay for
        # Lark grammar compilation, and vice versa.
        from .lark_backend import parse_module
        return parse_module(text, source_path=str(src))

    if backend is Backend.SERAPI:
        from .serapi_backend import parse_module
        return parse_module(text, source_path=str(src))

    raise ValueError(f"unknown backend: {backend!r}")

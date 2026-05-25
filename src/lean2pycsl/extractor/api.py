"""Backend-agnostic entry point.

`extract(path, backend=...)` returns a `LeanModule`. The default
backend is the hand-rolled Lark parser; `backend=Backend.LEAN_SCRIPT`
opts into the `lake env lean` JSON path (when implemented).
"""

from __future__ import annotations

import enum
from pathlib import Path

from .lean_ast import LeanModule


class Backend(str, enum.Enum):
    LARK = "lark"
    LEAN_SCRIPT = "lean-script"


def extract(path: str | Path, *, backend: Backend = Backend.LARK) -> LeanModule:
    """Parse `path` and return the surface AST.

    Raises FileNotFoundError if `path` does not exist.
    Raises ValueError on parse failure with a path:line:col message.
    Raises NotImplementedError if the Lean-script backend is selected
    but `lake` isn't on PATH (with install instructions).
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"no such .lean file: {path}")
    text = src.read_text()

    if backend is Backend.LARK:
        from .lark_backend import parse_module
        return parse_module(text, source_path=str(src))

    if backend is Backend.LEAN_SCRIPT:
        from .lean_script_backend import parse_module
        return parse_module(text, source_path=str(src))

    raise ValueError(f"unknown backend: {backend!r}")

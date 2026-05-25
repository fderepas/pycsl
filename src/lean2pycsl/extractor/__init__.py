"""Backend-agnostic extraction interface.

`extract(path, backend=...)` returns a `LeanModule` populated from the
given `.lean` file. Both backends share the surface AST in
`lean2pycsl.extractor.lean_ast`.
"""

from .lean_ast import (
    LApp,
    LBinOp,
    LDvd,
    LExists,
    LForall,
    LeanDef,
    LeanModule,
    LeanNode,
    LLit,
    LTheorem,
    LUnaryOp,
    LUnsupported,
    LVar,
)
from .api import Backend, extract

__all__ = [
    "Backend",
    "LApp",
    "LBinOp",
    "LDvd",
    "LExists",
    "LForall",
    "LeanDef",
    "LeanModule",
    "LeanNode",
    "LLit",
    "LTheorem",
    "LUnaryOp",
    "LUnsupported",
    "LVar",
    "extract",
]

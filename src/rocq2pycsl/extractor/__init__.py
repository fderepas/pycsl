"""Backend-agnostic extraction interface.

`extract(path, backend=...)` returns a `GallinaModule` populated from
the given `.v` file. The two backends share the surface AST in
`rocq2pycsl.extractor.gallina`.
"""

from .gallina import (
    GallinaModule,
    GallinaNode,
    GApp,
    GBinOp,
    GDivides,
    GExists,
    GForall,
    GFunctionDef,
    GLit,
    GTheorem,
    GUnaryOp,
    GUnsupported,
    GVar,
)
from .api import Backend, extract

__all__ = [
    "Backend",
    "GallinaModule",
    "GallinaNode",
    "GApp",
    "GBinOp",
    "GDivides",
    "GExists",
    "GForall",
    "GFunctionDef",
    "GLit",
    "GTheorem",
    "GUnaryOp",
    "GUnsupported",
    "GVar",
    "extract",
]

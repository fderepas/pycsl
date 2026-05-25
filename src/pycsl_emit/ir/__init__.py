"""IR — language-agnostic first-order proposition AST.

The IR is the contract between rocq2pycsl/lean2pycsl extractors and the
downstream emitter/checker. Once a converter produces these nodes, all
language-specific concerns are gone.

Node types are defined in nodes.py; pretty.py renders an IR tree for
debugging and snapshot tests.
"""

from .nodes import (
    Node,
    Var,
    Lit,
    App,
    BinOp,
    UnaryOp,
    Forall,
    Exists,
    Divides,
    Result,
    Unsupported,
    Theorem,
    FunctionDef,
)
from .pretty import pretty

__all__ = [
    "Node",
    "Var",
    "Lit",
    "App",
    "BinOp",
    "UnaryOp",
    "Forall",
    "Exists",
    "Divides",
    "Result",
    "Unsupported",
    "Theorem",
    "FunctionDef",
    "pretty",
]

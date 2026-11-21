r"""Test 9027 -- route #567 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR): `.name` (projected to `name_of`) on a value narrowed by a TUPLE-of-classes isinstance to a file record `Box` with its own `name` field; CPython Em().is_x(Box("x")) == 1
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Dict

def mutable_state(cls): return cls

@dataclass
class Box:
    name: str

@dataclass
class Crate:
    name: str

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def is_x(self, node: "ExprIR") -> int:
        if isinstance(node, (Box, Crate)):
            b = node
            if b.name == "x":
                return 1
        return 0

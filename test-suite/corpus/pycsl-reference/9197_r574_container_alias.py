r"""Test 9197 -- route #574 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR; closes route #567's named container residual): the alias goes through a list, `xs = [node]; dv = xs[0]` (a display element and a subscript are coarse edges: every attribute refused); CPython Em().is_keys_view(DictView("d", "keys")) == 1
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Dict

def mutable_state(cls): return cls

@dataclass
class DictView:
    coll: str
    kind: str

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def is_keys_view(self, node: "ExprIR") -> int:
        xs = [node]
        dv = xs[0]
        if isinstance(dv, DictView):
            if node.kind == "keys":
                return 1
        return 0

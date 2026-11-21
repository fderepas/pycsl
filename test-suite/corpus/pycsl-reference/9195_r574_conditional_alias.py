r"""Test 9195 -- route #574 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR): the alias is one arm of a conditional expression, `dv = node if c > 0 else other`: either arm may be the tested value; CPython Em().is_keys_view(DictView("d", "keys"), DictView("e", "values"), 1) == 1
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
    def is_keys_view(self, node: "ExprIR", other: "ExprIR", c: int) -> int:
        dv = node if c > 0 else other
        if isinstance(dv, DictView):
            if node.kind == "keys":
                return 1
        return 0

r"""Test 9193 -- route #574 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR): `dv` is re-bound (`dv = other; dv = node`) before the test: the closure is flow-insensitive, every binding of `dv` is an alias; CPython Em().is_keys_view(DictView("d", "keys"), DictView("e", "values")) == 1
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
    def is_keys_view(self, node: "ExprIR", other: "ExprIR") -> int:
        dv = other
        dv = node
        if isinstance(dv, DictView):
            if node.kind == "keys":
                return 1
        return 0

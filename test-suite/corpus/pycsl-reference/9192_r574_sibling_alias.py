r"""Test 9192 -- route #574 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR): two aliases of one parameter, `a = node; b = node`, the test on `a` and the read on `b` (backward to `node`, then forward to `b`); CPython Em().is_keys_view(DictView("d", "keys")) == 1
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
        a = node
        b = node
        if isinstance(a, DictView):
            if b.kind == "keys":
                return 1
        return 0

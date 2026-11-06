r"""Test 9026 -- route #567 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR): the same misprojection without the alias, `node.kind` read inside `isinstance(node, DictView)`; CPython Em().is_keys_view(DictView("d", "keys")) == 1
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
        if isinstance(node, DictView):
            if node.kind == "keys":
                return 1
        return 0

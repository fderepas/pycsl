r"""Test 9190 -- route #574 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR; witnesses-r574/h567_backward_alias.py): the BACKWARD alias `dv = node; if isinstance(dv, DictView): ... node.kind` lowered `node.kind` to `kind_of node` (route #567's closure ran forward only), so the false `ensures \result == 0` was a theorem of the model; CPython Em().is_keys_view(DictView("d", "keys")) == 1
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
        dv = node
        if isinstance(dv, DictView):
            if node.kind == "keys":
                return 1
        return 0

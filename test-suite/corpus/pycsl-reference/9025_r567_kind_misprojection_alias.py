r"""Test 9025 -- route #567 (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR; vm-irnode review toy f1, witnesses-r567/w567_kind_misproj.py): `if isinstance(node, DictView): dv = node; if dv.kind == "keys": return 1` lowered `dv.kind` to `kind_of dv`, the emit_ir constructor tag, none of whose arms is "keys", so the false `ensures \result == 0` was a theorem of the model; CPython Em().is_keys_view(DictView("d", "keys")) == 1
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
            dv = node
            if dv.kind == "keys":
                return 1
        return 0

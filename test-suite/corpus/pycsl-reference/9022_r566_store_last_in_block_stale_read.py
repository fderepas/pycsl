r"""Test 9022 -- route #566 (expected FAIL: REFUSED PYCSL-R566-EMITIR-ITEM-STORE): the store is the LAST statement of its block (nothing dropped), but the model keeps the node immutable, so `d.name` read after the `if` is the OLD "" and the callee precondition `an == ""` held; CPython Em().bump("x") passes "x"
"""
# pycsl-expected: FAIL
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ requires an == ""
    #@ assigns \nothing
    def need_empty(self, an: str) -> None:
        pass

    #@ assigns \nothing
    def bump(self, an: str) -> None:
        d = {"type": "Var", "name": ""}
        if an == "x":
            d["name"] = an
        self.need_empty(d.name)

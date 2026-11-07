r"""Test 9021 -- route #566 (expected FAIL: REFUSED PYCSL-R566-EMITIR-ITEM-STORE): the statement after an item store into an emit_ir node is a `raise`; with the continuation dropped `#@ no_exception \all` held of a body that always raises ValueError in CPython
"""
# pycsl-expected: FAIL
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ assigns \nothing
    def mk(self, k: str) -> "ExprIR":
        return {"type": "Var", "name": k}

    #@ no_exception \all
    #@ assigns \nothing
    def bump(self, an: str) -> None:
        d = self.mk(an)
        d["act_name"] = an
        raise ValueError("after the store")

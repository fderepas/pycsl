r"""Test 9020 -- route #566 (expected FAIL: PROVED at base, REFUSED PYCSL-R566-EMITIR-ITEM-STORE; vm-irnode review toy f2o, witnesses-r566/w566_dropped_tail_precond.py): `d = self.mk(an); d["act_name"] = an; self.need_empty(an)` in a @mutable_state class; the store lowered to `()` and the rest of the block (the callee precondition `an == ""`) vanished; CPython Em().bump("x") violates need_empty's precondition
"""
# pycsl-expected: FAIL
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ assigns \nothing
    def mk(self, k: str) -> "ExprIR":
        return {"type": "Var", "name": k}

    #@ requires an == ""
    #@ assigns \nothing
    def need_empty(self, an: str) -> None:
        pass

    #@ assigns \nothing
    def bump(self, an: str) -> None:
        d = self.mk(an)
        d["act_name"] = an
        self.need_empty(an)

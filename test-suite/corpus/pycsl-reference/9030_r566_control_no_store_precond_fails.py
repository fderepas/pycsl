r"""Test 9030 -- route #566 (control, expected FAIL: the same program as 9020 WITHOUT the store; the violated callee precondition `an == ""` is reported at base and at HEAD, PyCSL-R167 sub-goal)
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
        self.need_empty(an)

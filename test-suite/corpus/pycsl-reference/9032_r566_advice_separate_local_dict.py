r"""Test 9032 -- route #566 (control / advice, expected PASS): the refusal's second advice followed -- the extra data lives in a separate local `Dict[str, str]`, whose store and read-back are modelled
"""
# pycsl-expected: PASS
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ assigns \nothing
    def mk(self, k: str) -> "ExprIR":
        return {"type": "Var", "name": k}

    #@ ensures \result == an
    #@ assigns \nothing
    def bump(self, an: str) -> str:
        d = self.mk(an)
        extra: Dict[str, str] = {}
        extra["act_name"] = an
        return extra["act_name"]

# f2o_control: same as f2o WITHOUT the emit_ir store -- the precondition violation MUST be reported.
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def mk(self, k: str) -> "ExprIR":
        return {"type": "Var", "name": k}

    #@ requires an == ""
    #@ ensures True
    #@ assigns \nothing
    def need_empty(self, an: str) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def bump(self, an: str) -> None:
        d = self.mk(an)
        self.need_empty(an)

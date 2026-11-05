# f2o: the continuation after `<emit_ir>[k] = v` is dropped, so a CALL after the store whose
# precondition is violated is never checked. CPython: Em().bump("x") calls need_empty("x")
# which violates `requires an == ""`. PyCSL must report a precondition failure; if it reports
# SUCCESS the dropped continuation is a fail-OPEN.
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
        d["act_name"] = an
        self.need_empty(an)

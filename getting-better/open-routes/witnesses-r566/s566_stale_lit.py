# staleness probe (dict-literal emit_ir local): store LAST in its block, then `.name` read after the block.
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
        d = {"type": "Var", "name": ""}
        if an == "x":
            d["name"] = an
        self.need_empty(d.name)

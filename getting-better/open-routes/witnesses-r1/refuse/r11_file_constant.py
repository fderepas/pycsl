# R1 REFUSE (#567): a file-defined record `Constant` tested bare. CPython: 1 under `ensures \result == 0`.
from dataclasses import dataclass

def mutable_state(cls): return cls

@dataclass
class Constant:
    value: int
    kind: str

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        if isinstance(elt, Constant) and isinstance(elt.value, (int, float)):
            if elt.kind == "keys":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(Constant(5, "keys"))
    print("VIOLATION contract" if r != 0 else "result", r)

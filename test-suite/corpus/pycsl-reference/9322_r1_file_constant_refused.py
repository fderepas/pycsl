r"""Test 9322 -- R1 RED TEAM (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base and HEAD, every model): (#567): a file-defined record `Constant` tested bare. CPython: 1 under `ensures \result == 0`.
"""
# pycsl-expected: FAIL
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

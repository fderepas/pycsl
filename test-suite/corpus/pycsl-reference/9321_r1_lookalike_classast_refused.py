r"""Test 9321 -- R1 RED TEAM (expected FAIL: REFUSED PYCSL-R567-EMITIR-ATTR-ON-NONIR at base and HEAD, every model): (#579): a FILE-defined `class ast` with a nested `Constant` record is not resolved. CPython: 1 under `ensures \result == 0`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

def mutable_state(cls): return cls

class ast:
    @dataclass
    class Constant:
        value: int
        kind: str

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, elt: "ExprIR") -> int:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float)):
            if elt.kind == "keys":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f(ast.Constant(5, "keys"))
    print("VIOLATION contract" if r != 0 else "result", r)
